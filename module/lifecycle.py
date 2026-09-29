"""Feature lifecycle orchestration, independent of Blender.

The host supplies saved intent, legacy preference cleanup and error reporting.
Feature hooks keep their existing zero-argument contract. ACTIVE means register
returned normally; hooks remain responsible for their own resources.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType


class ModuleState(str, Enum):
    DISABLED = "disabled"
    ACTIVE = "active"
    ENABLE_FAILED = "enable_failed"
    CLEANUP_FAILED = "cleanup_failed"


@dataclass(frozen=True)
class LifecycleError:
    stage: str
    message: str


@dataclass(frozen=True)
class ModuleStatus:
    name: str
    desired: bool
    state: ModuleState
    errors: tuple[LifecycleError, ...] = ()


@dataclass(frozen=True)
class LifecycleStep:
    name: str
    register: Callable[[], None]
    unregister: Callable[[], None]


class AddonLifecycle:
    """One catalog and cleanup ledger shared by startup, toggles and shutdown.

    Repeated commands are idempotent. Failed features are retried only by retry,
    a changed intent, or a new start after stop. Reentrant commands are ignored
    while hooks or host preference updates are in progress.
    """

    def __init__(self, groups, host, *, before_features=(), after_features=()):
        self.groups = MappingProxyType({name: tuple(modules) for name, modules in groups.items()})
        self._modules = {}
        for modules in self.groups.values():
            for module in modules:
                name = module.__name__.rsplit(".", 1)[-1]
                if name in self._modules:
                    raise ValueError(f"Duplicate feature module name: {name}")
                self._modules[name] = module
        self._host = host
        self._before_features = tuple(before_features)
        self._after_features = tuple(after_features)
        self._before_cleanup = []
        self._after_cleanup = []
        self._statuses = {name: ModuleStatus(name, True, ModuleState.DISABLED) for name in self._modules}
        # Entries are inserted before registration. True means the feature hook
        # still needs cleanup; False means only legacy preferences need cleanup.
        self._cleanup = {}
        self._busy = False
        self._running = False
        self._core_ready = False

    def status(self, name):
        """Return an immutable snapshot, without reading or changing the host."""
        return self._statuses[name]

    def start(self):
        if self._busy or self._running:
            return self._snapshot()
        self._busy = True
        startup_attempted = False
        try:
            # A failed core cleanup must be resolved before replacing its types.
            errors = self._cleanup_steps(self._after_cleanup) + self._cleanup_steps(self._before_cleanup)
            if errors:
                raise errors[0]
            startup_attempted = True
            for step in self._before_features:
                self._start_step(step, self._before_cleanup)
            self._core_ready = True
            for name in self._modules:
                self._set_status(name, desired=bool(self._host.desired(name)))
                self._reconcile(name)
            for step in self._after_features:
                self._start_step(step, self._after_cleanup)
            self._running = True
        except Exception:
            # Cleanup reports its own errors without masking the startup error.
            if startup_attempted:
                self._stop()
            raise
        finally:
            self._busy = False
        return self._snapshot()

    def stop(self):
        if self._busy:
            return self._snapshot()
        self._busy = True
        try:
            self._stop()
        finally:
            self._busy = False
        return self._snapshot()

    def set_enabled(self, name, desired):
        current = self.status(name)
        if self._busy:
            return current
        desired = bool(desired)
        self._busy = True
        try:
            self._host.set_desired(name, desired)
            self._set_status(name, desired=desired)
            if self._running and current.desired != desired:
                self._reconcile(name)
        finally:
            self._busy = False
        return self.status(name)

    def retry(self, name):
        current = self.status(name)
        if self._busy or not self._running:
            return current
        self._busy = True
        try:
            self._set_status(name, desired=bool(self._host.desired(name)))
            self._reconcile(name)
        finally:
            self._busy = False
        return self.status(name)

    def _snapshot(self):
        return tuple(self._statuses.values())

    def _set_status(self, name, **changes):
        current = self.status(name)
        self._statuses[name] = ModuleStatus(
            name,
            changes.get("desired", current.desired),
            changes.get("state", current.state),
            changes.get("errors", current.errors),
        )

    def _feature_error(self, name, stage, error):
        errors = tuple(item for item in self.status(name).errors if item.stage != stage)
        error_text = f"{type(error).__name__}: {error}"
        self._set_status(name, errors=errors + (LifecycleError(stage, error_text),))
        self._host.report_error(name, stage, error)

    def _reconcile(self, name):
        current = self.status(name)
        if current.state == ModuleState.ACTIVE and current.desired:
            return
        if name in self._cleanup and not self._cleanup_feature(name):
            return
        if not current.desired:
            self._set_status(name, state=ModuleState.DISABLED, errors=())
            return
        self._set_status(name, errors=())
        self._cleanup[name] = True
        try:
            self._modules[name].register()
        except Exception as error:
            self._feature_error(name, "register", error)
            if self._cleanup_feature(name):
                self._set_status(name, state=ModuleState.ENABLE_FAILED)
        else:
            self._set_status(name, state=ModuleState.ACTIVE, errors=())

    def _cleanup_feature(self, name):
        stage = "unregister"
        try:
            if self._cleanup[name]:
                self._modules[name].unregister()
                self._cleanup[name] = False
            stage = "preferences"
            self._host.after_disable(name)
        except Exception as error:
            self._set_status(name, state=ModuleState.CLEANUP_FAILED)
            self._feature_error(name, stage, error)
            return False
        del self._cleanup[name]
        self._set_status(name, state=ModuleState.DISABLED)
        return True

    def _start_step(self, step, ledger):
        # Include the failing stage: it may have created resources before raising.
        ledger.append(step)
        try:
            step.register()
        except Exception as error:
            self._host.report_error(step.name, "core_register", error)
            raise

    def _cleanup_steps(self, ledger):
        errors = []
        for step in reversed(tuple(ledger)):
            try:
                step.unregister()
            except Exception as error:
                errors.append(error)
                self._host.report_error(step.name, "core_unregister", error)
            else:
                ledger.remove(step)
        return errors

    def _stop(self):
        self._cleanup_steps(self._after_cleanup)
        if self._core_ready:
            for name in reversed(tuple(self._cleanup)):
                if self._cleanup_feature(name):
                    self._set_status(name, errors=())
        self._cleanup_steps(self._before_cleanup)
        self._core_ready = False
        self._running = False
