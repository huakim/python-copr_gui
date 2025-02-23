from ...static.spec_types import CallableDict, MergePath
from operator import ge, le
import re
import datetime
import json5
combine = datetime.datetime.combine
from . import uistatusbar

def show_json(json, parent=None, title=''):
    dropjson = json
    while isinstance(dropjson, dict):
        dropjson.pop('__response__', 0)
        dropjson.pop('__proxy__', 0)
        dropjson = dropjson.get('__config__')
    uistatusbar.show_text_frame(json5.dumps(json, indent=4), title, parent)

def create_custom_build(client, name, script,
    chroot, builddeps, resultdir, repos,
    buildopts):
    
    return client.build_proxy.create_from_custom(
        script, chroot, builddeps, resultdir, 
        repos, buildopts
    )
def create_other_build(client, source_type, buildopts, **source):
    method = getattr(client.build_proxy, f'create_from_{source_type}')
    return method(buildopts=buildopts, **source)

build_methods = {
'custom': create_custom_build,
'distgit': create_other_build,
'scm': create_other_build,
'rubygems': create_other_build,
'pypi': create_other_build,
'urls': create_other_build,
}

def create_new_build(client, settings):
    settings = settings.copy()

    source = settings.pop('source_dict')
    source_type = settings.pop('source_type')

    for i in ['ownername', 'projectname', 'project_dirname']:
        source[i] = settings.pop(i)

    return build_methods[source_type](client,
        source_type, buildopts=settings, **source)


def create_build_from_package(client, settings, package):

    source = {  }
    settings = settings.copy()
    for i in ['ownername', 'projectname', 'project_dirname']:
        source[i] = settings.pop(i)
    source['packagename'] = package['name']

    return client.package_proxy.build(buildopts=settings,**source)

def run_monitor(class_object, parent, *args, filter_args=None):
    obj = class_object(parent, args, filter_args=filter_args)
    obj.Show()

def date_matcher(date, greater):
    if greater:
        func = ge
    else:
        func = le
    return lambda obj: func(date, obj)

def create_filter(obj_dict, type_array, id_array, path_array):
    filter_data = []
    data = CallableDict(None, filter(filter_data))
    for i in range(1, len(type_array)):
        nameid=id_array[i]
        obj = obj_dict.get(nameid, None)
        type = type_array[i]
        if not isinstance(obj, CallableDict):
            func = None
            if isinstance(obj, dict):
                status = obj['status']
                if status == 'ignore':
                    pass
                elif type == 'date':
                    enable = obj['enable']
                    funcs = []
                    less = (status == 'skip')
                    if enable['timedate_from']:
                        datetime_from = combine(obj['date_from'], obj['time_from'])
                        funcs.append(date_matcher(date, less))
                    if enable['timedate_to']:
                        datetime_to = combine(obj['date_to'], obj['time_to'])
                        funcs.append(date_matcher(date, not less))                
                    if len(funcs) > 0:
                        if len(funcs) == 1:
                            func = funcs[0]
                        else:
                            func = lambda obj, func1=funcs[0], func2=funcs[1]: func1(obj) and func2(obj)
                elif type == 'str':
                    enable = obj['filter_type']
                    if status != 'skip':
                        text = str(obj['text'])
                        if enable == 'substring':
                            func = lambda obj, text=text: text in str(obj)
                        elif enable == 'fulltext':
                            func = lambda obj, text=text: text == str(obj)
                        elif enable == 'regex':
                            func = lambda obj, text=text: bool(re.match(text, str(obj)))
                    else:
                        text = str(obj['text'])
                        if enable == 'substring':
                            func = lambda obj, text=text: not text in str(obj)
                        elif enable == 'fulltext':
                            func = lambda obj, text=text: text != str(obj)
                        elif enable == 'regex':
                            func = lambda obj, text=text: not bool(re.match(text, str(obj)))
            else:
                obj = None
            obj = CallableDict(obj, func)
        data[nameid] = obj
        filter_data.append((path_array[i], obj))
    return data
# class DateTimeFilter:
    # def __init__(self, datetime, comparer):
        # self.__datetime = datetime
        # self.__comparer = comparer
    # def date(self):
        # return self.datetime.date()
    # def time(self):
        # return self.datetime.time()
    # def __call__(self, datetime):
        # return self.__comparer(self.__datetime, datetime)

def filter(comparearray):
    def _(item_old):
        for i in comparearray:
            path = i[0]
            compare = i[1]
         #   print('#####################COMPARE')
         #   print(compare)
        #    print('#####################PATH')
       #     print(path)
            item = path(item_old)
       #     print('#####################ITEM')
       #     print(item)
      #      print('#####################END')
            if not bool(compare(item)):
                return False
        return True
    return _


additional_types = []
