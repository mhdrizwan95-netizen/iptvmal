#!/usr/bin/env python3
"""Generate a channels file for iptv-org/epg without filtering.

The script fetches guide metadata from iptv-org and writes a channels XML file
compatible with the `iptv-org/epg` grabber. All available guide entries are
included; IPTV clients will map only the channels they use.
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import urlopen

GUIDES_URL = "https://iptv-org.github.io/api/guides.json"


def fetch_json(url: str):
    """Return parsed JSON content from *url* using the standard library."""

    with urlopen(url, timeout=30) as response:  # nosec: trusted iptv-org host
        return json.loads(response.read().decode("utf-8"))


def build_channels_xml(guides):
    """Create the XML root element with all available guide entries."""

    root = ET.Element("channels")
    seen: set[tuple[str, str, str]] = set()

    for guide in guides:
        channel_id = guide.get("channel")
        site = guide.get("site")
        site_id = guide.get("site_id")

        if not channel_id or not site or not site_id:
            continue

        key = (str(site), str(site_id), str(channel_id))
        if key in seen:
            continue
        seen.add(key)

        name = guide.get("site_name") or channel_id
        lang = guide.get("lang") or "en"

        element = ET.SubElement(
            root,
            "channel",
            {
                "site": str(site),
                "site_id": str(site_id),
                "xmltv_id": str(channel_id),
                "lang": str(lang),
            },
        )
        element.text = str(name)

    root[:] = sorted(
        root,
        key=lambda elem: (
            elem.get("site") or "",
            elem.get("site_id") or "",
            elem.get("xmltv_id") or "",
        ),
    )
    return root


def write_xml(root: ET.Element, destination: Path) -> None:
    """Write the XML tree to *destination* with an XML declaration."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(root)
    tree.write(destination, encoding="utf-8", xml_declaration=True)


def generate(output_path: Path) -> None:
    guides = fetch_json(GUIDES_URL)
    xml_root = build_channels_xml(guides)
    write_xml(xml_root, output_path)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an iptv-org/epg channels file from guide metadata",
    )
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
