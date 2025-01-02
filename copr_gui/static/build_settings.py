def getBuildFields(chroots, fields):
    return [
        {
            'name': 'Bootstrap',
            'type': 'combobox',
            'values' : ["default", "image", "on", "off" ]
        },
        { 'id': 'ownername', 'name': 'Owner name', 'type': 'line' },
        { 'id': 'projectname', 'name': 'Project name', 'type': 'line' },
        { 'id': 'project_dirname', 'name': 'Project directory', 'type': 'line' },
        { 'name': 'Timeout', 'type': 'line' },
        { 'id': 'after_build_id', 'name': 'Build after', 'type': 'line' },
        { 'id': 'with_build_id', 'name': 'Build with', 'type': 'line' },
        { 'name': 'Chroots', 'type': 'checkbox', 'values':
            [ {'id':i} for i in chroots] },
        { 'id': 'enable_net', 'name': 'Enable network', 'type': 'checkbox' },
        *fields,
        { 'id': 'add', 'name': 'Build', 'type': 'button'}
    ]

def __test():
    import uistatusbar  as wx
    app = wx.CreateApp()


    from settings import runSettingsPanel

    runSettingsPanel(getBuildFields(['chroot1', 'chroot2'], []), title="Dynamic Form Example").Show()
    wx.InitApp(app)
