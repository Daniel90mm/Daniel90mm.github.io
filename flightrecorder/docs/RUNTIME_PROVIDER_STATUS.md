# Runtime provider status API

Read-only endpoint for checking provider readiness without exposing secrets.

## Endpoint

`GET /api/runtime`

Returns safe runtime status the frontend can display before a user hits
chat or extract.

## Response 200

```json
{
    "runtime_home": "/data/data/com.termux/files/home/flightrecorder",
    "roles": {
        "brainstorm": {
            "provider": "anthropic",
            "model": "claude-sonnet-4-5",
            "configured": true,
            "issues": []
        },
        "idea_capture": {
            "provider": "anthropic",
            "model": "claude-haiku-4-5",
            "configured": true,
            "issues": []
        }
    }
}
```

- `runtime_home` (string): the resolved runtime home path from config.
- `roles` (object): one entry per configured role. Currently `brainstorm`
  and `idea_capture`.
- `roles.{name}.provider` (string): the provider name from config.
- `roles.{name}.model` (string): the model string from config.
- `roles.{name}.configured` (boolean): true if the role exists, uses an
  implemented provider, has a non-placeholder API key, and has a matching
  pricing entry.
  The `prototype` provider is the exception: it is local-only and does not
  require an API key.
- `roles.{name}.issues` (array of strings): empty when configured, otherwise
  machine-readable reasons such as `role_missing`, `provider_missing`,
  `api_key_missing`, `provider_not_implemented`, `pricing_missing`, or
  `pricing_provider_mismatch`.

## Status codes

| Code | Meaning |
|------|---------|
| 200 | Always succeeds (read-only, no runtime state required). |

## Security

This endpoint must never return:

- API keys or secret material of any kind.
- Full provider config objects.
- Environment variables.
- Database contents.
- `config.toml` file paths or raw content.

The frontend should treat `configured` as the gate for chat/extract and use
`issues` only to explain what needs to be fixed.
