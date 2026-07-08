# MAon-DAExt to Linked Art Converter

Converts [MAon-DAExt](https://example.org/sample/ontology/maon-daext) OWL instance files (Turtle) to Linked Art JSON-LD.

**MAon Digital Archive Extension for a digital martial arts archive (MAon-DAExt)** is a provisional digital archive extension of MAon for modelling digital martial arts archive-level entities, digital documents, moving-image resources, motion-capture-derived outputs, textual records, installations, exhibitions, agents, and file-level relations for Linked Art alignment. It imports [MAon](https://purl.org/maont/ontology) and adds a file/archive layer for a digital martial arts archive.

## Requirements

Python 3.10+

```
pip install rdflib
```

## Web UI

```bash
python run.py
```

Installs dependencies if missing, starts the server, and opens `http://localhost:5050` automatically. Three steps: paste/upload TTL → review agent types → convert and download.

## CLI

```bash
# Print all records as JSONL to stdout
python converter.py instances.ttl

# Write one .jsonld file per resource into a folder
python converter.py instances.ttl output/
```

## Output

One JSON-LD record per `owl:NamedIndividual` with a recognised class, using the Linked Art v1 context (`https://linked.art/ns/v1/linked-art.json`).

| TTL class | Linked Art type |
|---|---|
| `hda:Digital_Archive` | `Set` |
| `hda:Exhibition` | `Event` |
| `hda:Instructional_video`, `hda:MoCap_animation`, `hda:MoCap_item`, `hda:Interactive_system`, `hda:Digital_Learning_Platform` | `DigitalObject` |
| `hda:Programme` | `Activity` |
| `hda:Agent` | `Person` or `Group` (name heuristic) |
| `mao:MA_Master` | `Person` |
| `mao:E53_place` | `Place` |

## Overriding agent types

Pass a dict of `{uri: "Person"|"Group"}` to `convert_ttl()` when using the module directly:

```python
from converter import convert_ttl

with open("instances.ttl") as f:
    records = convert_ttl(f.read(), agent_type_overrides={
        "https://example.org/sample/resource/person_a": "Person"
    })
```
