# Supplementary Materials

Supplementary materials for:

**From Media Records to Knowledge Graph: Interoperable Ontology Modeling for a Multimodal Martial Arts Archive**

This repository provides the sample case data, conversion toolkit, and ontology metrics referenced in the paper. The materials are organized around three parts of the study: sample instantiation for The Archive, conversion from MAon-DAExt instances to Linked Art-compatible JSON-LD, and ontology metric reporting.

## Repository Contents

### `four-cases/`

Sample data for the four case records discussed in the paper:

- `sample_archive_instances_revision.ttl`: Turtle sample instances used as converter input.
- `re-case1_the_archive_set.jsonld`: Linked Art-compatible representation of The Archive as a `Set`.
- `re-case2_gwaa_ceoi_instructional_video.jsonld`: Linked Art-compatible representation of an instructional video case as a `DigitalObject`.
- `re-case3_sei_moon_baak_daa_mocap_animation.jsonld`: Linked Art-compatible representation of a motion-capture-derived animation case as a `DigitalObject`.
- `re-case4_anonymous_exhibition.jsonld`: Linked Art-compatible representation of an exhibition case as an `Event`.
- `catalog-v001.xml`: XML catalog for resolving ontology IRIs without local absolute paths.

The case files use neutral labels such as `The Archive`, `Exhibition A`, `Organization A`, and `Person A`, matching the paper's anonymized case presentation.

### `converter/`

Python toolkit for converting MAon-DAExt Turtle instances into Linked Art-compatible JSON-LD.

- `converter.py`: command-line conversion module.
- `app.py`, `run.py`, `index.html`: optional local web interface.
- `requirements.txt`: Python dependencies.

### `ontology-metrics/`

Ontology metrics associated with the ontology artifacts discussed in the paper.

- `ontology_metrics.md`: selected ontology metrics used in the paper.
- `maon_sql_widget.html`: local inspection/helper artifact associated with SQL-based ontology parsing.

The full ontology TTL files are not included in this supplementary package; this repository provides the reported metrics, case samples, and conversion code needed to inspect the workflow.

## Quick Start

Install dependencies:

```bash
pip install -r converter/requirements.txt
```

Run the converter:

```bash
python converter/converter.py four-cases/sample_archive_instances_revision.ttl
```

Or start the local web interface:

```bash
python converter/run.py
```

## Review Note

Original person, archive, organization, place, and exhibition names in the four sample cases have been replaced with neutral labels. Local filesystem paths and platform cache files are omitted.
