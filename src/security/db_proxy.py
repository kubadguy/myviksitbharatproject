# src/security/db_proxy.py
"""
Transparent SQLite DB proxy wrapper.

How it works:
- Call install_sqlite_wrapper() early (before other modules call sqlite3.connect).
- It monkeypatches sqlite3.connect so returned connections produce wrapped cursors.
- WrappedCursor.execute()/executemany() run the injection detector.
  - If query is NOT suspicious -> executed on the real DB as normal.
  - If query IS suspicious -> the wrapper redirects execution to the honeypot DB
    (Settings.HONEYPOT_DB_PATH) and replaces the cursor so subsequent fetchall()
    or other cursor operations will operate on the honeypot results.
This achieves a transparent, "plug-in" security layer: client code calls
sqlite3.connect() and uses the API unchanged.
"""

from __future__ import annotations
import functools
import logging
import sqlite3 as _sqlite3
import threading
from typing import Any, Optional

# Import your project's settings and detector
try:
    from config.settings import Settings
except Exception:
    # Fallback defaults if Settings not available
    class Settings:
        HONEYPOT_DB_PATH = "honeypot_database.db"

try:
    from security.injection_detector import InjectionDetector
except Exception:
    # If the module isn't present yet, we provide a simple fallback detector.
    class InjectionDetector:
        def detect_sql_injection(self, query: str):
            return False, ""
        def score_sql_risk(self, query: str):
            return 0.0

logger = logging.getLogger("db_proxy")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[db_proxy] %(levelname)s: %(message)s"))
    logger.addHandler(ch)

_detector_lock = threading.Lock()
_detector: Optional[InjectionDetector] = None

def _get_detector() -> InjectionDetector:
    global _detector
    if _detector is None:
        with _detector_lock:
            if _detector is None:
                _detector = InjectionDetector()
    return _detector

def install_sqlite_wrapper():
    """
    Replace sqlite3.connect with a wrapper that returns a WrappedConnection.
    Call this before other modules call sqlite3.connect().
    """
    real_connect = _sqlite3.connect

    @functools.wraps(real_connect)
    def wrapped_connect(*args, **kwargs):
        # create a real sqlite connection
        real_conn = real_connect(*args, **kwargs)
        return WrappedConnection(real_conn, args, kwargs)

    _sqlite3.connect = wrapped_connect
    logger.info("Installed sqlite3 wrapper (transparent DB proxy)")

class WrappedConnection:
    def __init__(self, real_conn: _sqlite3.Connection, ctor_args, ctor_kwargs):
        self._real_conn = real_conn
        self._ctor_args = ctor_args
        self._ctor_kwargs = ctor_kwargs
        # track honeypot connection per-wrapped-connection if we redirect
        self._honeypot_conn: Optional[_sqlite3.Connection] = None

    def cursor(self, *args, **kwargs):
        real_cur = self._real_conn.cursor(*args, **kwargs)
        return WrappedCursor(real_cur, self)

    # Expose the most used connection methods transparently
    def commit(self):
        # commit real DB only
        return self._real_conn.commit()

    def rollback(self):
        return self._real_conn.rollback()

    def close(self):
        try:
            # close any honeypot connection first
            if self._honeypot_conn:
                try:
                    self._honeypot_conn.close()
                except Exception:
                    pass
                self._honeypot_conn = None
        finally:
            return self._real_conn.close()

    def __getattr__(self, name):
        return getattr(self._real_conn, name)

class WrappedCursor:
    def __init__(self, real_cursor: _sqlite3.Cursor, conn_wrapper: WrappedConnection):
        self._cur = real_cursor
        self._conn_wrapper = conn_wrapper
        self._is_on_honeypot = False
        self._honeypot_cursor: Optional[_sqlite3.Cursor] = None

    def execute(self, query: str, params: Any = None):
        """
        Intercept query; if suspicious, redirect to honeypot DB.
        """
        detector = _get_detector()
        try:
            # Prefer score if available
            score = 0.0
            if hasattr(detector, "score_sql_risk"):
                try:
                    score = float(detector.score_sql_risk(query))
                except Exception:
                    score = 0.0
            else:
                # fallback to boolean detect
                is_inj, _ = detector.detect_sql_injection(query)
                score = 1.0 if is_inj else 0.0
        except Exception as e:
            logger.exception("Injection detector failed; treating query as safe by default: %s", e)
            score = 0.0

        # Threshold: treat score >= 0.6 as suspicious (redirect to honeypot)
        suspicious = (score >= 0.6)
        if suspicious:
            logger.warning("Suspicious SQL detected (score=%.2f). Redirecting to honeypot: %s", score, _short(query))
            # Open honeypot connection lazily
            try:
                if not self._conn_wrapper._honeypot_conn:
                    self._conn_wrapper._honeypot_conn = _sqlite3.connect(Settings.HONEYPOT_DB_PATH)
                # create a real honeypot cursor and execute there
                self._honeypot_cursor = self._conn_wrapper._honeypot_conn.cursor()
                if params is None:
                    self._honeypot_cursor.execute(query)
                else:
                    self._honeypot_cursor.execute(query, params)
                self._is_on_honeypot = True
                # replace the 'active' cursor so subsequent fetchall() uses honeypot results
                self._cur = self._honeypot_cursor
                return None  # same as sqlite cursor.execute()
            except Exception as e:
                logger.exception("Honeypot execution failed, falling back to real DB: %s", e)
                # fall through to executing on real DB
                suspicious = False

        # Not suspicious (or fallback): execute on real DB cursor
        if params is None:
            return self._cur.execute(query)
        else:
            return self._cur.execute(query, params)

    def executemany(self, query: str, seq_of_params):
        detector = _get_detector()
        try:
            score = 0.0
            if hasattr(detector, "score_sql_risk"):
                try:
                    score = float(detector.score_sql_risk(query))
                except Exception:
                    score = 0.0
            else:
                is_inj, _ = detector.detect_sql_injection(query)
                score = 1.0 if is_inj else 0.0
        except Exception:
            score = 0.0

        suspicious = (score >= 0.6)
        if suspicious:
            logger.warning("Suspicious executemany (score=%.2f). Redirecting to honeypot: %s", score, _short(query))
            try:
                if not self._conn_wrapper._honeypot_conn:
                    self._conn_wrapper._honeypot_conn = _sqlite3.connect(Settings.HONEYPOT_DB_PATH)
                self._honeypot_cursor = self._conn_wrapper._honeypot_conn.cursor()
                return self._honeypot_cursor.executemany(query, seq_of_params)
            except Exception as e:
                logger.exception("Honeypot executemany failed; falling back to real DB: %s", e)

        return self._cur.executemany(query, seq_of_params)

    # Allow fetchall/fetchone/etc to work (they operate on self._cur)
    def fetchall(self):
        return self._cur.fetchall()

    def fetchone(self):
        return self._cur.fetchone()

    def fetchmany(self, size: int = None):
        if size is None:
            return self._cur.fetchmany()
        return self._cur.fetchmany(size)

    def close(self):
        try:
            if self._is_on_honeypot and self._honeypot_cursor:
                try:
                    self._honeypot_cursor.close()
                except Exception:
                    pass
                self._honeypot_cursor = None
                self._is_on_honeypot = False
        finally:
            return self._cur.close()

    def __getattr__(self, name):
        # delegate other attributes to active cursor
        return getattr(self._cur, name)

def _short(x, n=160):
    try:
        s = str(x)
        return (s[:n] + "...") if len(s) > n else s
    except Exception:
        return "<non-string>"
