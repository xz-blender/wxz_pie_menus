"""Blender class lifecycle helpers and decorators.

Decorate register/unregister with the same ordered class sequence. Classes are
registered before setup and removed in reverse order after resource cleanup.
"""

from contextlib import contextmanager
from functools import wraps

import bpy

_REGISTERING_DEPTH = 0


@contextmanager
def _registering():
    global _REGISTERING_DEPTH
    _REGISTERING_DEPTH += 1
    try:
        yield
    finally:
        _REGISTERING_DEPTH -= 1


def is_registering():
    return _REGISTERING_DEPTH > 0


def _registered_class(cls):
    # Reloading creates a new Python object; unregister the actual RNA owner.
    registered = getattr(bpy.types, cls.__name__, None)
    if registered is not None:
        return registered
    if getattr(cls, "is_registered", False):
        return cls
    # Operators are not necessarily exposed on bpy.types.
    for base in cls.__mro__[1:]:
        lookup = getattr(base, "bl_rna_get_subclass_py", None)
        if lookup is not None:
            registered = lookup(cls.__name__, None)
            if registered is not None:
                return registered
    return None


def safe_register_class(classes):
    """Register in dependency order, replacing objects left by hot reload."""
    registered = []
    with _registering():
        try:
            for cls in classes:
                previous = _registered_class(cls)
                if previous is not None:
                    bpy.utils.unregister_class(previous)
                bpy.utils.register_class(cls)
                registered.append(cls)
        except Exception:
            safe_unregister_class(registered)
            raise


def safe_unregister_class(classes):
    """Remove classes in reverse dependency order; tolerate absent classes."""
    with _registering():
        for cls in reversed(tuple(classes)):
            registered = _registered_class(cls)
            if registered is not None:
                bpy.utils.unregister_class(registered)


def register_classes(classes):
    """Register classes before the decorated setup function."""
    classes = tuple(classes)

    def decorate(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            with _registering():
                safe_register_class(classes)
                try:
                    return func(*args, **kwargs)
                except Exception:
                    safe_unregister_class(classes)
                    raise

        return wrapped

    return decorate


def unregister_classes(classes):
    """Remove classes even when the decorated resource cleanup fails."""
    classes = tuple(classes)

    def decorate(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            with _registering():
                try:
                    return func(*args, **kwargs)
                finally:
                    safe_unregister_class(classes)

        return wrapped

    return decorate
