"""NanoLab hinge-family toolchain (NL3-001, EX-NL3-001-R1).

Frozen, deterministic, stdlib-only structural reproduction checks for the
Shi-Castro-Arya DNA hinge family. The source is REFERENCE_ONLY (rights
UNKNOWN): this toolchain never stores, generates or vendors source bytes - it
digest-verifies user-side downloads against the frozen pins registry and
records machine-derived structural facts.
"""

TOOL_REVISION = "HINGE-FAMILY-R1"

__all__ = ["TOOL_REVISION"]
