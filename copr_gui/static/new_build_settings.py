#!/usr/bin/python3

from .source_type_settings import getSourceTypeFields
from .build_settings import getBuildFields

def getNewBuildFields(chroots, scm_types, fields):
    return getBuildFields(chroots,
        getSourceTypeFields(scm_types, fields, True))
        
def __test():
    import uistatusbar
    app = uistatusbar.CreateApp()
    from settings import runSettingsPanel
    from build_settings import getBuildFields

    frame = runSettingsPanel(
        getNewBuildFields(['chroot1', 'chroot2'], [], []),
        title="Dynamic Form Example")
    panel = frame.panel
    frame.Show()
    button = panel.fields_widgets['add']
    panel.bindButton(button, lambda a: print(panel.extract_settings()))
    uistatusbar.InitApp(app)



