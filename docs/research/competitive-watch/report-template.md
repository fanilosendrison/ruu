---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "report-projection-template"
domain: "ruu-competitive-watch"
severity: "strict"
name: "Ruu / Ruu Cloud Competitive Watch Report Template"
---

# Veille Ruu / Ruu Cloud — Rapport du {{date_locale}}

- **report_id :** `{{report_id}}`
- **type :** `{{report_kind}}`
- **fenêtre observée :** `{{period_start}}` → `{{period_end}}`
- **généré à :** `{{generated_at}}`
- **référence Ruu :** `{{basis.ruu_repository}}@{{basis.ruu_commit}}`
- **référence Ruu Cloud :** `{{basis.ruu_cloud_repository}}@{{basis.ruu_cloud_commit}}`
- **version du schéma :** `{{schema_version}}`
- **version de la méthode :** `{{methodology_version}}`
- **statut de Ruu Cloud :** `{{basis.ruu_cloud_status}}`
- **caractère partiel éventuel :** `{{partiality_statement}}`

Ce modèle est une projection de `report.json`. Il ne contient aucune
observation concurrentielle. Le rendu ne doit ajouter aucun jugement, niveau,
fait, source ou conclusion absent du JSON.

## 1. Fenêtre d'observation et bases Ruu / Ruu Cloud

{{observation_window_and_basis}}

Présenter les deux bases immuables, la méthode, le schéma, la période couverte,
la date de génération et toute histoire indisponible.

## 2. Synthèse

{{summary}}

Préserver les limites, inconnues et couvertures partielles. Une absence de
preuve publique ne devient pas une preuve d'absence de capacité.

## 3. Tableau des niveaux de menace

<!-- markdownlint-disable MD013 -->

| Acteur / composant | Autonomous versioning outcome | Ruu Core guarantees | Ruu Cloud guarantees | Downstream version intelligence | Confiance | Disponibilité | Dernière observation | Réévalué pendant ce passage ? |
| ------------------ | ----------------------------- | ------------------- | -------------------- | ------------------------------- | --------- | ------------- | -------------------- | ------------------------------ |
| {{display_name}} / `{{component_id}}` | {{autonomous_versioning_outcome}} | {{ruu_core_guarantees}} | {{ruu_cloud_guarantees}} | {{downstream_version_intelligence}} | {{dimension_confidences}} | {{availability}} | {{last_observed_at}} | {{revalidated_this_run}} |

<!-- markdownlint-enable MD013 -->

Afficher la couleur et le libellé de chaque `level` :

- `U` — ⚪ INDETERMINATE ;
- `L0` — 🟢 ADJACENT_OR_COMPLEMENTARY ;
- `L1` — 🟡 ISOLATED_PRIMITIVE ;
- `L2` — 🟠 SUBSTANTIAL_PARTIAL_SUBSTITUTE ;
- `L3` — 🔴 NEAR_EQUIVALENCE ;
- `L4` — 🟣 DEMONSTRATED_SCOPED_EQUIVALENCE.

Afficher toujours tous les acteurs retenus dans le radar, y compris ceux dont
les évaluations sont reconduites, les acteurs dormants et ceux arrêtés par
instruction explicite. Ne calculer aucune moyenne.

### Détails par acteur et composant

#### {{display_name}} — `{{actor_id}}` / `{{component_id}}`

- **rôles :** {{roles}}
- **résumé :** {{actor.summary}}
- **périmètre, justification et preuves des quatre notes :** {{rating_details}}
- **dépendances externes :** {{external_dependencies}}
- **axes :** {{axis_assessments}}
- **dernière inspection de code :** {{monitoring.last_code_inspection_at}}
- **prochaine échéance :** {{monitoring.next_review_due_at}}
- **couverture :** {{monitoring.coverage_status}}
- **cycle de vie :** {{monitoring.actor_lifecycle}}
- **questions et investigations en attente :** {{monitoring.pending_investigations}}

## 4. Évolutions techniques et constats

{{findings}}

Chaque constat indique son identifiant stable, son acteur et composant, son
cycle de vie, ses axes, ses causes de changement et ses `evidence_ids`. Une
fermeture ne retire pas l'acteur. Une correction référence le constat corrigé
sous la forme `<report_id>#<finding_id>`.

## 5. Versioning invisible et charge cognitive résiduelle

{{versioning_invisibility_and_residual_cognitive_load}}

Distinguer la qualité des primitives de fusion de la nécessité résiduelle pour
le user ou le coding agent de choisir branches, worktrees, lanes, views, bases,
ordre des repos, ordre de merge, stacks, refresh, retries ou topologie de
publication.

### Autonomie locale, dépendances obligatoires et substitution commerciale

Pour chaque acteur pertinent, distinguer explicitement : moteur de versioning
réellement exécuté sur la machine ; CLI/extension locale adossée à un service ;
SCM côté serveur ; distribution gratuite ou payante ; nécessité d'un compte ou
d'une forge particulière ; fonctionnement avec des harnesses tiers ; support
des repositories sans remote ; continuité locale sans réseau.

Évaluer séparément (a) la substitution technique aux garanties de Ruu Core,
(b) la possibilité de remplacer commercialement Ruu Cloud par une expérience
native jugée suffisante, et (c) la capacité d'acquisition d'utilisateurs locaux
avant tout besoin de coordination multi-hôtes. Un produit gratuit ne prouve
pas l'équivalence ; une fonctionnalité propriétaire ne prouve pas l'absence de
substitution commerciale. Dire `indéterminé` sans preuve disponible.

Ces observations doivent provenir exclusivement des champs existants de
`report.json` : `actors[].summary`, évaluations R1/R2/R9 (et C5/C6/C7 le
cas échéant), preuves associées, et `positioning_implications`. Cette
section n'ajoute aucun champ au schéma ni aucune cinquième note technique.

## 6. Convergence, fraîcheur, exact dependencies et recovery Core

{{core_convergence_freshness_exact_dependencies_and_recovery}}

Présenter la convergence continue, l'interleaving, la disponibilité de l'état
exact sûr, la réconciliation du stale work, les dépendances exactes in-flight,
les effets inconnus, les retries et les frontières d'autorité.

## 7. Ruu Cloud, convergence team-wide et downstream

{{ruu_cloud_team_wide_convergence_and_downstream}}

Présenter l'autorité multi-host, la disponibilité partagée exacte, la
Useful-State Latency, le Canonical Team Development State, le mode dégradé, les
opérations distribuées, l'indépendance provider et les usages downstream.

## 8. Recherche de nouveaux entrants et compositions

- **statut de découverte :** {{discovery.status}}
- **recherches réellement effectuées :** {{discovery.searches}}
- **acteurs admis :** {{discovery.admitted_actor_ids}}
- **candidats en attente :** {{discovery.pending_candidates}}
- **doublons, forks, renommages et lignées :** {{discovery.duplicates_and_lineage}}
- **limites :** {{discovery.limitations}}

{{new_entrants_and_available_compositions}}

Ne présenter une composition comme disponible que lorsque ses composants et
ses frontières sont réellement accessibles et adéquats.

## 9. Trajectoires

{{trajectories}}

Dans le rapport hebdomadaire du premier lundi du mois, cette section porte la
synthèse mensuelle. Seul `implementation_change` établit une progression
technique concurrente.

## 10. Implications pour le positionnement

{{positioning_implications}}

Ces implications restent de la recherche. Elles ne modifient aucune autorité
produit Ruu ou Ruu Cloud. Faire ressortir distinctement l'avantage ou le risque
lié à la distribution, au prix et au coût de changement, sans convertir ces
éléments en preuve d'équivalence technique.

## 11. Couverture, retards et investigations ouvertes

{{coverage}}

- **acteurs en retard :** {{radar_continuity.overdue_actor_ids}}
- **questions ouvertes :** {{open_questions}}
- **continuité du radar :** {{radar_continuity.status}}
- **notes de réconciliation :** {{radar_continuity.reconciliation_notes}}

Un passage non réalisé reste `not_checked` ou `overdue`; ses dates et curseurs
ne sont pas avancés. Une évaluation reconduite conserve sa date et utilise
`revalidated_this_run=false`.

## 12. Sources et éléments de preuve

{{evidence}}

Afficher l'identifiant, la catégorie, l'URL, les dates disponibles, la révision
et le chemin éventuels, la proposition étayée, les limites et les détails
d'exécution pour `reproduced`. Ne pas confondre claim, documentation, code lu,
tests lus, reproduction et preuve.

## 13. Références historiques et corrections

- **rapports précédents :** {{previous_report_ids}}
- **rapports corrigés :** {{corrects}}
- **acteurs précédents :** {{radar_continuity.previous_actor_ids}}
- **nouvelles admissions :** {{radar_continuity.newly_admitted_actor_ids}}
- **radar courant :** {{radar_continuity.current_actor_ids}}
- **arrêts demandés :** {{radar_continuity.user_stopped_actor_ids}}
- **références des instructions :** {{radar_continuity.user_instruction_refs}}

{{historical_references_and_corrections}}

Le tableau et les détails sont rendus depuis le JSON et ne sont jamais édités
indépendamment pour changer une conclusion.
