# Hostile audit — ADR-069

## Scope

This pass attempts to falsify ADR-069's work-bearing invocation identity, PromotionGroup occurrence semantics, group-local exact-state binding, correction behavior, terminal freeze, and interaction with ADR-050 descendant restacking.

## Scenario 1 — same logical invocation retried after lost response

```text
initial: invocation I17 prepared with cohort {CU-A,CU-B}
call: seal/accept I17
crash: response lost after durable acceptance
restart: caller retries I17 with same immutable definition
```

Expected/observed model result:

```text
same I17
→ same logical invocation
→ same PromotionGroup
→ no duplicate group occurrence
```

Classification: **PASS**.

## Scenario 2 — invocation id reused with a changed cohort

```text
I17 first definition = {CU-A,CU-B}
retry/reuse claims I17 = {CU-A,CU-C}
```

Result:

```text
immutable-definition mismatch
→ integrity failure / fail closed
```

Classification: **PASS**.

## Scenario 3 — later ordinary invocation uses the same ConvergenceUnits

```text
I1: CU-A1→X, CU-B1→Y → G1={X,Y}
I2: CU-A2→X, CU-B2→Y → G2={X,Y}
```

Result:

```text
I1 != I2
→ G1 != G2
membership_fingerprint may be equal
```

A terminal `G1` therefore cannot capture/poison the later occurrence.

Classification: **PASS; closes 30.42**.

## Scenario 4 — live ConvergenceUnit advances under a later group

```text
G1[X]=A
later I2 advances live X to B for G2
```

Result:

```text
G1[X] remains A
G2[X] may be B
```

No unqualified `current(X)` refresh occurs for G1.

Classification: **PASS**.

## Scenario 5 — terminal G1 while another group reopens X

```text
G1 terminal with G1[X]=A
G2 nonterminal
X later advances to B
```

Result:

```text
G1 exact resolution frozen at A
```

Classification: **PASS; closes 30.43**.

## Scenario 6 — review correction of G1 after G2 already owns later work

```text
G1[X]=A
G2[X]=B where A→B is later independent work
CHANGES_REQUESTED on G1
```

ADR-069 requires correction authoring from exact G1/reviewed state `A`, not live `B`.

Result:

```text
A → A' for G1
A' does not silently absorb B-owned work
```

Concrete Git smoke confirms this property.

Classification: **PASS**.

## Scenario 7 — forward propagation of the G1 correction into the descendant

For clean state transplant:

```text
old parent A
child owned B
new parent A'
Restack(A,B,A') → H'
```

Result:

```text
G2 internal owned anchor B remains immutable
provider/submission projection updates to H'
```

Classification: **PASS via retained ADR-050 contract + new smoke**.

## Scenario 8 — descendant transplant conflict

If `A→A'` conflicts semantically with child-owned `A→B`:

```text
clean automatic restack unavailable
→ RECONCILIATION_REQUIRED(G2)
```

Without explicit semantic reconciliation authority, G2's owned exact state is unchanged. With current explicit authority, a later work-bearing invocation may use `REVISE_EXISTING_GROUP(G2, authority_ref)`.

Classification: **PASS**.

## Scenario 9 — correction touches only one member of a multi-member group

```text
G={X@A,Y@Q}
correction touches only X
```

Result:

```text
G' exact mapping = {X@A',Y@Q}
```

`Y` is not refreshed from unrelated live `current(Y)`.

Classification: **PASS**.

## Scenario 10 — multiple work-bearing invocations coalesced into one reconciler run

```text
I17 durable
I18 durable
both raise demand
one global executor run services both
```

Result:

```text
coalesced demand/run
≠ coalesced logical invocation identities
```

No FIFO workflow-job semantics are introduced.

Classification: **PASS; ADR-041 preserved with narrowed wording**.

## Scenario 11 — partial multi-repository handoff before invocation seal

```text
A handoff prepared for I17
B handoff prepared for I17
crash before C / before seal
```

Result:

```text
I17 not accepted/sealed
→ no partial PromotionGroup occurrence
→ preparation may resume/abort
```

After all handoffs are durably frozen/bound, one seal linearizes cohort acceptance; subsequent physical Git checkpoint/integration can recover incrementally.

Classification: **PASS at specification level; implementation requires durable invocation/handoff records**.

## Scenario 12 — old group PromotionUnit supersession after unrelated new work

```text
G1 owns P1 from X@A
G2 later owns X@B
```

Result:

```text
G2 does NOT supersede G1/P1
```

ADR-067 `SUPERSEDED` applies only when the same nonterminal group legitimately adopts a newer group-local exact resolution.

Classification: **PASS**.

## Residual hostile findings

ADR-069 intentionally does **not** close hostile backlog 30.44–30.48:

```text
30.44 semantic disposition causal authorization fence
30.45 cancellation linearization vs unmanaged Git progress
30.46 OS run-lock descriptor inheritance/CLOEXEC
30.47 Development-System-independent authoring ingress
30.48 broader hostile state-space coverage
```

30.48 remains open despite v37 adding targeted ADR-069 dimensions; the broader hostile-audit request extends beyond this decision family.

## Verdict

**ADR-069 survives the targeted hostile pass.** No new contradiction was found in the ratified invocation/group-local-resolution model. The principal implementation obligation is to make work-bearing invocation identity/cohort seal and per-group exact bindings durable before depending on them for recovery.
