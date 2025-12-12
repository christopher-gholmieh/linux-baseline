# Written by: Christopher Gholmieh
# Imports:

# Toolkit:
from prompt_toolkit.shortcuts import radiolist_dialog

# Loguru:
from loguru import logger

# OS:
import os


# Functions:
def choose_comparison_file(prompt) -> str:
    # Variables (Assignment):
    # Files:
    files: list[str] = os.listdir("database")

    # Result:
    result = radiolist_dialog(
        # Title:
        title="Comparison",

        # Text:
        text=prompt,

        # Values:
        values=[
            (file, file) for file in files
                if os.path.isfile(os.path.join("./database/", file)) and file != ".gitkeep"
        ]
    ).run()

    if result is None:
        # Message:
        logger.error("[!] No comparison file selected! Exiting!")

        # Logic:
        exit(1)
    
    # Logic:
    return result
