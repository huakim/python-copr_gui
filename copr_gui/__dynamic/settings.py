from bidict import bidict
from collections import OrderedDict
from collections.abc import Iterable

from ...static.spec_types import NamedDict, BooleanDict, getName, getId, getFunc
from . import uisettings
from . import uistatusbar

SettingsScrolledWindow=uisettings.SettingsScrolledWindow
time_blttowx = uistatusbar.time_to_wx_datetime
date_blttowx = uistatusbar.date_to_wx_datetime
time_wxtoblt = uistatusbar.wx_datetime_to_time
date_wxtoblt = uistatusbar.wx_datetime_to_date


import datetime

def createFunc(self, func):
    def _(event):
        return func(self, event)
    return _

class SettingsPanel(uisettings.UiSettingsPanel):
    def deploy_settings(self, settings):
        widgets = self.fields_widgets
        fields = self.fields
        field_indexes = self.indexes
        aliases = self.aliases
        for key in settings:
            namekey = aliases.get(key) or key
            index = field_indexes.get(namekey, -1)
            if index == -1:
                continue
            field = fields[index]
            widget = widgets[namekey]
            func = field.get('get')
            if not callable(func):
                def func(obj, name):
                    return obj[name]
            keys = field.get('values')
            type = field['type']
            value = func(settings, key)
            if type == 'text':
                self.SetTextValue(widget, value or '')
            if type == 'line':
                self.SetLineValue(widget, value or '')
            if type == 'date':
                self.SetDateValue(widget, date_blttowx(value or 0))
            if type == 'time':
                self.SetTimeValue(widget, time_blttowx(value or 0))
            elif type == 'combobox':
                indexes = widget['-indexes']
                combobox = widget['-combobox']
                self.SetComboBoxSelection(combobox, indexes.get(value, 0))
            elif type == 'panel':
                items = widget['-items']
                name = value.name()
                indexes = widget['-indexes']
                notebook = widget['-notebook']
                index = indexes.inverse.get(name, 0)
                self.SetTabWidgetSelection(notebook, index)
                items[index].deploy_settings(value)
            elif type == 'combined':
                indexes = widget['-indexes']
                items = widget['-items']
                for key, value in value.items():
                    index = indexes.inverse[key]
                    items[index].deploy_settings(value)
            elif type == 'checkbox':
                if keys is None:
                    self.SetCheckBoxValue(widget, bool(value))
                else:
                    default = value.default()
                    true = value.true()
                    false = value.false()
                    if isinstance(true, Iterable):
                        for i in true:
                            self.SetCheckBoxValue(widget[i], True)
                    else:
                        true=[]
                    if isinstance(false, Iterable):
                        for i in false:
                            self.SetCheckBoxValue(widget[i], False)
                    else:
                        false=[]
                    if not default is None:
                        for i in set(widget.keys()).difference(true+false):
                            self.SetCheckBoxValue(widget[i], default)
            elif type == 'list':
                self.SetListValue(widget, value)

    def extract_settings(self, name=""):
        fields = self.fields
        indexes = self.indexes
        settings = NamedDict(name=name)
        widgets = self.fields_widgets
        for name, index in indexes.items():
            field = fields[index]
            type = field['type']
            values = field.get('values')
            func = field.get('set')
            field = widgets[name]
            if not callable(func):
                def func(obj, name, value):
                    obj[name] = value
                    return value
            if type == 'text':
                func(settings, name, self.GetTextValue(field))
            if type == 'line':
                func(settings, name, self.GetLineValue(field))
            if type == 'date':
                func(settings, name, date_wxtoblt(self.GetDateValue(field)))
            if type == 'time':
                func(settings, name, time_wxtoblt(self.GetTimeValue(field)))
            elif type == 'combobox':
                index = self.GetComboBoxSelection(field['-combobox'])
                if index < 0:
                    index = 0
                func(settings, name, getId(values[index]))
            elif type == 'panel':
                notebook = field['-notebook']
                indexes = field['-indexes']
                field = field['-items']
                index = self.GetTabWidgetSelection(notebook)
                id = indexes.get(index)
                panel = field.get(index)
                func(settings, name, panel.extract_settings(id))
            elif type == 'combined':
                indexes = field['-indexes']
                field = field['-items']
                d = dict()
                for i in range(len(indexes)):
                    panel = field.get(i)
                    id = indexes.get(i)
                    d[id] = panel.extract_settings(id)
                func(settings, name, d)
            elif type == 'list':
                func(settings, name, self.GetListValue(field))
            elif type == 'checkbox':
                if values is None:
                    func(settings, name, bool(self.GetCheckBoxValue(field)))
                else:
                    s = BooleanDict()
                    for i in values:
                        i = getId(i)
                        s[i] = self.GetCheckBoxValue(field[i])
                    func(settings, name, s)
        return settings

    def __init__(self, frame, fields, *args, panel_class=SettingsScrolledWindow, **kwargs):
        super().__init__(frame, *args, **kwargs)

        self.fields = fields
        self.aliases = aliases = dict()
        self.indexes = indexes = bidict()
        self.fields_widgets = fld = {}

        scrolled_window = panel_class(self)
        self.scrolled_window = scrolled_window
        self.startInit()

        for index, field in enumerate(fields):
            field_name = getName(field)
            func = getFunc(field)
            if callable(func):
                func = createFunc(self, func)
            field_super_name = getId(field)
            indexes[field_super_name] = index
            for i in (field.get('aliases') or []):
                aliases[i] = field_super_name
            field_type = field['type']
            field_values = field.get('values', None)
            field_class = None
            if (field_values is None):
                if field_type == 'checkbox':
                    field_class = self.addCheckBox
                    field_int = self.bindCheckBox
                elif field_type == 'button':
                    field_class = self.addButton
                    field_int = self.bindButton
                if field_class:
                    checkbox = field_class(field_name)
                    fld[field_super_name] = checkbox
                    if callable(func):
                        field_int(checkbox, func)
            if not (field_class is None):
                pass
            elif field_type == 'list':
                add_button = self.addLabelPlusButton(field_name)
                fields = self.addList()

                self.bindButton(add_button, (lambda *a, flds=fields, add=self.incList: add(flds)))
                fld[field_super_name] = fields
            else:
                if field_name:
                    self.addLabel(field_name)

                if field_type == 'panel' or field_type == 'combined':
                    notebook = self.addTabWidget()

                    checkboxes = {}
                    ind = bidict()
                    for index, field in enumerate(field_values):
                        value=field[0]
                        valuename = getId(value)
                        value = getName(value)
                        if valuename in checkboxes:
                            raise KeyError(f"duplicate key: {valuename}")

                        checkbox = SettingsPanel(notebook, field[1], panel_class=self.create_panel)
                        checkboxes[index] = checkbox
                        ind[index] = valuename
                        self.incTabWidget(notebook, checkbox, value)

                    boxes = {}
                    boxes['-notebook'] = notebook
                    boxes['-indexes'] = ind
                    boxes['-items'] = checkboxes
                    fld[field_super_name] = boxes

                elif field_type == 'text':
                    fld[field_super_name] = text_ctrl = self.addText()

                elif field_type == 'line':
                    fld[field_super_name] = text_ctrl = self.addLine()

                elif field_type == 'date':
                    fld[field_super_name] = text_ctrl = self.addDate()

                elif field_type == 'time':
                    fld[field_super_name] = text_ctrl = self.addTime()

                elif field_type == 'combobox':
                    combobox = self.addComboBox([getName(i) for i in field_values])
                    ind = bidict()
                    for index, value in enumerate(field_values):
                        value = getId(value)
                        ind[value] = index
                    if callable(func):
                        self.bindComboBox(combobox, func)
                    fld[field_super_name] = {'-combobox': combobox, '-indexes': ind}
                else:
                    field = None
                    if field_type == 'checkbox':
                        field = self.addCheckBoxPanel
                    elif field_type == 'button':
                        field = self.addButtonPanel
                    if not field is None:
                        checkboxes={}
                        ind = bidict()
                        fld[field_super_name] = checkboxes
                        checkboxes_sizer = field()
                        for value in field_values:
                            valuename = getId(value)
                            value = getName(value)
                            if valuename in checkboxes:
                                raise KeyError(f"duplicate key: {valuename}")
                            checkbox = checkboxes_sizer.add(value)
                            #field(scrolled_window, label=value)
                            funcf = getFunc(value, func)
                            if id(func) != id(funcf):
                                if callable(funcf):
                                    funcf = lambda event, funcf=funcf: funcf(event)
                                    checkboxes_sizer.bind(checkbox, funcf)
                            elif callable(func):
                                checkboxes_sizer.bind(checkbox, func)
                            checkboxes[valuename] = checkbox
        self.Init()

def runSettingsPanel(fields=[], title='', type=SettingsPanel, parent=None):
    frame = uistatusbar.Frame(parent, title=title)
    main_panel = type(frame, fields)
    frame.panel = main_panel
    return frame

if __name__ == '__main__':
    app = uistatusbar.CreateApp()
    from spec_types import NamedDict, BooleanDict
    fields = [{
                    'name': 'Subfield 1',
                    'type': 'list'
                },{
                    'name': 'Subfield 12',
                    'type': 'time'
                    },
                {
                    'name': 'Subfield 13',
                    'type': 'date'
                },
                {
                    'name': 'Subfield 2',
                    'type': 'text',
                    'id': 'field2'
                },
                {
                    'name': 'Subfield 3',
                    'type': 'combined',
                    'id': 'field_0',
                    'values': [
                        ['key',
                            [
                                {'name':'one', 'type':'text'},
                                {'name':'two', 'type':'text'}
                            ]
                        ],
                        ['value',
                            [{'name':'one', 'type':'text'}]
                        ]
                    ]
                },
                {
                    'name': 'Subfield 4',
                    'type': 'line'
                },
                {
                    'name': 'Subfield 5',
                    'type': 'checkbox',
                    'id':'subfield_5',
                    'values': ['one', 'two', 'three', 'four', 'five', *[str(i) for i in range(30)]]
                },
                {
                    'name': 'super_button',
                    'type': 'button'
                },
                {
                    'name': 'Subfield 6',
                    'type': 'combobox',
                    'id':'subfield_6',
                    'values': ['one', 'two', 'three', 'four', 'five']
                },
    ]
    frame = runSettingsPanel(fields, title="Dynamic Form Example")
    panel = frame.panel
    panel.deploy_settings({
    'field_0':
        {
        'key':{'one':'fine'},
        'value':{'one':'fineload'}
        },
    'subfield_1':['123','24', 'funnnyload'], 'field2': 'super text',
        'subfield_5': BooleanDict({'one':True, 'two':False}, True)})

    print(panel.fields_widgets['super_button'])
    panel.bindButton(panel.fields_widgets['super_button'], lambda *a: print(panel.extract_settings()))
    frame.Show()
    uistatusbar.InitApp(app)
