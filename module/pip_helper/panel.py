from .packages import check_package_is_installed


def _draw_pip_output(layout, lines):
    text = "\n".join(item.line for item in lines)
    if hasattr(layout, "label_multiline"):
        layout.label_multiline(text=text)
    else:
        for line in text.splitlines():
            layout.label(text=line)


def draw_dependencies(self, context, layout):
    from .manifest import PIP_Packeges_Dict

    layout = layout.column()
    pip_output = context.scene.PIE_pip_output
    output: bool = any([pip_output.TEXT_OUTPUT, pip_output.ERROR_OUTPUT, pip_output.RETRUNCODE_OUTPUT])
    main_sp_fac = 0.65
    layout.label(text="依赖包设置")

    # ---
    layout = self.layout
    row = layout.box().row()
    split = row.split(factor=main_sp_fac)

    row = split.row()

    sub_split = row.split(factor=0.7)
    row = sub_split.row()
    row.prop(self, "use_china_mirror", text="阿里镜像源")

    row = split.row()
    row.operator("pie.pip_install_default")
    # ---
    layout = self.layout.box()

    row = layout.row()
    split = row.split(factor=main_sp_fac)
    row_l = split.row()
    row_l.operator("pie.ensure_pip")
    row_r = split.row(align=True)
    row_r.operator("pie.upgrade_pip")
    row_r.operator("pie.pip_show_list")

    row = layout.row(align=True)
    split = row.split(factor=main_sp_fac)
    split.scale_y = 1.4
    row_l = split.row()
    split_l = row_l.split(factor=0.4, align=True)
    row_ll = split_l.row()
    row_ll.label(text="输入包名(空格分割):")
    row_lr = split_l.row()
    row_lr.prop(self, "install_custom_pip_packages", text="")
    row_r = split.row(align=True)
    row_r.operator("pie.pip_install")
    row_r.operator("pie.pip_remove")

    col = layout.column(align=True)
    col.scale_y = 0.8
    # 使用网格布局，4 列等宽，最后一行不足列数也能对齐
    grid = col.grid_flow(row_major=True, columns=4, even_columns=False, even_rows=False, align=True)
    for key, value in PIP_Packeges_Dict.items():
        box = grid.box()
        if check_package_is_installed(value):
            icon = "CHECKMARK"
        else:
            icon = "PANEL_CLOSE"
        box.label(text=key, icon=icon)

    # ---
    layout = layout.box()

    row = layout.row()
    sub_row = row.split(factor=0.65)
    row = sub_row.row()
    row.label(text="最后一次输出:", icon="CONSOLE")
    row = sub_row.row()
    row.operator("pie.pip_cleartext", text="清除文本")

    if output:
        row = layout.row()
        box = row.column(align=True)

        if pip_output.RETRUNCODE_OUTPUT:
            row = box.row().box()
            row.label(text=f"执行结果:   {pip_output.RETRUNCODE_OUTPUT}")

        if pip_output.TEXT_OUTPUT:
            row = box.row().box().column(align=True)
            row.label(text="输出结果:")
            _draw_pip_output(row, pip_output.TEXT_OUTPUT)

        if pip_output.ERROR_OUTPUT:
            row = box.row().box().column(align=True)
            row.label(text="错误信息:")
            _draw_pip_output(row, pip_output.ERROR_OUTPUT)
