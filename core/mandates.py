import os
from typing import Optional, Protocol, runtime_checkable

@runtime_checkable
class BoltEngine(Protocol):
    def stream_chat(self, prompt: str, model: str = "default", options: Optional[dict] = None): ...

@runtime_checkable
class PaletteComponent(Protocol):
    def apply_theme(self): ...

@runtime_checkable
class SentinelGuard(Protocol):
    def scan_integrity(self) -> bool: ...

def aura_component(cls):
    if not hasattr(cls, "__slots__"):
        setattr(cls, "__slots__", ())
    def check_mandates(self):
        results = {
            "Bolt": isinstance(self, BoltEngine),
            "Palette": isinstance(self, PaletteComponent),
            "Sentinel": isinstance(self, SentinelGuard)
        }
        return all(results.values())
    cls.check_mandates = check_mandates
    return cls
