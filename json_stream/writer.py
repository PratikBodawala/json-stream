from collections import deque
from functools import wraps


class Streamable:
    def __init__(self, iterable, use_lock=None):
        super().__init__()
        self._it = iter(iterable)
        self._cache = deque()
        self.use_lock = use_lock

    def __iter__(self):
        return self

    def __next__(self):
        if self._cache:
            return self._cache.popleft()
        if self.use_lock:
            with self.use_lock:
                return next(self._it)
        else:
            return next(self._it)

    def _peek(self):
        try:
            if self.use_lock:
                with self.use_lock:
                    peek = next(self._it)
            else:
                peek = next(self._it)
        except StopIteration:
            pass
        else:
            self._cache.append(peek)

    def __bool__(self):
        self._peek()
        return bool(self._cache)

    def __repr__(self):  # pragma: no cover
        return f'<{type(self).__name__} for {self._it}>'


class StreamableList(Streamable, list):
    """
        Class specifically designed to pass isinstance(o, list)
        and conform to the implementation of json.dump(o)
        for lists, except items are provided by passed in
        generator
    """


class StreamableDict(Streamable, dict):
    """
        Class specifically designed to pass isinstance(o, dict)
        and conform to the implementation of json.dump(o)
        for lists, except items are provided by passed in
        generator. Generator must produce pairs of key/value
    """
    def items(self):
        return self


def streamable_dict(fn):
    if not callable(fn):
        return StreamableDict(fn)

    @wraps(fn)
    def wrapper(*args, **kwargs):
        return StreamableDict(fn(*args, **kwargs))
    return wrapper


def streamable_list(fn):
    if not callable(fn):
        return StreamableList(fn)

    @wraps(fn)
    def wrapper(*args, **kwargs):
        return StreamableList(fn(*args, **kwargs))
    return wrapper


__all__ = ['streamable_dict', 'streamable_list']
