"""Owned cleanup retains retryable items without touching unrelated keymaps."""

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch


class KeymapCleanupTests(unittest.TestCase):
    def setUp(self):
        package = 'wxz_owned_cleanup_test'
        items = ModuleType(f'{package}.items')
        items.All_Pie_keymaps = []
        self.updates = []
        bpy = SimpleNamespace(context=SimpleNamespace(window_manager=SimpleNamespace(
            keyconfigs=SimpleNamespace(update=lambda **kwargs: self.updates.append(kwargs)))))
        spec = importlib.util.spec_from_file_location(
            f'{package}.module.keymaps', Path(__file__).resolve().parents[1] / 'module/keymaps.py')
        self.helper = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'bpy': bpy, items.__name__: items}):
            spec.loader.exec_module(self.helper)
        self.tracked = items.All_Pie_keymaps

    def test_retry_retains_failures_once_removes_successes_and_preserves_peers(self):
        entries = []
        attempts = []
        failing = {1}
        live = {}

        def remove(item):
            attempts.append(item.id)
            if item.id in failing:
                raise RuntimeError('busy')
            del live[item.id]

        km = SimpleNamespace(as_pointer=lambda: 100, keymap_items=SimpleNamespace(
            from_id=live.get, remove=remove))
        for identifier in (1, 2, 3):
            live[identifier] = SimpleNamespace(id=identifier, as_pointer=lambda i=identifier: i)
        failed, successful, peer = ((km, live[i]) for i in (1, 2, 3))
        entries[:] = [failed, failed, successful]
        self.tracked[:] = [failed, successful, peer]
        self.helper._OWNERS['owner'] = entries
        with self.assertRaisesRegex(RuntimeError, 'WXZ keymap cleanup failed: busy'):
            self.helper.unregister_owned(entries)
        self.assertEqual(attempts, [1, 2])
        self.assertEqual(entries, [failed])
        self.assertEqual(self.tracked, [peer, failed])
        self.assertIs(self.helper._OWNERS['owner'], entries)
        self.assertEqual(self.updates, [{'keep_properties': True}] * 2)
        failing.clear()
        self.helper.unregister_owned(entries)
        self.assertEqual(entries, [])
        self.assertEqual(self.tracked, [peer])
        self.assertEqual(self.helper._OWNERS, {})
        self.assertEqual(attempts, [1, 2, 1])
        self.assertEqual(list(live), [3])

    def test_removal_error_after_item_disappears_does_not_require_retry(self):
        item = SimpleNamespace(id=1, as_pointer=lambda: 1)
        live = {1: item}

        def remove(item):
            del live[item.id]
            raise ReferenceError('already gone')

        km = SimpleNamespace(as_pointer=lambda: 100, keymap_items=SimpleNamespace(
            from_id=live.get, remove=remove))
        entries = [(km, item)]
        self.tracked[:] = entries
        self.helper.unregister_owned(entries)
        self.assertEqual(entries, [])
        self.assertEqual(self.tracked, [])


if __name__ == '__main__':
    unittest.main()
