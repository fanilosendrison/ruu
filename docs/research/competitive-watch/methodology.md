---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "research-methodology"
domain: "ruu-competitive-watch"
severity: "strict"
name: "Ruu / Ruu Cloud Competitive Watch Methodology"
---

# Ruu / Ruu Cloud Competitive Watch Methodology

Methodology version: 1.1.0

This version identifies the research method, not a Ruu or Ruu Cloud product
version. The method governs competitive-watch operations only. Its axes are
research questions grounded in existing product authorities; they create no new
Ruu promise, invariant, obligation, architecture, mechanism, implementation
requirement, or Ruu Cloud semantics.

## Governing comparison outcome

The primary benchmark is:

> **You manage intent; Ruu manages versions.**

The watch determines how far a product lets a user launch agents, give them
work, and let them author across one or more repositories, including common
repositories and files, concurrently or sequentially, from different
environments and machines, with stale work, intermediate dependencies, crashes,
and retries, without having to reason routinely about versioning.

The user or coding agent should ideally not have to choose or coordinate:

```text
which branch
which worktree
which lane
which view
which base SHA
which repo first
which merge first
who must rebase
who must wait
which stack
which parent PR
which state must be refreshed
which push must be retried
which publication topology
```

A strong CRDT, patch-theory, merge, or conflict-resolution primitive is not
therefore automatic Ruu equivalence. If the user or coding agent still drives
version topology explicitly, merge quality is assessed separately from the
autonomous versioning outcome.

## Semantic responsibility boundary

The benchmark preserves this responsibility split:

```text
Development System
→ intent
→ semantic authoring
→ validation
→ semantic dependency selection
→ reasoning/context correctness

Ruu
→ exact version state
→ isolation
→ checkpoint
→ convergence
→ stale-state reconciliation
→ dependency realization
→ publication
→ crash/retry recovery
```

The watch does not penalize Ruu for responsibilities explicitly outside Ruu.
For example, a system that tracks an agent's read-set and detects that the agent
reasoned from a file that later changed may provide an excellent Development
System capability. It is not automatically a Ruu gap. Credit it against Ruu
only when the capability replaces a versioning responsibility that Ruu actually
claims.

## Core research axes

### R1 — Versioning invisibility / zero routine cognitive burden

Evaluate whether ordinary use lets the user and coding agent avoid reasoning
about branches, worktrees, views, lanes, bases, repository order, merge order,
stacks, stale refresh, retries, and publication topology.

### R2 — Zero-preflight harness integration and substrate independence

Evaluate whether one-time installation lets a supported harness automatically
establish the required pre-edit state without a start/create/provision command,
and whether several conforming authoring substrates can coexist.

### R3 — Aggressive concurrent overlap without preventive ownership

Evaluate whether several producers may touch common repositories and files
without a human mutex, file reservation, preventive partitioning, or surprise
mutation of an active producer-owned surface.

### R4 — Continuous eager convergence / interleaving

Evaluate whether authoritative intermediate checkpoints may converge before the
ContributionUnit closes, while the same producer continues later:

```text
A1
→ B1
→ A2
→ C1
```

Distinguish this from batch-only integration:

```text
A finished
B finished
C finished
→ merge
```

### R5 — Fresh safe exact state / stale-work reconciliation

Evaluate whether stale work is normal input, current state is re-observed, and
avoidable divergence is reduced mechanically without manual refresh or rebase.
Freshness must remain subordinate to exactness and must not authorize surprise
mutation of active producer-owned state.

### R6 — Exact in-flight dependency semantics

Evaluate whether B may consume A at an exact state while A continues producing,
without waiting for `main`, PR completion, or task completion and without
silently following a moving tip.

### R7 — Global invoke-anywhere multi-repository fixed point

Evaluate whether CWD, session, and current repository do not define real scope,
and whether one demand can progress all known nonterminal obligations,
including multi-repository obligations.

### R8 — Crash/retry/unknown-effect correctness

Evaluate logical identities, physical attempts, authoritative observations,
semantic adoption, compare-and-swap, fencing, re-observation, and ambiguous
result handling.

### R9 — Git-native interoperability and authority-plane separation

Evaluate whether Git remains a native substrate and interoperability boundary,
and whether local Git, remote Git, and provider workflow evidence remain
separate authority domains.

### R10 — Semantic-authority boundary

Evaluate whether the system stops when a genuine semantic decision is required
instead of treating LLM output, confidence scoring, or a merge heuristic as
versioning authority. Do not penalize Ruu for explicitly external semantic
responsibilities.

## Cloud research axes

### C1 — Team-wide coordination domain

Evaluate multi-host authority, fencing, stale-host exclusion, recovery, and the
requirement that Core and Cloud derive the same mechanical conclusion from the
same facts and policies.

### C2 — Shared exact in-flight availability

Evaluate whether an authoritative exact checkpoint can become genuinely
retrievable and consumable on another host before final publication.

### C3 — Useful-State Latency / continuously executable development

Measure:

```text
authoritative useful checkpoint exists
→ safely consumable elsewhere
```

Determine whether branch, PR, and `main` boundaries are artificial barriers to
otherwise safe dependent work.

### C4 — Canonical Team Development State

Evaluate whether one machine-readable model exposes:

```text
what progresses
what is safely available
what is blocked
why
which dependencies became satisfied
what work became executable
```

Human UI, APIs, automations, and agents should consume projections of that same
state rather than scrape one another.

### C5 — Local correctness during Cloud unavailability

Evaluate whether correct local work may continue while shared progression pauses
where team-wide authority is unavailable, without inventing shared authority.

### C6 — Managed distributed operations and portability

Evaluate persistence, identity, fencing, recovery, upgrades, availability,
migrations, monitoring, backups, security, and exit without requiring an opaque
hosted source format.

### C7 — Provider independence and publication separation

Evaluate whether GitHub, GitLab, and bare remotes remain transport or projection
surfaces instead of defining the Cloud state machine.

### C8 — Downstream longitudinal version intelligence

Evaluate opportunities genuinely supported by available signal:

```text
Useful-State-Latency analytics
dependency/blocker analysis
convergence failure corpora
agent/model/harness evaluation and routing
recovery analytics
scheduler improvement
assurance
audit
forensics
training/eval datasets
cross-repository intelligence
```

For every use, identify who produces the exact required signal, what is missing,
and whether the composition is actually available.

## Cross-cutting deployment, adoption and commercial-substitution profile

This profile is mandatory for each scoped competitor/component assessment, but
is **not** an additional Ruu technical guarantee, fifth technical rating,
or revision to any Product Intent. It separates where an alternative operates
from what it actually guarantees. Record `unknown` rather than infer absence.

Evaluate and evidence each dimension separately:

1. **Local installation and routine invisibility.** Can a developer install
   once on their own machine, start a supported pre-existing coding harness,
   and obtain pre-edit isolation plus safe version progression without
   repeating setup or manually planning Git topology? Distinguish an actual
   local version-control engine from a local CLI that merely invokes a hosted
   agent, server SCM, provider API, or vendor account.
2. **Local autonomy and external prerequisites.** Identify whether a local
   repository without a configured remote remains usable, whether a GitLab/
   GitHub account or vendor service is mandatory, which operations need
   network access, and exactly what remains correct offline. Do not demand
   offline remote publication or multi-host authority: only evaluate the
   local scope for which the competitor claims independent functionality.
3. **Harness, model, provider and repository independence.** Check supported
   harness adapters, whether the user can retain their chosen coding harness
   and model, whether multiple local repositories are supported, and whether
   GitHub, GitLab and bare Git remotes remain interchangeable. A local app
   that works only with its own agent or forge must not be called universal.
4. **Cost, licence and feature boundaries.** Record verified free functions,
   mandatory subscriptions, paid credits/usage, hosting/compute expenses,
   enterprise restrictions and which correctness capabilities are gated.
   Distinguish free of charge, source available, fair-code and OSI-approved
   open source; neither the product name nor a repository's visibility proves
   licence or entitlement. Do not conflate Ruu Core's intended complete
   free/fair-code model with a verified shipped offering.
5. **Distribution and switching costs.** Compare separately the ease of
   individual adoption, pre-installed/bundled forge distribution, the need
   to migrate SCM or agent workflows, enterprise procurement, and the path
   from individual local adoption to team-wide Cloud adoption. Claims about
   adoption or pricing require dated evidence.
6. **Commercial substitution independently of technical equivalence.**
   Determine whether a vendor-native, bundled or sufficiently-good partial
   solution could remove a buyer's reason to pay for Ruu Cloud, even while
   falling short of Ruu's exact-state guarantees. Conversely, a technically
   equivalent local and provider-independent engine is a direct Core
   substitute even if its provider offers no managed Cloud product.
   Do not derive commercial-threat likelihood from a four-dimensional
   technical rating, and never treat free price as proof of technical parity.

For GitLab and GitHub, explicitly distinguish their remotely hosted SCM and
agent platform from any genuinely local, third-party-harness-independent
versioning engine. A local CLI, extension, sandbox or checkout alone does not
establish the latter. Inspect actual dependency paths and product prerequisites.

Within the existing JSON schema, place source-bounded deployment findings
in the component's `summary` and R1/R2/R9 axis `scope`, `evidence_ids`
and `remaining_gaps`; use C5/C6/C7 for independently relevant Cloud
conditions. Record economic/distribution implications in
`positioning_implications`, with evidence or marked uncertainty in the
report narrative. The report renderer must not add unrepresented findings.
Keep the four existing technical ratings unchanged; do not invent a fifth
rating, alter `report.schema.json` silently, or retroactively modify reports.

## Discriminating scenarios

Retain exactly these fourteen scenarios as analysis questions:

1. 40 agents touch unknown subsets of 17 repositories; the user does not
   pre-plan version topology.

2. A and B start from S0. A produces A1 and remains active toward A2.
   Determine whether A1 can converge before A finishes and whether B1 later
   reconciles against the newer managed reality without manual refresh.

3. A1 → B1 → A2 → C1 while producers remain active.

4. Two agents edit the same file. Mechanically compatible work should not
   require preventive ownership; genuine semantic incompatibility must be
   surfaced without invented meaning.

5. B consumes A@exact-OID while A remains active and later creates A2.
   B must not silently move to A2.

6. One logical work occurrence spans several repositories with different
   publication policies. Invocation happens from an arbitrary managed repo.

7. Two convergence demands race. The user must not act as the mutex.

8. A remote/provider effect succeeds but acknowledgement is lost.

9. An active authoring surface becomes stale but remains producer-owned;
   freshness must not authorize surprise mutation.

10. Cloud host A exposes safe A1, host B consumes it, A continues, host C is
    temporarily disconnected, then authority recovers without stale-host
    resurrection.

11. A competitor has exceptional CRDT/patch-theory merge but requires explicit
    view/lane/branch/insert/rebase topology. Rate merge quality separately
    from autonomous_versioning_outcome.

12. A competitor tracks agent read-sets and detects reasoning staleness.
    Determine first whether this belongs to semantic Development-System
    validation rather than Ruu's versioning responsibility.

13. A developer installs a versioning tool once on their machine, then
    uses two different supported coding harnesses on several local repositories,
    including one without any Git remote. No provider account or hosted service
    is available. Inspect pre-edit integration, overlapping concurrent work,
    checkpointing, convergence and local crash recovery, and record every
    manual setup/version-topology step still required.

14. A GitLab/GitHub user has access to a bundled agent platform and server
    SCM feature. Compare its ordinary user-level substitution against the
    same developer using a third-party harness on a different forge or an
    unhosted Git repository. Distinguish a hosted workflow with local CLI
    access from an autonomous local version-control engine; assess commercial
    substitution separately from exact technical equivalence.

These scenarios are research questions. They are not new normative Ruu or Ruu
Cloud requirements.

## Permanent radar

Once an identifiable actor, product, or component is evaluated on any scope, it
remains monitored indefinitely while the watch operates unless the user gives
an explicit instruction to stop active monitoring.

An actor is never removed automatically because of:

- low threat;
- complementarity;
- no recent news;
- indeterminate evidence;
- closed source;
- an archived repository;
- acquisition, rename, or shutdown; or
- finding closure.

Monitoring membership, technical level, confidence, availability/readiness,
lifecycle, and strategic role are separate facts. A dormant or discontinued
actor retains its history and is checked for revival, successors, forks, and
transferred technology.

A rename preserves identity. A genuine fork or successor receives a linked
identity. An identity error is corrected in a new report without erasing
history.

The effective roster is the cumulative union of:

- watchlist seeds;
- all prior report admissions;
- explicit user additions; and
- recoverable pending registrations.

`watchlist.json` never overrides prior report admissions. Stopping monitoring
changes current monitoring status while preserving all identities and history.

## Two mandatory activities for every execution

Every execution performs both:

- **A — accumulated-radar monitoring:** inspect every retained actor according
  to current coverage obligations and source cursors;
- **B — open discovery:** search for new actors, products, components, forks,
  research projects, features, and available compositions.

No run may perform only one without declaring the other incomplete. Open
discovery happens every run, not only during weekly or monthly synthesis, and
is not limited to known names.

Search by problems and outcomes, rotate the discovery topics in
`watchlist.json`, and record the channels, queries, and times actually used.
“No new entrant found” is acceptable only after a real search and never proves
that no entrant exists. A hypothetical integration that would still need to be
developed is not an available composition.

## Technical implementation analysis

Do not stop at public positioning when a conclusion depends on implementation.
When accessible, follow the real production path:

```text
harness integration
→ authoring state
→ identity
→ isolation
→ checkpoint
→ convergence
→ stale reconciliation
→ dependency adoption
→ persistence
→ authority/fencing
→ retry/recovery
→ remote sync
→ provider publication
→ downstream capture
```

Inspect:

- defaults and configuration;
- feature flags and disableable controls;
- product and production reachability;
- bypass, unknown, and error paths;
- wrappers and delegated components;
- positive and negative tests;
- differences among branches, releases, and deployed services; and
- relevant source changes even without a public announcement.

Reproduce useful tests or counterexamples when the environment permits safe,
isolated execution without user secrets.

## Evidence discipline

Never collapse these evidence classes:

```text
claim
!= documentation
!= source_inspection
!= tests_inspected
!= reproduced
!= proof_artifact
```

Prefer primary sources. Source inspection identifies immutable repository
revisions and precise paths. Distinguish event, publication, and observation
dates.

For `reproduced`, preserve command, environment, result, and a real artifact
reference. A proof artifact is described only for the scope it proves; naming
or file extension does not establish proof. Never invent a SHA, URL, test,
result, author, timestamp, or unavailable source.

Preserve these distinctions:

- merge quality is not autonomous versioning;
- capture is not authority;
- configured recovery is not recovered exact state;
- observation is not semantic adoption;
- a hash is not truth of content;
- absence of public evidence is not impossibility;
- an announcement is not availability; and
- a useful synthetic scenario is not historical evidence.

Apply the same evidence standard to Ruu and Ruu Cloud: Product Intent is not an
implemented or verified capability.

## Levels and dimensions

Assess these dimensions independently:

- `autonomous_versioning_outcome`;
- `ruu_core_guarantees`;
- `ruu_cloud_guarantees`; and
- `downstream_version_intelligence`.

Never average or aggregate them.

<!-- markdownlint-disable MD013 -->

| Level | Rendered label | Meaning |
| ----- | -------------- | ------- |
| `U` | ⚪ INDETERMINATE | Information is insufficient; this does not mean low threat. |
| `L0` | 🟢 ADJACENT_OR_COMPLEMENTARY | The examined scope does not replace the considered guarantee. |
| `L1` | 🟡 ISOLATED_PRIMITIVE | A relevant primitive exists without the required composed guarantee. |
| `L2` | 🟠 SUBSTANTIAL_PARTIAL_SUBSTITUTE | A substantial subset is established and identified gaps remain. |
| `L3` | 🔴 NEAR_EQUIVALENCE | A composition covers most of the declared scope and decisive gaps are explicit. |
| `L4` | 🟣 DEMONSTRATED_SCOPED_EQUIVALENCE | End-to-end equivalence is established for the declared scope with sufficient assumptions, dependencies, and verification. |

<!-- markdownlint-enable MD013 -->

Every rating states its scope, rationale, evidence, confidence, and external
dependencies. Technical level, confidence, availability/readiness, lifecycle,
and strategic role remain separate. A demonstrated equivalence on one declared
sub-scope is not equivalence to all of Ruu Core or Ruu Cloud. Reputation,
funding, and repository stars do not change technical levels. An announcement
may trigger investigation but cannot promote a level.

## History and trajectories

Every published report is immutable. Corrections are new reports. Actor,
component, finding, and evidence IDs remain stable.

Classify changes independently with:

- `implementation_change`;
- `new_evidence`;
- `assessment_correction`;
- `ruu_baseline_change`;
- `ruu_cloud_baseline_change`; and
- `methodology_change`.

Only `implementation_change` establishes competitor technical progress. Never
rewrite historical ratings under a later method or baseline. Every report pins
both repositories, schema, and methodology.

A carried-forward assessment keeps its original observation date and sets
`revalidated_this_run` to `false`. Analyze gaps actually closed, reduced,
reopened, or made dependent on another system.

## Publication controls beyond JSON Schema

Structural schema validation is necessary but insufficient. Before publication,
verify:

- uniqueness of actor, component, finding, and evidence identifiers;
- resolution of evidence and historical references;
- presence of every required axis, using explicit `unknown` when unevaluated;
- consistency among report ID, generated time, and report directory;
- temporal consistency of the observation window;
- consistency among entrants, admissions, and continuity sets;
- equality between current actor IDs and represented actors;
- inclusion of all historical actors and new admissions;
- `user_stopped` only with a verifiable user instruction;
- no invented observation, revalidation, cursor advance, or rating;
- justification for every technical level;
- separation of carried-forward values from new observations;
- JSON/Markdown equivalence; and
- immutability of all prior reports.

Successful structural validation never proves competitive conclusions or
cross-report continuity. Those require evidence review and separate continuity
checks.
