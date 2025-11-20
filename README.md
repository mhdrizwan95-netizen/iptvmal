# Malayalam EPG Helper

This repository provides a helper script to generate the Malayalam channel map
expected by the [`iptv-org/epg`](https://github.com/iptv-org/epg) grabber.

## Generate `malayalam.channels.xml`

1. Install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the generator:

   ```bash
   python scripts/generate_malayalam_channels.py --output malayalam.channels.xml
   ```

The script downloads channel and guide metadata from the iptv-org API, filters
Malayalam (`ml`/`mal`) entries, and writes an XML file compatible with
`iptv-org/epg`.

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
