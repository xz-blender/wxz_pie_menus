"""Owned add-on keymaps. Never edit Blender's default or user key configuration.

Keep the actual RNA objects we created, not names or operator-based deletion
queries. The owner table also survives feature-module reloads.
"""

from functools import wraps
import bpy
from ..items import All_Pie_keymaps

_OWNERS = {}


def _pointer(value):
    try:
        return value.as_pointer()
    except (ReferenceError, RuntimeError):
        return 0


def _live(km, kmi):
    try:
        return bool(_pointer(kmi)) and km.keymap_items.from_id(kmi.id) == kmi
    except (ReferenceError, RuntimeError):
        return False


def track_keymaps(entries):
    known = {(_pointer(km), _pointer(kmi)) for km, kmi in All_Pie_keymaps}
    for km, kmi in entries:
        identity = (_pointer(km), _pointer(kmi))
        if _live(km, kmi) and identity not in known:
            All_Pie_keymaps.append((km, kmi))
            known.add(identity)


def unregister_owned(entries):
    """Attempt every owned removal; retain failed items for lifecycle retry."""
    if not entries:
        return
    # Flush pending native UI edits while the original templates still exist.
    # Otherwise Blender may diff a just-edited user item against a removed base.
    wm = getattr(bpy.context, "window_manager", None)
    if wm is not None:
        wm.keyconfigs.update(keep_properties=True)
    identities = {(_pointer(km), _pointer(kmi)) for km, kmi in entries}
    All_Pie_keymaps[:] = [pair for pair in All_Pie_keymaps if (_pointer(pair[0]), _pointer(pair[1])) not in identities]
    failed = []
    errors = []
    seen = set()
    for km, kmi in tuple(entries):
        identity = (_pointer(km), _pointer(kmi))
        if identity in seen:
            continue
        seen.add(identity)
        if not _live(km, kmi):
            continue
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError) as exc:
            if _live(km, kmi):
                failed.append((km, kmi))
                errors.append(str(exc))
    entries[:] = failed
    for owner, owned in list(_OWNERS.items()):
        if owned is entries or not any(_live(*pair) for pair in owned):
            if not failed:
                _OWNERS.pop(owner, None)
    track_keymaps(failed)
    # Rebuild the native merged map while custom operators still exist. If
    # classes disappear first, Blender 4.3 can lose the saved user diff when
    # it cleans zombie operator properties. This is a native merge only.
    if wm is not None:
        wm.keyconfigs.update(keep_properties=True)
    if errors:
        raise RuntimeError("WXZ keymap cleanup failed: " + "; ".join(errors))


def owned_keymaps(register):
    """Idempotent registration with rollback, including untracked new items."""

    @wraps(register)
    def wrapped(*args, **kwargs):
        entries = register.__globals__["addon_keymaps"]
        owner = register.__module__
        previous = _OWNERS.get(owner, entries)
        if previous is not entries:
            entries[:] = previous
            _OWNERS[owner] = entries
        live = [pair for pair in entries if _live(*pair)]
        if live:
            # Do not recreate templates and disturb Blender's user diff mapping.
            entries[:] = live
            track_keymaps(entries)
            return
        entries.clear()
        wm = getattr(bpy.context, "window_manager", None)
        addon = wm.keyconfigs.addon if wm else None
        if addon is None:
            return
        before = {_pointer(kmi) for km in addon.keymaps for kmi in km.keymap_items}
        try:
            result = register(*args, **kwargs)
        except Exception:
            entries[:] = [(km, kmi) for km in addon.keymaps for kmi in km.keymap_items if _pointer(kmi) not in before]
            unregister_owned(entries)
            raise
        # Capture every item the synchronous registration actually created. This
        # also catches accidental missing append calls, without touching peers.
        entries[:] = [(km, kmi) for km in addon.keymaps for kmi in km.keymap_items if _pointer(kmi) not in before]
        _OWNERS[owner] = entries
        track_keymaps(entries)
        return result

    return wrapped
