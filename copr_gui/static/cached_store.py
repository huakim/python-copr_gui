import time


class Call:
    def __init__(self, func, *args, **kwargs):
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs

    def __call__(self):
        return self.__func(*self.__args, **self.__kwargs)

    def __eq__(self, obj):
        if self.__func == obj.__func:
            if self.__args == obj.__args:
                if self.__kwargs == obj.__kwargs:
                    return True
        return False

    def __hash__(self):
        h = hash(self.__func)
        for i in self.__args:
            h += hash(i)
        for i, k in self.__kwargs.items():
            h += hash(i)
            h += hash(k)
        return h


class CallCache:
    def __init__(self):
        self.__call_times = {}
        self.__call_responses = {}

    def __call__(self, func, args, kwargs, cache):
        if not callable(func):
            raise TypeError(type(func) + " is not callable")
        c = Call(func, *args, **kwargs)
        call_times = self.__call_times
        call_responses = self.__call_responses
        try:
            last_local_call_time = cache[c]
        except KeyError:
            last_local_call_time = 0

        last_global_call_time = call_times.get(c, 0)

        if last_global_call_time > last_local_call_time:
            cache[c] = last_global_call_time
            return call_responses.get(c)
        else:
            resp = c()
            last_local_call_time = time.time()
            cache[c] = last_local_call_time
            call_times[c] = last_local_call_time
            call_responses[c] = resp
            return resp


class CallCacheMock:
    def __init__(self, obj, callcache=None):
        if isinstance(callcache, CallCache):
            self._cache = callcache
        else:
            self._cache = CallCache()
        self.__times = {}
        self.__obj = obj

    def __call__(self, *args, **kwargs):
        return self._cache(self.__obj, args, kwargs, self.__times)

    def __getattr__(self, name):
        obj = self.__obj
        attr = CallCacheMock(getattr(obj, name), self._cache)
        setattr(self, name, attr)
        return attr
