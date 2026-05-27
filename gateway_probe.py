"""
Confirm the LLM gateway is reachable before doing real work.

Sends one trivial chat completion and reports the result. The point
is to fail fast and visibly if anything is misconfigured -- wrong
key, wrong base URL, network unreachable, wrong model id -- so the
operator finds out here rather than partway through a real run.

Reads configuration from the same environment variables as
`run_llm.py`, so if this script works, `run_llm.py` will too:

    export PROXY_API_KEY=<your gateway API key>
    export PROXY_BASE_URL=<the gateway URL>

Then:

    python gateway_probe.py

A success message means you're set. Any other outcome prints the
exception type and message, which is usually enough to tell whether
the problem is the key, the URL, the network, or the model id.
"""

import os
import sys

from openai import OpenAI


# Headers the gateway expects to identify the client. Kept in step
# with run_llm.py.
CLIENT_HEADERS = {
    "X-Client-Source": "anaconda-cli-dev",
    "X-Client-Version": "0.0.1",
}

# The model id used for the smoke test. Matches the default in
# run_llm.py so this script verifies the same path the bulk runs
# will use.
MODEL_ID = "us.anthropic.claude-opus-4-7"


def make_client() -> OpenAI:
    """Build the gateway client from environment configuration.

    Refuses to run if either required environment variable is
    missing, with a clear message rather than a confusing SDK
    error later.
    """
    key = os.environ.get("PROXY_API_KEY")
    if not key:
        raise SystemExit(
            "PROXY_API_KEY is not set; export it and re-run.",
        )
    base_url = os.environ.get("PROXY_BASE_URL")
    if not base_url:
        raise SystemExit(
            "PROXY_BASE_URL is not set; export it and re-run.",
        )
    return OpenAI(
        base_url=base_url,
        api_key=key,
        default_headers=CLIENT_HEADERS,
    )


def main() -> int:
    """Send one message and report what happened."""
    client = make_client()
    print(f"Model:  {MODEL_ID}")
    print("Sending a test message...")
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            max_tokens=64,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Reply with exactly: gateway is working."
                    ),
                },
            ],
        )
    except Exception as exc:
        # A bare except is deliberate: this is a diagnostic tool
        # and we want to surface whatever went wrong, not just the
        # subset of errors we anticipated.
        print(f"\nFAILED: {type(exc).__name__}: {exc}")
        return 1
    reply = completion.choices[0].message.content or ""
    print(f"\nReply: {reply.strip()!r}")
    usage = completion.usage
    print(
        f"Usage: {usage.prompt_tokens} in, "
        f"{usage.completion_tokens} out",
    )
    print("\nSuccess: the gateway is reachable and responding.")
    return 0


if __name__ == "__main__":
    sys.exit(main())