"""checkout: a tiny Cloud Run service used as an AgentOps test target.

GET / prices a fixed basket with pricing.quote(). Every log line carries the
commit it was built from (GIT_SHA, set by the deploy workflow), so a failure in
Cloud Logging names the commit that introduced it.
"""
import json
import os
import sys
import traceback

from flask import Flask, jsonify

import pricing

GIT_SHA = os.environ.get("GIT_SHA", "unknown")
GIT_REPO = os.environ.get("GIT_REPO", "")
REVISION = os.environ.get("K_REVISION", "")

BASKET = [
    {"sku": "TEE-01", "price": 19.99, "qty": 2},
    {"sku": "MUG-07", "price": 12.50, "qty": 1},
]

app = Flask(__name__)


def log(severity, message, **fields):
    # Cloud Run turns one-line JSON on stdout into a structured log entry; the
    # special labels field becomes labels.git_sha on the entry itself.
    entry = {
        "severity": severity,
        "message": message,
        "git_sha": GIT_SHA,
        "git_repo": GIT_REPO,
        "revision": REVISION,
        "logging.googleapis.com/labels": {"git_sha": GIT_SHA},
        **fields,
    }
    print(json.dumps(entry), flush=True)


log("INFO", f"checkout starting: commit {GIT_SHA} from {GIT_REPO or 'unknown repo'}")


def _innermost_frame(exc):
    frame = traceback.extract_tb(exc.__traceback__)[-1]
    return f"{os.path.basename(frame.filename)}:{frame.lineno} in {frame.name}"


@app.get("/healthz")
def healthz():
    return "ok"


@app.get("/")
def checkout():
    try:
        quote = pricing.quote(BASKET)
    except Exception as e:  # noqa: BLE001 - every failure is a 500 for this demo
        where = _innermost_frame(e)
        log(
            "ERROR",
            f"checkout failed: {type(e).__name__}: {e} at {where} (commit {GIT_SHA[:7]})",
            error_type=type(e).__name__,
            error_location=where,
            stack_trace="".join(traceback.format_exception(*sys.exc_info())),
        )
        return jsonify(error="could not price basket"), 500
    return jsonify(status="ok", commit=GIT_SHA[:7], **quote)
