from .source_type_settings import getSourceTypeFields

def getPackageFields(scm_types, fields):
    return [
        { 'id': 'ownername', 'name': 'Owner name', 'type': 'line' },
        { 'id': 'projectname', 'name': 'Project name', 'type': 'line' },
        { 'id': 'packagename', 'name': 'Package name', 'type': 'line', 'aliases': ['name'] },
        *getSourceTypeFields(scm_types, fields, False),
        { 'id': 'add', 'name': 'Save', 'type': 'button'}
    ]

if __name__ == '__main__':
    import uistatusbar as wx
    app = wx.CreateApp()
    from settings import runSettingsPanel

    frame = runSettingsPanel(getPackageFields([], []), title="Dynamic Form Example")
    frame.Show()
    panel = frame.panel
    button = panel.fields_widgets['add']
    extract = panel.extract_settings
    button.Bind(wx.EVT_BUTTON, lambda a: print(extract()))
    wx.InitApp(app)
