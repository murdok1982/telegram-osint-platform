# -*- coding: utf-8 -*-
import os
import sys
import socket
import getpass
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def audit():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
    except Exception:
        hostname = "unknown"
        ip = "0.0.0.0"
    return {
        "usuario": getpass.getuser(),
        "hostname": hostname,
        "ip": ip,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def log_audit():
    info = audit()
    logger.info(f"HISPANSHIELD AUDIT | User: {info['usuario']} | Host: {info['hostname']} | IP: {info['ip']}")
    return info
