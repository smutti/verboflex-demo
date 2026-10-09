#!/usr/bin/env python3
"""Validate the demo contract; optionally use the actual VerboFlex parsers.

No network, third-party packages, credentials, or repository writes are needed.
The .strings reader deliberately accepts this fixture's JSON-quoted subset only.
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate key: {key}")
        result[key] = value
    return result


def scalar_values(path, fmt):
    content = path.read_text(encoding="utf-8")
    if fmt == "json":
        return json.loads(content, object_pairs_hook=unique_pairs)
    if fmt == "ios_strings":
        decoder = json.JSONDecoder()
        pairs = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("/*") and line.endswith("*/"):
                continue
            key, end = decoder.raw_decode(line)
            tail = line[end:].strip()
            if not tail.startswith("="):
                raise ValueError(f"Missing assignment in {path}")
            tail = tail[1:].strip()
            value, end = decoder.raw_decode(tail)
            if tail[end:].strip() != ";":
                raise ValueError(f"Missing terminator in {path}")
            pairs.append((key, value))
        return unique_pairs(pairs)
    tree = ET.fromstring(content)
    if fmt == "android_xml":
        return unique_pairs(
            (s.attrib["name"], "".join(s.itertext())) for s in tree.findall("string")
        )
    return unique_pairs(
        (s.attrib["id"], s.findtext("translation") or "")
        for s in tree.findall("./context/message")
        if s.get("numerus") != "yes"
    )


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(verboflex_root=None):
    manifest = json.loads((ROOT / "demo.json").read_text())
    require(
        len(manifest["files"]) == 16, "Expected four catalogs in each of four formats"
    )
    allowed_files = {item["path"] for item in manifest["files"]}
    discovered = {
        str(p.relative_to(ROOT))
        for product in manifest["products"]
        for p in (ROOT / product["root"]).rglob("*")
        if p.is_file()
    }
    require(discovered == allowed_files, "Catalog file inventory changed")
    total = 0
    for product in manifest["products"]:
        files = [f for f in manifest["files"] if f["format"] == product["format"]]
        values = {
            f["language"]: scalar_values(ROOT / f["path"], f["format"]) for f in files
        }
        require(set(values) == set(manifest["languages"]), "Language inventory changed")
        base = values["en"]
        require(len(base) == 24, "Expected 24 base scalar keys")
        for item in files:
            lang = item["language"]
            current = values[lang]
            require(
                len(current) == item["scalar_count"],
                f"Scalar count changed: {item['path']}",
            )
            require(
                set(base) - set(current) == set(manifest["missing_keys"][lang]),
                f"Missing-key scenario changed: {lang}",
            )
            require(not set(current) - set(base), "Unexpected target-only keys")
            require(
                all(isinstance(v, str) for v in current.values()),
                "Only scalar strings supported here",
            )
            require(all(v for v in base.values()), "Base strings must be populated")
            total += len(current)
            for key, target in current.items():
                if not target:
                    continue
                pattern = r"\{\w+\}|%\d+\$[sd]|%ld|%@|%\d+"
                require(
                    sorted(re.findall(pattern, base[key]))
                    == sorted(re.findall(pattern, target)),
                    f"Placeholder mismatch: {item['path']}/{key}",
                )
        require(
            all(values["it"][k] == "" for k in manifest["empty_it_keys"]),
            "Italian empty-field scenarios changed",
        )
        require(
            base["save_profile"] == base["save_changes"], "Exact reuse scenario changed"
        )
        require(
            values["it"]["save_changes"] == "Salva modifiche",
            "Exact reuse target changed",
        )
        require(
            base["save_profile_changes"] == "Save profile changes",
            "Fuzzy reuse source changed",
        )
        require(
            len(values["it"]["settings_button"]) > 8, "Length-warning scenario changed"
        )
        require(
            "workspace" in values["it"]["create_workspace"],
            "Glossary warning scenario changed",
        )
        for item in files:
            if item["format"] == "android_xml":
                tree = ET.parse(ROOT / item["path"])
                expected = {
                    "en": {"one", "other"},
                    "it": {"one", "many", "other"},
                    "vi": {"other"},
                    "ar": {"zero", "one", "two", "few", "many", "other"},
                }[item["language"]]
                families = tree.findall("plurals")
                require(len(families) == 2, "Expected two Android plural families")
                for plural in families:
                    actual = [i.attrib["quantity"] for i in plural.findall("item")]
                    required = expected - (
                        {"zero", "two"}
                        if item["language"] == "ar"
                        and plural.attrib["name"] == "uploads_pending"
                        else set()
                    )
                    require(
                        len(actual) == len(set(actual)) and set(actual) == required,
                        "Android plural scenario changed",
                    )
            if item["format"] == "qt_ts":
                tree = ET.parse(ROOT / item["path"])
                families = tree.findall('./context/message[@numerus="yes"]')
                require(len(families) == 2, "Expected two Qt plural families")
                for family in families:
                    forms = family.findall("./translation/numerusform")
                    require(
                        len(forms)
                        == {"en": 2, "it": 2, "vi": 1, "ar": 6}[item["language"]],
                        "Qt form order/count changed",
                    )
                    for index, form in enumerate(forms):
                        empty = (
                            item["language"] == "ar"
                            and family.get("id") == "uploads_pending"
                            and index == 0
                        )
                        require(
                            (not form.text) if empty else "%n" in (form.text or ""),
                            "Qt plural content changed",
                        )
    print(
        f"PASS: 16 catalogs, 4 formats, 4 languages, {total} scalar values; demo scenarios intact."
    )
    if verboflex_root:
        sys.path.insert(0, str(Path(verboflex_root).resolve() / "backend/src"))
        from verboflex.localization.importing.registry import parse_canonical_mapping
        from verboflex.localization.preview.registry import detect_preview_layouts
        from verboflex.services.import_jobs import confirmed_file_parser_input
        from verboflex.services.repository_discovery import RepositorySourceFile

        for product in manifest["products"]:
            files = tuple(
                RepositorySourceFile(
                    path=f["path"], content=(ROOT / f["path"]).read_bytes()
                )
                for f in manifest["files"]
                if f["format"] == product["format"]
            )
            candidates = detect_preview_layouts(
                files, repository_side="direct"
            ).candidates
            require(
                len(candidates) == 1,
                f"Expected one exact preview layout: {product['slug']}",
            )
            inputs = tuple(
                confirmed_file_parser_input(
                    candidates,
                    repository_side="direct",
                    path=f.path,
                    content=f.content,
                    base_language="en",
                )
                for f in files
            )
            require(all(i is not None for i in inputs), "Unassigned file")
            parsed = parse_canonical_mapping(inputs)
            require(not parsed.issues, str(parsed.issues))
            require(
                {v.language for v in parsed.values} == set(manifest["languages"]),
                "Canonical locale mismatch",
            )
            print(
                f"PASS: VerboFlex {product['format']}: {len(parsed.values)} canonical values, layout {candidates[0].layout_identity}"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verboflex-root", type=Path)
    args = parser.parse_args()
    try:
        validate(args.verboflex_root)
    except (ValueError, ET.ParseError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
