#!/usr/bin/env python3
"""
MahalaOS Device Registration Client
Handles the optional, anonymous device registration POST to register.mahalaos.org.
Registration is fire-and-forget — failure is silent and non-blocking.
Result stored at /var/lib/mahalaos/registration-status
"""

import json
import logging
import os
import urllib.request
import urllib.error
from device_uuid import get_device_uuid

REGISTRATION_URL = "https://register.mahalaos.org/v1/device"
STATUS_PATH = "/var/lib/mahalaos/registration-status"
TIMEOUT_SECONDS = 10

logger = logging.getLogger(__name__)


def _write_status(status: str):
    """Persist registration status: 'registered', 'skipped', or 'failed'."""
    try:
        os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
        with open(STATUS_PATH, "w") as f:
            f.write(status)
    except Exception as e:
        logger.warning(f"Could not write registration status: {e}")


def get_registration_status() -> str | None:
    """Return current registration status, or None if not yet attempted."""
    try:
        if os.path.exists(STATUS_PATH):
            with open(STATUS_PATH) as f:
                return f.read().strip()
    except Exception:
        pass
    return None


def skip_registration():
    """User opted out — record skipped status."""
    _write_status("skipped")
    logger.info("Device registration skipped by user")


def register_device() -> bool:
    """
    Submit anonymous device registration.
    Returns True on success, False on failure.
    Non-blocking — caller should not depend on return value for flow control.
    """
    device_uuid = get_device_uuid()

    payload = json.dumps({
        "device_id": device_uuid,
        "os": "mahalaos",
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            REGISTRATION_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "MahalaOS-Registration/1.0",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            if response.status in (200, 201, 204):
                _write_status("registered")
                logger.info(f"Device registered successfully (UUID: {device_uuid})")
                return True
            else:
                _write_status("failed")
                logger.warning(f"Registration returned unexpected status: {response.status}")
                return False

    except urllib.error.URLError as e:
        _write_status("failed")
        logger.warning(f"Registration request failed: {e}")
        return False
    except Exception as e:
        _write_status("failed")
        logger.warning(f"Unexpected registration error: {e}")
        return False


if __name__ == "__main__":
    status = get_registration_status()
    if status == "skipped":
        print("Registration previously skipped.")
    elif status == "registered":
        print(f"Already registered. UUID: {get_device_uuid()}")
    else:
        print("Attempting registration...")
        success = register_device()
        print("Success" if success else "Failed — will retry next opportunity")
