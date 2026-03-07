#!/usr/bin/env python3
"""
MahalaOS Device Registration Server
Minimal API to receive anonymous device registrations.
Stores only: device_id (hashed UUID), first_seen, last_seen, count.
No IP addresses, no personal data, no device fingerprints stored.

Deploy at: register.mahalaos.org
Requirements: flask, flask-limiter, sqlite3 (stdlib)
"""

import sqlite3
import logging
import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
DB_PATH = os.environ.get("MAHALA_DB_PATH", "/var/lib/mahalaos/registrations.db")

# Rate limit: 5 registrations per IP per hour — blocks spam, allows legitimate use
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per hour"],
    storage_uri="memory://",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                device_id   TEXT PRIMARY KEY,
                first_seen  TEXT NOT NULL,
                last_seen   TEXT NOT NULL,
                reg_count   INTEGER DEFAULT 1
            )
        """)
        conn.commit()
    logger.info("Database initialised")


@app.route("/v1/device", methods=["POST"])
@limiter.limit("5 per hour")
def register_device():
    """
    Accept anonymous device registration.
    Upserts on device_id — reflashes update last_seen, not insert duplicates.
    Stores nothing personally identifiable.
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    device_id = data.get("device_id", "").strip()

    # Basic validation — must look like a UUID
    if not device_id or len(device_id) != 36 or device_id.count("-") != 4:
        return jsonify({"error": "Invalid device_id"}), 400

    now = datetime.now(timezone.utc).isoformat()

    try:
        with get_db() as conn:
            existing = conn.execute(
                "SELECT device_id, reg_count FROM devices WHERE device_id = ?",
                (device_id,)
            ).fetchone()

            if existing:
                # Device already registered — update last_seen and bump count
                conn.execute(
                    "UPDATE devices SET last_seen = ?, reg_count = reg_count + 1 WHERE device_id = ?",
                    (now, device_id)
                )
                logger.info(f"Re-registration: {device_id[:8]}... (count: {existing['reg_count'] + 1})")
            else:
                # New device
                conn.execute(
                    "INSERT INTO devices (device_id, first_seen, last_seen, reg_count) VALUES (?, ?, ?, 1)",
                    (device_id, now, now)
                )
                logger.info(f"New registration: {device_id[:8]}...")

            conn.commit()

        return jsonify({"status": "ok"}), 200

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Server error"}), 500


@app.route("/v1/stats", methods=["GET"])
def stats():
    """
    Public endpoint — returns total unique device count only.
    Safe to expose: no device IDs, no timestamps returned.
    """
    try:
        with get_db() as conn:
            total = conn.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
        return jsonify({"registered_devices": total}), 200
    except sqlite3.Error as e:
        logger.error(f"Stats query failed: {e}")
        return jsonify({"error": "Server error"}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
