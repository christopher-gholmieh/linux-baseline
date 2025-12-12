# Written by: Christopher Gholmieh
# Imports:

# Typing:
from typing import Any

# JSON:
import json


# Functions:
def json_file_to_dictionary(path: str) -> dict[str, Any]:
    with open(path, "r") as json_file:
        return json.load(json_file)

def set_difference(list_one: list[str], list_two: list[str]) -> tuple[set, set]:
    return set(list_two) - set(list_one), set(list_one) - set(list_two)


# Comparator:
class Comparator:
    # Initialization:
    def __init__(self, baseline_path: str, current_path: str) -> None:
        # Baseline:
        self.baseline = json_file_to_dictionary(baseline_path)

        # Current:
        self.current = json_file_to_dictionary(current_path)

    # Methods:
    def compare_packages(self) -> list[str]:
        # Variables (Assignment):
        # Baseline:
        baseline = self.baseline["packages"]

        # Current:
        current = self.current["packages"]

        # Appended & Removed:
        appended, removed = set_difference(baseline, current)

        # Issues:
        issues = []


        # Logic:
        for package in sorted(appended):
            issues.append(f"[PACKAGE +] Added package: {package}")
        
        for package in sorted(removed):
            issues.append(f"[PACKAGE -] Removed package: {package}")

        return issues

    def compare_services(self) -> list[str]:
        # Variables (Assignment):
        # Issues:
        issues = []

        # Logic:
        for state in ("enabled", "disabled", "masked"):
            # Variables (Assignment):
            # Baseline:
            baseline = set(self.baseline["services"].get(state, []))

            # Current:
            current = set(self.current["services"].get(state, []))

            # Gained:
            gained = current - baseline

            # Lost:
            lost = baseline - current


            # Logic:
            for service in sorted(gained):
                issues.append(f"[SERVICE] {service} is now {state}!")

            for service in sorted(lost):
                issues.append(f"[SERVICE] {service} no longer {state}!")

        return issues

    def compare_trees(self) -> list[str]:
        # Variables (Assignment):
        # Issues:
        issues = []

        # Baseline:
        baseline = {file["path"]: file for file in self.baseline["trees"]}

        # Current:
        current = {file["path"]: file for file in self.current["trees"]}


        # Logic:
        for path, baseline_recording in baseline.items():
            # Validation:
            if path not in current:
                # Message:
                issues.append(f"[FILE -] Missing file: {path}")

                # Logic:
                continue

            # Variables (Assignment):
            # Current:
            current_recording = current[path]

            # Logic:
            for key in ["mode", "owner", "group"]:
                if baseline_recording[key] != current_recording[key]:
                    issues.append(
                        # Message:
                        f"[FILE !] {path} {key} changed "
                        f"({baseline_recording[key]} → {current_recording[key]})"
                    )

        for path in current.keys() - baseline.keys():
            issues.append(f"[FILE +] New file: {path}")

        return issues

    def compare_fingerprints(self) -> list[str]:
        # Variables (Assignment):
        # Issues:
        issues = []

        # Baseline:
        baseline = {file["path"]: file["sha256"] for file in self.baseline["fingerprints"]}

        # Current:
        current = {file["path"]: file["sha256"] for file in self.current["fingerprints"]}


        # Logic:
        for path, baseline_hash in baseline.items():
            # Validation:
            if path not in current:
                # Message:
                issues.append(f"[HASH -] Missing critical file: {path}")

                # Logic:
                continue

            # Logic:
            if current[path] != baseline_hash:
                # Message:
                issues.append(f"[HASH] File modified: {path}")

        for path in current.keys() - baseline.keys():
            # Message:
            issues.append(f"[HASH  New fingerprinted file: {path}")

        # Issues:
        return issues

    def run(self) -> list[str]:
        # Variables (Assignment):
        # Issues:
        issues = []

        # Logic:
        issues.extend(self.compare_packages())
        issues.extend(self.compare_services())
        issues.extend(self.compare_trees())
        issues.extend(self.compare_fingerprints())

        # Issues:
        return issues