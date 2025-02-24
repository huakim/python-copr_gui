from .monitor import SafePath as S, MergePath as M, ItemPath as I, IfPath as C, DefPath as D, DateTimePath as T, ItemStore, MonitorCommon
from .monitor import ContextCommon
from ...static.package_settings import getPackageFields
from ...static.old_build_settings import getOldBuildFields
from . import uistatusbar
from .settings import runSettingsPanel
from ...static.spec_types import default_true
from copr import v3

from .monitor_helper import create_build_from_package, additional_types, run_monitor
from .builds_monitor import BuildsMonitor
create_base = create_build_from_package

class ContextPackagesMenu(ContextCommon):
    def __init__(self, parent, obj):
        super().__init__(parent,
            ['Show builds', 'Build', 'Edit', 'Drop'], obj)

    def show_json_title(self):
        return f'Json of package {self.obj[1]}'

    def on_show_builds_option(self, event):
        name = self.obj[1]
        parent = self.parent
        run_monitor(BuildsMonitor, None, parent.client, 
            parent.owner, parent.project, filter_args={'package_name':{
                'filter_type': 'fulltext', 'text': name, 
                'status': 'match'}})

    def on_build_option(self, event):
        self.parent.build_action([self.obj])

    def on_edit_option(self, event):
        self.parent.add_action(dict(self.obj.object))

    def on_drop_option(self, event):
        self.parent.drop_action([self.obj])
        
class PackagesMonitor(MonitorCommon):
    
    def refresh_object(self, obj):
        client = self.client
        def build(obj):
            build = client.package_proxy.get(obj['ownername'], obj['projectname'], obj['name'])
            self.add([build])
        uistatusbar.execute_data_with_progress([obj], build, 'transferring', f'Refresh package with name {obj["name"]}')

    def configure(self, client, owner, project):
        self.client = client
        self.owner = owner
        self.project = project
        
    def get_element_list(self):
        pkgs = self.client.package_proxy.get_list(self.owner, self.project, with_latest_build=True, with_latest_succeeded_build=True)
        return pkgs

    def button_build_clicked(self, event):
        items = self.model.GetItemsByCheck()
        self.build_action(items)
    
    def build_action(self, items):
        if not items:
            return
        chroots = self.get_chroots()
        frame = runSettingsPanel(getOldBuildFields(
            chroots, [i[1] for i in items]), 'Build packages', parent=self)
        items = {i[1]: i.object for i in items}
        panel = frame.panel
        panel.deploy_settings(self.add_default_values())
        client = self.client
        button = self.bind_add_button(panel, 
        lambda event: self.build_event(client, panel, frame, items))
        frame.Show()
    
    @staticmethod
    def build_event(client, panel, frame, items):
        settings = panel.extract_settings()
    #    print(settings)
        chroots = settings['chroots']
        settings['chroots'] = [i for i in chroots if chroots[i]]
        packages = settings.pop('packages')
        enabled = [i for i in packages if packages[i]]
        def build(data):
            return create_base(client, settings, items[data])
        uistatusbar.execute_data_with_progress(enabled, build, 'transferring', 'Build package')
        frame.Close()
    
    def drop_one(self, item):
        self.client.package_proxy.delete(
            item['ownername'], 
            item['projectname'], 
            item['name'])

    def add_default_values(self):
        return {'bootstrap': 'default', 
            'ownername': self.owner, 
            'projectname': self.project,
            'timeout': '36000',
            'chroots': default_true,
            'packages': default_true}

    def add_settings(self):
        pkgs = getPackageFields(additional_types, [])
        return pkgs
        
    def add_package(self, settings):
        proxy = self.client.package_proxy
        try:
            pkg = proxy.edit(**settings)
            self.add([pkg])
        except v3.exceptions.CoprNoResultException:
            try:
                pkg = proxy.add(**settings)
                self.add([pkg])
            except Exception as e:
                uistatusbar.error(str(e), 'Error when add', self)
        except Exception as e:
            uistatusbar.error(str(e), 'Error when edit', self)
    
    add=BuildsMonitor.add
            
    def get_title(self):
        return f'Packages of {self.owner}/{self.project}'

    def run_add(self, settings):
        uistatusbar.execute_data_with_progress([settings],
            self.add_package, 'transferring', 'Add/edit package')

    def edit_cell(self, package):
        self.add_action(dict(package))
            
    def menu_cell_item(self, package, column):
        if column == 1:
            context_menu = ContextPackagesMenu(self, package)
            self.PopupMenu(context_menu)
        
    def __init__(self, parent, config_args, filter_args=None, **kwargs):
        MonitorCommon.__init__(self, parent, ['Build'], [
'Package Name', 'Last Build Version', 
{'name':'Last Build Date','type':'date'}, 
'Last Build Status'], **kwargs)
        none = D('')
        zero = D(0)
        name = S(C(I('name'), none), none) 
     #   def get_build(dct, name):
     #       u= dct['builds']
     #       return u['latest_succeeded'] 
  #      get=M( I('builds'), C( I('latest_succeeded'), I('latest') ) )
        get=M( I('builds'), I('latest') )
        version = S(C(M( get, I('source_package'), I('version') ), none), none) 
        date = T(S(C(M( get, I('ended_on') ), zero), zero) )
        status = S(C(M( get, I('state') ), none), none)
        store = ItemStore( (name, name, version, date, status ))
        self.initialize(store, config_args, filter_args)
        
def __test():
    import uistatusbar as wx
    app = wx.CreateApp()
    
    from copr.v3 import Client
    client = Client.create_from_config_file('~/.config/copr')
    frame = PackagesMonitor(None, (client, 'huakim', 'matrix'))
    frame.Show()
    wx.InitApp(app)
