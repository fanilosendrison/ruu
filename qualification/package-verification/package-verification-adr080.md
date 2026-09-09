# Ruu — Package Verification through ADR-080

- **Date:** 2026-09-08
- **Current architecture:** ADR-001..ADR-080
- **Current finite technical audit:** `STATE-SPACE-AUDIT-v45.md` / **16,380 combinations**
- **Native observation cluster:** 30.49 CLOSED; 30.50–30.55 all CLOSED

## Integrated decision

ADR-080 closes backlog 30.55 and the 30.49 umbrella with one source-domain contract:

```text
LOCAL_GIT
→ local exact state + narrow managed-binding causal observation

REMOTE_GIT
→ current authoritative remote refs/OIDs
→ exact-preconditioned remote mutation + re-observation

PROVIDER
→ optional provider-owned workflow/governance/finalization facts
```

Remote-tracking refs are caches. Bare Git remotes are first-class. Webhooks may wake and may add positive authenticated provider evidence under demonstrated semantics, but are never generic completeness/current-state/global-ordering authority. Remote publication topology never creates local managed-binding disposition semantics.

## Retained regressions

```text
state-space-audit-v44.py: 16,124 PASS
git-native-observation-smoke-v5.sh: PASS
```

ADR-079 persistence/admission semantics remain unchanged.

## New finite-model regression

`state-space-audit-v45.py` adds 256 ADR-080 combinations:

```text
ADR-080 source-domain authority family: 32 PASS
ADR-080 remote-cache/currentness family: 32 PASS
ADR-080 remote-CAS/recovery family: 32 PASS
ADR-080 provider-optionality family: 32 PASS
ADR-080 webhook-positive-evidence family: 32 PASS
ADR-080 delivery-idempotency family: 32 PASS
ADR-080 cross-source-causality family: 32 PASS
ADR-080 remote-artifact-semantics family: 32 PASS
new combinations: 256 PASS
retained v44 baseline: 16124
v45 total: 16380 PASS
```

## New bare-remote Git regression

`git-remote-observation-smoke-v1.sh` uses two clones and one bare remote with no provider API:

```text
remote_tracking_is_stale_cache: PASS
direct_remote_observation_current: PASS
exact_old_remote_cas_rejects_stale: PASS
exact_old_remote_cas_success: PASS
remote_deletion_not_equal_tracking_cache: PASS
provider_free_bare_remote_progression: PASS
git-remote observation smoke v1: PASS
```

This demonstrates the current Git-core transport profile without making `ls-remote`/`force-with-lease` command spelling architectural requirements.


## Qualification-lineage restoration

A packaging traceability regression was found after the original ADR-080 package verification: historical Markdown reports remained, but state-space v2–v37 executable/recorded-output pairs and older Git smoke suites had disappeared without an explicit archive/supersession record. ADR-073 v38/intermediate smoke evidence had also not been retained downstream.

This revision repairs packaging/qualification only; it does **not** create ADR-081 or change ADR-080 semantics.

Exact restoration sources were verified before copy:

```text
ADR-070 source ZIP sha256
2d164a160e3a41e33633fdce564e6debfb7b42c8b78b015892cafa43951ac984
source manifest: PASS / 210 entries
→ 88 historical files were restored exactly before the subsequent project-name migration

ADR-073 source ZIP sha256
4638e4d9edaa5b941c35ee41bdd364659fb588b830574f1865aa18a44c78277b
source manifest: PASS / 137 entries
→ 5 historical files were restored exactly before the subsequent project-name migration
```

Restored state-space lineage:

```text
v2..v37  report + restored executable + recorded output, then rename-migrated where required
v38       report + restored executable + recorded output, then rename-migrated where required
v39..v45 report + executable + recorded output retained from current line

contiguous versions: 2..45 / 44 versions
```

Retained smoke lineage contains **15 scripts**: eight pre-observation Git primitive suites from ADR-070, two ADR-073 intermediate suites, and five native/remote observation suites from the current line. All 15 smoke scripts replay successfully in the restored ADR-080 package.

Historical `.txt` outputs were not overwritten by replay. They may differ from pre-rename bytes only by the mechanical project-name migration. Historical state-space scripts are likewise not patched to make them forward-compatible with ADR-080 beyond the naming migration. Direct execution of v3..v37 inside the current package therefore reaches their historical package/ADR-number static assertions; source-context checkpoint replays verify v37 in ADR-070 and v38 in ADR-073, while v38..v45 pass on the current line. Full details are in `QUALIFICATION-REPLAY-ADR080.txt`.

`QUALIFICATION-LINEAGE.json` records exact per-artifact hashes/provenance and `verify-qualification-lineage.py` enforces the anti-disappearance rule.

## Architecture overview integration

`ARCHITECTURE-OVERVIEW.md` is included at the package root with its architecture content preserved and its project naming migrated consistently to Ruu. It is explicitly non-normative, points readers to the normative specification/ECP/ADR sources on conflict, and is now the first recommended reading item in `README.md`. Package validation checks all local Markdown targets referenced by the overview; **90 links / 50 unique local targets resolve successfully**.

## Ruu project-name migration

The complete package has been migrated to the product name **Ruu** with CLI spelling **`ruu`**. The former product-name token is absent from all packaged filenames and textual artifacts. `RUU-SPEC.md` is the normative primary specification and `ruu-requirements-v1-merge-policy.md` remains its byte-identical compatibility alias.

Because the zero-occurrence requirement applies to historical qualification artifacts too, files that contained the former token are now rename-migrated snapshots rather than byte-identical pre-rename bytes. `QUALIFICATION-LINEAGE.json` records their new current SHA-256 values and retains source-package hashes as provenance anchors. See `RENAME-MIGRATION-RUU.md`.

## Static package checks

Required final checks:

```text
ADR numeric continuity 001..080
ARCHITECTURE-OVERVIEW.md present as non-normative map and local Markdown links resolve
RUU-SPEC.md == ruu-requirements-v1-merge-policy.md byte-for-byte
30.55 CLOSED by ADR-080
30.49 umbrella CLOSED by ADR-080
Spec/ECP/ADR-080 agree LOCAL_GIT != REMOTE_GIT != PROVIDER authority
Spec/ECP/ADR-080 agree provider is optional for provider-free remote Git routes
Spec/ECP/ADR-080 agree remote-tracking refs are caches
Spec/ECP/ADR-080 agree webhook absence is never negative/completeness proof
Spec/ADR-080 agree remote publication artifacts never imply local ABANDON/CONTINUATION
Markdown fence parity
state-space v44 retained PASS
state-space v45 PASS
Git native observation smoke v5 PASS
Git remote observation smoke v1 PASS
qualification lineage v2..v45 contiguous + SHA exact PASS
all 15 retained Git smoke scripts replay PASS
all state-space Python files compile PASS
all smoke shell scripts bash -n PASS
legacy project-name forms absent from filenames and textual artifacts PASS
MANIFEST.sha256 regenerated after final content freeze
ZIP extraction + manifest verification PASS
```

## Verdict

**PASS.** The qualification-lineage-restored, Ruu-rename-migrated ADR-080 package contains a regenerated **282-entry** SHA-256 manifest, preserves the complete v2..v45 state-space report/executable/output chain with current post-migration hashes, retains **15** Git smoke scripts, passes the lineage verifier, v44/v45 current audits, all 15 smoke replays, syntax/static checks, clean ZIP extraction, and final manifest verification. Architecture remains ADR-001..080; no ADR-081 was created because this is a packaging/qualification correction, not an architectural change.
