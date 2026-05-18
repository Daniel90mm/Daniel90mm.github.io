# Project registry contract

Draft of the expected `projects.json` fields used by the tagger, idea-capture,
and matchmaker to reference known projects.

## File location

`$FLIGHTRECORDER_HOME/projects.json`

## Shape

```json
[
  {
    "name": "Pulse Oximeter",
    "ref": "pulse-oximeter",
    "path": "~/Documents/Projekter/pulse-oximeter",
    "description": "DTU thesis project: a reflectance pulse oximeter with wireless logging.",
    "active": true
  }
]
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Human-readable project display name |
| `ref` | string | yes | Slug/kebab reference, matches document filenames |
| `path` | string | no | Laptop-side project path, used by `fr-sync-projects` |
| `description` | string | no | Short project summary for matchmaker context |
| `active` | bool | no | Whether the project is currently active (default true) |
| `last_synced` | iso8601 | no | Timestamp of last `fr-sync-projects` run |

## Open questions

- Should the `path` field be stored on pa-server for future implementation-marking
  automation (detecting commits that reference idea IDs)?
- Should `projects.json` include a per-project matchmaker summary or is the
  full project document always provided as context?
- Should `last_synced` be a column on the project object or a separate top-level
  field for the whole registry file?

## Not implemented

The `projects.json` format is a draft. The registry API endpoint, sync script,
and matchmaker integration have not been built.
