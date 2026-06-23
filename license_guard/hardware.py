import hashlib
import os
import platform


FINGERPRINT_ENV = "AIHUB_HARDWARE_FINGERPRINT"


def get_hardware_hash() -> str:
    fingerprint = os.getenv(FINGERPRINT_ENV)
    if not fingerprint:
        fingerprint = f"{platform.node()}|{platform.system()}|{platform.machine()}"
    digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"
