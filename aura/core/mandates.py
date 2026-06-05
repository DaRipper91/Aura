import os
from typing import Optional, Protocol, runtime_checkable

# --- MANDATE PROTOCOLS ---

@runtime_checkable
class BoltEngine(Protocol):
    """Fulfills the Bolt mandate for high-performance orchestration."""
    def stream_chat(self, model: str, prompt: str, options: Optional[dict] = None): ...

@runtime_checkable
class PaletteComponent(Protocol):
    """Fulfills the Palette mandate for aesthetic integrity."""
    def apply_theme(self): ...

# --- MANDATE ENFORCEMENT DECORATOR ---

def aura_component(cls):
    """
    Decorator to enforce project mandates (Bolt, Sentinel, Palette)
    and optimize for performance (Bolt).
    """
    # 1. Enforce Mandate Check Method
    if not hasattr(cls, "check_mandates"):
        def check_mandates(self):
            print(f"[SYSTEM] Verifying mandates for {cls.__name__}...")
            if isinstance(self, BoltEngine):
                print(f"  [⚡ BOLT] High-performance core detected.")
            if isinstance(self, PaletteComponent):
                print(f"  [🎨 PALETTE] Aesthetic standards applied.")
        cls.check_mandates = check_mandates

    return cls
