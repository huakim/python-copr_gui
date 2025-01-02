#!/usr/bin/python3
from .build_settings import getBuildFields

def getOldBuildFields(chroots, packages, fields=[]):
    return getBuildFields(chroots, [
    {'name': 'Packages', 'type': 'checkbox', 
        'values': [{'id':i} for i in packages]},
    *fields
    ])

def __test():
    import uistatusbar as wx
    app = wx.CreateApp()
    from settings import runSettingsPanel
    from build_settings import getBuildFields

    frame = runSettingsPanel(
        getOldBuildFields(['chroot1', 'chroot2'], ['one', 'two'], []),
        title="Dynamic Form Example")
    panel = frame.panel
    frame.Show()
    button = panel.fields_widgets['add']
    button.Bind(wx.EVT_BUTTON, lambda a: print(panel.extract_settings()))
    wx.InitApp(app)



