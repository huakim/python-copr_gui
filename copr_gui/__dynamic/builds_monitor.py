from ...static.spec_types import (
    DateTimePath,
    SafePath,
    ItemPath,
    IfPath,
    DefPath)

from .monitor import ItemStore, MonitorCommon
from . import uistatusbar
from ...static.spec_types import default_true
from ...static.new_build_settings import getNewBuildFields
from .monitor_helper import additional_types, create_new_build, run_monitor

from .monitor import ContextCommon


class ContextBuildsMenu(ContextCommon):
    def __init__(self, parent, obj):
        super().__init__(
            parent, ["Show result", "Show chroots", "Clone", "Stop", "Drop"], obj
        )

    def on_clone_option(self, event):
        obj = self.obj.object
        parent = self.parent
        vals = BuildChrootsMonitor.add_default_values(parent, obj)
        parent.add_action(vals)

    def show_json_title(self):
        id = self.obj.object["id"]
        return f"Json of build {id}"

    def on_show_result_option(self, event):
        obj = self.obj.object
        url = f'{obj["repo_url"]}/srpm-builds/0{obj["id"]}'
        uistatusbar.browser(url)

    def on_show_chroots_option(self, event):
        name = self.obj[1]
        parent = self.parent
        run_monitor(BuildChrootsMonitor, None, parent.client, name, filter_args={})

    def on_stop_option(self, event):
        self.parent.button_stop_clicked(None, [self.obj.object["id"]])

    def on_drop_option(self, event):
        self.parent.drop_action([self.obj])


class ContextBuildChrootsMenu(ContextCommon):
    def __init__(self, parent, obj):
        super().__init__(parent, ["Show result"], obj)

    def show_json_title(self):
        return f"Json of build chroot {self.obj[1]}"

    def on_show_result_option(self, event):
        url = self.obj.object["result_url"]
        uistatusbar.browser(url)


class BuildsMonitor(MonitorCommon):
    def edit_cell(self, build):
        run_monitor(BuildChrootsMonitor, self, self.client, build["id"])

    def refresh_object(self, obj):
        client = self.client

        def build(obj):
            build = client.build_proxy.get(obj["id"])
            self.add([build])

        uistatusbar.execute_data_with_progress(
            [obj], build, "transferring", f'Refresh build with id {obj["id"]}'
        )

    def add(self, package):
        owner = self.owner
        project = self.project
        package = [
            i
            for i in package
            if (i["ownername"] == owner and i["projectname"] == project)
        ]
        return MonitorCommon.add(self, package)

    def configure(self, client, owner, project):
        self.client = client
        self.owner = owner
        self.project = project

    def get_title(self):
        return f"Builds of {self.owner}/{self.project}"

    def menu_cell_item(self, package, column):
        if column == 1:
            context_menu = ContextBuildsMenu(self, package)
            self.PopupMenu(context_menu)

    def add_default_values(self):
        return {
            "bootstrap": "default",
            "ownername": self.owner,
            "projectname": self.project,
            "timeout": "36000",
            "chroots": default_true,
            "packages": default_true,
        }

    def add_settings(self):
        chroots = self.get_chroots()
        pkgs = getNewBuildFields(chroots, additional_types, [])
        return pkgs

    def add_build_json(self, build):
        if not isinstance(build, list):
            build = [build]
        self.add(build)

    @staticmethod
    def add_package_title():
        return "New build"

    def add_build(self, settings):
        client = self.client
        chroots = settings["chroots"].true()
        settings["chroots"] = chroots
        try:
            build = create_new_build(client, settings)
        except Exception as e:
            uistatusbar.error(str(e), "Error when build", self)
            return None
        self.add_build_json(build)
        return build

    def run_add(self, settings):
        uistatusbar.execute_data_with_progress(
            [settings], self.add_build, "transferring", "Add build"
        )

    def get_element_list(self):
        ret = self.cached_client().build_proxy.get_list(self.owner, self.project)
        return ret

    def button_stop_clicked(self, event, items=None):
        if items is None:
            items = self.model.GetItemsByCheck()
            items = [i.object["id"] for i in items]
        count = len(items)
        if count > 0:
            if count > 1:
                label = f"Are you sure (stop {count} builds)?"
            else:
                label = f"Are you sure (stop build with id {items[0]})?"
            if uistatusbar.question(label, "Question", self):
                cancel = self.client.build_proxy.cancel
                add = self.add_build_json

                def build():
                    for i in items:
                        try:
                            i = cancel(i)
                            add(i)
                            yield i
                        except Exception:
                            yield None

                uistatusbar.execute_with_progress(
                    build(), count, "transferring", "Build package"
                )

    def drop_one(self, item):
        proxy = self.client.build_proxy
        item = item["id"]
        try:
            proxy.cancel(item)
        except Exception:
            pass
        return proxy.delete_list([item])

    def __init__(self, parent, config_args, filter_args=None, **kwargs):
        MonitorCommon.__init__(
            self,
            parent,
            ["Stop"],
            [
                "Build Id",
                "Package Name",
                "Package Version",
                {"name": "DateTime of Start", "type": "date"},
                {"name": "DateTime of End", "type": "date"},
                "Status",
            ],
            **kwargs,
        )
        none = DefPath("")
        zero = DefPath(0)
        src = "source_package"
        id = SafePath(IfPath(ItemPath("id"), zero), zero)
        name = SafePath(IfPath(ItemPath(src, "name"), none), none)
        ver = SafePath(IfPath(ItemPath(src, "version"), none), none)
        ston = DateTimePath(SafePath(IfPath(
            ItemPath("started_on"), zero), zero))
        enon = DateTimePath(SafePath(IfPath(
            ItemPath("ended_on"), zero), zero))
        state = SafePath(IfPath(ItemPath("state"), none), none)
        store = ItemStore((id, id, name, ver, ston, enon, state))
        self.initialize(store, config_args, filter_args)


class BuildChrootsMonitor(BuildsMonitor):

    def refresh_object(self, obj):
        client = self.cached_client()

        def build(obj):
            build = client.build_chroot_proxy.get(
                self.build["id"], obj["name"])
            self.add([build])

        uistatusbar.execute_data_with_progress(
            [obj],
            build,
            "transferring",
            f'Refresh build chroot with name {obj["name"]}',
        )

    def button_stop_clicked(self, event):
        return BuildsMonitor.button_stop_clicked(self, event, [self.id])

    def configure(self, client, id):
        self.client = client
        self.id = id

    def edit_cell(self, package):
        url = package["result_url"]
        if url:
            uistatusbar.browser(url)
        else:
            uistatusbar.error("Source build failed", "Error")

    def get_title(self):
        return f"Chroots of build with id {self.id}"

    def __getattr__(self, name):
        if name in ["project", "owner"]:
            return self.build[f"{name}name"]
        elif name == "build":
            id = self.id
            build = None
            try:
                build = self.__build
                if build["id"] != id:
                    raise AttributeError()
            except AttributeError:
                build = self.client.build_proxy.get(id)
                self.__build = build
            return build
        else:
            return super(BuildsMonitor, self).__getattr__(name)

    def get_element_list(self):
        ret = self.client.build_chroot_proxy.get_list(self.id)
        return ret

    def add_default_values(self, build=None):
        b = build or self.build
        b = b or {}
        b = b.get("source_package") or {}
        b = b.get("url") or None
        d = BuildsMonitor.add_default_values(self)
        if b is not None:
            d["source_type"] = "urls"
            d["source_dict"] = {"pkgs": [b]}
        return d

    add = MonitorCommon.add

    def add_build_json(self, build):
        try:
            if self.id == build["id"]:
                self.__build = build
        except Exception:
            pass

    def menu_cell_item(self, package, column):
        if column == 1:
            context_menu = ContextBuildChrootsMenu(self, package)
            self.PopupMenu(context_menu)

    def __init__(self, parent, config_args, filter_args=None, **kwargs):
        MonitorCommon.__init__(
            self,
            parent,
            [{"id": "add", "name": "Clone"}, "Stop"],
            [
                "Chroot Name",
                {"name": "DateTime of Start", "type": "date"},
                {"name": "DateTime of End", "type": "date"},
                "Status",
            ],
            editable=False,
            **kwargs,
        )
        none = DefPath("")
        zero = DefPath(0)
        name = SafePath(
            IfPath(ItemPath("name"), none), none)
        ston = DateTimePath(SafePath(IfPath(
            ItemPath("started_on"), zero), zero))
        enon = DateTimePath(SafePath(IfPath(
            ItemPath("ended_on"), zero), zero))
        state = SafePath(IfPath(ItemPath("state"), none), none)
        store = ItemStore((name, name, ston, enon, state))
        self.initialize(store, config_args, filter_args)


# def __test():
#     import uistatusbar as wx

#     app = wx.CreateApp()

#     from copr.v3 import Client

#     client = Client.create_from_config_file("~/.config/copr")
#     frame = BuildsMonitor(None, (client, "huakim", "matrix"))
#     wx.InitApp(app)
