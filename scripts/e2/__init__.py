"""NanoLab E2 pre-flight toolkit (NL3-002A).

Frozen, stdlib-only, byte-deterministic tools prepared BEFORE the E2 campaign:

* ``compat_audit``         -- author sim-input vs pinned engine option registry
* ``topology_mapping``     -- caDNAno design paths vs oxDNA topology strands (gap G2)
* ``restraints_inventory`` -- artificial restraints semantics (init-only vs production)
* ``observables``          -- hinge angle + structural integrity (definitions frozen
                              in docs/research/E2_OBSERVABLES_R1.md, v1)
* ``fixtures``             -- deterministic synthetic fixtures with analytically
                              known observables
* ``cost_probe``           -- bounded synthetic engine probe (wall time, no science)
* ``extract_engine_options`` -- regenerates engine_options.json from the pinned
                              engine documentation checkout

No bytes of the upstream source repository are embedded here. Scientific
campaign runs are out of scope: campaign NOT_EVALUATED, E2 = NOT_RUN.
"""
