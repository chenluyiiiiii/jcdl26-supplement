# Supplementary Ontology Metrics

## Ontology Axiom Profiles

### MAon_v1_2.ttl

| Metric | Value |
|---|---|
| Subclass axioms | 222 |
| Subproperty axioms | 34 |
| Domain axioms | 91 |
| Range axioms | 90 |
| Blank restrictions | 137 |
| Equivalent class axioms | 1 |
| Class label coverage | 97/97 (100%) |
| Class description/comment coverage | 88/97 (90.7%) |

### MAon_DAExt.ttl

| Metric | Value |
|---|---|
| Subclass axioms | 36 |
| Subproperty axioms | 4 |
| Domain axioms | 41 |
| Range axioms | 41 |
| Inverse property axioms | 1 |
| Class label coverage | 38/40 (95%) |
| Class description coverage | 37/40 (92.5%) |

## Full Local Core Package

*MAon_cv + MAon + MAon_DAExt + MAon_individual*

| Metric | Value |
|---|---|
| Triples | 8,074 |
| Declared classes | 137 total (135 local ontology classes excluding SKOS) |
| Object properties | 83 |
| Datatype properties | 30 |
| Annotation properties | 36 |
| Explicit named individuals | 662 (643 verified MAon individuals + 19 SKOS vocabulary individuals) |

## Per-Artifact Breakdown

| Artifact | Triples | Classes | Object props | Datatype props | Annotation props | Individuals |
|---|---|---|---|---|---|---|
| MAon.ttl | 1,639 | 97 declared | 58 | 14 | 32 | 0 |
| MAon_DAExt.ttl | 621 | 40 declared (38 local `hda:` + 2 SKOS) | 25 | 16 | 6 | 19 SKOS vocabulary individuals |
| MAon_individual.ttl | 5,547 | 0 | 0 | 0 | 0 | 643 verified named individuals |
| Sample cases TTL | 205 | 0 | 0 | 0 | 1 | 25 case individuals |
