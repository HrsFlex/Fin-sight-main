"""Session persistence layer using SQLite."""
from __future__ import annotations
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("session_store")

_SQLITE_PATH: Optional[Path] = None


def _get_sqlite_path() -> Path:
    global _SQLITE_PATH
    if _SQLITE_PATH is None:
        from config import SQLITE_PATH
        _SQLITE_PATH = SQLITE_PATH
    return _SQLITE_PATH


def _get_conn():
    db_path = _get_sqlite_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema() -> None:
    conn = _get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS credit_sessions (
                session_id     TEXT PRIMARY KEY,
                company_name   TEXT,
                pipeline_step  INTEGER DEFAULT 0,
                company_data   TEXT,
                research_data  TEXT,
                scoring_data   TEXT,
                five_cs_data   TEXT,
                gst_data       TEXT,
                committee_data TEXT,
                swot_data      TEXT,
                cam_path       TEXT,
                created_at     TEXT DEFAULT (datetime('now')),
                updated_at     TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS credit_documents (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id     TEXT REFERENCES credit_sessions(session_id),
                filename       TEXT,
                doc_type       TEXT,
                extracted_data TEXT,
                confidence     REAL,
                uploaded_at    TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS credit_audit (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                action     TEXT,
                payload    TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)
        conn.commit()
    finally:
        conn.close()


def upsert_session(session_id: str, session_state: dict) -> None:
    conn = _get_conn()
    try:
        now = datetime.now(timezone.utc).isoformat()
        conn.execute("""
            INSERT INTO credit_sessions
                (session_id, company_name, pipeline_step, company_data, research_data,
                 scoring_data, five_cs_data, gst_data, committee_data, swot_data, cam_path,
                 created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(session_id) DO UPDATE SET
                company_name   = excluded.company_name,
                pipeline_step  = excluded.pipeline_step,
                company_data   = excluded.company_data,
                research_data  = excluded.research_data,
                scoring_data   = excluded.scoring_data,
                five_cs_data   = excluded.five_cs_data,
                gst_data       = excluded.gst_data,
                committee_data = excluded.committee_data,
                swot_data      = excluded.swot_data,
                cam_path       = excluded.cam_path,
                updated_at     = excluded.updated_at
        """, (
            session_id,
            session_state.get("company_data", {}).get("company_name", "") if session_state.get("company_data") else "",
            session_state.get("pipeline_step", 0),
            _dump(session_state.get("company_data")),
            _dump(session_state.get("research_results")),
            _dump(session_state.get("scoring")),
            _dump(session_state.get("five_cs")),
            _dump(session_state.get("gst_validation")),
            _dump(session_state.get("committee_verdict")),
            session_state.get("swot_analysis"),
            session_state.get("cam_path"),
            now, now,
        ))
        conn.commit()
    except Exception as e:
        logger.warning(f"upsert_session warning: {e}")
    finally:
        conn.close()


def load_session(session_id: str) -> Optional[dict]:
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM credit_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "company_data":      _load(row["company_data"]),
            "research_results":  _load(row["research_data"]),
            "scoring":           _load(row["scoring_data"]),
            "five_cs":           _load(row["five_cs_data"]),
            "gst_validation":    _load(row["gst_data"]),
            "committee_verdict": _load(row["committee_data"]),
            "swot_analysis":     row["swot_data"],
            "cam_path":          row["cam_path"],
            "pipeline_step":     row["pipeline_step"] or 0,
        }
    except Exception as e:
        logger.warning(f"load_session warning: {e}")
        return None
    finally:
        conn.close()


def insert_document(session_id: str, filename: str, doc_type: str,
                    extracted_data: dict, confidence: float = 0.0) -> None:
    conn = _get_conn()
    try:
        conn.execute("""
            INSERT INTO credit_documents (session_id, filename, doc_type, extracted_data, confidence)
            VALUES (?,?,?,?,?)
        """, (session_id, filename, doc_type, _dump(extracted_data), confidence))
        conn.commit()
    except Exception as e:
        logger.warning(f"insert_document warning: {e}")
    finally:
        conn.close()


def log_audit(session_id: str, action: str, payload: Any = None) -> None:
    conn = _get_conn()
    try:
        conn.execute("""
            INSERT INTO credit_audit (session_id, action, payload)
            VALUES (?,?,?)
        """, (session_id, action, _dump(payload)))
        conn.commit()
    except Exception as e:
        logger.warning(f"log_audit warning: {e}")
    finally:
        conn.close()


def _dump(obj: Any) -> Optional[str]:
    if obj is None:
        return None
    try:
        return json.dumps(obj, default=str)
    except Exception:
        return str(obj)


def _load(text: Optional[str]) -> Any:
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return text


try:
    init_schema()
except Exception as _e:
    logger.warning(f"Schema init skipped: {_e}")
