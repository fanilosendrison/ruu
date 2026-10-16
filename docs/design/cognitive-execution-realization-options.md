---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "design-analysis"
domain: "ruu"
severity: "informational"
name: "Cognitive execution realization options"
---

# Ruu — Cognitive execution realization options

> **Non-normative design analysis.** This document records candidate ways to
> realize accepted requirements. It does not select a runtime, create a product
> requirement, or override the [Ruu specification](../specification/ruu-spec.md),
> [ADR-092](../adr/adr-092-allow-capability-based-cognitive-execution-without-mandatory-workflow-runtime.md),
> or [ADR-093](../adr/adr-093-make-commit-message-providers-user-selectable-with-main-agent-default.md).

## The decision not to make

The ability to request a commit message from the existing main agent does
not establish a need for a general workflow engine. A workflow engine may
be convenient and reusable, but the product promise is the capability and
its evidence of conformance, not any named implementation.

## Candidate realization classes

| Candidate | Possible contribution | Qualification question |
|---|---|---|
| Native coding-harness integration | Continue the actual authoring-session main agent | Does the returned execution preserve the same cognitive lineage, authorization, and immediate caller context? |
| Turnlock integration | Compose mechanical work and admitted main-agent, independent-agent, or bounded-model execution | Does the adapter preserve Ruu's state-driven reconciliation, global lock release, exact candidate binding, and session provenance? |
| Direct bounded LLM interface | Generate a message without interactive main-agent continuation | Is it used only when selected and bound to the authorized exact candidate? |
| Independent agent | Explore context or formulate a message in an isolated lineage | Is it never represented as continuation of the session main agent? |
| User-supplied external service or system | Produce a message through an open adapter contract | Are selection, input scoping, output validation, and failure localization honored without Git mutation rights? |

The alternatives are not necessarily mutually exclusive. One installation
may use different compatible resources for different admitted requests.
No candidate is declared conforming merely by appearing in this table.

## Evaluation questions before selecting a runtime

1. Can the relevant existing main agent actually continue, without silently
   replacing it with a new agent or a reconstructed model context?
2. Can a user replace the default with a subagent, raw model call, or arbitrary
   compatible external producer without changing Ruu's Git authority?
3. Does a request bind to the exact authored checkpoint candidate and only
   authorized context, rather than a moving branch or unrelated caller?
4. Can unbounded external cognitive work release the global Ruu run lock,
   preserve the frozen handoff, and return through fresh exact-state guards?
5. Does a failed, missing, or delayed provider remain a localized recoverable
   obligation while unrelated headless Git progression continues?
6. Can crashes and retries recover journaled physical effects and durably
   selected OID-affecting metadata without resampling the same message?
7. Does the realization add unnecessary packaging, resource, maintenance,
   security, or multi-harness integration obligations relative to alternatives?

A conforming answer to these questions requires evidence against the
governing contracts. The use of a named runtime by itself is not evidence.

## Current selection state

**Unselected.** Turnlock is a candidate, as are appropriate supported
harness-native mechanisms and other compliant combinations. Choosing an
initial implementation requires comparative conformance evidence and a
separate implementation decision; it must not be inferred from this note.
