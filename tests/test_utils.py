import socket

import pytest

from redisenv import util


def test_free_ports():
    for i in [10, 2, 15]:
        res = util.free_ports(i)
        assert len(res) == i
        assert len(set(res)) == i
