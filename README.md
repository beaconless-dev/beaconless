# beaconless

A small, typed Python client for the [Beaconless API](https://beaconless-api.pages.dev/api-reference) —
a REST service for streaming telemetry ingest and retrieval. JSON over HTTPS,
bearer-token auth, cursor pagination, automatic retries.

- **Docs:** https://beaconless-api.pages.dev/api-reference
- **API reference:** auth, `GET /events`, `POST /ingest`, error codes

## Install

```bash
pip install beaconless
```

> Not yet on PyPI — install from source for now:
> `pip install git+https://github.com/beaconless-dev/beaconless`

## Quickstart

```python
from beaconless import Client

client = Client(api_key="sk_live_...")          # or set BEACONLESS_API_KEY

# list the most recent telemetry events for your project
for event in client.events(limit=50):
    print(event["ts"], event["kind"])

# push a batch of events
client.ingest([
    {"kind": "temp", "value": 4.1, "unit": "C"},
    {"kind": "door", "value": "open"},
])
```

Set your key in the environment and the constructor picks it up:

```bash
export BEACONLESS_API_KEY=sk_live_...
```

## Why

Most telemetry clients make you hand-roll pagination, retry/backoff, and
error handling around a bare `requests` call. `beaconless` wraps the
endpoints documented at
[beaconless-api.pages.dev](https://beaconless-api.pages.dev/api-reference)
so you get typed results, cursor pagination, and retries on `429`/`5xx`
out of the box.

## Error handling

The client raises `BeaconlessError` with the HTTP status and the API's
error body:

| Status | Meaning        |
|--------|----------------|
| `401`  | invalid key    |
| `422`  | schema error   |
| `429`  | rate limited (retried automatically) |

## License

MIT — see [LICENSE](LICENSE).
