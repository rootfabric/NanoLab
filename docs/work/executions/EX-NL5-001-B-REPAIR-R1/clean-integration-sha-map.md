# Clean integration R1 — SHA map (old stacked subject → clean candidate)

- Old stacked repair head: `dc3063b7cf9cc1584e9a1141252862e32128adf4` (branch `repair/nl5-001-b-library-r1`, PR #38)
- Clean integration base: `9de094c8d423574568e62832854664b577e9f282` (main after PR #39 + quantum PR #37+#40)
- Rebuild method: 39 NL5-specific commits cherry-picked in order; excluded as already integrated: bottom 14 post-MVP route commits (PR #37), 6 post-MVP records carry commits (duplicated by PR #40), 2 CI carry commits (superseded by PR #39).
- Tree equivalence: `git diff dc3063b7c <clean-head>` over NL5 surfaces = empty; single whole-tree difference vs old stack head is `docs/work/executions/EX-POST-MVP-ROUTE-R1/events/0002-handoff-completed.json` (cosmetic JSON array formatting; canonical variant is the PR #40 version already reviewed and verified).

| # | old (stack) | new (clean candidate) | subject |
|---|---|---|---|
| 1 | a9543aa | 1b5e05424a79ae104cd0f14afa05b5cfd78277c5 | control: start WO-NL5-001-A-R1 release contract |
| 2 | 2efbed3 | bd12f3fd6e9142f069e4f116105a86effa130b57 | feat(nl5-001-a): release contract v0.1 - card/rights/manifest schemas, stdlib linter, example package, license memo |
| 3 | 9cbde33 | 8161536a199061462b43b531abe5de8e11153cfd | control: canonical execution records and handoff for WO-NL5-001-A-R1 |
| 4 | a4495b7 | 4f4e3c19e4520388031d10ca05a836402a078751 | control: start WO-NL5-001-B-R1 library assembly |
| 5 | be73c54 | 2377f6248c1e5f48969963b31175698a81ce5c6d | feat(nl5-001-b): assemble nanolab-components-v0.1 from published evidence via deterministic builder |
| 6 | 6285265 | 1b445e6dd285d9690b98222e2eef727df8a5aa4e | control: canonical execution records and handoff for WO-NL5-001-B-R1 |
| 7 | 7912e2b | 90df24e0ad67917c48adc92c8086b64cd28c0c6a | repair: start NL5-001-B reviewer fixes |
| 8 | 89eda66 | 54ff0f27f742b1099b039f7008323070c29563bf | repair: record NL5-001-B repair start |
| 9 | a1afbaf | 1ad1f79c1ef8385c19018bec003838a4c4a86ae1 | repair: freeze independent reproduction rule v0.1 |
| 10 | 798be15 | 3a8b037a47925b625110c039bfec3f936adeeef8 | repair: add frozen reproduction classifier |
| 11 | f3f96d1 | a6390b8cd7b0edcbf495697d21d2010bae94cc2f | repair: synchronize release contract R1.2 |
| 12 | 58db185 | da5ce88423ed3bbb5c19ccb5df544e7e38d32c18 | repair: remove stale A planning reference |
| 13 | 92a749f | cca5b29bc15d700798d8b3576642a66dde6f5890 | fix: correct exact A base SHA in repair note |
| 14 | e5428d8 | 18e73759422a2b0e3e4a4b4b15c3338ea1cb2547 | repair: harden release manifest and deterministic creation |
| 15 | b09dd3b | 32c81ee6e2f09d3f67bd90d29c6492d527abc48b | repair: allow deterministic manifest without wall clock |
| 16 | c89efc1 | 392bb11da659f589f2fab729f3fd89cdbb0ee4fc | repair: sync example manifest schema snapshot |
| 17 | c06295f | 7771dfa014ea0c6ad33503883400453540504eb2 | repair: sync release manifest schema snapshot |
| 18 | 5803bdf | 3143a34ee1b6ecf0937e3f82a1a4ebcc41f94763 | repair: add evidence-derived deterministic R1.2 builder |
| 19 | 1606231 | 81aa78ff9a2041ef0ffbb1c7478e124da6e58fda | test: add NL5-001-B repair regressions |
| 20 | 7352b9e | d93e0e4bce5b16ae740cbe493c9fa5fa5967b6a4 | repair: make example manifest schema snapshot byte-identical |
| 21 | b91e1c2 | 3a3834eb2878eccda3e67d5f7e06f9e51d16886a | repair: make release manifest schema snapshot byte-identical |
| 22 | e783216 | eb28ead13d195ff1c1071ecaee76af8c68c45d1b | repair: apply frozen reproduction rule to 11b card |
| 23 | 35a2dd1 | 80e1cd025ec6f9ee20c9932fe1ca515e2f889c8e | repair: apply frozen reproduction rule to 32b card |
| 24 | 7b32f8f | e2aeb64249edf9b4db61308f21a4b220b0ee44d2 | repair: apply frozen reproduction rule to 53b card |
| 25 | 5e42c0d | 23ff1c54aa21a69f04e4c2716c9c76d2cba22a92 | repair: apply frozen reproduction rule to 0b card |
| 26 | d332521 | 8b83b0497d2564fb943df586ad0ed81216a7d0a4 | repair: mark 74b card as R1.2 assembled |
| 27 | 2eee8dd | be06ed82a8f503536c683fc04ebf923b51ca008a | repair: include frozen reproduction rule in release package |
| 28 | 31840b3 | 53536c5fbcfbff87942dbc02301a780a7a5074df | test: make library checks evidence-derived and R1.2-aware |
| 29 | 65e5928 | da90dfbe2607d8e9daae32669e3f71ef69b80070 | repair: finalize R1.2 builder determinism semantics |
| 30 | 434f23c | c2abeabf50625a9cf0cf543cdd172aa9496d78b4 | test: forbid stale post-MVP execution-program references |
| 31 | e37ac05 | 89c98a13ffce54fb125f4bc3e0c27160c4e83769 | repair: refresh example deterministic manifest |
| 32 | 10d5b27 | b23739eb23a0eb96915a3e3a6737e7bea0132dba | repair: add NL5-001-B repair passport |
| 33 | 34671ea | fa36aa4bff9eb5cf0e0d8763e4d25624983b1838 | test: pin committed manifests to exact package bytes |
| 34 | c0bb28d | c9c9cdaab95c42d149d2c138da70e1a2c0da8e2a | repair: normalize NL5-001-B repair START event |
| 35 | 1b64c74 | 463e95a8cc5bf13a6b99fd027a605c9db25ae7d1 | repair: remove stale planning filename literal |
| 36 | cb63d0b | 2478a70a65c88698de15c6d0b455bbabe67e916a | repair: add repair execution id to START event |
| 37 | 54d8e03 | 2181b8f145f76d8fec60303f2b14fa6e8b9ba0b6 | fix(nl5-001-b): package regression layer green on exact R1.2 subject |
| 38 | af894ee | 11f08d30602c7d63ed0ce49dcf03f4f49005a113 | control(nl5-001-b): repair R1 continuation checkpoint R8 (package regression green) |
| 39 | dc3063b | 66e2270d07b2e7936257dfe2c028f65746e4048f | control(nl5-001-b): repair R1 handoff - package regression layer closed |
