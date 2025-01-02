#!/usr/bin/python3


class MergePath:
    def __init__(self, *attrs):
        self.__path = attrs
    def __call__(obj, self):
#        print('|=|=|=|=|', obj.__path)
        for i in obj.__path:
 #           print('>>>>>>>>>>>')
  #          print(i)
   #         print('<<<<<<<<<<<')
    #        print(self)
            self = i(self)
     #       print('###########')
      #      print(self)
       #     print('###########')
        #print('|$|$|$|$|')
        return self
    def __repr__(self):
        g=[i for i in self.__path]
        return f'MergePath(*{g})'
            
import datetime
fromtimestamp = datetime.datetime.fromtimestamp

class DateTimePath:
    def __init__(self, func):
        self.__function = func
    def __call__(obj, self):
        func = obj.__function
        i = 0
        try:
            i = int(func(self))
        except ValueError:
            pass
        return fromtimestamp(i)
    def __repr__(self):
        g=self.__function
        return f'DateTimePath({g})'

class ItemPath:
    def __init__(self, *attrs):
        self.__path = attrs
    def __call__(obj, self):
        for i in obj.__path:
            self = self[i]
        return self 
    def __repr__(self):
        g=self.__path
        return f'ItemPath(*{g})'

class IfPath:
    def __init__(self, firstaction, secondaction, condition=bool):
        self.__condition = condition
        self.__firstaction = firstaction
        self.__secondaction = secondaction
    def __call__(self, a):
        ab = self.__firstaction(a)
        if not self.__condition(ab):
            ab = self.__secondaction(a)
        return ab
    def __repr__(self):
        return f'IfPath(*{[ self.__firstaction, self.__secondaction, self.__condition ]})'
        
class DefPath:
    def __init__(self, default=None):
        self.__default = default
    def __call__(self, a):
        return self.__default
    def __repr__(self):
        return f'DefPath({self.__default})'
        
class SafePath:
    def __init__(self, action, catch=lambda *a: None, exception=Exception):
        self.__exception = exception
        self.__action = action
        self.__catch = catch
    def __call__(obj, self):
        try:
            return obj.__action(self)
        except obj.__exception:
            return obj.__catch(self)
    def __repr__(self):
        return f'SafePath(*{[self.__action, self.__catch,  self.__exception ]})'

class AttrPath:
    def __init__(self, *attrs):
        self.__path = attrs
    def __call__(obj, self):
        for i in obj.__path:
            self = getattr(self, str(i))
        return self
    def __repr__(self):
        return f'AttrPath(*{self.__path })'

class CallableDict(dict):
    def __init__(self, body=None, func=None):
        if callable(func):
            self.func(func)
        else:
            self.func(lambda *a, **b: True)
        if not body is None:
            self.update(body)

    def func(self, value=None):
        if value is None:
            value = self.__name
        else:
            self.__name = value
        return value
    def __call__(self, *a, **b):
        return self.func()(*a, **b)
    def __repr__(self):
        return f'CallableDict({super().__repr__()}, func={repr(self.func())})'


class NamedDict(dict):
    def __init__(self, body=None, name=None):
        if not name is None:
            self.name(name)
        else:
            self.name('')
        if not body is None:
            self.update(body)

    def name(self, value=None):
        if value is None:
            value = self.__name
        else:
            self.__name = value
        return value
    def __repr__(self):
        return f'NamedDict({super().__repr__()}, name={repr(self.name())})'

class BooleanDict(dict):
    def default(self, value=None):
        if value is None:
            value = self.__default_value
        else:
            value = bool(value)
            self.__default_value = value
        return value

    def __init__(self, body=None, default=False):
        self.__default_value = bool(default)
        if not body is None:
            self.update(body)
        
    def __repr__(self):
        return f'BooleanDict({super().__repr__()})'
        
    def __setitem__(self, key, value):
        super().__setitem__(key, bool(value))
    
    def __eq__(self, other):
        if isinstance(other, BooleanDict):
            return super().__eq__(other)
        return False
    
    def copy(self):
        new_dict = BooleanDict()
        new_dict.update(self)
        return new_dict
    
    @staticmethod
    def fromkeys(keys, value=False):
        value = bool(value)
        new_dict = BooleanDict()
        for key in keys:
            new_dict[key] = value
        return new_dict
    
    def true(self):
        return [ i for i in self.keys() if self[i] ]
    
    def false(self):
        return [ i for i in self.keys() if not self[i] ]
    
    def pop(self, key, default=None):
        if default is not None:
            default = bool(default)
        super().pop(key, default)
    
    def setdefault(self, key, default = None):
        if not default is None:
            default = bool(default)
        else:
            default = self.default()
        super().setdefault(key, default)
    
    def update(self, iterable, **kwargs):
        if hasattr(iterable, "keys"):
            for key in iterable.keys():
                self[key] = iterable[key]
        else:
            for key, value in iterable:
                self[key] = value
        for key in kwargs:
            self[key] = kwargs[key]
    
    def get(self, key, default=False):
        super().get(key, bool(default))

default_true = BooleanDict({}, True)
   
def getType(book, default):
    if isinstance(book, dict):
        default = book.get('type', default) 
    return default
   
def getName(book):
    if isinstance(book, dict):
        name = book.get('name', None)
        if not name is None:
            return name
        else:
            return book.get('id', '')
    return str(book)
    
def getFunc(book, default=None):
    if callable(book):
        if not callable(default):
            default = book
    if isinstance(book, dict):
        default = book.get('func', default)
    return default
    
def getId(book):
    if isinstance(book, dict):
        id = book.get('id', None)
        if not id is None:
            return id
        else:
            book = book.get('name', '')
    return str(book).lower().replace('-', '_').replace(' ', '_')

#BoolDict = BooleanDict
#bool_dict = BooleanDict
#n_dict = NamedDict

def __test():
    my_dict = BooleanDict()
    my_dict['key1'] = True
    my_dict['key2'] = False
    
    print(my_dict.keys())          # Output: ['key1', 'key2']
    print(my_dict.values())        # Output: [True, False]
    print(my_dict.items())         # Output: [('key1', True), ('key2', False)]
    
    my_dict['key3'] = True
    
    print(my_dict.keys())          # Output: ['key1', 'key2', 'key3']
    print(my_dict)
    print(my_dict.true())
    print(my_dict.false())
    del my_dict['key2']
    print(my_dict.keys())          # Output: ['key1', 'key3']
