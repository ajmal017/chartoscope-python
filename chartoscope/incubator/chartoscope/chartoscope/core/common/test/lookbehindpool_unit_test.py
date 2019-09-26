from chartoscope.core.common import LookBehindPool


class PoolItem:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def write(self, value):
        self._value = value


def test_capacity():
    pool = LookBehindPool(10, lambda: PoolItem(0))
    assert(pool.capacity == 10)


def test_writing():
    pool = LookBehindPool(10, lambda: PoolItem(0))
    assert(len(pool._pool) == 10)
    pool.set_forward(lambda item: item.write(1))
    assert(pool.current.value == 1)
    pool.set_forward(lambda item: item.write(2))
    assert(pool.current.value == 2)
    assert(pool[1].value == 1)


def test_rollover():
    pool = LookBehindPool(3)
    assert(pool._current_position == 0)
    pool.write_forward(1)
    assert(pool._current_position == 1)
    assert(pool.current == 1)
    pool.write_forward(2)
    assert(pool._current_position == 2)
    assert(pool.current == 2)
    pool.write_forward(3)
    assert(pool._current_position == 0)
    assert(pool.current == 3)
    assert(pool.previous == 2)


def test_read_back():
    pool = LookBehindPool(20, lambda: PoolItem(0))
    for i in range(10):
        pool.set_forward(lambda item: item.write(i))

    result = list(pool.read_back(5, lambda item: item.value))
    assert(len(result) == 5)
    assert(result[0] == 9)
    assert (result[4] == 5)
