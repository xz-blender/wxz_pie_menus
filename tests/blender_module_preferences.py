"""Run with blender --background --factory-startup --python-exit-code 1 --python this_file.

Import production lifecycle/RNA declarations under an inert package, exercising
real Blender preferences without importing unrelated tools or saving preferences.
"""

import importlib
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import bpy

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "_wxz_lifecycle_blender_test"
package = ModuleType(PACKAGE)
package.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = package
core = importlib.import_module(f"{PACKAGE}.module.lifecycle")
adapter = importlib.import_module(f"{PACKAGE}.module.lifecycle_blender")
reg = importlib.import_module(f"{PACKAGE}.module.reg")

events = []
failures = {}


def feature(name):
    def hook(stage):
        def invoke():
            events.append((name, stage))
            if failures.get((name, stage)):
                raise RuntimeError(f"{name} {stage} test failure")

        return invoke

    return SimpleNamespace(__name__=f"test_features.{name}", register=hook("register"), unregister=hook("unregister"))


groups = {
    "pie_modules": [feature("first"), feature("second")],
    "other_modules": [feature("broken")],
    "setting_modules": [feature("cleanup")],
}


class ProbePreferences(bpy.types.AddonPreferences):
    bl_idname = PACKAGE
    existing_preference: bpy.props.BoolProperty(default=True)  # type: ignore
    __annotations__.update(adapter.module_collection_properties())


adapter.bind_module_toggles(ProbePreferences, [module for modules in groups.values() for module in modules])
host = adapter.BlenderLifecycleHost(PACKAGE, lambda: ProbePreferences)
item_classes = [adapter.PIE_ModuleItem, adapter.PIE_Retry_Module]
lifecycle = core.AddonLifecycle(
    groups,
    host,
    before_features=(
        core.LifecycleStep(
            "items", lambda: reg.safe_register_class(item_classes), lambda: reg.safe_unregister_class(item_classes)
        ),
        core.LifecycleStep(
            "preferences",
            lambda: reg.safe_register_class([ProbePreferences]),
            lambda: reg.safe_unregister_class([ProbePreferences]),
        ),
    ),
    after_features=(core.LifecycleStep("lists", lambda: host.rebuild_collections(lifecycle.groups), lambda: None),),
)
adapter.bind_lifecycle(lifecycle)


class Layout:
    def __init__(self):
        self.labels = []
        self.operators = []

    def row(self):
        return self

    def label(self, **kwargs):
        self.labels.append(kwargs)

    def prop(self, owner, name, **kwargs):
        getattr(owner, name)

    def operator(self, operator_id, **kwargs):
        properties = SimpleNamespace(module_name="")
        self.operators.append((operator_id, properties))
        return properties


entry = bpy.context.preferences.addons.new()
entry.module = PACKAGE
try:
    for cycle in range(2):
        failures["broken", "register"] = True
        lifecycle.start()
        preferences = entry.preferences
        assert preferences.existing_preference, "Collection declarations must preserve other annotations"
        assert preferences.use_second is (cycle == 0), "Saved off intent must survive an unregister/register cycle"
        for name, modules in groups.items():
            collection = getattr(preferences, name)
            assert [item.name for item in collection] == [module.__name__.rsplit(".", 1)[-1] for module in modules]
            first_name = collection[0].name
            assert collection[first_name].name == first_name
            collection[0].name = "renamed"
            assert collection["renamed"].name == "renamed"
        host.rebuild_collections(lifecycle.groups)
        assert preferences.pie_modules["first"].name == "first"

        preferences.use_first = False
        assert lifecycle.status("first").state == core.ModuleState.DISABLED
        preferences.use_first = True
        assert lifecycle.status("first").state == core.ModuleState.ACTIVE

        assert preferences.use_broken, "A failed enable must not change the saved switch"
        assert lifecycle.status("broken").state == core.ModuleState.ENABLE_FAILED
        before_draw = list(events)
        layout = Layout()
        adapter.draw_module_item(layout, preferences, preferences.other_modules["broken"])
        assert any(label.get("icon") == "ERROR" for label in layout.labels)
        assert layout.operators[0][0] == "pie.retry_module"
        assert layout.operators[0][1].module_name == "broken"
        assert events == before_draw, "Drawing status must never retry hooks"
        assert "broken register test failure" in adapter.PIE_Retry_Module.description(
            bpy.context, layout.operators[0][1]
        )
        failures["broken", "register"] = False
        assert bpy.ops.pie.retry_module(module_name="broken") == {"FINISHED"}
        assert lifecycle.status("broken").state == core.ModuleState.ACTIVE
        assert not lifecycle.status("broken").errors

        failures["cleanup", "unregister"] = True
        preferences.use_cleanup = False
        assert not preferences.use_cleanup
        assert lifecycle.status("cleanup").state == core.ModuleState.CLEANUP_FAILED
        failures["cleanup", "unregister"] = False
        assert bpy.ops.pie.retry_module(module_name="cleanup") == {"FINISHED"}
        assert lifecycle.status("cleanup").state == core.ModuleState.DISABLED
        preferences.use_cleanup = True
        preferences.use_second = False
        lifecycle.stop()
        assert not ProbePreferences.is_registered
        assert all(not cls.is_registered for cls in item_classes)
        print(
            f"PASS: native collections, saved intent, callbacks, error display, retry and lifecycle cycle {cycle + 1}"
        )
finally:
    lifecycle.stop()
    adapter.bind_lifecycle(None)
    bpy.context.preferences.addons.remove(entry)
