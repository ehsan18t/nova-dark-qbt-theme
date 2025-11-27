# Nova Dark Icons

This folder contains the custom Phosphor icon set for the Nova Dark theme.

**Generated:** 88 icons using Phosphor Icons (weight: regular)

## Regenerating Icons

To regenerate all icons with the defined color palette:

```bash
cd src/nova-dark/scripts
python download_phosphor_icons.py
```

### Options

| Option | Description |
|--------|-------------|
| `--weight <w>` | Icon weight: thin, light, regular, bold, fill, duotone |
| `--mono` | Use single color for all icons |
| `--color <hex>` | Color for mono mode (default: #e0e0e0) |
| `--output <dir>` | Custom output directory |

## Color Palette

| Name | Color | Hex | Usage |
|------|-------|-----|-------|
| default | ![#b0b0b0](https://via.placeholder.com/16/b0b0b0/b0b0b0?text=+) | `#b0b0b0` | Default icons |
| accent | ![#4a9eff](https://via.placeholder.com/16/4a9eff/4a9eff?text=+) | `#4a9eff` | Primary actions, links |
| success | ![#4ade80](https://via.placeholder.com/16/4ade80/4ade80?text=+) | `#4ade80` | Downloads complete, connected |
| warning | ![#fbbf24](https://via.placeholder.com/16/fbbf24/fbbf24?text=+) | `#fbbf24` | Warnings, queued items |
| error | ![#f87171](https://via.placeholder.com/16/f87171/f87171?text=+) | `#f87171` | Errors, disconnected |
| upload | ![#c084fc](https://via.placeholder.com/16/c084fc/c084fc?text=+) | `#c084fc` | Uploads, seeding |
| info | ![#22d3ee](https://via.placeholder.com/16/22d3ee/22d3ee?text=+) | `#22d3ee` | Info, help, statistics |
| muted | ![#6b7280](https://via.placeholder.com/16/6b7280/6b7280?text=+) | `#6b7280` | Disabled, stopped |
| orange | ![#fb923c](https://via.placeholder.com/16/fb923c/fb923c?text=+) | `#fb923c` | Force actions |
| stalled | ![#8cb4b4](https://via.placeholder.com/16/8cb4b4/8cb4b4?text=+) | `#8cb4b4` | Stalled transfers |

## Icon List

| qBittorrent Icon | Phosphor Icon | Color |
|------------------|---------------|-------|
| `application-exit` | sign-out | error |
| `application-rss` | rss | orange |
| `application-url` | link | accent |
| `browser-cookies` | cookie | warning |
| `chart-line` | chart-line | info |
| `checked-completed` | check-circle | success |
| `configure` | gear | default |
| `connected` | wifi-high | success |
| `dialog-warning` | warning | warning |
| `directory` | folder | warning |
| `disconnected` | wifi-slash | error |
| `download` | download | success |
| `downloading` | arrow-circle-down | info |
| `edit-clear` | trash | error |
| `edit-copy` | copy | default |
| `edit-find` | magnifying-glass | upload |
| `edit-rename` | pencil-simple | default |
| `error` | warning-circle | error |
| `fileicon` | file | default |
| `filter-active` | funnel | success |
| `filter-all` | list | default |
| `filter-inactive` | funnel-simple | muted |
| `filter-stalled` | hourglass | warning |
| `firewalled` | shield-warning | error |
| `folder-documents` | folder-open | warning |
| `folder-new` | folder-plus | warning |
| `folder-remote` | cloud | accent |
| `force-recheck` | arrows-clockwise | orange |
| `go-bottom` | arrow-line-down | accent |
| `go-down` | arrow-down | accent |
| `go-top` | arrow-line-up | accent |
| `go-up` | arrow-up | accent |
| `hash` | hash | default |
| `help-about` | info | info |
| `help-contents` | question | info |
| `insert-link` | link | accent |
| `ip-blocked` | prohibit | error |
| `list-add` | plus-circle | success |
| `list-remove` | minus-circle | error |
| `loading` | spinner | muted |
| `mail-inbox` | envelope | accent |
| `name` | tag | default |
| `network-connect` | globe | info |
| `network-server` | hard-drives | default |
| `object-locked` | lock | warning |
| `pause-session` | pause | warning |
| `paused` | pause-circle | muted |
| `peers` | users | accent |
| `peers-add` | user-plus | success |
| `peers-remove` | user-minus | error |
| `plugins` | puzzle-piece | upload |
| `preferences-advanced` | sliders | upload |
| `preferences-bittorrent` | share-network | success |
| `preferences-desktop` | monitor | accent |
| `preferences-webui` | browser | info |
| `queued` | clock | warning |
| `ratio` | scales | info |
| `reannounce` | megaphone | orange |
| `rss_read_article` | article | muted |
| `rss_unread_article` | article-medium | orange |
| `security-high` | shield-check | success |
| `security-low` | shield | warning |
| `set-location` | map-pin | accent |
| `slow` | traffic-cone | warning |
| `slow_off` | rabbit | success |
| `speedometer` | gauge | warning |
| `stalledDL` | arrow-down | stalled |
| `stalledUP` | arrow-up | stalled |
| `stopped` | stop-circle | error |
| `system-log-out` | sign-out | error |
| `tags` | tag | accent |
| `task-complete` | check | success |
| `task-reject` | x | error |
| `torrent-creator` | file-plus | accent |
| `torrent-magnet` | magnet | upload |
| `torrent-start` | play | accent |
| `torrent-start-forced` | fast-forward | orange |
| `torrent-stop` | stop | error |
| `tracker-error` | warning-octagon | error |
| `tracker-warning` | warning | warning |
| `trackerless` | globe-simple | muted |
| `trackers` | list-bullets | default |
| `upload` | upload | upload |
| `view-categories` | folders | warning |
| `view-preview` | eye | info |
| `view-refresh` | arrow-clockwise | accent |
| `view-statistics` | chart-bar | info |
| `wallet-open` | heart | error |

## Files

- `icon-manifest.json` - Machine-readable icon configuration
- `*.svg` - Individual icon files

---
*This file is auto-generated by `download_phosphor_icons.py`*
