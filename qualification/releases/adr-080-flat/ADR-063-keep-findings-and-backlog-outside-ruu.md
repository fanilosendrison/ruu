# ADR-063 — Keep review findings and backlog outside `ruu`

- **Status:** Accepted
- **Date:** 2026-09-07
- **Decision order:** 063
- **Amends:** ADR-032, ADR-053, ADR-055, ADR-057, ADR-060 and the External Control Plane boundary

## Context

In an agentic development process, semantic review may produce multiple findings before or after a Git/provider publication boundary. Some findings must be fixed immediately; others are valid but intentionally deferred; some are accepted risks; others are rejected as irrelevant or incorrect.

A traditional Pull Request often conflates these distinct concerns because review comments, approval, CI, discussion, backlog reminders, and merge eligibility all live around one provider object.

After ADR-062, a provider submission is only a projection used when required by target/provider governance. It should therefore not become the canonical backlog simply because review happened near a PR.

The system needs an explicit boundary between:

```text
semantic review findings
```

and:

```text
provider-governance blocking state
```

so that a nonblocking deferred improvement does not keep a promotion artificially open, while a genuine provider `CHANGES_REQUESTED` state still creates durable correction work.

## Decision

### 1. Semantic findings are Development System objects

A semantic review finding belongs outside `ruu`.

Conceptually an external finding may carry:

```text
finding_id
origin review / reviewer / tool
exact candidate or commit/tree context
repository / path / symbol context when applicable
observation
risk / severity
recommended action when available
adjudication state
provenance
```

`ruu` does not need to understand the finding prose or decide whether it is correct.

### 2. Finding adjudication is external

The Development System / review-governance layer may classify a finding using semantics such as:

```text
FIX_NOW
DEFER
ACCEPT
REJECT
```

The exact vocabulary is external implementation policy; the architectural meanings are:

```text
FIX_NOW
→ current development work must address it before the relevant external quality/promotion intent is established

DEFER
→ finding remains valid enough to track, but is intentionally not a blocker for the current ship

ACCEPT
→ known concern/risk is consciously accepted for the current context

REJECT
→ finding is not considered actionable/valid
```

`ruu` consumes only the resulting lifecycle/governance facts that are already part of its existing contract. It does not run this adjudication.

### 3. Deferred findings become backlog objects, not long-lived provider submissions

A deferred finding should normally be projected into a durable backlog/tracker object.

For GitHub, the natural projection is typically a GitHub Issue.

For another environment it may be:

```text
GitLab Issue
Jira ticket
Linear issue
Notion task
internal Development System backlog record
another tracker object
```

The tracker object is a projection of the external finding, not a `ruu` identity.

A Pull Request / Merge Request / provider submission is not used merely to preserve “work to do later”, because it carries a candidate head/base/diff and implies a concrete integration proposal.

### 4. Deferred backlog records should preserve provenance

A useful deferred finding record should preserve enough context for later revalidation, for example:

```text
origin review identity
affected exact candidate/commit/tree when known
repository identity
path/symbol/location when relevant
observation and risk
reason deferred
recommended action
acceptance conditions
```

This provenance is Development System/tracker data, not a new Git authority.

### 5. Re-injected backlog work must be revalidated against current code

A later coding agent MUST NOT assume that an old deferred finding is still true merely because the ticket remains open.

The Development System should first revalidate the finding against the current target/code state:

```text
backlog finding
      ↓
revalidate against current code
      ↓
      ├── still applicable → ordinary new Work/ContributionUnit authoring
      └── stale/resolved   → close/supersede backlog item
```

This revalidation remains semantic development work outside `ruu`.

### 6. Blocking provider review state remains a distinct Ruu input

ADR-053 remains valid for an exact current provider-governance state equivalent to:

```text
CHANGES_REQUESTED
```

Such a state means the current provider submission cannot progress under current governance until correction/approval state changes. It therefore creates or refreshes one durable exact-generation ReviewCorrectionDemand.

This is not because every review comment is a core finding. It is because the provider reports a **blocking governance fact** for the exact current submission revision.

### 7. Nonblocking provider feedback does not automatically create correction work

Provider comments, suggestions, advisory review notes, or other nonblocking feedback MUST NOT automatically become:

```text
ReviewCorrectionDemand
promotion blocker
ConvergenceUnit reopen
```

unless current authoritative provider/repository governance actually classifies them as blocking or the external Development System independently decides to treat them as `FIX_NOW` and updates the relevant external lifecycle/governance intent.

The provider adapter should therefore normalize the distinction between:

```text
blocking correction-required governance
```

and:

```text
informational/nonblocking feedback
```

rather than treating all review prose as equivalent.

### 8. A deferred finding does not keep the current submission open

If a finding is adjudicated `DEFER` and all actual current promotion/provider requirements are otherwise satisfied:

```text
current provider submission may continue to final integration
+ deferred finding persists independently in backlog
```

The backlog item must not become a hidden replacement for a provider approval requirement.

Conversely, if provider governance itself remains blocking, an external decision to “defer” the concern does not magically bypass that governance. The review state must be legitimately changed/dismissed/approved according to authoritative policy before promotion can continue.

### 9. `ruu` does not own issue creation or backlog scheduling

`ruu` does not:

```text
create tracker issues from semantic review findings
prioritize backlog items
schedule coding agents for deferred work
interpret issue prose
close stale issues based on semantic judgment
```

Those responsibilities belong to the Development System / External Control Plane / tracker integration.

A future integration may automate issue projection, but that automation is outside the Git convergence core unless a future ADR establishes a narrow provider-side contract required for Git correctness.

## Rationale

The separation preserves the meaning of each object:

```text
ProviderSubmission
→ concrete candidate being proposed for integration

Finding
→ semantic observation about code/work

Backlog item
→ durable future work obligation/reminder
```

Using PRs as backlog objects would keep stale heads, diffs, checks, mergeability, and review lifecycle alive long after there is no concrete candidate intended for integration.

Issues/tracker objects are better suited to deferred work and can survive code evolution without pretending an old branch should eventually merge.

The distinction also prevents `ruu` from accidentally becoming a semantic project-management system.

## Consequences

- Agentic review findings remain external to `ruu`.
- Deferred findings may be projected to GitHub Issues or another tracker.
- Backlog items retain provenance and are revalidated before future implementation.
- Provider `CHANGES_REQUESTED` remains a first-class blocking provider fact under ADR-053.
- Nonblocking review comments do not automatically create ReviewCorrectionDemand.
- A deferred finding does not block current promotion unless provider/repository governance independently says it does.
- PR/provider submissions remain concrete integration projections rather than long-lived backlog containers.
- The Development System owns backlog reinjection into coding agents.

## Rejected alternatives

### Keep every review finding as an open PR

Rejected. It conflates a future-work record with a concrete candidate/head intended for integration and causes unnecessary drift/check/conflict lifecycle.

### Make `ruu` parse review comments and create Issues automatically

Rejected. Semantic finding interpretation and project-management policy are outside Git convergence correctness.

### Treat every provider comment as `CHANGES_REQUESTED`

Rejected. Provider review prose may be advisory/nonblocking. Only authoritative blocking governance state creates the ADR-053 correction obligation automatically.

### Allow external `DEFER` to bypass an actually blocking provider review

Rejected. External semantic adjudication cannot manufacture provider/governance authorization.
