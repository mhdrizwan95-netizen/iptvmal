"""Generate a Malayalam channel mapping file for iptv-org/epg.

The script downloads iptv-org guide and channel metadata, filters Indian
Malayalam channels, and writes them to an XML file compatible with
iptv-org/epg.
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


def index_guides_by_channel(guides: Iterable[Mapping[str, object]]) -> dict[str, list[Mapping[str, object]]]:
    """Return a mapping of channel id to its guide entries."""

    by_channel: dict[str, list[Mapping[str, object]]] = {}
    for guide in guides:
        channel_id = guide.get("channel")
        if not channel_id:
            continue
        by_channel.setdefault(str(channel_id), []).append(guide)
    return by_channel


def filter_malayalam_channels(channels: Iterable[Mapping[str, object]]) -> list[Mapping[str, object]]:
    """Return channel entries marked as Indian and Malayalam."""

    filtered: list[Mapping[str, object]] = []
    for channel in channels:
        countries = channel.get("countries") or []
        languages = channel.get("languages") or []

        if "IN" not in countries:
            continue
        if not any(lang in MALAYALAM_CODES for lang in languages):
            continue

        filtered.append(channel)
    return filtered


def build_channels_xml(
    channels: Iterable[Mapping[str, object]],
    guides_by_channel: Mapping[str, Sequence[Mapping[str, object]]],
) -> ET.Element:
    """Create the XML root element for Malayalam channels."""

    root = ET.Element("channels")
    seen_keys: set[tuple[str, str]] = set()

    for channel in channels:
        channel_id = channel.get("id")
        if not channel_id:
            continue
        channel_guides = guides_by_channel.get(str(channel_id))
        if not channel_guides:
            continue

        for guide in channel_guides:
            site = guide.get("site")
            site_id = guide.get("site_id")
            if not site or not site_id:
                continue

            key = (str(site), str(site_id))
            if key in seen_keys:
                continue
            seen_keys.add(key)

            name = guide.get("site_name") or channel.get("name") or channel_id

            element = ET.SubElement(
                root,
                "channel",
                {
                    "site": str(site),
                    "lang": "ml",
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

    guides_by_channel = index_guides_by_channel(guides)
    malayalam_channels = filter_malayalam_channels(channels_list)
    xml_root = build_channels_xml(malayalam_channels, guides_by_channel)
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
