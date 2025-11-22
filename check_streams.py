"""Utility script to validate IPTV stream URLs in an M3U playlist."""

import argparse
import concurrent.futures
import pathlib
import sys
from typing import Iterable, List, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def parse_m3u(file_path: pathlib.Path) -> List[str]:
    """Extract playable URLs from an M3U file.

    The parser looks for non-comment, non-empty lines because M3U playlists
    describe streams using `#EXTINF` metadata lines followed by the URL on the
    next line.
    """

    urls: List[str] = []
    with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            urls.append(stripped)
    return urls


def check_url(url: str, timeout: float) -> Tuple[str, bool, int]:
    """Issue a lightweight request to verify the stream is reachable."""

    request = Request(url, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            ok = status < 400
    except HTTPError as exc:
        status = exc.code
        ok = False
    except URLError:
        status = 0
        ok = False

    return url, ok, status if ok else 0


def check_urls(urls: Iterable[str], timeout: float, workers: int) -> Tuple[List[str], List[str]]:
    reachable: List[str] = []
    unreachable: List[str] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_url = {executor.submit(check_url, url, timeout): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url, ok, status = future.result()
            if ok:
                reachable.append(f"{url} (status {status})")
            else:
                unreachable.append(url)

    return reachable, unreachable


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "playlist",
        type=pathlib.Path,
        default=pathlib.Path("india.m3u"),
        nargs="?",
        help="Path to the M3U playlist to validate (default: india.m3u).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Request timeout in seconds for each stream (default: 5).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of concurrent requests (default: 10).",
    )
    return parser


def main(argv: List[str]) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if not args.playlist.exists():
        parser.error(f"Playlist file not found: {args.playlist}")

    urls = parse_m3u(args.playlist)
    if not urls:
        print("No stream URLs found in the playlist.")
        return 1

    print(f"Checking {len(urls)} stream URLs from {args.playlist} ...")
    reachable, unreachable = check_urls(urls, timeout=args.timeout, workers=args.workers)

    print(f"\nReachable streams: {len(reachable)}")
    for url in sorted(reachable):
        print(f"  ✓ {url}")

    print(f"\nUnreachable streams: {len(unreachable)}")
    for url in sorted(unreachable):
        print(f"  ✗ {url}")

    return 0 if not unreachable else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
