#!/usr/bin/env python3
"""
MahalaOS Device UUID Generator
Generates a stable, anonymous UUID derived from hardware identifiers.
UUID is one-way hashed — cannot be reversed to identify device or user.
Stored at /var/lib/mahalaos/device-uuid after first generation.
"""

import hashlib
import uuid
import os
import subprocess
import logging

UUID_PATH = "/var/lib/mahalaos/device-uuid"
SALT = "mahalaos:"

logger = logging.getLogger(__name__)


def _get_mac_address() -> str | None:
    """Read the primary network interface MAC address."""
    try:
        # Try wlan0 first (most likely primary on a phone)
        for iface in ["wlan0", "eth0", "usb0"]:
            path = f"/sys/class/net/{iface}/address"
            if os.path.exists(path):
                with open(path) as f:
                    mac = f.read().strip()
                if mac and mac != "00:00:00:00:00:00":
                    return mac
    except Exception as e:
        logger.warning(f"Could not read MAC address: {e}")
    return None


def _get_machine_id() -> str | None:
    """Read /etc/machine-id — stable per install but resets on reflash."""
    try:
        with open("/etc/machine-id") as f:
            return f.read().strip()
    except Exception as e:
        logger.warning(f"Could not read machine-id: {e}")
    return None


def _get_cpu_serial() -> str | None:
    """Extract CPU/SoC serial from /proc/cpuinfo if available."""
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.lower().startswith("serial"):
                    parts = line.split(":")
                    if len(parts) == 2:
                        serial = parts[1].strip()
                        if serial and serial != "0000000000000000":
                            return serial
    except Exception as e:
        logger.warning(f"Could not read CPU serial: {e}")
    return None


def _derive_uuid(hardware_string: str) -> str:
    """
    Derive a UUID from a hardware string using SHA-256 with MahalaOS salt.
    Output is formatted as a standard UUID v4-style string.
    The salt prevents cross-referencing against other databases.
    """
    salted = SALT + hardware_string
    hash_bytes = hashlib.sha256(salted.encode()).digest()
    # Use first 16 bytes of hash to form a UUID
    derived = uuid.UUID(bytes=hash_bytes[:16])
    return str(derived)


def _generate_uuid() -> str:
    """
    Attempt to generate a hardware-derived UUID.
    Priority: MAC address > CPU serial > machine-id fallback.
    If nothing hardware-bound is available, falls back to random UUID
    (accepts duplicate risk on reflash in that edge case).
    """
    hardware_value = _get_mac_address() or _get_cpu_serial()

    if hardware_value:
        logger.info("Generating hardware-derived device UUID")
        return _derive_uuid(hardware_value)
    else:
        # Last resort: machine-id is reflash-volatile but better than nothing
        machine_id = _get_machine_id()
        if machine_id:
            logger.info("Falling back to machine-id for UUID derivation")
            return _derive_uuid(machine_id)
        else:
            # Truly nothing available — random UUID, accept duplicate risk
            logger.warning("No hardware identifiers found, generating random UUID")
            return str(uuid.uuid4())


def get_device_uuid() -> str:
    """
    Return the device UUID, generating and storing it if not already present.
    Idempotent — safe to call multiple times.
    """
    # Return cached UUID if it exists
    if os.path.exists(UUID_PATH):
        try:
            with open(UUID_PATH) as f:
                cached = f.read().strip()
            if cached:
                return cached
        except Exception as e:
            logger.warning(f"Could not read cached UUID: {e}")

    # Generate new UUID
    device_uuid = _generate_uuid()

    # Persist it
    try:
        os.makedirs(os.path.dirname(UUID_PATH), exist_ok=True)
        with open(UUID_PATH, "w") as f:
            f.write(device_uuid)
        logger.info(f"Device UUID stored at {UUID_PATH}")
    except Exception as e:
        logger.warning(f"Could not persist device UUID: {e}")

    return device_uuid


if __name__ == "__main__":
    print(get_device_uuid())
