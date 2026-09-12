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
| `--output <dir>` | Custom output directory |

## Colour

These files are GEOMETRY. Every themed icon below is written with the
placeholder fill `#808080` and recoloured on the way into each build
by `scripts/recolour_icons.py`, which resolves the icon's role through
`source/icons/<treatment>.json` onto a palette variable.

That is why one set of files serves every palette and every icon
treatment, and why adding a treatment never touches the network. If you
see the placeholder colour in a packed theme, the recolour step was
skipped.

| Role | Meaning |
|------|---------|
| `accent` | Primary actions, links |
| `default` | Default icons |
| `error` | Errors, disconnected |
| `info` | Info, help, statistics |
| `muted` | Disabled, stopped |
| `orange` | Force actions |
| `stalled` | Stalled transfers |
| `success` | Downloads complete, connected |
| `upload` | Uploads, seeding |
| `warning` | Warnings, queued items |

## Icon List

| qBittorrent Icon | Phosphor Icon | Color |
|------------------|---------------|-------|
| `application-exit` | sign-out | `error` |
| `application-rss` | rss | `orange` |
| `application-url` | link | `accent` |
| `browser-cookies` | cookie | `warning` |
| `chart-line` | chart-line | `info` |
| `checked-completed` | check-circle | `success` |
| `configure` | gear | `default` |
| `connected` | wifi-high | `success` |
| `dialog-warning` | warning | `warning` |
| `directory` | folder | `warning` |
| `disconnected` | wifi-slash | `error` |
| `download` | download | `success` |
| `downloading` | arrow-circle-down | `info` |
| `edit-clear` | trash | `error` |
| `edit-copy` | copy | `default` |
| `edit-find` | magnifying-glass | `upload` |
| `edit-rename` | pencil-simple | `default` |
| `error` | warning-circle | `error` |
| `fileicon` | file | `default` |
| `filter-active` | funnel | `success` |
| `filter-all` | list | `default` |
| `filter-inactive` | funnel-simple | `muted` |
| `filter-stalled` | hourglass | `warning` |
| `firewalled` | shield-warning | `error` |
| `folder-documents` | folder-open | `warning` |
| `folder-new` | folder-plus | `warning` |
| `folder-remote` | cloud | `accent` |
| `force-recheck` | arrows-clockwise | `orange` |
| `go-bottom` | arrow-line-down | `accent` |
| `go-down` | arrow-down | `accent` |
| `go-top` | arrow-line-up | `accent` |
| `go-up` | arrow-up | `accent` |
| `hash` | hash | `default` |
| `help-about` | info | `info` |
| `help-contents` | question | `info` |
| `insert-link` | link | `accent` |
| `ip-blocked` | prohibit | `error` |
| `list-add` | plus-circle | `success` |
| `list-remove` | minus-circle | `error` |
| `loading` | spinner | `muted` |
| `mail-inbox` | envelope | `accent` |
| `name` | tag | `default` |
| `network-connect` | globe | `info` |
| `network-server` | hard-drives | `default` |
| `object-locked` | lock | `warning` |
| `pause-session` | pause | `warning` |
| `paused` | pause-circle | `muted` |
| `peers` | users | `accent` |
| `peers-add` | user-plus | `success` |
| `peers-remove` | user-minus | `error` |
| `plugins` | puzzle-piece | `upload` |
| `preferences-advanced` | sliders | `upload` |
| `preferences-bittorrent` | share-network | `success` |
| `preferences-desktop` | monitor | `accent` |
| `preferences-webui` | browser | `info` |
| `queued` | clock | `warning` |
| `ratio` | scales | `info` |
| `reannounce` | megaphone | `orange` |
| `rss_read_article` | article | `muted` |
| `rss_unread_article` | article-medium | `orange` |
| `security-high` | shield-check | `success` |
| `security-low` | shield | `warning` |
| `set-location` | map-pin | `accent` |
| `slow` | traffic-cone | `warning` |
| `slow_off` | rabbit | `success` |
| `speedometer` | gauge | `warning` |
| `stalledDL` | arrow-down | `stalled` |
| `stalledUP` | arrow-up | `stalled` |
| `stopped` | stop-circle | `error` |
| `system-log-out` | sign-out | `error` |
| `tags` | tag | `accent` |
| `task-complete` | check | `success` |
| `task-reject` | x | `error` |
| `torrent-creator` | file-plus | `accent` |
| `torrent-magnet` | magnet | `upload` |
| `torrent-start` | play | `accent` |
| `torrent-start-forced` | fast-forward | `orange` |
| `torrent-stop` | stop | `error` |
| `tracker-error` | warning-octagon | `error` |
| `tracker-warning` | warning | `warning` |
| `trackerless` | globe-simple | `muted` |
| `trackers` | list-bullets | `default` |
| `upload` | upload | `upload` |
| `view-categories` | folders | `warning` |
| `view-preview` | eye | `info` |
| `view-refresh` | arrow-clockwise | `accent` |
| `view-statistics` | chart-bar | `info` |
| `wallet-open` | heart | `error` |

## Files

- `icon-manifest.json` - Machine-readable icon configuration
- `*.svg` - Individual icon files

---
*This file is auto-generated by `download_phosphor_icons.py`*
