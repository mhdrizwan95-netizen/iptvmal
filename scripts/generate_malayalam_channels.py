#!/usr/bin/env python3
"""Generate an iptv-org/epg channels file for Indian channels.

The script fetches iptv-org channel and guide metadata, filters to channels
based in India, and writes an XML file compatible with `iptv-org/epg` grabber
runs.
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import urlopen

GUIDES_URL = "https://iptv-org.github.io/api/guides.json"
CHANNELS_URL = "https://iptv-org.github.io/api/channels.json"


def fetch_json(url: str):
    """Return parsed JSON content from *url* using the standard library."""

    with urlopen(url, timeout=30) as response:  # nosec: trusted iptv-org host
        return json.loads(response.read().decode("utf-8"))


def build_channels_xml(channels, guides_by_id):
    """Create the XML root element for Indian channels with guides."""

    root = ET.Element("channels")

    for guide in guides_by_id:
        channel_id = guide.get("channel")
        if not channel_id:
            continue

        channel = channels.get(channel_id)
        if not channel:
            continue

        countries = channel.get("countries") or []
        if "IN" not in countries:
            continue

        site = guide.get("site")
        site_id = guide.get("site_id")
        if not site or not site_id:
            continue

        name = guide.get("site_name") or channel.get("name") or channel_id
        lang = guide.get("lang") or "en"

        element = ET.SubElement(
            root,
            "channel",
            {
                "site": str(site),
                "lang": str(lang),
                "xmltv_id": str(channel_id),
                "site_id": str(site_id),
            },
        )
        element.text = str(name)

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

    channels_by_id = {str(channel.get("id")): channel for channel in channels_list if channel.get("id")}
    xml_root = build_channels_xml(channels_by_id, guides)
    write_xml(xml_root, output_path)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Indian channel map for iptv-org/epg")
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
