"""Verify Python operator renames preserve RNA IDs and hot-reload cleanup."""

import importlib.util
from pathlib import Path
import bpy
root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('registration_probe', root / 'module/reg.py')
reg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reg)
def operator(name):
    return type(name, (bpy.types.Operator,), {'bl_idname': 'wxz_test.naming_probe', 'bl_label': 'Probe', 'execute': lambda s,c: {'CANCELLED'}})
old = operator('WXZ_OT_naming_probe')
reg.safe_register_class([old])
assert old.bl_rna.identifier == 'WXZ_TEST_OT_naming_probe'
new = operator('WxzNamingProbe')
assert reg._registered_class(new) is old
reg.safe_register_class([new])
assert not old.is_registered and new.is_registered
assert bpy.ops.wxz_test.naming_probe() == {'CANCELLED'}
reg.safe_unregister_class([old])
assert not new.is_registered
assert bpy.types.Operator.bl_rna_get_subclass_py('WXZ_TEST_OT_naming_probe', None) is None
assert bpy.types.Operator.bl_rna_get_subclass_py('WXZ_INTERNAL_OT_keymap_type_refresh', None) is None
print('OPERATOR_RENAME_LIFECYCLE_PASS')
