"""Class lifecycle tests without a Blender installation."""

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.types = SimpleNamespace()
        self.fail = None

        def register(cls):
            if cls is self.fail:
                raise ValueError("registration failed")
            setattr(self.types, cls.__name__, cls)
            self.events.append(("register", cls))

        def unregister(cls):
            self.assertIs(getattr(self.types, cls.__name__), cls)
            delattr(self.types, cls.__name__)
            self.events.append(("unregister", cls))

        bpy = SimpleNamespace(types=self.types, utils=SimpleNamespace(register_class=register, unregister_class=unregister))
        spec = importlib.util.spec_from_file_location("registration_under_test", Path(__file__).parents[1] / "module/reg.py")
        self.reg = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"bpy": bpy}):
            spec.loader.exec_module(self.reg)
        self.a = type("A", (), {})
        self.b = type("B", (), {})

    def test_order_and_repeated_unload(self):
        @self.reg.register_classes([self.a, self.b])
        def setup():
            self.assertTrue(self.reg.is_registering())
            self.events.append("setup")
            return 42

        @self.reg.unregister_classes([self.a, self.b])
        def cleanup():
            self.events.append("cleanup")

        self.assertEqual(setup(), 42)
        cleanup()
        self.assertEqual(self.events, [("register", self.a), ("register", self.b), "setup", "cleanup",
                                       ("unregister", self.b), ("unregister", self.a)])
        cleanup()
        self.assertFalse(self.reg.is_registering())

    def test_reload_replaces_old_object(self):
        self.reg.safe_register_class([self.a])
        replacement = type("A", (), {})
        self.reg.safe_register_class([replacement])
        self.assertEqual(self.events[-2:], [("unregister", self.a), ("register", replacement)])
        self.reg.safe_unregister_class([self.a])
        self.assertFalse(hasattr(self.types, "A"))

    def test_registration_failure_rolls_back(self):
        self.fail = self.b
        with self.assertRaisesRegex(ValueError, "registration failed"):
            self.reg.safe_register_class([self.a, self.b])
        self.assertFalse(hasattr(self.types, "A"))
        self.assertFalse(self.reg.is_registering())

    def test_rna_lookup_for_classes_not_exposed_on_bpy_types(self):
        old = type("HiddenOperator", (), {})

        class Operator:
            @classmethod
            def bl_rna_get_subclass_py(cls, name, default=None):
                return old if name == "HiddenOperator" else default

        replacement = type("HiddenOperator", (Operator,), {})
        self.assertIs(self.reg._registered_class(replacement), old)

    def test_callback_failures_release_classes_and_guard(self):
        def fail():
            raise ValueError("callback failed")

        with self.assertRaisesRegex(ValueError, "callback failed"):
            self.reg.register_classes([self.a])(fail)()
        self.assertFalse(hasattr(self.types, "A"))
        self.reg.safe_register_class([self.a])
        with self.assertRaisesRegex(ValueError, "callback failed"):
            self.reg.unregister_classes([self.a])(fail)()
        self.assertFalse(hasattr(self.types, "A"))
        self.assertFalse(self.reg.is_registering())


if __name__ == "__main__":
    unittest.main()
