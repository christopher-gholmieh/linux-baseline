# Written by: Christopher Gholmieh
# Imports:

# Datetime:
from datetime import datetime

# Subprocess:
import subprocess

# Hashlib:
import hashlib

# Socket:
import socket

# Path:
from pathlib import Path

# JSON:
import json

# PWD:
import pwd

# GRP:
import grp


# Recorder:
class Recorder:
    # Initialization:
    def __init__(self, path: str) -> None:
        # Path:
        self.path = Path(path)

    # Methods:
    def query_packages(self) -> list[str]:
        # Variables (Assignment):
        # Result:
        result = subprocess.run(
            # Command:
            ["dpkg-query", "-f", "${binary:Package}\n", "-W"],

            # Output:
            capture_output=True,

            # Text:
            text=True,

            # Check:
            check=True
        )
        return sorted(result.stdout.splitlines())

    def query_services(self) -> dict[str, list[str]]:
        # Variables (Assignment):
        # Services:
        services = {
            # Enabled:
            "enabled": [],

            # Disabled:
            "disabled": [],

            # Masked:
            "masked": []
        }

        # Logic:
        try:
            # Variables (Assignment):
            # Result:
            result = subprocess.run(
                # Command:
                ["systemctl", "list-unit-files", "--type=service", "--no-pager"],

                # Output:
                capture_output=True,

                # Text:
                text=True,

                # Check:
                check=True
            )
        except subprocess.CalledProcessError:
            return services

        # Logic:
        for line in result.stdout.splitlines():
            # Variables (Assignment):
            # Line:
            line = line.strip()

            # Logic:
            if not line or line.startswith("UNIT FILE") or line.startswith("0 unit"):
                continue

            # Parts:
            parts = line.split()

            if len(parts) < 2:
                continue

            # Name & State:
            name, state = parts[0], parts[1]

            # Logic:
            if state in ["enabled", "enabled-runtime"]:
                services["enabled"].append(name)
            elif state == "masked":
                services["masked"].append(name)
            else:
                services["disabled"].append(name)

        # Logic:
        for key in services:
            services[key].sort()

        return services

    def query_trees(self, roots: list[str]) -> list[dict]:
        # Variables (Assignment):
        # Records:
        records = []

        # Logic:
        for root in roots:
            # Variables (Assignment):
            # Path:
            root_path = Path(root)

            if not root_path.exists():
                continue

            # Logic:
            for path in root_path.rglob("*"):
                # Validation:
                if not path.is_file():
                    continue

                # Logic:
                try:
                    # Variables (Assignment):
                    # Stat:
                    stat = path.stat()
                except (PermissionError, FileNotFoundError):
                    continue

                # Logic:
                try:
                    # Variables (Assignment):
                    # Owner:
                    owner = pwd.getpwuid(stat.st_uid).pw_name
                except KeyError:
                    # Variables (Assignment):
                    # Owner:
                    owner = str(stat.st_uid)

                # Logic:
                try:
                    # Variables (Assignment):
                    # Group:
                    group = grp.getgrgid(stat.st_gid).gr_name
                except KeyError:
                    # Variables (Assignment):
                    # Group:
                    group = str(stat.st_gid)

                # Logic:
                records.append({
                    # Path:
                    "path": str(path),

                    # Mode:
                    "mode": oct(stat.st_mode & 0o777),

                    # Owner:
                    "owner": owner,

                    # Group:
                    "group": group
                })

        # Logic:
        return sorted(records, key=lambda item: item["path"])

    def query_fingerprints(self, targets: list[str]) -> list[dict]:
        # Variables (Assignment):
        # Records:
        records = []

        # Logic:
        for path_string in targets:
            # Variables (Assignment):
            # Path:
            path = Path(path_string)

            if not path.exists() or not path.is_file():
                continue

            # Logic:
            try:
                # Variables (Assignment):
                # Data:
                data = path.read_bytes()
            except (PermissionError, FileNotFoundError):
                continue

            # Variables (Assignment):
            # Hash:
            sha256: str = hashlib.sha256(data).hexdigest()

            # Logic:
            records.append({
                # Path:
                "path": path_string,

                # Hash:
                "sha256": sha256
            })

        # Logic:
        return sorted(records, key=lambda x: x["path"])

    def record(self) -> None:
        # Variables (Assignment):
        # Data:
        data = {
            # Metadata:
            "metadata": {
                # Hostname:
                "hostname": socket.gethostname(),

                # Format:
                "recorded_at": datetime.utcnow().isoformat() + "Z"
            },

            # Packages:
            "packages": self.query_packages(),

            # Services:
            "services": self.query_services(),

            # Trees:
            "trees": self.query_trees([
                "/etc",
            ]),

            # Fingerprints:
            "fingerprints": self.query_fingerprints([
                "/etc/passwd",
                "/etc/shadow",
                "/etc/group",
                "/etc/sudoers",
                "/etc/ssh/sshd_config",
                "/etc/login.defs"
            ])
        }

        # Logic:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # JSON;
        with self.path.open("w") as json_file:
            json.dump(data, json_file, indent=4)
