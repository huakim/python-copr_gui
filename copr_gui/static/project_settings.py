def _():
    def get_if_str(obj, name):
        l = obj[name]
        if isinstance(l, str):
            l = eval(l)
        return l
    def text(id, **kwargs):
        return {'id': id, 'type': 'text', **kwargs}
    def line(id, **kwargs):
        return {'id': id, 'type': 'line', **kwargs}
    int=line
    def list(id, **kwargs):
        return {'id': id, 'type': 'list', **kwargs}
    def bool(id, **kwargs):
        return {'id': id, 'type': 'checkbox', **kwargs}
    def combo(id, *types, **kwargs):
        return {'id': id, 'type': 'combobox', 'values': types, **kwargs}
    """ :param str ownername:
        :param str projectname:
        :param list chroots:
        :param str description:
        :param str instructions:
        :param str homepage:
        :param str contact:
        :param list additional_repos:
        :param bool unlisted_on_hp: project will not be shown on Copr homepage
        :param bool enable_net: if builder can access net for builds in this project
        :param bool auto_prune: if backend auto-deletion script should be run for the project
        :param bool use_bootstrap_container: obsoleted, use the 'bootstrap'argument and/or the 'bootstrap_image'.
        :param bool devel_mode: if createrepo should run automatically
        :param int delete_after_days: delete the project after the specfied period of time
        :param bool module_hotfixes: allow packages from this project to override packages from active module streams.
        :param str bootstrap: Mock bootstrap feature setup. Possible values are 'default', 'on', 'off', 'image'.
        :param str isolation: Mock isolation feature setup. Possible values are 'default', 'simple', 'nspawn'.
        :param bool follow_fedora_branching: If newly branched chroots should be automatically enabled and populated.
        :param str bootstrap_image: Name of the container image to initialize the bootstrap chroot from.  This also implies 'bootstrap=image'. This is a noop parameter and its value is ignored.
        :param bool fedora_review: Run fedora-review tool for packages in this project
        :param bool appstream: Disable or enable generating the appstream metadata
        :param str runtime_dependencies: List of external repositories (== dependencies, specified as baseurls) that will be automatically enabled together with this project repository.
        :param list packit_forge_projects_allowed: List of forge projects that will be allowed to build in the project via Packit"""
    return [
line("ownername") ,
line("projectname", aliases=['name']) ,
list("chroots", aliases=['chroot_repos']) ,
text("description") ,
text("instructions") ,
text("homepage") ,
text("contact") ,
list("additional_repos") ,
bool("unlisted_on_hp") ,
bool("enable_net") ,
bool("auto_prune") ,
bool("use_bootstrap_container") ,
bool("devel_mode") ,
int("delete_after_days") ,
bool("module_hotfixes") ,
combo("bootstrap", 'default', 'on', 'off', 'image') ,
combo("isolation", 'default', 'simple', 'nspawn') ,
bool("follow_fedora_branching") ,
line("bootstrap_image") ,
bool("fedora_review") ,
bool("appstream") ,
text("runtime_dependencies") ,
list("packit_forge_projects_allowed", get=get_if_str) ,
{'id': 'add', 'name': 'Edit/Add', 'type': 'button'}
    ]

ProjectSettings = _()

def getProjectFields():
    return ProjectSettings
