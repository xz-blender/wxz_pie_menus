"""Lifecycle contract tests without importing Blender or the add-on entrypoint."""

import importlib
import sys
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "_wxz_lifecycle_test"
package = ModuleType(PACKAGE)
package.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = package
lifecycle_module = importlib.import_module(f"{PACKAGE}.module.lifecycle")
AddonLifecycle = lifecycle_module.AddonLifecycle
LifecycleStep = lifecycle_module.LifecycleStep
ModuleState = lifecycle_module.ModuleState


class Host:
    def __init__(self, events):
        self.events = events
        self.preferences = {}
        self.errors = []
        self.on_change = None
        self.cleanup_error = None

    def desired(self, name):
        return self.preferences.get(name, True)

    def set_desired(self, name, desired):
        self.preferences[name] = desired
        if self.on_change:
            self.on_change(name, desired)

    def after_disable(self, name):
        if self.cleanup_error:
            raise self.cleanup_error

    def report_error(self, name, stage, error):
        self.errors.append((name, stage, error))


class AddonLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.failures = {}
        self.host = Host(self.events)
        self.features = [self.feature(name) for name in ("alpha", "beta", "gamma")]
        self.lifecycle = AddonLifecycle(
            {"pie_modules": self.features[:2], "other_modules": self.features[2:], "setting_modules": []},
            self.host,
            before_features=[self.step("types"), self.step("preferences")],
            after_features=[self.step("translation")],
        )

    def hook(self, name, stage):
        def invoke():
            self.events.append((name, stage))
            error = self.failures.get((name, stage))
            if error:
                raise error

        return invoke

    def feature(self, name):
        return SimpleNamespace(
            __name__="addon.features." + name,
            register=self.hook(name, "register"),
            unregister=self.hook(name, "unregister"),
        )

    def step(self, name):
        return LifecycleStep(name, self.hook(name, "register"), self.hook(name, "unregister"))

    def test_startup_order_and_reverse_shutdown_keep_core_alive(self):
        self.lifecycle.start()
        self.lifecycle.stop()
        order = ["types", "preferences", "alpha", "beta", "gamma", "translation"]
        self.assertEqual(
            self.events,
            [(name, "register") for name in order] + [(name, "unregister") for name in reversed(order)],
        )
        self.assertEqual(self.lifecycle.status("alpha").state, ModuleState.DISABLED)

    def test_saved_off_choice_survives_two_cycles_and_defaults_are_enabled(self):
        self.host.preferences["beta"] = False
        for _ in range(2):
            self.lifecycle.start()
            self.assertEqual(self.lifecycle.status("alpha").state, ModuleState.ACTIVE)
            self.assertEqual(self.lifecycle.status("beta").state, ModuleState.DISABLED)
            self.assertFalse(self.lifecycle.status("beta").desired)
            self.lifecycle.stop()
        self.assertNotIn(("beta", "register"), self.events)
        self.assertEqual(self.events.count(("alpha", "register")), 2)
        self.assertFalse(self.host.preferences["beta"])

    def test_unchanged_commands_and_repeated_shutdown_do_not_repeat_hooks(self):
        self.lifecycle.start()
        first_start = list(self.events)
        self.lifecycle.start()
        self.lifecycle.set_enabled("alpha", True)
        self.lifecycle.retry("alpha")
        self.assertEqual(self.events, first_start)
        self.lifecycle.set_enabled("alpha", False)
        self.lifecycle.set_enabled("alpha", False)
        self.lifecycle.set_enabled("alpha", True)
        self.assertEqual(self.events.count(("alpha", "register")), 2)
        self.assertEqual(self.events.count(("alpha", "unregister")), 1)
        self.lifecycle.stop()
        stopped = list(self.events)
        self.lifecycle.stop()
        self.assertEqual(self.events, stopped)

    def test_failed_registration_never_becomes_active_and_later_modules_continue(self):
        failure = ValueError("registration failed")
        self.failures["beta", "register"] = failure
        self.lifecycle.start()
        status = self.lifecycle.status("beta")
        self.assertEqual(status.state, ModuleState.ENABLE_FAILED)
        self.assertTrue(status.desired)
        self.assertTrue(self.host.desired("beta"))
        self.assertEqual(self.lifecycle.status("gamma").state, ModuleState.ACTIVE)
        self.assertIn(("beta", "unregister"), self.events)
        self.assertIn(("beta", "register", failure), self.host.errors)
        self.assertEqual(status.errors[0].message, "ValueError: registration failed")

    def test_failure_is_retried_only_on_explicit_retry_or_new_start(self):
        self.failures["beta", "register"] = RuntimeError("temporary")
        self.lifecycle.start()
        self.lifecycle.set_enabled("beta", True)
        self.lifecycle.status("beta")
        self.lifecycle.start()
        self.assertEqual(self.events.count(("beta", "register")), 1)
        del self.failures["beta", "register"]
        self.lifecycle.retry("beta")
        self.assertEqual(self.events.count(("beta", "register")), 2)
        self.assertEqual(self.lifecycle.status("beta").state, ModuleState.ACTIVE)
        self.assertEqual(self.lifecycle.status("beta").errors, ())

    def test_new_start_retries_failed_enable_without_changing_saved_intent(self):
        self.failures["beta", "register"] = RuntimeError("temporary")
        self.lifecycle.start()
        self.lifecycle.stop()
        del self.failures["beta", "register"]
        self.lifecycle.start()
        self.assertEqual(self.lifecycle.status("beta").state, ModuleState.ACTIVE)
        self.assertTrue(self.host.desired("beta"))

    def test_registration_and_cleanup_errors_are_both_retained(self):
        self.failures["beta", "register"] = ValueError("cannot enable")
        self.failures["beta", "unregister"] = RuntimeError("cannot clean up")
        self.lifecycle.start()
        status = self.lifecycle.status("beta")
        self.assertEqual(status.state, ModuleState.CLEANUP_FAILED)
        self.assertEqual([error.stage for error in status.errors], ["register", "unregister"])
        del self.failures["beta", "register"]
        self.lifecycle.retry("beta")
        self.assertEqual(self.events.count(("beta", "register")), 1)
        del self.failures["beta", "unregister"]
        self.lifecycle.retry("beta")
        self.assertEqual(self.events[-2:], [("beta", "unregister"), ("beta", "register")])
        self.assertEqual(self.lifecycle.status("beta").state, ModuleState.ACTIVE)

    def test_turning_off_clean_failed_enable_does_not_call_cleanup_twice(self):
        self.failures["beta", "register"] = ValueError("cannot enable")
        self.lifecycle.start()
        old_events = list(self.events)
        self.lifecycle.set_enabled("beta", False)
        self.assertEqual(self.events, old_events)
        self.assertEqual(self.lifecycle.status("beta").state, ModuleState.DISABLED)
        self.assertEqual(self.lifecycle.status("beta").errors, ())

    def test_changed_intent_retries_a_failed_enable(self):
        self.failures["beta", "register"] = ValueError("temporary")
        self.lifecycle.start()
        self.lifecycle.set_enabled("beta", False)
        del self.failures["beta", "register"]
        self.lifecycle.set_enabled("beta", True)
        self.assertEqual(self.lifecycle.status("beta").state, ModuleState.ACTIVE)

    def test_failed_disable_continues_shutdown_and_keeps_cleanup_debt(self):
        self.lifecycle.start()
        self.failures["beta", "unregister"] = RuntimeError("cleanup failed")
        self.lifecycle.set_enabled("beta", False)
        self.assertFalse(self.lifecycle.status("beta").desired)
        self.assertEqual(self.lifecycle.status("beta").state, ModuleState.CLEANUP_FAILED)
        self.lifecycle.stop()
        self.assertIn(("alpha", "unregister"), self.events)
        self.assertEqual(self.events[-1], ("types", "unregister"))
        stopped = list(self.events)
        self.lifecycle.stop()
        self.lifecycle.retry("beta")
        self.assertEqual(self.events, stopped, "Cannot retry feature cleanup after shared types are gone")
        del self.failures["beta", "unregister"]
        self.lifecycle.start()
        next_start = self.events[len(stopped) :]
        self.assertLess(next_start.index(("preferences", "register")), next_start.index(("beta", "unregister")))
        self.assertNotIn(("beta", "register"), next_start)
        self.assertEqual(self.lifecycle.status("beta").state, ModuleState.DISABLED)

    def test_cleanup_debt_precedes_reenable_on_new_start(self):
        self.lifecycle.start()
        self.failures["beta", "unregister"] = RuntimeError("cleanup failed")
        self.lifecycle.stop()
        del self.failures["beta", "unregister"]
        self.events.clear()
        self.lifecycle.start()
        self.assertLess(self.events.index(("beta", "unregister")), self.events.index(("beta", "register")))

    def test_preference_cleanup_retry_does_not_repeat_successful_feature_cleanup(self):
        self.lifecycle.start()
        self.host.cleanup_error = RuntimeError("preferences busy")
        self.lifecycle.set_enabled("beta", False)
        self.assertEqual(self.lifecycle.status("beta").state, ModuleState.CLEANUP_FAILED)
        self.host.cleanup_error = None
        self.lifecycle.retry("beta")
        self.assertEqual(self.events.count(("beta", "unregister")), 1)
        self.assertEqual(self.lifecycle.status("beta").state, ModuleState.DISABLED)

    def test_core_failure_unwinds_failed_stage_and_preserves_original_error(self):
        original = ValueError("cannot create preferences")
        self.failures["preferences", "register"] = original
        self.failures["preferences", "unregister"] = RuntimeError("partial cleanup")
        with self.assertRaises(ValueError) as caught:
            self.lifecycle.start()
        self.assertIs(caught.exception, original)
        self.assertEqual(
            self.events,
            [
                ("types", "register"),
                ("preferences", "register"),
                ("preferences", "unregister"),
                ("types", "unregister"),
            ],
        )
        self.assertEqual([stage for _, stage, _ in self.host.errors], ["core_register", "core_unregister"])

    def test_post_feature_failure_unwinds_features_before_core(self):
        self.failures["translation", "register"] = RuntimeError("translation failed")
        with self.assertRaisesRegex(RuntimeError, "translation failed"):
            self.lifecycle.start()
        self.assertEqual(
            self.events[-6:],
            [
                ("translation", "unregister"),
                ("gamma", "unregister"),
                ("beta", "unregister"),
                ("alpha", "unregister"),
                ("preferences", "unregister"),
                ("types", "unregister"),
            ],
        )
        self.failures.clear()
        self.lifecycle.start()
        self.assertEqual(self.lifecycle.status("alpha").state, ModuleState.ACTIVE)

    def test_unresolved_core_cleanup_blocks_new_registration_without_retry_loop(self):
        self.lifecycle.start()
        self.failures["preferences", "unregister"] = RuntimeError("core cleanup failed")
        self.lifecycle.stop()
        self.events.clear()
        with self.assertRaisesRegex(RuntimeError, "core cleanup failed"):
            self.lifecycle.start()
        self.assertEqual(self.events, [("preferences", "unregister")])
        self.failures.clear()
        self.lifecycle.start()
        self.assertEqual(self.lifecycle.status("alpha").state, ModuleState.ACTIVE)

    def test_host_updates_and_feature_hooks_cannot_reenter_lifecycle(self):
        self.host.on_change = self.lifecycle.set_enabled
        original_hook = self.features[0].register

        def register():
            self.lifecycle.retry("alpha")
            self.lifecycle.set_enabled("alpha", True)
            original_hook()

        self.features[0].register = register
        self.lifecycle.start()
        self.lifecycle.set_enabled("alpha", False)
        self.lifecycle.set_enabled("alpha", True)
        self.assertEqual(self.events.count(("alpha", "register")), 2)
        self.assertEqual(self.events.count(("alpha", "unregister")), 1)

    def test_catalog_and_status_snapshots_cannot_be_changed_by_callers(self):
        self.lifecycle.start()
        status = self.lifecycle.status("alpha")
        self.lifecycle.set_enabled("alpha", False)
        self.assertEqual(status.state, ModuleState.ACTIVE)
        self.assertEqual(
            [module.__name__ for module in self.lifecycle.groups["pie_modules"]],
            [
                "addon.features.alpha",
                "addon.features.beta",
            ],
        )
        with self.assertRaises(TypeError):
            self.lifecycle.groups["pie_modules"] = ()


if __name__ == "__main__":
    unittest.main()
