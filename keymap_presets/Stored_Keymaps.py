keyconfig_version = (3, 3, 6)
keyconfig_data = \
[]


if __name__ == "__main__":
    # Only add keywords that are supported.
    from bpy.app import version as blender_version
    keywords = {}
    if blender_version >= (2, 92, 0):
        keywords["keyconfig_version"] = keyconfig_version
    import os
    from bl_keymap_utils.io import keyconfig_import_from_data
    keyconfig_import_from_data(
        os.path.splitext(os.path.basename(__file__))[0],
        keyconfig_data,
        **keywords,
    )
