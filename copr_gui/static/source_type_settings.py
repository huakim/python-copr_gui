from .spec_types import NamedDict, BooleanDict


def list_get(obj, name):
    value = obj[name]
    if not isinstance(value, dict):
        value = BooleanDict({i: True for i in list(value)})
    return value


def list_set(obj, name, value):
    if isinstance(value, dict):
        value = [i for i in value if value[i]]
    obj[name] = value
    return value


def _setSourceType(obj, name, value):
    # type = obj['source_type']
    obj["source_type"] = value.name()
    obj["source_dict"] = value


def _getSourceType(obj, name):
    value = obj["source_type"]
    if not isinstance(value, NamedDict):
        return NamedDict(obj["source_dict"], value)
    return value


def getSourceTypeFields(scm_types, fields, direct_build):
    if direct_build:
        direct_build = [
            ["URLs", [{"name": "URLs", "type": "list", "aliases": ["pkgs"]}]]
        ]
    else:
        direct_build = []
    return [
        {
            "name": "Source type",
            "type": "panel",
            "id": "source_type",
            "set": _setSourceType,
            "get": _getSourceType,
            "values": [
                *direct_build,
                [
                    "SCM",
                    [
                        {
                            "name": "SCM type",
                            "type": "combobox",
                            "values": ["git", "svn"],
                            "aliases": ["type"],
                            "id": "scm_type",
                        },
                        {"name": "Clone url", "type": "line"},
                        {"name": "Committish", "type": "line"},
                        {"name": "Subdirectory", "type": "line"},
                        {"id": "spec", "name": "Specfile", "type": "line"},
                        {
                            "id": "source_build_method",
                            "name": "Build method",
                            "type": "combobox",
                            "values": ["rpkg", "tito", "tito_test", "make_srpm"],
                        },
                    ],
                ],
                [
                    "DistGit",
                    [
                        {
                            "id": "packagename",
                            "name": "DistGit package name",
                            "type": "line",
                        },
                        {
                            "id": "distgit",
                            "name": "DistGit instance",
                            "type": "combobox",
                            "values": [
                                "fedora",
                                "centos",
                                "centos-stream",
                                "copr",
                                "copr-dev",
                            ],
                        },
                        {
                            "id": "namespace",
                            "name": "DistGit namespace",
                            "type": "line",
                        },
                        {"name": "Committish", "type": "line"},
                    ],
                ],
                [
                    "PyPI",
                    [
                        {"name": "PyPI package name", "type": "line"},
                        {"name": "PyPI package version", "type": "line"},
                        {
                            "name": "Spec generator",
                            "type": "combobox",
                            "values": ["pyp2spec", "pyp2rpm"],
                        },
                        {
                            "name": "Spec template",
                            "type": "combobox",
                            "values": ["fedora", "mageia", "pld"],
                        },
                        {
                            "name": "Python versions",
                            "type": "checkbox",
                            "get": list_get,
                            "set": list_set,
                            "values": ["2", "3"],
                        },
                    ],
                ],
                ["RubyGems", [{"name": "Gem name", "type": "line"}]],
                [
                    "Custom",
                    [
                        {"id": "chroot", "name": "Chroot", "type": "line"},
                        {"id": "resultdir", "name": "Result directory", "type": "line"},
                        {
                            "id": "builddeps",
                            "name": "Build dependencies",
                            "type": "text",
                        },
                        {
                            "id": "repos",
                            "name": "External repositories",
                            "type": "text",
                        },
                        {"id": "script", "name": "Build script", "type": "text"},
                    ],
                ],
                *scm_types,
            ],
        },
        *fields,
    ]
