from copr.v3 import Client
from .uimonitor import MonitorFrame, ContextMenu
create_config = Client.create_from_config_file
import threading
#import wx
from . import uistatusbar
from .settings import runSettingsPanel
from ...static.spec_types import AttrPath, SafePath, DefPath, IfPath, ItemPath, DateTimePath, MergePath, CallableDict
from .monitor_helper import create_filter, show_json

class ContextCommon(ContextMenu):
    def __init__(self, parent, fields, obj):
        super().__init__(parent,
            ['Show json', 'Update', *fields])
        self.obj = obj

    def on_show_json_option(self, event):
        show_json(self.obj.object, self.parent, title=self.show_json_title())

    def on_update_option(self, event):
        parent = self.parent
        obj = self.obj.object
        parent.refresh_object(obj)

class Item:
    def __repr__(self):
        return repr(self.object)

    def __str__(self):
        return str(self.object)

    def __hasitem__(self, index):
        return len(self.path) > index
    
    def __index__(self):
        return self.path[0](self.object)
    
    def __hash__(self):
        return hash(self.__index__())
    
    def __le__(self, other):
        return self.__index__() < other.__index__()
    
    def __eq__(self, other):
        if not isinstance(other, Item): return False
        return self.__index__() == other.__index__()

    def __setitem__(self, index, value):
        if index == 0:
            try:
                if value:
                    self.checked.add(self)
                else:
                    self.checked.remove(self)
            except KeyError:
                pass
                
    def __getitem__(self, index):
        if index == 0:
            return '1' if self in self.checked else ''
        else:
            return self.path[index](self.object)
    
    def __init__(self, patharray, obj, checked=None):
        self.path = patharray
        self.checked = set() if checked == None else checked
        self.object = obj

class ItemStore:
    def Clear(self):
        self.checked = set()
        self.all = dict()
    
    def Get(index):
        return self.all.get(index)
    
    def Drop(self, item):
        try:
            self.checked.remove(item)
        except KeyError:
            pass
        try:
            del self.all[item.__index__()]
        except KeyError:
            pass
            
    def __init__(self, patharray):
        self.path = patharray
        self.Clear()
    
    def newItem(self, obj):
        obj = Item(self.path, obj, set())
        return obj
    
    def addItem(self, obj):
        index = obj.__index__()
        all = self.all
        checked = self.checked
        if index in all:
            old = all[index]
            old.object = obj.object 
            obj = old
        else:
            obj.checked = checked
            all[index] = obj
        return obj

class MonitorCommon(MonitorFrame):
    def __init__(self, parents, buttons, columns, editable=True, 
            **kwargs):
     #   title=self.get_title()
        array = ['Filter', 'Update']
      #  self.custom_filter=custom_filter
        self.__data = {}
        if editable:
            array += ['Add', 'Drop']
        MonitorFrame.__init__(self, parents, array + buttons, columns, 
            **kwargs)
        self.chroots = None
        self.projectjson = None
        
    def get_title(self):
        return ''
    
    def OnCellRightClick(self, event):
        row = event.GetRow()
        col = event.GetCol()
        value = self.model.GetRowItem(row)
        self.menu_cell_item(value, col)
        
    def OnCellDoubleClick(self, event):
        row = event.GetRow()
        col = event.GetCol()
        value = self.model.GetRowItem(row)
        self.edit_cell_item(value, col)
    
    def menu_cell_item(self, value, col):
        if col == 1:
            self.menu_cell(value.object)
    
    def edit_cell_item(self, value, col):
        if col == 1:
            self.edit_cell(value.object)
    
    def button_drop_clicked(self, event):
        self.drop_action()
    
    def drop_action(self, items=None):
    #    print(items)
        if items is None:
            items = self.model.GetItemsByCheck()
        count = len(items)
        if count:
            answer = uistatusbar.question(f'Are you sure (drop {count} items)?', 'Question', self)
            if answer:# == wx.ID_YES:
                self.model.DropItems(items)
                uistatusbar.execute_with_progress(self.drop_items(items), count, 'dropping', 'Drop package')
    
     #   self.run_drop()
    def drop_items(self, items):
        for i in items:
            self.drop_one(i.object)
            self.store.Drop(i)
            yield 1    
     
    def button_add_clicked(self, event):
        self.add_action(self.add_default_values())
        
    @staticmethod
    def add_package_title():
        return 'Add/Edit Package'
    
    def initialize(self, store, config_args, filter_args=None):
        self.store = store
        self.configure(*config_args)
        if isinstance(filter_args, dict):
            if not isinstance(filter_args, CallableDict):
                filter_args = self.create_filter(filter_args)
            self.filter = filter_args
        self.update_run_thread() 
        self.SetTitle(self.get_title())   
    
    def add_action(self, default):
        #default = self.add_default_values()
        frame = self.add_settings()
        frame = runSettingsPanel(frame, title=self.add_package_title(), parent=self)
        panel = frame.panel
        panel.deploy_settings(default)
        self.bind_add_button(panel, lambda event: self.add_event(panel, frame))
        frame.Show()

    @staticmethod
    def bind_add_button(panel, func):
        button = panel.fields_widgets['add']
        panel.bindButton(button, func)

    def add_event(self, panel, frame):
        st = panel.extract_settings()
        self.run_add(st)
        frame.Close()
    
    def get_project_json(self):
        obj = self.projectjson
        if obj is None:
            client = self.client
            owner = self.owner
            project = self.project
            try:
                obj = self.client.project_proxy.get(owner, project)
            except Exception:
                obj = {}
            self.projectjson = obj
        return obj
    
    def get_chroots(self):
        chroots = self.chroots
        if chroots is None:
            try:
                obj = self.get_project_json()
                chroots = list(obj['chroot_repos'].keys())
            except Exception:
                chroots = []
            self.chroots = chroots
        return chroots
        
    def button_update_clicked(self, event):
        self.update_run_thread()

    def update_run_thread(self):
        # Create a new thread to run the update in the background
        thread = threading.Thread(target=self.update_background)
        thread.start()
        
    def update_background(self):
        # Run the update logic here
        list = self.get_element_list()
        self.clear()
        self.chroots = None
        self.projectjson = None
        self.add(list)
        
    def clear(self):
        model = self.model
        store = self.store
        model.Clear()
        store.Clear()
    
    def button_filter_clicked(self, event):
        frame = runSettingsPanel(self.filter_data, parent=self)
        panel = frame.panel
        try:
            filter_args = self.filter
        except AttributeError:
            filter_args = None
        if not filter_args is None:
            panel.deploy_settings({'':filter_args})

        frame.Show()

 #   def create_filter(self, dictionary):
 #       store = self.store
 #       model = self.model
 #       types = model.column_types
 #       path = store.path
 #       ids = model.column_ids
 #       return create_filter(dictionary, types, ids, path)

    def __getattr__(self, name):
        if name == 'filter_data' or name == 'create_filter':
            __data = self.__data
            if not name in __data:
                self.__generate_filter_data()
            return __data[name]
        else:
            raise AttributeError(name)
            
    def __generate_filter_data(self):
        __data = self.__data
        model = self.model
        store = self.store
        path = store.path
        ids = model.column_ids
        types = model.column_types
        names = model.column_names
        data = []
    #    dictionary = {}
    #    print(types)
    #    print(model.columns)
        for i in range(1,len(types)):
            name = names[i]
            nick = ids[i]
            type = types[i]
    #        dictionary[nick] = type
            if type == 'str':
                field = [{'type': 'combobox', 
                    'name': 'Filter Type', 'id': 'filter_type', 
                    'values':['substring', 'fulltext', 'regex']},
                    {'type': 'text', 'name': 'Text'}, 
                    {'type': 'combobox', 'name': 'Filter Status', 
            'id': 'status', 'values':['ignore', 'match', 'skip']}
                    ]
            elif type == 'date':
                field = [
                {'type': 'date', 'name': 'Date From'},
                {'type': 'time', 'name': 'Time From'},
                {'type': 'date', 'name': 'Date To'},
                {'type': 'time', 'name': 'Time To'},
                {'type': 'checkbox', 'name': '', 'id': 'enable', 
                    'values':[ 'TimeDate From', 'TimeDate To']}, 
                    {'type': 'combobox', 'name': 'Filter Status', 
            'id': 'status', 'values':['ignore', 'match', 'skip']}
                    ]
            data.append([ { 'id': nick, 'name': name}, field])
            
        def getfunc(obj, name):
            return obj[name]
            
        def setfunc_filter(dictionary, path=path, types=types, ids=ids):
            return create_filter(dictionary, types, ids, path)
        
        __data['create_filter'] = setfunc_filter
        
        def setfunc(obj, name, value, func=setfunc_filter):
            value = func(value)
            obj[name] = value
            return value
            
        __data['filter_data'] = [{ 'get':getfunc,'set':setfunc,
            'name': '', 'type': 'combined', 'values': data},
            {'name': 'Save', 'type': 'button', 'func': 
                lambda frame, event, self=self: self.run_filter_data(frame, event)}]
     #   return data
      #  path = store.path[1:]
    def run_filter_data(self, frame, event):
        settings = frame.extract_settings()['']
      #  custom_filter = self.custom_filter
    #    print(settings)
      #  if custom_filter is None:
        self.filter = settings
       # else:
       #     self.filter = lambda item: settings(item) and custom_filter(item)
        self.update_filter()
    
    def update_filter(self):
        model = self.model
        model.Clear()
        store = self.store
        for i in store.all.values():
            try:
                filter = self.filter
           #     print(filter)
                if not filter(i.object):
                    continue
            except AttributeError:
                pass
            model.AppendRow(i)
    
    def add(self, jsons):
        store = self.store
        for i in jsons:
            store.addItem(store.newItem(i))
        self.update_filter()

#create_config('/home/lenovo/.config/copr')

if __name__ == '__main__':
    from uimonitor import MonitorFrame
    from uistatusbar import CreateApp, InitApp
    
    app = CreateApp()
    
    button_names = []
    column_names = ['Name']
    frame = MonitorCommon(None, button_names, column_names)
    model = frame.model
    
    InitApp(app)









