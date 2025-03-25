def _():
    def text(id, **kwargs):
        return {"id": id, "type": "text", **kwargs}

    def str(id, **kwargs):
        return {"id": id, "type": "line", **kwargs}

    # int = str

    def list(id, **kwargs):
        return {"id": id, "type": "list", **kwargs}

    def bool(id, **kwargs):
        return {"id": id, "type": "checkbox", **kwargs}

    def combo(id, *types, **kwargs):
        return {"id": id, "type": "combobox", "values": types, **kwargs}

    """ :param str ownername:
        :param str projectname:
        :param str chrootname:
        :param list additional_packages: buildroot packages for the chroot
        :param list additional_repos: buildroot additional additional_repos
        :param list additional_modules: list of modules that will be enabled or disabled in the given chroot, e.g. ['module1:stream', '!module2:stream'].
        :param str comps: file path to the comps.xml file
        :param bool delete_comps: if True, current comps.xml will be removed
        :param list with_opts: Mock --with option
        :param list without_opts: Mock --without option
        :param str bootstrap: Allowed values 'on', 'off', 'image', 'default', 'untouched' (equivalent to None)
        :param str bootstrap_image: Implies 'bootstrap=image'.
        :param str isolation: Mock isolation feature setup. Possible values are 'default', 'simple', 'nspawn'.
        :param list reset_fields: list of chroot attributes, that should be reseted to their respective defaults. Possible values are `additional_packages`, `additional_modules`, `isolation`, etc. See the output of `ProjectProxy.get` for all the possible field names."""
    return [
        str("ownername"),
        str("projectname"),
        str("chrootname", aliases=["mock_chroot"]),
        list("additional_packages"),
        list("additional_repos"),
        list("with_opts"),
        list("without_opts"),
        # list('additional_modules'),
        {"id": "add", "name": "Edit", "type": "button"},
    ]


ProjectChrootSettings = _()


def getProjectChrootFields():
    return ProjectChrootSettings
