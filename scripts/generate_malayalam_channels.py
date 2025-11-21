#!/usr/bin/env python3
"""Generate channel definitions for Malayalam playlist entries only.

This script:
* Downloads the iptv-org Malayalam playlist (mal.m3u) and extracts all `tvg-id`
  values.
* Downloads `guides.json` and keeps only guide entries whose channel id is in
  that Malayalam playlist.
* Writes `malayalam.channels.xml` compatible with the iptv-org/epg grabber.

The result is a compact channels file limited to the playlist you actually use,
which speeds up `npm run grab` while staying fully compatible with IPTV
clients.
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from urllib.request import urlopen

GUIDES_URL = "https://iptv-org.github.io/api/guides.json"
MAL_PLAYLIST_URL = "https://iptv-org.github.io/iptv/languages/mal.m3u"


def fetch_json(url: str):
    with urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_text(url: str) -> str:
    with urlopen(url) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_tvg_ids_from_m3u(m3u_text: str) -> set[str]:
    tvg_ids: set[str] = set()
    for line in m3u_text.splitlines():
        line = line.strip()
        if not line.startswith("#EXTINF:"):
            continue
        marker = 'tvg-id="'
        idx = line.find(marker)
        if idx == -1:
            continue
        start = idx + len(marker)
        end = line.find('"', start)
        if end == -1:
            continue
        tvg_id = line[start:end].strip()
        if tvg_id:
            tvg_ids.add(tvg_id)
    return tvg_ids


def main(output_file: str = "malayalam.channels.xml") -> None:
    print("[INFO] Fetching Malayalam playlist...")
    m3u = fetch_text(MAL_PLAYLIST_URL)
    tvg_ids = extract_tvg_ids_from_m3u(m3u)
    print(f"[INFO] Found {len(tvg_ids)} tvg-id(s) in mal.m3u")

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

        # Only include channels that are actually in the Malayalam playlist
        if channel_id not in tvg_ids:
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
