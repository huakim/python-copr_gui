def dynamic():
    # from sys import modules
    import sys
    import os
    import importlib.abc
    import importlib

    # from importlib import import_module
    # from importlib.util import spec_from_file_location, module_from_spec
    join = os.path.join
    generic = __package__ + '.generic'
    # dynamic = __package__ + '.dynamic'

    dirname = join(os.path.dirname(__file__), "__dynamic")
    dynamic_names = {f[:-3] for f in os.listdir(dirname) if f.endswith(".py")}

    class PyFile:
        def __init__(self, name):
            self.name = name

        def __getattr__(self, name):
            if name == "path":
                value = join(dirname, self.name + ".py")
            elif name == "content":
                path = self.path
                value = compile(open(path, "r").read(), path, "exec")
            else:
                raise AttributeError(name)
            setattr(self, name, value)
            return value

    class DictObject(dict):
        def __getitem__(self, name):
            if name in self:
                return super().__getitem__(name)
            elif name in dynamic_names:
                self[name] = PyFile(name)

    class CustomPackageLoader(importlib.abc.InspectLoader):
        def __init__(self, obj):
            self.obj = obj

        def create_module(self, spec):
            return None

        def exec_module(self, module):
            module_content = self.obj[module.__name__.rsplit(".", 1)[1]].content
            exec(module_content, module.__dict__)

        def get_filename(self, fullname):
            try:
                return self.obj[fullname.rsplit(".", 1)[1]].path
            except AttributeError:
                return None

        def get_code(self, fullname):
            return None

        def get_source(self, fullname):
            return None

        def is_package(self, fullname):
            return False

    custom_loader = CustomPackageLoader(DictObject())

    class CustomModuleFinder(importlib.abc.MetaPathFinder):
        def __init__(self, module_dict):
            self.module_dict = module_dict

        def find_spec(self, fullname, path, target=None):
            namedict = fullname.rsplit(".", 2)
            if len(namedict) != 3:
                return None
            if namedict[0] != generic:
                return None
            if namedict[2] not in dynamic_names:
                return None
            spec = importlib.util.spec_from_loader(fullname, custom_loader)
            return spec

    module_dict = dict()

    sys.meta_path.append(CustomModuleFinder(module_dict))


dynamic()
del dynamic
