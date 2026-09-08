# NL0-001 — Доступность входов и воспроизводимый путь получения

Исполнение: `EX-NL0-001-R1`. Дата inspection: 2026-09-08. В NanoLab **не копировались** сторонние scientific input/data files; сохранены exact refs, hashes и пути получения.

## E1 selected — oxDNA DSDNA8 / MD

Upstream repository: `lorenzo-rovigatti/oxDNA`  
Pinned commit: `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`  
Upstream tree: `f03ce1de5c0f3a336cb00ad363686c4841600d10`  
Repository license observed: GNU GPL v3.

Exact files inspected through GitHub at that commit:

| Path | Git blob SHA-1 | Size | SHA-256 of fetched content |
|---|---|---:|---|
| `test/DNA/DSDNA8/dsdna8.top` | `1811af7ea4bea8a86519456cba608d1e6d44ed3b` | 148 B | `f1aded90b5f6e1d9adab0e55925bba778477467be2957b4093d1264160c03fc4` |
| `test/DNA/DSDNA8/init.dat` | `856be1878ece7115a91f988b2cbd7ad650daf2db` | 4498 B | `0ff76d541728e0925f199970ff6296254fe6116d23e44fdf0d361d0f8891a9e0` |
| `test/DNA/DSDNA8/MD/quick_input` | `07eef592f070f9b8955f9001e0fd292de9862a4a` | 533 B | `8935c4bc623ca96d406429c3c5177901f12540ffe61bcd3299931f0689af74a2` |
| `test/DNA/DSDNA8/MD/quick_compare` | `74a088ec4ceb1bc01ab2e385e4700eb2d3907f40` | 51 B | `86a8b6ac50f382ba25e5aacbbef629cc5a1788f44e6c28d113509c8448e3ce27` |

The topology text declares `16 2`: 16 nucleotides in two strands. `quick_compare` contains the quantitative upstream regression oracle.

### Re-obtain procedure

Checkout/fetch the exact upstream commit, then read the four paths above. A future experiment manifest should record both upstream commit and content SHA-256; using moving `master` alone is forbidden.

### Rights boundary

GPLv3 was observed for the oxDNA repository. NL0-002 still must decide whether NanoLab references upstream files in-place, downloads them during setup, or redistributes any fixture. This Work Order does not make that licensing decision.

## E1 fallback B — SSDNA15 / MD

Same upstream commit. Verified entries:

```text
test/DNA/SSDNA15/MD/init.dat       blob 8e4d3850448c46f7f6bef5e0998944cba90a82bd
test/DNA/SSDNA15/MD/ssdna15.top    blob fb2ea2088fd510d4f658cae935e1c0c833ff8888
test/DNA/SSDNA15/MD/quick_input    blob ef5b692178dcae0fcc02fba452b92fcf505a821b
test/DNA/SSDNA15/MD/quick_compare  blob ce263d419452fc3830b71e2c1e2ae656eace7126
```

`quick_compare` contains two ColumnAverage checks. Candidate is available but not selected.

## E1 fallback C — HAIRPIN

Same upstream commit. Verified directory `examples/HAIRPIN/` contains topology, initial configuration, multiple inputs, forces, run script and documentation. Selected input requests 100,000,000 VMMC steps at 334 K, so it is intentionally deferred until the minimal DSDNA8 path works.

## E2 source S08 — access result

DOI: `10.1021/acsnano.7b06470`.

Observed public ACS Supporting Information advertises one PDF containing measured-angle/extension definitions and additional simulation results plus several trajectory movies. During this bounded inspection no separate public caDNAno/oxDNA topology/configuration/input pack tied to the paper was located.

Status: `INPUT_PACK_NOT_LOCATED`, not `NO_DATA_EXISTS`.

Recovery path if S08 becomes necessary: inspect author-supplied archive if found or contact corresponding authors. Do not reconstruct a design and call it the original.

## E2 selected — mechanically compliant hinge family

Paper DOI: `10.1021/acsnano.7b00242`.  
Author data repository: `gauravarya77/DNA-hinge-simulations`.  
Pinned commit: `23fd1ff7731e9017bd776f49206dc42d70d9fe91`.  
Pinned tree: `b2d6cebc7a33ed13e4e9c8d79fe8350ce11e82b9`.

Verified design blobs:

```text
Design_Hinges/0b.json   0ed4075c3a0d2f29601d35c5ce70f2df6b0be1ed  173059 B
Design_Hinges/11b.json  7f1936970196ace1f9d30fc5da8f8387e80f9a3e  173145 B
Design_Hinges/32b.json  6adb55af1d46f0a2f751b0bf1ba14ab17293ff28  173315 B
Design_Hinges/53b.json  3ffdb753a63f799e8d08f9e6b42846c8f4f53e69  173481 B
Design_Hinges/74b.json  776725c154457ff6b4001a4c150098d90347acf4  173595 B
```

Verified MD inputs include paired `.top`/`.conf` files for all five variants plus `MD_Hinges/pro_CPU.in` (blob `89d76310ce726eaec9e7acb312bd7b0fc43fa735`) and `pro_GPU.in`. The 0b pre-equilibrated configuration alone is about 2.29 MB, so this is a real machine input pack rather than article-only metadata.

### Rights boundary

No standalone `LICENSE` file was observed in the complete pinned repository tree. Therefore public accessibility is recorded, but redistribution/modification rights are `UNKNOWN` pending NL0-002. NanoLab should reference exact upstream objects rather than copying them into the repository until that audit is complete.

## Rich future benchmark — leaf-spring nanoengine

Primary article: Nature Nanotechnology `s41565-023-01516-x`. It explicitly points to Nanobase structure 196 for design/oxDNA starting structures, Zenodo record `8248808` for MD simulation data and `sulcgroup/hinges` for processed data/analysis code. Zenodo currently exposes four large archives totaling about 46.2 GB, so this is not a sensible E1 or first E2 dependency.

`sulcgroup/hinges` was inspected at commit `7c8b04a654b2440e4b6bab5b0abcb7e4335824d9`; README documents angle extraction and analysis, but no root LICENSE was observed in the inspected repository listing. Treat rights as unresolved until NL0-002.

## Integrity note

Git blob SHA-1 identifies exact upstream Git objects. SHA-256 above is additionally recorded for the selected E1 files so a future downloader can verify bytes independent of Git object framing. No simulation result is claimed by this file.
