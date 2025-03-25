#!/bin/bash
import cached_store as cs
from time import time, sleep


class ComplicatedCache:
    def get_time(self):
        return time()


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
