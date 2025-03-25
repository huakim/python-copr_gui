from ...static.spec_types import (
    # DateTimePath as T,
    SafePath,
    # MergePath as M,
    ItemPath,
    IfPath,
    DefPath)

from .monitor import ItemStore, MonitorCommon, ContextCommon
from . import uistatusbar
from .monitor_helper import run_monitor
from .packages_monitor import PackagesMonitor
from .project_chroots_monitor import ProjectChrootsMonitor
from .builds_monitor import BuildsMonitor
from ...static.project_settings import getProjectFields
from copr import v3


class ContextProjectsMenu(ContextCommon):
    def __init__(self, parent, obj):
        super().__init__(
            parent,
            ["Show builds", "Show packages", "Show chroots", "Edit", "Drop"],
            obj,
        )

    def on_show_option(self, event, monitor):
        obj = self.obj.object
        project = obj["name"]
        owner = obj["ownername"]
        parent = self.parent
        run_monitor(monitor, None, parent.client, owner, project, filter_args={})

    def on_show_builds_option(self, event):
        self.on_show_option(event, BuildsMonitor)

    def on_show_packages_option(self, event):
        self.on_show_option(event, PackagesMonitor)

    def on_show_chroots_option(self, event):
        self.on_show_option(event, ProjectChrootsMonitor)

    def show_json_title(self):
        return f"Json of package {self.obj[1]}"

    def on_edit_option(self, event):
        self.parent.add_action(dict(self.obj.object))

    def on_drop_option(self, event):
        self.parent.drop_action([self.obj])


class ProjectsMonitor(MonitorCommon):
    def menu_cell_item(self, package, column):
        if column == 1:
            context_menu = ContextProjectsMenu(self, package)
            self.PopupMenu(context_menu)

    def refresh_object(self, obj):
        client = self.client

        def build(obj):
            build = client.project_proxy.get(obj["ownername"], obj["name"])
            self.add([build])

        uistatusbar.execute_data_with_progress(
            [obj], build, "transferring", f'Refresh project with name {obj["name"]}'
        )

    def add(self, package):
        owner = self.owner
        package = [i for i in package if (i["ownername"] == owner)]
        return MonitorCommon.add(self, package)

    def drop_one(self, item):
        self.client.project_proxy.delete(item["ownername"], item["name"])

    def configure(self, client, owner):
        self.client = client
        if not owner:
            owner = client.config["username"]
        self.owner = owner

    add_settings = staticmethod(getProjectFields)

    def get_title(self):
        return f"Projects of {self.owner}"

    def add_default_values(self):
        return {"ownername": self.owner}

    def run_add(self, settings):
        uistatusbar.execute_data_with_progress(
            [settings], self.add_project, "transferring", "Add/edit project"
        )

    def edit_cell(self, package):
        self.add_action(dict(package))

    def add_project(self, settings):
        proxy = self.client.project_proxy
        try:
            pkg = proxy.edit(**settings)
            self.add([pkg])
        except v3.exceptions.CoprNoResultException:
            try:
                pkg = proxy.add(**settings)
                self.add([pkg])
            except Exception as e:
                uistatusbar.error(str(e), "Error when add", self)
        except Exception as e:
            uistatusbar.error(str(e), "Error when edit", self)

    def get_element_list(self):
        return self.client.project_proxy.get_list(self.owner)

    def __init__(self, parent, config_args, filter_args=None, **kwargs):
        MonitorCommon.__init__(
            self, parent, [], ["Project Name", "Project Description"], **kwargs
        )
        none = DefPath("")
        name = SafePath(IfPath(ItemPath("name"), none), none)
        description = SafePath(IfPath(ItemPath("description"), none), none)
        store = ItemStore((name, name, description))
        self.initialize(store, config_args, filter_args)


# if __name__ == "__main__":
#     import uistatusbar
#
#     app = uistatusbar.CreateApp()
#
#     frame = BuildChrootsMonitor(None)
#     frame = BuildsMonitor(None)
#     from copr.v3 import Client
#
#     client = Client.create_from_config_file("~/.config/copr")
#     frame = ProjectsMonitor(None, (client, "huakim"))
#     frame.Show()
#
#     uistatusbar.InitApp(app)
