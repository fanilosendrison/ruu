# Hostile Audit — ADR-080 local/remote/provider observation boundary

- **Date:** 2026-09-08
- **Decision under attack:** ADR-080
- **Cluster result:** 30.55 CLOSED; 30.49 umbrella CLOSED
- **Finite audit:** `STATE-SPACE-AUDIT-v45.md` / 16,380 PASS
- **Concrete Git regression:** `git-remote-observation-smoke-v1.sh` on Git 2.47.3 / PASS

## Attack 1 — Local hook is mistaken for remote causality

**Counterexample:** another clone or provider moves a remote ref without executing against the local repository.

**Required result:** local hook has no authority. The reconciler obtains current remote/provider facts from those source domains. A later local cache update is not rewritten into a causal remote event.

**Verdict:** PASS.

## Attack 2 — `refs/remotes/origin/main` is stale but treated as remote truth

Concrete bare-remote regression:

```text
A tracking ref = OLD
B pushes remote main = NEW
A direct `ls-remote` = NEW
```

The local tracking ref remains stale while direct remote observation sees the current ref.

**Verdict:** PASS.

## Attack 3 — Concurrent remote writer is clobbered

A attempts an exact-old remote mutation using stale `OLD` after B has moved the ref to `NEW`.

Git 2.47.3 with explicit `--force-with-lease=<ref>:<OLD>` rejects the update as stale. After fresh observation and a candidate based on the current remote OID, exact-current expected-old publication succeeds.

This is evidence for the Git-core transport profile, not a universal command-name requirement.

**Verdict:** PASS.

## Attack 4 — Lost push acknowledgement causes blind replay

ADR-080 retains ADR-042/052 recovery:

```text
Attempt outcome UNKNOWN
→ authoritative remote re-observation
→ exact new present: adopt under current guards
→ exact old present: effect not realized
→ other state: concurrent drift
```

No event-stream exactly-once assumption is required.

**Verdict:** PASS.

## Attack 5 — Provider becomes mandatory merely because a remote exists

A bare Git remote supports direct observation, exact-preconditioned publication, deletion observation and recovery with no provider object/API/webhook.

If policy instead requires `PROVIDER_SUBMISSION`, absence of a provider adapter is a localized missing capability, not permission to emulate PR/review/queue semantics with Git refs.

**Verdict:** PASS.

## Attack 6 — Webhook absence is interpreted as event absence

GitHub's current documentation states that failed webhook deliveries are not automatically redelivered; redelivery is separately recoverable only within a bounded window. Therefore generic webhook delivery cannot be completeness authority.

ADR-080 permits positive authenticated provider-scoped historical evidence when exact adapter semantics are demonstrated, but absence of delivery proves nothing.

**Verdict:** PASS.

## Attack 7 — Duplicate/redelivered webhook repeats a semantic transition

Delivery occurrence identity is kept separate from managed semantic identity. Duplicate/delayed evidence is deduplicated/idempotent and cannot create a second Adoption/finalization.

**Verdict:** PASS.

## Attack 8 — Arrival timestamps create a fake global causal order

Local Git, remote reads, provider webhooks/APIs and policy sources have independent clocks/delivery paths. ADR-080 permits timestamps for diagnostics/freshness only. A transition requiring chronology needs exact source-owned revisions/operation identities/before-after bindings or fails closed.

**Verdict:** PASS.

## Attack 9 — Remote branch deletion abandons a local ContributionUnit

Remote deletion is publication topology, not local managed-binding causal disposition. The local `CONTINUATION | ABANDON` classifier remains scoped to the current local managed authoring ref under ADR-074/075.

**Verdict:** PASS.

## Attack 10 — Provider merge historical fact is erased by later target drift

ADR-080 keeps provider finalization `H → R` historical evidence distinct from current target containment. Later target drift changes current topology but does not rewrite already-proven provider history or terminal historical `PROMOTED` meaning.

**Verdict:** PASS.

## Source/implementation evidence checked

- Git `ls-remote`: lists references available in a remote repository with their OIDs.
- Git `push --force-with-lease=<ref>:<expect>`: updates only when the current remote ref equals the explicit expected value; otherwise fails.
- GitHub webhook handling: failed deliveries are not automatically redelivered; redelivery is a separate bounded mechanism.
- GitHub webhook delivery records expose a delivery GUID useful for delivery-level deduplication/redelivery, not managed semantic identity.

These are adapter/profile evidence only. ADR-080 remains capability/source-domain based rather than GitHub- or command-name-based.

## Verdict

**PASS.** No source-domain conflation survives the hostile cases. The architecture does not require provider infrastructure for Git correctness, does not elevate local caches/webhooks to authoritative truth, and fails closed only where a transition genuinely needs unavailable cross-source proof.
