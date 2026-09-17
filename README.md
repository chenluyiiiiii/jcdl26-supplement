# Supplementary Materials

Supplementary materials for:

**From Media Records to Knowledge Graph: Interoperable Ontology Modeling for a Multimodal Martial Arts Archive**

This repository provides the sample case data, conversion toolkit, and ontology metrics referenced in the paper. The materials are organized around three parts of the study: sample instantiation for The Archive, conversion from MAon-DAExt instances to Linked Art-compatible JSON-LD, and ontology metric reporting.

## Repository Contents

### Ontology Resources

For access to MAon data and the query interface, visit the [MAon resource page](https://purl.org/maont/techCorpus).

The ontology and individual resources are maintained externally and are available through the following persistent URLs:

- [MAon ontology (MAon.ttl)](https://purl.org/maont/ontology)
- [MAon individual registry (MAon_individual.ttl)](http://purl.org/maont/ontology_individual)
- [Digital Archive Extension (MAon_DAExt.ttl)](http://purl.org/hkmala/ontology/maon-daext)))

This repository provides supplementary case data, conversion code, and ontology metrics.

### `four-cases/`

Sample data for the four case records discussed in the paper:

- `sample_archive_instances_revision.ttl`: Turtle sample instances used as converter input.
- `re-case1_the_archive_set.jsonld`: Linked Art-compatible representation of The Archive as a `Set`.
- `re-case2_gwaa_ceoi_instructional_video.jsonld`: Linked Art-compatible representation of an instructional video case as a `DigitalObject`.
- `re-case3_sei_moon_baak_daa_mocap_animation.jsonld`: Linked Art-compatible representation of a motion-capture-derived animation case as a `DigitalObject`.
- `re-case4_300_years_hakka_kung_fu_exhibition.jsonld`: Linked Art-compatible representation of an exhibition case as an `Event`.
- `catalog-v001.xml`: XML catalog for resolving ontology IRIs without local absolute paths.

### `converter/`

Python toolkit for converting MAon-DAExt Turtle instances into Linked Art-compatible JSON-LD.

- `converter.py`: command-line conversion module.
- `app.py`, `run.py`, `index.html`: optional local web interface.
- `requirements.txt`: Python dependencies.

### `ontology-metrics/`

Ontology metrics associated with the ontology artifacts discussed in the paper.

- `ontology_metrics.md`: selected ontology metrics used in the paper.
  


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
