# Written by: Christopher Gholmieh
# Imports:

# Loguru:
from loguru import logger

# Argparse:
import argparse

# Source:
from source import (
    # Utilities:
    choose_comparison_file,

    # Comparator:
    Comparator,

    # Recorder:
    Recorder
)


# Variables (Assignment):
# Parser:
argument_parser: argparse.ArgumentParser = argparse.ArgumentParser()

# Action:
argument_parser.add_argument("action")

# Arguments:
arguments = argument_parser.parse_args()

# Action:
action: str = arguments.action.lower()


# Program:
if not action in ["compare", "record"]:
    logger.error("[!] The only valid actions are: compare | record!")

match action:
    # Compare:
    case "compare":
        # Variables (Assignment):
        # Comparator:
        comparator: Comparator = Comparator(
            baseline_path="./database/" + choose_comparison_file("Which file is the true baseline file?"),
            current_path="./database/"  + choose_comparison_file("Which file is the recording of your current system?")
        )

        # Issues:
        issues: list[str] = comparator.run()

        # Logic:
        if not issues:
            logger.info("[OK] No differences found.")
        else:
            for issue in issues:
                logger.warning(issue)

    # Record:
    case "record":
        # Variables (Assignment):
        # File:
        comparison_file: str = input("[+] What would you like to save the file as: ").strip()

        if len(comparison_file) == 0:
            # Message:
            logger.error("[!] Comparison file inputted is NULL!")

            # Logic:
            exit(1)

        comparison_file = f"./database/{comparison_file}"

        if not comparison_file.endswith(".json"):
            comparison_file += ".json"

        # Recorder:
        recorder: Recorder = Recorder(comparison_file)

        
        # Operation:
        recorder.record()