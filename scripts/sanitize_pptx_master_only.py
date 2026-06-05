#!/usr/bin/env python3
"""Create privacy-safe PPTX template files that retain masters/layouts only.

The output keeps reusable presentation style assets: slide masters, layouts,
themes, table styles, and media referenced by those template parts. It removes
source slides, notes, comments, custom XML, document properties, embedded files,
and other author/content-bearing parts, then creates one blank placeholder slide.
"""

from __future__ import annotations

import argparse
import posixpath
import re
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET


PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
PML_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

ET.register_namespace("", PML_NS)
ET.register_namespace("r", REL_NS)

SLIDE_REL = f"{REL_NS}/slide"
SLIDE_LAYOUT_REL = f"{REL_NS}/slideLayout"
SLIDE_MASTER_REL = f"{REL_NS}/slideMaster"
THEME_REL = f"{REL_NS}/theme"
TABLE_STYLES_REL = f"{REL_NS}/tableStyles"
PRES_PROPS_REL = f"{REL_NS}/presProps"
VIEW_PROPS_REL = f"{REL_NS}/viewProps"
IMAGE_REL = f"{REL_NS}/image"

SAFE_PRESENTATION_RELS = {
    SLIDE_MASTER_REL,
    THEME_REL,
    TABLE_STYLES_REL,
    PRES_PROPS_REL,
    VIEW_PROPS_REL,
}

SAFE_PART_PREFIXES = (
    "ppt/slideMasters/",
    "ppt/slideLayouts/",
    "ppt/theme/",
    "ppt/media/",
)

SAFE_EXACT_PARTS = {
    "[Content_Types].xml",
    "_rels/.rels",
    "ppt/presentation.xml",
    "ppt/_rels/presentation.xml.rels",
    "ppt/tableStyles.xml",
    "ppt/presProps.xml",
    "ppt/viewProps.xml",
}

UNSAFE_PREFIXES = (
    "docProps/",
    "customXml/",
    "ppt/slides/",
    "ppt/notesSlides/",
    "ppt/notesMasters/",
    "ppt/comments/",
    "ppt/commentAuthors",
    "ppt/tags/",
    "ppt/embeddings/",
    "ppt/charts/",
    "ppt/diagrams/",
    "ppt/handoutMasters/",
    "ppt/printerSettings/",
)


def rels_path_for(part_name: str) -> str:
    part = PurePosixPath(part_name)
    return str(part.parent / "_rels" / f"{part.name}.rels")


def resolve_target(source_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    base_dir = str(PurePosixPath(source_part).parent)
    return posixpath.normpath(posixpath.join(base_dir, target)).lstrip("/")


def relative_target(source_part: str, target_part: str) -> str:
    base_dir = str(PurePosixPath(source_part).parent)
    return posixpath.relpath(target_part, base_dir).replace("\\", "/")


def read_xml(zf: zipfile.ZipFile, name: str) -> ET.Element | None:
    try:
        return ET.fromstring(zf.read(name))
    except KeyError:
        return None


def parse_rels(zf: zipfile.ZipFile, part_name: str) -> list[ET.Element]:
    root = read_xml(zf, rels_path_for(part_name))
    if root is None:
        return []
    return list(root)


def serialize_xml(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def new_relationships(rels: list[tuple[str, str, str]]) -> bytes:
    root = ET.Element("Relationships", xmlns=PKG_REL_NS)
    for rel_id, rel_type, target in rels:
        ET.SubElement(root, "Relationship", Id=rel_id, Type=rel_type, Target=target)
    return serialize_xml(root)


def collect_template_closure(zf: zipfile.ZipFile) -> set[str]:
    keep: set[str] = set()
    queue: list[str] = []

    for rel in parse_rels(zf, "ppt/presentation.xml"):
        rel_type = rel.attrib.get("Type", "")
        target = rel.attrib.get("Target", "")
        if rel_type in SAFE_PRESENTATION_RELS and target:
            part = resolve_target("ppt/presentation.xml", target)
            if part in zf.namelist():
                queue.append(part)

    while queue:
        part = queue.pop()
        if part in keep:
            continue
        if not (part in SAFE_EXACT_PARTS or part.startswith(SAFE_PART_PREFIXES)):
            continue
        keep.add(part)
        rels_name = rels_path_for(part)
        if rels_name in zf.namelist():
            keep.add(rels_name)
        for rel in parse_rels(zf, part):
            rel_type = rel.attrib.get("Type", "")
            target = rel.attrib.get("Target", "")
            if not target or rel.attrib.get("TargetMode") == "External":
                continue
            target_part = resolve_target(part, target)
            if rel_type in {SLIDE_LAYOUT_REL, SLIDE_MASTER_REL, THEME_REL, IMAGE_REL}:
                if target_part in zf.namelist():
                    queue.append(target_part)

    return keep


def clean_content_types(zf: zipfile.ZipFile, kept_parts: set[str]) -> bytes:
    root = read_xml(zf, "[Content_Types].xml")
    if root is None:
        raise RuntimeError("Missing [Content_Types].xml")

    allowed_overrides = kept_parts | {"ppt/slides/slide1.xml"}
    for child in list(root):
        part_name = child.attrib.get("PartName", "").lstrip("/")
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "Override" and part_name not in allowed_overrides:
            root.remove(child)

    def has_override(part_name: str) -> bool:
        wanted = f"/{part_name}"
        return any(child.attrib.get("PartName") == wanted for child in root)

    if not has_override("ppt/slides/slide1.xml"):
        ET.SubElement(
            root,
            f"{{{CT_NS}}}Override",
            PartName="/ppt/slides/slide1.xml",
            ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml",
        )
    return serialize_xml(root)


def clean_root_rels(zf: zipfile.ZipFile) -> bytes:
    root = read_xml(zf, "_rels/.rels")
    if root is None:
        raise RuntimeError("Missing _rels/.rels")
    for child in list(root):
        target = child.attrib.get("Target", "")
        if target != "ppt/presentation.xml":
            root.remove(child)
    return serialize_xml(root)


def clean_presentation(zf: zipfile.ZipFile) -> tuple[bytes, bytes, str]:
    pres = read_xml(zf, "ppt/presentation.xml")
    if pres is None:
        raise RuntimeError("Missing ppt/presentation.xml")

    pres_rels = parse_rels(zf, "ppt/presentation.xml")
    safe_rels: list[tuple[str, str, str]] = []
    master_rel_ids: list[str] = []
    next_id = 2
    for rel in pres_rels:
        rel_type = rel.attrib.get("Type", "")
        target = rel.attrib.get("Target", "")
        rel_id = rel.attrib.get("Id", "")
        if rel_type in SAFE_PRESENTATION_RELS and target and rel_id:
            safe_rels.append((rel_id, rel_type, target))
            if rel_type == SLIDE_MASTER_REL:
                master_rel_ids.append(rel_id)
            match = re.match(r"rId(\d+)$", rel_id)
            if match:
                next_id = max(next_id, int(match.group(1)) + 1)

    slide_rel_id = f"rId{next_id}"
    layout_rel_id = "rId1"
    safe_rels.append((slide_rel_id, SLIDE_REL, "slides/slide1.xml"))

    ns = {"p": PML_NS, "r": REL_NS}
    sld_id_lst = pres.find("p:sldIdLst", ns)
    if sld_id_lst is None:
        sld_id_lst = ET.SubElement(pres, f"{{{PML_NS}}}sldIdLst")
    for child in list(sld_id_lst):
        sld_id_lst.remove(child)
    ET.SubElement(sld_id_lst, f"{{{PML_NS}}}sldId", id="256", attrib={f"{{{REL_NS}}}id": slide_rel_id})

    sld_master_lst = pres.find("p:sldMasterIdLst", ns)
    if sld_master_lst is None:
        sld_master_lst = ET.SubElement(pres, f"{{{PML_NS}}}sldMasterIdLst")
    for child in list(sld_master_lst):
        rid = child.attrib.get(f"{{{REL_NS}}}id")
        if rid and rid not in master_rel_ids:
            sld_master_lst.remove(child)

    layout_target = find_first_layout_target(zf)
    slide_xml = blank_slide_xml(layout_rel_id)
    slide_rels = new_relationships([(layout_rel_id, SLIDE_LAYOUT_REL, layout_target)])

    return serialize_xml(pres), new_relationships(safe_rels), layout_target, slide_xml, slide_rels


def find_first_layout_target(zf: zipfile.ZipFile) -> str:
    for rel in parse_rels(zf, "ppt/slideMasters/slideMaster1.xml"):
        if rel.attrib.get("Type") == SLIDE_LAYOUT_REL:
            target = rel.attrib.get("Target", "")
            if target:
                return relative_target("ppt/slides/slide1.xml", resolve_target("ppt/slideMasters/slideMaster1.xml", target))
    for name in zf.namelist():
        if name.startswith("ppt/slideLayouts/slideLayout") and name.endswith(".xml"):
            return relative_target("ppt/slides/slide1.xml", name)
    raise RuntimeError("No slide layout found")


def blank_slide_xml(layout_rel_id: str) -> bytes:
    root = ET.Element(f"{{{PML_NS}}}sld")
    c_sld = ET.SubElement(root, f"{{{PML_NS}}}cSld")
    sp_tree = ET.SubElement(c_sld, f"{{{PML_NS}}}spTree")
    nv_grp = ET.SubElement(sp_tree, f"{{{PML_NS}}}nvGrpSpPr")
    ET.SubElement(nv_grp, f"{{{PML_NS}}}cNvPr", id="1", name="")
    ET.SubElement(nv_grp, f"{{{PML_NS}}}cNvGrpSpPr")
    ET.SubElement(nv_grp, f"{{{PML_NS}}}nvPr")
    grp = ET.SubElement(sp_tree, f"{{{PML_NS}}}grpSpPr")
    xfrm = ET.SubElement(grp, f"{{http://schemas.openxmlformats.org/drawingml/2006/main}}xfrm")
    ET.SubElement(xfrm, f"{{http://schemas.openxmlformats.org/drawingml/2006/main}}off", x="0", y="0")
    ET.SubElement(xfrm, f"{{http://schemas.openxmlformats.org/drawingml/2006/main}}ext", cx="0", cy="0")
    ET.SubElement(xfrm, f"{{http://schemas.openxmlformats.org/drawingml/2006/main}}chOff", x="0", y="0")
    ET.SubElement(xfrm, f"{{http://schemas.openxmlformats.org/drawingml/2006/main}}chExt", cx="0", cy="0")
    ET.SubElement(root, f"{{{PML_NS}}}clrMapOvr").append(
        ET.Element(f"{{http://schemas.openxmlformats.org/drawingml/2006/main}}masterClrMapping")
    )
    return serialize_xml(root)


def is_safe_to_copy(name: str, keep: set[str]) -> bool:
    if name.endswith("/"):
        return False
    if name in keep:
        return True
    if name in SAFE_EXACT_PARTS:
        return True
    if any(name.startswith(prefix) for prefix in UNSAFE_PREFIXES):
        return False
    return False


def sanitize_pptx(src: Path, dst: Path) -> None:
    with zipfile.ZipFile(src, "r") as zf:
        kept_parts = collect_template_closure(zf)
        pres_xml, pres_rels, _layout_target, slide_xml, slide_rels = clean_presentation(zf)
        content_types = clean_content_types(zf, kept_parts)
        root_rels = clean_root_rels(zf)

        dst.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED) as out:
            written: set[str] = set()
            for name in zf.namelist():
                if not is_safe_to_copy(name, kept_parts):
                    continue
                data = zf.read(name)
                if name == "[Content_Types].xml":
                    data = content_types
                elif name == "_rels/.rels":
                    data = root_rels
                elif name == "ppt/presentation.xml":
                    data = pres_xml
                elif name == "ppt/_rels/presentation.xml.rels":
                    data = pres_rels
                out.writestr(name, data)
                written.add(name)
            if "ppt/slides/slide1.xml" not in written:
                out.writestr("ppt/slides/slide1.xml", slide_xml)
            out.writestr("ppt/slides/_rels/slide1.xml.rels", slide_rels)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", type=Path)
    parser.add_argument("dst", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sanitize_pptx(args.src, args.dst)
    print(f"Wrote sanitized master-only PPTX: {args.dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
