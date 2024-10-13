from typing import Iterable
import itertools
from functools import singledispatch

import bpy
from bpy.types import Area, UILayout


def pop_message(message="", title="Message Box", icon="INFO"):
    def draw(self: UILayout, context):
        self.layout.label(text=message)

    if not bpy.app.background:
        bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
    else:
        print(message)


def get_image_editors(context):
    def _is_image_editor(area):
        return area.type == "IMAGE_EDITOR"

    windows = context.window_manager.windows
    screens = [window.screen for window in windows]

    areas = itertools.chain.from_iterable(screen.areas for screen in screens)
    return filter(_is_image_editor, areas)


@singledispatch
def image_editors_by_active(active, editors: Iterable[Area]):
    raise NotImplementedError


@image_editors_by_active.register
def _image_editor_active_is_none(active: None, editors: Iterable[Area]):
    return (
        ed for ed in editors
        if ed.spaces[0].image is None
    )


@image_editors_by_active.register
def _image_editor_by_image_name(active: str, editors: Iterable[Area]):
    editors_with_active = (
        ed for ed in editors
        if ed.spaces[0].image is not None
    )
    for ed in editors_with_active:
        if ed.spaces[0].name == active:
            yield ed


@image_editors_by_active.register
def _image_editor_by_image(active: str, editors: Iterable[Area]):
    editors_with_active = (
        ed for ed in editors
        if ed.spaces[0].image is not None
    )
    for ed in editors_with_active:
        # print(ed.spaces[0].image.name)
        if ed.spaces[0].image.name == active:
            yield ed

# print(list(get_image_editors(bpy.context)))