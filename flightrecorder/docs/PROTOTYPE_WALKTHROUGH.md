# Prototype walkthrough

No API keys required. Start here to exercise the full dogfood loop locally.

## 1. Start the prototype

```sh
cd flightrecorder
scripts/dev-prototype.sh
```

This uses `config.prototype.toml` and `pricing.prototype.toml` with a
deterministic local provider that responds without network calls.

## 2. Open the browser

Navigate to `http://127.0.0.1:8000/`.

## 3. Verify runtime readiness

The runtime panel at the top shows whether `brainstorm` and `idea_capture`
are configured. With the prototype config, both should read `ok`.

## 4. Create a session

Fill in provider (default `anthropic`), model (default `claude-sonnet-4-5`),
and an optional slug. Click **Create Session**.

## 5. Chat

Select the session from the list, type a message, and click **Send**. The
assistant streams its response in the transcript area.

## 6. Extract ideas

Click **Extract Ideas**. The deterministic prototype provider generates one
project append and one spaghetti idea.

## 7. Inspect results

After extraction, the **Documents** and **Spaghetti** panels populate
automatically. The first project document and first spaghetti idea load
their markdown bodies for inspection.

## 8. Check budget and calls

The **Budget** panel shows current spend against thresholds (zero-cost for
the prototype). The **Calls** panel lists the provider calls that were logged
during chat and extraction.
