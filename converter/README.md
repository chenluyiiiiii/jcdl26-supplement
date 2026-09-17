# MAon-DAExt to Linked Art Converter

**MAon Digital Archive Extension for a digital martial arts archive (MAon-DAExt)** is a provisional digital archive extension of MAon for modelling digital martial arts archive-level entities, digital documents, moving-image resources, motion-capture-derived outputs, textual records, installations, exhibitions, agents, and file-level relations for Linked Art alignment. It imports [MAon](https://purl.org/maont/ontology) and adds a file/archive layer for a digital martial arts archive.

This toolkit converts RDF instance data modelled with MAon-DAExt classes and properties into Linked Art-compatible JSON-LD.

The [MAon_DAExt.ttl](https://purl.org/hkmala/ontology/maon-daext)
 ontology file itself defines the schema and controlled vocabulary; it is not the demonstration instance input for the converter. The supplied demonstration input is:

```text
four-cases/sample_archive_instances_revision.ttl
```

The converter processes resources that are explicitly declared as `owl:NamedIndividual` and have a recognised MAon-DAExt or MAon class. Consequently, converting [MAon_DAExt.ttl](https://purl.org/hkmala/ontology/maon-daext) itself may return `0 records`: its named individuals are controlled-vocabulary concepts rather than archive instances belonging to the classes mapped by this converter.



## Requirements

Python 3.10+

From the `converter/` directory:

```bash
cd converter
pip install -r requirements.txt
```

Manual dependency installation is optional when using `run.py`, which checks for required packages and installs missing dependencies automatically.

## Web UI

From the `converter/` directory:

```bash
python run.py
```

The launcher starts the local Flask server and opens:

```text
http://localhost:5050
```

The workflow has three steps:

1. Paste or upload Turtle instance data.
2. Review automatically detected agent types.
3. Convert and download the Linked Art-compatible JSON-LD records.

The HTML file is not a standalone static application. It calls the local Flask endpoints `/preview` and `/convert`. Do not open `index.html` directly; launch the interface with `python run.py` and use `http://localhost:5050`.

## CLI

From the `converter/` directory:

```bash
# Convert the supplied demonstration dataset and print records as JSONL
python converter.py ../four-cases/sample_archive_instances_revision.ttl

# Convert another Turtle instance file
python converter.py instances.ttl

# Write one .jsonld file per converted resource into a folder
python converter.py instances.ttl output/
```

## Output

The converter produces one JSON-LD record for each recognised `owl:NamedIndividual`, using the Linked Art v1 context:

```text
https://linked.art/ns/v1/linked-art.json
```

| TTL class | Linked Art type |
|---|---|
| `hda:Digital_Archive` | `Set` |
| `hda:Exhibition` | `Event` |
| `hda:Instructional_video` | `DigitalObject` |
| `hda:MoCap_animation` | `DigitalObject` |
| `hda:MoCap_item` | `DigitalObject` |
| `hda:Interactive_system` / `hda:New_media_installation` | `DigitalObject` |
| `hda:Digital_Learning_Platform` | `DigitalObject` |
| `hda:Programme` | `Activity` |
| `hda:Agent` | `Person` or `Group` |
| `mao:MA_master` | `Person` |
| `mao:E53_place` | `Place` |
| `mao:MA_style` | `Type` |
| `mao:MA_technique` | `Type` |
| `mao:Form_move` | `Type` |

For `hda:Agent`, the converter initially distinguishes `Person` and `Group` using a name-keyword heuristic. The detected type can be reviewed and changed in the Web UI or overridden programmatically.

## Overriding agent types

When using the converter as a Python module, pass a dictionary of `{uri: "Person"|"Group"}` to `convert_ttl()`:

```python
from converter import convert_ttl

with open("instances.ttl", encoding="utf-8") as f:
    records = convert_ttl(
        f.read(),
        agent_type_overrides={
            "https://hkmala.org/resource/hing_chao": "Person"
        }
    )
```
