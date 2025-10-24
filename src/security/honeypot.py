"""
src/security/honeypot.py

Lightweight honeypot / alerting module.

Functions:
- alert_on_suspicious(query, params, score, warn_only=False)

This module intentionally keeps alerts simple (write to a log file and optionally
simulate honeypot DB population). In a production system you'd wire this to:
- persistent audit log, ELK/Graylog, Splunk, or alerting (PagerDuty/email/webhook)
- a real honeypot DB instance with controlled fake data
"""

import logging
import os
import json
import datetime

logger = logging.getLogger("honeypot")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s honeypot: %(message)s"))
    logger.addHandler(ch)

# file to append alerts to (relative to project)
_ALERT_FILE = os.environ.get("HONEYPOT_ALERT_FILE", "honeypot_alerts.log")


def _append_alert(record: dict):
    try:
        with open(_ALERT_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")
    except Exception:
        logger.exception("Failed to write honeypot alert file")


def alert_on_suspicious(query: str, params: object = None, score: float = 1.0, warn_only: bool = False):
    """
    Called when db_proxy detects suspicious activity.
    - query: raw SQL text
    - params: parameters (may be None)
    - score: risk score 0..1
    - warn_only: if True, do not escalate beyond logging
    """
    rec = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "score": float(score),
        "query": str(query)[:2000],
        "params_summary": _summarize_params(params),
        "warn_only": bool(warn_only),
    }
    # write to file
    _append_alert(rec)
    # also log
    if warn_only:
        logger.warning("Suspicious query logged (warn_only): score=%.3f query=%s", score, _short(query))
    else:
        logger.error("Suspicious query ALERT: score=%.3f query=%s", score, _short(query))

    # TODO: trigger external alert (webhook/pagerduty) for high scores if desired


def _short(x, n=160):
    try:
        s = str(x)
        return (s[:n] + "...") if len(s) > n else s
    except Exception:
        return "<non-string>"


def _summarize_params(params):
    try:
        if params is None:
            return None
        if isinstance(params, (list, tuple)):
            return [type(x).__name__ for x in params][:10]
        return type(params).__name__
    except Exception:
        return "params_unknown"
