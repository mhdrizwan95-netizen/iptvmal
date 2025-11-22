# GitHub-Hosted Indian IPTV Playlist & EPG (Educational)

## Project Description
This repository hosts a curated M3U playlist of free-to-air Indian TV channels for educational purposes. The playlist is designed to be used with any IPTV player that supports M3U and XMLTV formats. It integrates with a publicly available Electronic Program Guide (EPG) to provide channel information.

## Disclaimer
**This project is for educational purposes only.**
All content links are gathered from publicly available sources on the internet. This repository does not host any video content or streams. The maintainers are not responsible for the availability, legality, or content of the streams. If you are a copyright holder and believe your content is being linked to improperly, please contact the source of the stream or submit an issue/pull request to remove the link from this playlist.

## Channel List
The playlist includes a selection of Indian channels across various genres including:
- News
- Entertainment
- Movies
- Music
- Religious
- Regional (Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, etc.)

(Note: Channel availability depends on the source streams and may change over time.)

## Usage Instructions

### M3U Playlist URL
To use this playlist, enter the following URL into your IPTV player:
```
https://[Your-Username].github.io/[Your-Repo-Name]/india.m3u
```
*(Replace `[Your-Username]` and `[Your-Repo-Name]` with your actual GitHub username and repository name if you fork this, or use the raw link from this repo once deployed.)*

### EPG URL
The playlist is pre-configured to use the following EPG source:
```
https://avkb.short.gy/epg.xml.gz
```
Most players should automatically detect this from the playlist header. If your player requires a separate EPG URL, you can use the one above.

### Compatible Players
- **VLC Media Player** (PC/Mobile)
- **TiviMate** (Android TV)
- **IPTV Smarters**
- **OTT Navigator**
- **Kodi** (PVR IPTV Simple Client)

## Maintenance
The playlist is periodically checked for dead links.
- **Manual Testing:** We recommend testing links in VLC.
- **Automated Checks:** A GitHub Action workflow is set up to validate streams.

## Credits
- Channel links sourced from [iptv-org](https://github.com/iptv-org/iptv).
- EPG data provided by [mitthu786/tvepg](https://github.com/mitthu786/tvepg).
