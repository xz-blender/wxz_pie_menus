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


def _rna_identifier(cls):
    # Explicit operator IDs are independent of Python class names. Blender
    # exposes e.g. pie.mesh_f_gesture as PIE_OT_mesh_f_gesture in RNA.
    operator_type = getattr(bpy.types, "Operator", None)
    if operator_type is not None and issubclass(cls, operator_type):
        category, separator, name = getattr(cls, "bl_idname", "").partition(".")
        if separator:
            return f"{category.upper()}_OT_{name}"
    return cls.__name__


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
            # None from a concrete RNA family is final. Falling through to
            # generic bpy_struct can dereference freed RNA after unregister.
            return lookup(_rna_identifier(cls), None)
    return None


def _tag_legacy_operator_keymap_refresh(classes):
    """Backport the native operator-registration refresh for Blender < 4.5.3.

    Blender #143838 (4.5 LTS commit dabca7703b) fixed operator registration
    failing to tag dormant keymap properties for an RNA-type refresh. Without
    that flag a feature disabled across another operator's removal can lose its
    customized shortcut on re-enable. There is no public Python tag API on old
    versions. Registering/removing our private, inert operator supplies the same
    native flag. It never runs and owns no keymap, handler or lasting class.
    No default/user item is read, cached, copied or written by this workaround.
    https://www.blender.org/releases/4-5/ (4.5.3 corrective release, #143838)
    """
    version = getattr(getattr(bpy, "app", None), "version", (999, 0, 0))
    operator_type = getattr(bpy.types, "Operator", None)
    if version >= (4, 5, 3) or operator_type is None:
        return
    if not any(issubclass(cls, operator_type) for cls in classes):
        return

    class WxzKeymapTypeRefresh(operator_type):
        bl_idname = "wxz_internal.keymap_type_refresh"
        bl_label = "WXZ Internal Keymap Type Refresh"
        bl_options = {"INTERNAL"}

        def execute(self, context):
            return {"CANCELLED"}

    if _registered_class(WxzKeymapTypeRefresh) is not None:
        raise RuntimeError("WXZ temporary keymap refresh operator is unexpectedly registered")
    registered = False
    try:
        bpy.utils.register_class(WxzKeymapTypeRefresh)
        registered = True
    finally:
        if registered:
            # Removing this inert type marks operator metadata dirty; Blender's
            # normal native update then reconnects diffs to the restored types.
            bpy.utils.unregister_class(WxzKeymapTypeRefresh)


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
            _tag_legacy_operator_keymap_refresh(registered)
        except Exception:
            safe_unregister_class(registered)
            raise


def safe_unregister_class(classes):
    """Remove classes in reverse dependency order; tolerate absent classes."""
    removed = False
    with _registering():
        for cls in reversed(tuple(classes)):
            registered = _registered_class(cls)
            if registered is not None:
                bpy.utils.unregister_class(registered)
                removed = True
        # Preserve dormant native user-keymap diffs while another feature's
        # operators are absent during a full add-on disable/reload sequence.
        context = getattr(bpy, "context", None)
        wm = getattr(context, "window_manager", None)
        configs = getattr(wm, "keyconfigs", None)
        if removed and configs is not None:
            configs.update(keep_properties=True)


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
