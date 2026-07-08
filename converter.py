"""
converter.py — MAon-DAExt TTL → Linked Art JSON-LD converter
MAon-DAExt Toolkit  |  Core conversion module

Usage (CLI):
    python converter.py input.ttl [output_dir]

    If output_dir is omitted, prints all records as JSONL to stdout.
    If output_dir is given, writes one <id>.jsonld file per resource.
"""

import json
import os
import sys
import re
from typing import Optional

from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal, URIRef
from rdflib.namespace import XSD, SKOS

# ── Namespaces ────────────────────────────────────────────────────────────────
HDA    = Namespace("https://purl.org/maont/daext/")
MAO    = Namespace("https://purl.org/maont/ontology/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
AAT    = Namespace("http://vocab.getty.edu/aat/")
LA_CONTEXT = "https://linked.art/ns/v1/linked-art.json"

# ── Class → Linked Art type ───────────────────────────────────────────────────
CLASS_TO_LA_TYPE: dict[str, str] = {
    str(HDA.Digital_Archive):        "Set",
    str(HDA.Exhibition):             "Event",
    str(HDA.Instructional_video):    "DigitalObject",
    str(HDA.MoCap_animation):        "DigitalObject",
    str(HDA.MoCap_item):             "DigitalObject",
    str(HDA.New_media_installation): "DigitalObject",
    str(HDA.Digital_Learning_Platform): "DigitalObject",
    str(HDA.Programme):              "Activity",
    str(HDA.Agent):                  "Group",    # refined by classify_agent()
    str(MAO.MA_Master):              "Person",
    str(MAO.MA_style):               "Type",
    str(MAO.MA_technique):           "Type",
    str(MAO.Form_move):              "Type",
    str(MAO.E53_place):              "Place",
}

# Keywords that signal an organisational (Group) agent name
ORG_KEYWORDS = [
    "university", "universiti", "université", "universität",
    "centre", "center", "museum", "association", "department",
    "institute", "laboratory", "lab", "office", "bureau",
    "ltd", "limited", "foundation", "academy", "college",
    "school", "organization", "organisation", "research",
    "committee", "council", "society", "board", "network",
    "studio", "company", "corp", "cooperation",
]

AAT_DESCRIPTION = "http://vocab.getty.edu/aat/300435416"
AAT_NOTE        = "http://vocab.getty.edu/aat/300435415"
AAT_CREDIT      = "http://vocab.getty.edu/aat/300026687"
AAT_EXHIBITIONS = "http://vocab.getty.edu/aat/300054766"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_org_name(name: str) -> bool:
    nl = name.lower()
    return any(kw in nl for kw in ORG_KEYWORDS)


def _label(g: Graph, uri: URIRef) -> str:
    """Best single label for a resource."""
    for prop in (MAO.name_en, HDA.hasTitle, RDFS.label):
        val = g.value(uri, prop)
        if val:
            return str(val)
    return str(uri).split("/")[-1].split("#")[-1]


def _names(g: Graph, uri: URIRef) -> list[dict]:
    """All identified_by Name entries from name properties."""
    seen: set[str] = set()
    result = []
    for prop in (HDA.hasTitle, MAO.name_en, MAO.name_zh,
                 MAO.otherName_en, MAO.name_romanCAN, MAO.name_romanMAN):
        for val in g.objects(uri, prop):
            content = str(val)
            if content not in seen:
                seen.add(content)
                result.append({"type": "Name", "content": content})
    return result


def _primary_class(g: Graph, uri: URIRef) -> Optional[str]:
    """Return the first class URI in CLASS_TO_LA_TYPE order."""
    for cls in g.objects(uri, RDF.type):
        if str(cls) in CLASS_TO_LA_TYPE:
            return str(cls)
    return None


def classify_agent(g: Graph, uri: URIRef) -> str:
    """Heuristic: determine whether an hda:Agent is a Person or Group."""
    # Explicitly typed as MA_Master → Person
    if (uri, RDF.type, MAO.MA_Master) in g:
        return "Person"
    # Check all name literals for org keywords
    for prop in (MAO.name_en, MAO.name_zh, RDFS.label):
        val = g.value(uri, prop)
        if val and _is_org_name(str(val)):
            return "Group"
    # Default: treat as Person (personal names have no org keyword)
    return "Person"


def _ref(g: Graph, uri: URIRef, la_type: Optional[str] = None) -> dict:
    """Minimal reference stub: {id, type, _label}."""
    if la_type is None:
        cls = _primary_class(g, uri)
        la_type = CLASS_TO_LA_TYPE.get(cls, "Type") if cls else "Type"
    if la_type == "Group":
        la_type = classify_agent(g, uri)
    return {"id": str(uri), "type": la_type, "_label": _label(g, uri)}


def _ling(content: str, aat_uri: str, aat_label: str) -> dict:
    """Convenience: LinguisticObject wrapper."""
    return {
        "type": "LinguisticObject",
        "classified_as": [{"id": aat_uri, "type": "Type", "_label": aat_label}],
        "content": content,
    }


def _note(content: str) -> dict:
    return _ling(content, AAT_NOTE, "Note")


def _desc(content: str) -> dict:
    return _ling(content, AAT_DESCRIPTION, "Description")


# ── Per-class converters ──────────────────────────────────────────────────────

def _map_digital_archive(g: Graph, uri: URIRef, rec: dict):
    """hda:Digital_Archive → Set"""
    # created_by: timespan + collaborators
    created_by: dict = {"type": "Creation"}
    yr = g.value(uri, DCTERMS.created)
    if yr:
        created_by["timespan"] = {
            "type": "TimeSpan",
            "begin_of_the_begin": f"{yr}-01-01T00:00:00Z",
        }
    collabs = [_ref(g, c) for c in g.objects(uri, HDA.hasCollaborator)]
    if collabs:
        created_by["carried_out_by"] = collabs
    if len(created_by) > 1:
        rec["created_by"] = created_by

    # description
    desc = g.value(uri, HDA.hasDescription)
    if desc:
        rec["referred_to_by"] = [_desc(str(desc))]

    # access URL → subject_of
    url = g.value(uri, HDA.hasAccessURL)
    if url:
        rec["subject_of"] = [{
            "type": "LinguisticObject",
            "_label": f"{rec['_label']} project webpage",
            "digitally_carried_by": [{
                "type": "DigitalObject",
                "access_point": [{"id": str(url), "type": "DigitalObject"}],
                "format": "text/html",
            }],
        }]


def _map_exhibition(g: Graph, uri: URIRef, rec: dict):
    """hda:Exhibition → Event"""
    # timespan
    start = g.value(uri, HDA.hasStartDate)
    end   = g.value(uri, HDA.hasEndDate)
    if start or end:
        ts: dict = {"type": "TimeSpan"}
        if start:
            ts["begin_of_the_begin"] = f"{start}T00:00:00Z"
        if end:
            ts["end_of_the_end"]     = f"{end}T23:59:59Z"
        rec["timespan"] = ts

    # venue
    vp = g.value(uri, HDA.hasVenuePlace)
    if vp:
        rec["took_place_at"] = [_ref(g, vp, "Place")]

    # carried_out_by: organizers + curators + collaborators
    cob: list[dict] = []
    for u in g.objects(uri, HDA.hasOrganizer):
        cob.append(_ref(g, u))
    for u in g.objects(uri, HDA.hasCurator):
        r = _ref(g, u)
        r["type"] = "Person"          # curators are always persons
        cob.append(r)
    for u in g.objects(uri, HDA.hasCollaborator):
        cob.append(_ref(g, u))
    if cob:
        rec["carried_out_by"] = cob

    # referred_to_by
    rby: list[dict] = []
    desc = g.value(uri, HDA.hasDescription)
    if desc:
        rby.append(_desc(str(desc)))

    # credit note (auto-generated)
    org_names   = [_label(g, u) for u in g.objects(uri, HDA.hasOrganizer)]
    cur_names   = [_label(g, u) for u in g.objects(uri, HDA.hasCurator)]
    collab_names = [_label(g, u) for u in g.objects(uri, HDA.hasCollaborator)]
    credit_parts = []
    if org_names:
        credit_parts.append(f"Co-organizers: {', '.join(org_names)}.")
    if cur_names:
        credit_parts.append(f"Curators: {', '.join(cur_names)}.")
    if collab_names:
        credit_parts.append(f"Collaborators: {', '.join(collab_names)}.")
    if credit_parts:
        rby.append(_ling(" ".join(credit_parts), AAT_CREDIT, "Credit/Acknowledgement"))

    # digital resources note
    refs = list(g.objects(uri, HDA.references))
    if refs:
        parts = [f"{_label(g, r)} ({r})" for r in refs]
        rby.append(_note(
            "Digital resources used in the exhibition include "
            + ", ".join(parts) + "."
        ))

    if rby:
        rec["referred_to_by"] = rby

    # archive membership
    arch = g.value(uri, HDA.memberOfArchive)
    if arch:
        rec["member_of"] = [_ref(g, arch, "Set")]

    # access URL → subject_of
    url = g.value(uri, HDA.hasAccessURL)
    if url:
        rec["subject_of"] = [{
            "type": "LinguisticObject",
            "_label": f"{rec['_label']} webpage",
            "digitally_carried_by": [{
                "type": "DigitalObject",
                "access_point": [{"id": str(url), "type": "DigitalObject"}],
                "format": "text/html",
            }],
        }]


def _common_digital(g: Graph, uri: URIRef, rec: dict):
    """Shared properties for all DigitalObject subtypes."""
    arch = g.value(uri, HDA.memberOfArchive)
    if arch:
        rec["member_of"] = [_ref(g, arch, "Set")]

    url = g.value(uri, HDA.hasAccessURL)
    if url:
        rec["access_point"] = [{"id": str(url), "type": "DigitalObject"}]

    desc = g.value(uri, HDA.hasDescription)
    if desc:
        rec.setdefault("referred_to_by", []).append(_desc(str(desc)))


def _content_description(g: Graph, uri: URIRef, rec: dict):
    """Auto-generate content description from style/technique/master triples."""
    style     = g.value(uri, HDA.documentsStyle)
    technique = g.value(uri, HDA.documentsTechnique)
    master    = g.value(uri, HDA.featuresMaster)
    parts: list[str] = []
    if style:
        parts.append(f"documenting {_label(g, style)}")
    if technique:
        parts.append(f"and the {_label(g, technique)} technique")
    if master:
        parts.append(f"featuring {_label(g, master)}")
    if parts:
        rec.setdefault("referred_to_by", []).append(
            _desc("This digital object " + ", ".join(parts) + ".")
        )


def _map_instructional_video(g: Graph, uri: URIRef, rec: dict):
    """hda:Instructional_video → DigitalObject"""
    _common_digital(g, uri, rec)

    for assoc in g.objects(uri, HDA.associatedWith):
        cls = _primary_class(g, assoc)
        if cls == str(HDA.Digital_Learning_Platform):
            rec["part_of"] = _ref(g, assoc, "DigitalObject")
        elif cls == str(HDA.Programme):
            rec.setdefault("used_for", []).append({
                "type": "Activity",
                "_label": _label(g, assoc),
                "classified_as": [{
                    "id": str(HDA.Programme),
                    "type": "Type",
                    "_label": "Programme",
                }],
            })

    _content_description(g, uri, rec)


def _map_mocap_animation(g: Graph, uri: URIRef, rec: dict):
    """hda:MoCap_animation → DigitalObject"""
    _common_digital(g, uri, rec)

    # created_by
    creators = [_ref(g, c, "Person") for c in g.objects(uri, HDA.createdBy)]
    derived  = g.value(uri, HDA.derivedFrom)
    cb: dict = {"type": "Creation"}
    if derived:
        cb["referred_to_by"] = [_note(
            f"Derived from {_label(g, derived)} ({derived})."
        )]
    if creators:
        cb["carried_out_by"] = creators
    if len(cb) > 1:
        rec["created_by"] = cb

    # used_for: shown at exhibition(s)
    used_for: list[dict] = []
    for ev in g.objects(uri, HDA.shownAt):
        used_for.append({
            "type": "Activity",
            "_label": f"Shown at {_label(g, ev)}",
            "classified_as": [{"id": AAT_EXHIBITIONS, "type": "Type", "_label": "exhibitions"}],
            "referred_to_by": [_note(
                f"Shown at the exhibition {_label(g, ev)} ({ev})."
            )],
        })
    for assoc in g.objects(uri, HDA.associatedWith):
        used_for.append({
            "type": "Activity",
            "_label": f"Use in {_label(g, assoc)}",
            "referred_to_by": [_note(
                f"Used in {_label(g, assoc)} ({assoc})."
            )],
        })
    if used_for:
        rec["used_for"] = used_for

    _content_description(g, uri, rec)


def _map_mocap_item(g: Graph, uri: URIRef, rec: dict):
    """hda:MoCap_item → DigitalObject"""
    _common_digital(g, uri, rec)

    # technical metadata as a Note
    dur  = g.value(uri, HDA.hasDuration)
    fps  = g.value(uri, HDA.hasFrameRate)
    if dur or fps:
        bits = []
        if dur: bits.append(f"Duration: {dur}")
        if fps: bits.append(f"Frame rate: {fps}")
        rec.setdefault("referred_to_by", []).append(_note("; ".join(bits) + "."))

    _content_description(g, uri, rec)


def _map_new_media_installation(g: Graph, uri: URIRef, rec: dict):
    """hda:New_media_installation → DigitalObject"""
    _common_digital(g, uri, rec)

    # created_by: artists
    artists = [_ref(g, a, "Person") for a in g.objects(uri, HDA.hasArtist)]
    if artists:
        rec["created_by"] = {"type": "Creation", "carried_out_by": artists}

    # collaborators note
    collabs = list(g.objects(uri, HDA.hasCollaborator))
    if collabs:
        names = [_label(g, c) for c in collabs]
        rec.setdefault("referred_to_by", []).append(
            _note("Collaborators: " + ", ".join(names) + ".")
        )

    # used_for: present_at
    used_for: list[dict] = []
    for ev in g.objects(uri, HDA.present_at):
        used_for.append({
            "type": "Activity",
            "_label": f"Presented at {_label(g, ev)}",
            "referred_to_by": [_note(
                f"Presented at {_label(g, ev)} ({ev})."
            )],
        })
    if used_for:
        rec["used_for"] = used_for

    # digital files note
    files = list(g.objects(uri, HDA.usesDigitalFile))
    if files:
        parts = [f"{_label(g, f)} ({f})" for f in files]
        rec.setdefault("referred_to_by", []).append(
            _note("Uses digital files: " + ", ".join(parts) + ".")
        )

    # usesSystemOrTechnology → classified_as entries
    for concept in g.objects(uri, HDA.usesSystemOrTechnology):
        pref = g.value(concept, SKOS.prefLabel) or g.value(concept, RDFS.label)
        concept_label = str(pref) if pref else str(concept).split("#")[-1]
        rec.setdefault("classified_as", []).append({
            "id": str(concept),
            "type": "Type",
            "_label": concept_label,
        })


def _map_digital_learning_platform(g: Graph, uri: URIRef, rec: dict):
    """hda:Digital_Learning_Platform → DigitalObject"""
    _common_digital(g, uri, rec)

    for assoc in g.objects(uri, HDA.associatedWith):
        cls = _primary_class(g, assoc)
        if cls == str(HDA.Programme):
            rec.setdefault("used_for", []).append({
                "type": "Activity",
                "_label": _label(g, assoc),
                "classified_as": [{
                    "id": str(HDA.Programme),
                    "type": "Type",
                    "_label": "Programme",
                }],
            })

    refs = list(g.objects(uri, HDA.references))
    if refs:
        parts = [f"{_label(g, r)} ({r})" for r in refs]
        rec.setdefault("referred_to_by", []).append(
            _note("References: " + ", ".join(parts) + ".")
        )


def _map_programme(g: Graph, uri: URIRef, rec: dict):
    """hda:Programme → Activity"""
    arch = g.value(uri, HDA.memberOfArchive)
    if arch:
        rec["part_of"] = [_ref(g, arch, "Set")]


# ── Main conversion entry point ───────────────────────────────────────────────

def convert_individual(
    g: Graph,
    uri: URIRef,
    agent_type_overrides: Optional[dict] = None,
) -> Optional[dict]:
    """
    Convert one TTL named individual to a Linked Art JSON-LD dict.

    agent_type_overrides: {uri_string: "Person"|"Group"} — manual overrides
                          supplied by the UI.
    Returns None for individuals whose class is not mapped.
    """
    primary_cls = _primary_class(g, uri)
    if not primary_cls:
        return None

    la_type = CLASS_TO_LA_TYPE.get(primary_cls)
    if not la_type:
        return None

    # Resolve agent type
    if (agent_type_overrides or {}).get(str(uri)):
        la_type = agent_type_overrides[str(uri)]
    elif la_type == "Group":
        la_type = classify_agent(g, uri)

    label = _label(g, uri)

    rec: dict = {
        "@context": LA_CONTEXT,
        "id": str(uri),
        "type": la_type,
        "_label": label,
    }

    # identified_by
    names = _names(g, uri)
    if names:
        rec["identified_by"] = names

    # classified_as: custom ontology class
    cls_label = primary_cls.split("#")[-1].split("/")[-1]
    rec["classified_as"] = [{"id": primary_cls, "type": "Type", "_label": cls_label}]
    if primary_cls == str(HDA.Exhibition):
        rec["classified_as"].append({
            "id": AAT_EXHIBITIONS, "type": "Type", "_label": "exhibitions"
        })

    # Class-specific mappings
    if la_type == "Set":
        _map_digital_archive(g, uri, rec)
    elif la_type == "Event":
        _map_exhibition(g, uri, rec)
    elif la_type == "DigitalObject":
        dispatch = {
            str(HDA.Instructional_video):       _map_instructional_video,
            str(HDA.MoCap_animation):           _map_mocap_animation,
            str(HDA.MoCap_item):                _map_mocap_item,
            str(HDA.New_media_installation):    _map_new_media_installation,
            str(HDA.Digital_Learning_Platform): _map_digital_learning_platform,
        }
        fn = dispatch.get(primary_cls, _common_digital)
        fn(g, uri, rec)
    elif la_type == "Activity":
        _map_programme(g, uri, rec)
    # Person, Group, Place, Type → names/label already set; no extra triples needed

    # Strip empty lists / dicts
    return {k: v for k, v in rec.items() if v not in (None, [], {})}


def convert_ttl(
    ttl_content: str,
    agent_type_overrides: Optional[dict] = None,
) -> list[dict]:
    """
    Parse a Turtle string and return a list of Linked Art JSON-LD dicts,
    one per owl:NamedIndividual with a recognised class.

    agent_type_overrides: {uri_string: "Person"|"Group"}
    """
    g = Graph()
    g.parse(data=ttl_content, format="turtle")

    records: list[dict] = []
    for uri in g.subjects(RDF.type, OWL.NamedIndividual):
        if not isinstance(uri, URIRef):
            continue
        rec = convert_individual(g, uri, agent_type_overrides)
        if rec:
            records.append(rec)

    # Stable order: by id
    records.sort(key=lambda r: r.get("id", ""))
    return records


def detect_individuals(ttl_content: str) -> dict[str, list[dict]]:
    """
    Return all mapped named individuals grouped by their Linked Art type.

    Structure:
    {
      "Person":        [{"uri": ..., "label": ..., "auto_type": "Person"|"Group", "hda_class": ...}, ...],
      "Group":         [...],
      "DigitalObject": [{"uri": ..., "label": ..., "hda_class": ...}, ...],
      "Event":         [...],
      "Set":           [...],
      "Activity":      [...],
      "Place":         [...],
      "Type":          [...],
    }

    Only classes present in CLASS_TO_LA_TYPE are included.
    Agents carry an "auto_type" field for the Person/Group review step.
    All entries carry a "hda_class" field with the local DAExt/MAO class name.
    """
    g = Graph()
    g.parse(data=ttl_content, format="turtle")

    buckets: dict[str, list[dict]] = {}

    for uri in g.subjects(RDF.type, OWL.NamedIndividual):
        if not isinstance(uri, URIRef):
            continue
        cls = _primary_class(g, uri)
        if not cls:
            continue
        la_type = CLASS_TO_LA_TYPE.get(cls)
        if not la_type:
            continue

        cls_local = cls.split("#")[-1].split("/")[-1]
        entry: dict = {
            "uri":       str(uri),
            "label":     _label(g, uri),
            "hda_class": cls_local,
        }

        # Agents get Person/Group disambiguation; bucket by resolved type
        if cls in (str(HDA.Agent), str(MAO.MA_Master)):
            entry["auto_type"] = classify_agent(g, uri)
            la_type = entry["auto_type"]

        buckets.setdefault(la_type, []).append(entry)

    for bucket in buckets.values():
        bucket.sort(key=lambda e: e["label"])

    return buckets


def detect_agents(ttl_content: str) -> list[dict]:
    """
    Backwards-compatible wrapper: return only agent entries for the
    Person/Group review step.
    [{"uri": ..., "label": ..., "auto_type": "Person"|"Group"}, ...]
    """
    result = detect_individuals(ttl_content)
    agents = result.get("Person", []) + result.get("Group", [])
    agents.sort(key=lambda a: a["label"])
    return agents


# ── CLI entry point ───────────────────────────────────────────────────────────

def _safe_filename(uri: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_\-]", "_", uri.split("/")[-1].split("#")[-1])
    return slug or "record"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python converter.py <input.ttl> [output_dir]", file=sys.stderr)
        sys.exit(1)

    ttl_path = sys.argv[1]
    out_dir  = sys.argv[2] if len(sys.argv) > 2 else None

    with open(ttl_path, encoding="utf-8") as fh:
        ttl_text = fh.read()

    records = convert_ttl(ttl_text)

    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        for rec in records:
            fname = _safe_filename(rec["id"]) + ".jsonld"
            fpath = os.path.join(out_dir, fname)
            with open(fpath, "w", encoding="utf-8") as fh:
                json.dump(rec, fh, ensure_ascii=False, indent=2)
            print(f"  → {fpath}")
        print(f"\n✓ {len(records)} records written to {out_dir}/")
    else:
        for rec in records:
            print(json.dumps(rec, ensure_ascii=False))
