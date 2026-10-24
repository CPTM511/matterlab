"""Capture actual method returns without changing their values or call counts."""
from functools import wraps

def capture_method(instance, name, callback):
    original = getattr(instance, name)
    @wraps(original)
    def wrapped(*args, **kwargs):
        result = original(*args, **kwargs)
        callback(result)
        return result
    setattr(instance, name, wrapped)
    return original
