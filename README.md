# Malayalam EPG Helper

This repository provides a helper script to generate the channel map expected
by the [`iptv-org/epg`](https://github.com/iptv-org/epg) grabber.

## Generate `malayalam.channels.xml`

1. Run the generator (no external dependencies needed):

   ```bash
   python scripts/generate_malayalam_channels.py --output malayalam.channels.xml
   ```

The script downloads the iptv-org Malayalam playlist to collect all `tvg-id`
values, then filters `guides.json` to only those ids. The resulting XML keeps
only the channels that actually appear in the Malayalam playlist, which keeps
`npm run grab` fast while remaining fully compatible with IPTV clients.

## Grab the EPG

With `malayalam.channels.xml` generated, you can build the EPG file using
`iptv-org/epg`:

```bash
git clone https://github.com/iptv-org/epg.git
cd epg
npm install
cp /path/to/malayalam.channels.xml .
npm run grab --- --channels=malayalam.channels.xml --output=malayalam_epg.xml
```

`malayalam_epg.xml` can then be hosted anywhere that serves static files
(e.g., GitHub Raw URLs) for use in IPTV clients alongside the Malayalam
playlist from iptv-org: <https://iptv-org.github.io/iptv/languages/mal.m3u>.

## Automate with GitHub Actions

This repository includes a workflow that regenerates both
`malayalam.channels.xml` and `malayalam_epg.xml` daily (and on manual
trigger): `.github/workflows/generate-malayalam-epg.yml`.

The workflow:

1. Checks out this repository.
2. Runs `python scripts/generate_malayalam_channels.py --output malayalam.channels.xml`.
3. Clones `iptv-org/epg` and runs the grabber to produce `malayalam_epg.xml`.
4. Commits any changes back to the repository using the provided `GITHUB_TOKEN`.

After the first successful run, you can point IPTV clients at the generated
EPG file for this repository directly:

```
https://raw.githubusercontent.com/mhdrizwan95-netizen/iptvmal/main/malayalam_epg.xml
```

The playlist URL remains:

```
https://iptv-org.github.io/iptv/languages/mal.m3u
```
