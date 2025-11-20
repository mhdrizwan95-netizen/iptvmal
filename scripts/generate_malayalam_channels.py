"""Generate a Malayalam channel mapping file for iptv-org/epg.

The script downloads iptv-org guide and channel metadata, filters Malayalam
entries, and writes them to an XML file compatible with iptv-org/epg.
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, Mapping, Sequence
from urllib.request import urlopen

GUIDES_URL = "https://iptv-org.github.io/api/guides.json"
CHANNELS_URL = "https://iptv-org.github.io/api/channels.json"
MALAYALAM_CODES = {"ml", "mal"}


def fetch_json(url: str) -> Sequence[Mapping[str, object]]:
    """Return parsed JSON content from *url* using stdlib only."""

    with urlopen(url, timeout=30) as response:  # nosec: trusted iptv-org host
        return json.loads(response.read().decode("utf-8"))


def filter_malayalam_guides(guides: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    """Filter guides to Malayalam-language entries."""

    filtered: list[dict[str, object]] = []
    for guide in guides:
        lang = guide.get("lang")
        channel_id = guide.get("channel")
        if not channel_id or lang not in MALAYALAM_CODES:
            continue
        filtered.append(dict(guide))
    return filtered


def build_channels_xml(
    guides: Iterable[Mapping[str, object]],
    channels: Mapping[str, Mapping[str, object]],
) -> ET.Element:
    """Create the XML root element for Malayalam channels."""

    root = ET.Element("channels")
    seen_keys: set[tuple[str, str]] = set()

    for guide in guides:
        channel_id = str(guide.get("channel"))
        site = guide.get("site")
        site_id = guide.get("site_id")
        if not channel_id or not site or not site_id:
            # Skip malformed entries quietly; iptv-org data occasionally misses fields.
            continue

        key = (str(site), str(site_id))
        if key in seen_keys:
            continue
        seen_keys.add(key)

        channel_info = channels.get(channel_id, {})
        name = guide.get("site_name") or channel_info.get("name") or channel_id

        element = ET.SubElement(
            root,
            "channel",
            {
                "site": str(site),
                "lang": "ml",
                "xmltv_id": channel_id,
                "site_id": str(site_id),
            },
        )
        element.text = str(name)

    # Sort elements for deterministic output
    root[:] = sorted(root, key=lambda elem: (elem.text or "", elem.get("xmltv_id") or ""))
    return root


def write_xml(root: ET.Element, destination: Path) -> None:
    """Write the XML tree to *destination* with an XML declaration."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(root)
    tree.write(destination, encoding="utf-8", xml_declaration=True)


def generate(output_path: Path) -> None:
    guides = fetch_json(GUIDES_URL)
    channels_list = fetch_json(CHANNELS_URL)
    channels_by_id = {str(ch.get("id")): ch for ch in channels_list if "id" in ch}

    mal_guides = filter_malayalam_guides(guides)
    xml_root = build_channels_xml(mal_guides, channels_by_id)
    write_xml(xml_root, output_path)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Malayalam channels file for iptv-org/epg")
    parser.add_argument(
        "--output",
        default="malayalam.channels.xml",
        type=Path,
        help="Where to write the generated XML (default: malayalam.channels.xml)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    generate(args.output)
    print(f"Written {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
