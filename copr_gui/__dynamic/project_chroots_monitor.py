from .monitor import (
    #  DateTimePath as T,
    SafePath,
    #  MergePath as M,
    ItemPath,
    IfPath,
    DefPath,
    ItemStore,
    MonitorCommon,
)
from . import uistatusbar
from .uimonitor import ContextMenu
from .monitor_helper import show_json  # , run_monitor
from ...static.project_chroot_settings import getProjectChrootFields


class ContextProjectChrootsMenu(ContextMenu):
    def __init__(self, parent, obj):
        super().__init__(parent, ["Show json", "Edit"])
        self.obj = obj

    def on_show_json_option(self, event):
        show_json(self.obj.object, self.parent, title=f"Json of package {self.obj[1]}")

    def on_edit_option(self, event):
        self.parent.add_action(dict(self.obj.object))


# class uninitialized_dict(dict):
#    def __init__(self, initialize):
#        self.__finish = initialize#
#    def __hasitem__(self, name):


class ProjectChrootsMonitor(MonitorCommon):
    def menu_cell_item(self, package, column):
        if column == 1:
            context_menu = ContextProjectChrootsMenu(self, package)
            self.PopupMenu(context_menu)

    def refresh_object(self, obj):
        client = self.client

        def build(obj):
            build = client.project_chroot_proxy.get(
                self.owner, self.project, obj["mock_chroot"]
            )
            self.add([build])

        uistatusbar.execute_data_with_progress(
            [obj],
            build,
            "transferring",
            f'Refresh project with name {obj["mock_chroot"]}',
        )

    def configure(self, client, owner, project):
        self.client = client
        self.owner = owner
        self.project = project

    add_settings = staticmethod(getProjectChrootFields)

    def get_title(self):
        return f"Project chroot of {self.owner}/{self.project}"

    def run_add(self, settings):
        uistatusbar.execute_data_with_progress(
            [settings], self.add_project, "transferring", "Add/edit project"
        )

    def edit_cell(self, package):
        self.add_action(dict(package))

    def add_project(self, settings):
        proxy = self.client.project_chroot_proxy.edit
        try:
            pkg = proxy(**settings)
            self.add([pkg])
        except Exception as e:
            uistatusbar.error(str(e), "Error", self)

    def get_element_list(self):
        chroots = self.get_chroots()
        owner = self.owner
        project = self.project
        proxy = self.client.project_chroot_proxy
        get = proxy.get

        #   get_build = proxy.get_build_config
        def projectjsoniterator():
            for i in chroots:
                item = get(owner, project, i)
                #            item.update(get_build(owner, project, i))
                yield (item)

        return projectjsoniterator()

    def __init__(self, parent, config_args, filter_args=None, **kwargs):
        MonitorCommon.__init__(
            self, parent, [], ["Project Chroot Name"], editable=False, **kwargs
        )
        none = DefPath("")
        name = SafePath(IfPath(ItemPath("mock_chroot"), none), none)
        store = ItemStore((name, name))
        self.initialize(store, config_args, filter_args)


if __name__ == "__main__":
    import uistatusbar as wx

    app = wx.CreateApp()

    # frame = BuildChrootsMonitor(None)
    # frame = BuildsMonitor(None)
    from copr.v3 import Client

    client = Client.create_from_config_file("~/.config/copr")
    frame = ProjectChrootsMonitor(None, (client, "huakim", "matrix"))

    wx.InitApp(app)
