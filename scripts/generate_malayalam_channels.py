#!/usr/bin/env python3
"""Generate channel definitions for iptv-org Indian EPG entries.

This script downloads `guides.json`, keeps only guide entries whose channel ids
end with `.in` (iptv-org's convention for Indian channels), deduplicates them,
and writes a channels XML compatible with the iptv-org/epg grabber.

The resulting file ensures the grabber sees a non-empty, India-focused set of
channels while remaining compatible with any IPTV playlist that uses matching
`xmltv_id` values (e.g., the Malayalam playlist from iptv-org).
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from urllib.request import urlopen

GUIDES_URL = "https://iptv-org.github.io/api/guides.json"


def fetch_json(url: str):
    with urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main(output_file: str = "malayalam.channels.xml") -> None:
    print("[INFO] Fetching guides.json...")
    guides = fetch_json(GUIDES_URL)

    root = ET.Element("channels")
    seen = set()
    count = 0

    for guide in guides:
        channel_id = guide.get("channel")
        site = guide.get("site")
        site_id = guide.get("site_id")

        if not channel_id or not site or not site_id:
            continue

        # iptv-org uses `.in` suffix for Indian channels; keep only those
        if not channel_id.endswith(".in"):
            continue

        key = (site, site_id, channel_id)
        if key in seen:
            continue
        seen.add(key)

        name = guide.get("site_name") or channel_id
        lang = guide.get("lang") or "en"

        element = ET.SubElement(
            root,
            "channel",
            {
                "site": site,
                "site_id": site_id,
                "xmltv_id": channel_id,
                "lang": lang,
            },
        )
        element.text = name
        count += 1

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"[OK] Written {output_file} with {count} channel(s)")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "malayalam.channels.xml"
    main(out)
