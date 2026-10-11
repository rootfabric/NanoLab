"""NanoLab R2 activation tooling (INFRA3-003 child WO WO-INFRA3-R2-ACTIVATION-R1).

Science-free infrastructure code: this package implements the mechanical R2
activation procedure (host fingerprint, run contract, executor, supervisor,
gates, activation decision). It contains and produces NO scientific claims;
the scientific outcome recorded by this tooling layer is always
NOT_EVALUATED (AGENTS.md: exit code 0 is not a scientific pass).

Policy invariants enforced in code (not by convention):
- host must be native-eligible U1 before any executing subcommand runs;
  `outenemy` (EXTERNAL_U2_ONLY) can never pass host validation;
- attempt IDs are never reused (append-only ledger);
- gates record PASS only with existing evidence;
- R2_ACTIVATED=YES is computable only when every gate/control is PASS, the
  fingerprint is frozen and native-eligible, fresh review/verify records
  exist, and the human gate is approved.
"""

from __future__ import annotations

TOOLING_VERSION = "r2-activation-r1"

FORBIDDEN_AUTHOR_HOSTNAMES = ("outenemy",)

PINNED_U2_HOSTNAMES = ("outenemy",)
"""Hostnames pinned as EXTERNAL_U2_ONLY reproduction platforms.

U2 readiness R1 / tooling-repair R1: the U2 executor path (``r2.cli run-u2``)
requires the host to BE the pinned external platform — the U2 role is pinned
by policy (FROZEN_R2 protocol §5 P-B; NATIVE_UBUNTU_EXECUTION_POLICY_R1 §1
OUTENEMY_ROLE = EXTERNAL_U2_ONLY), never self-declared. An unknown hostname is
fail-closed rejected for U2 duty exactly like a forbidden hostname is rejected
for U1 duty.
"""

NATIVE_FILESYSTEMS = ("ext4", "xfs", "btrfs")
