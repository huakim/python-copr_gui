#!/bin/bash
import cached_store as cs
from time import time, sleep


class ComplicatedCache:
    def get_time(self, arg=''):
        return time()


def test_with_argument():
    cc = ComplicatedCache()
    cache = cs.CallCache()
    mock1 = cs.CallCacheMock(cc, cache)
    mock2 = cs.CallCacheMock(cc, cache)
    mock3 = cs.CallCacheMock(cc, cache)
    mock4 = cs.CallCacheMock(cc, cache)
    t1 = mock1.get_time("F")
    sleep(0.1)
    t2 = mock2.get_time("F")
    sleep(0.1)
    t3 = mock3.get_time("F")
    sleep(0.1)
    t4 = mock4.get_time("D")
    sleep(0.1)
    t5 = mock3.get_time("D")
    assert t1 == t2
    assert t1 == t3
    assert t1 != t4
    assert t4 == t5


def test_simple_cache():
    t1 = time()
    sleep(0.1)
    t2 = time()
    assert t1 != t2
    cache = cs.CallCache()
    mock1 = cs.CallCacheMock(time, cache)
    mock2 = cs.CallCacheMock(time, cache)
    t1 = mock1()
    sleep(0.1)
    t2 = mock2()
    assert t1 == t2
    t2 = mock2()
    assert t1 != t2
    

def test_redefined_cache():
    cc = ComplicatedCache()
    cache = cs.CallCache()
    mock1 = cs.CallCacheMock(cc, cache)
    mock2 = cs.CallCacheMock(cc, cache)
    t1 = mock1.get_time()
    sleep(0.1)
    t2 = mock2.get_time()
    assert t1 == t2
    mock1.get_time = time
    t1 = mock1.get_time()
    sleep(0.1)
    t2 = mock2.get_time()
    assert t1 != t2


def test_complicated_cache():
    cache = cs.CallCache()
    cc = ComplicatedCache()
    cc.c1 = ComplicatedCache()
    mock3 = cs.CallCacheMock(cc, cache)
    mock4 = cs.CallCacheMock(cc, cache)
    t1 = mock3.c1.get_time()
    sleep(0.1)
    t2 = mock4.c1.get_time()
    assert t1 == t2
    t2 = mock4.c1.get_time()
    assert t1 != t2
    t1 = mock3.c1.get_time()
    assert t1 == t2

