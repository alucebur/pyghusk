"""Constants used by pyghusk."""
from datetime import datetime
from pathlib import Path


# GitHub API url. If you are using GitHub Enterprise with a custom hostname,
# the format should be "https://{hostname}/api/v3" for using the API v3
# More information about API v3 in https://developer.github.com/v3/
GH_API_URL = "https://api.github.com"

# Logfile name format. Example: 2019_08_21_08_35_59
CURRENT_DATE = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

# How the program identifies itself (semantic versioning)
PROGRAM = "pyghusk"
VERSION = "0.1.0"

# Group used by the keyring if OAuth tokens are used
KEYRING_SYSTEM = f"{PROGRAM}:{GH_API_URL}"

# Directory used by the program to get configuration
PROGRAM_DIR = Path.home() / f".config/{PROGRAM}/"

# Directory with template documents (`/docs`, `.gitignore`, `/licenses`)
TEMPLATE_DIR = PROGRAM_DIR / "templates/"

# Logfile path
LOG_FILE = PROGRAM_DIR / f"logs/{CURRENT_DATE}.log"

# Current directory, used as default local project folder
CURRENT_DIR = Path.cwd()

# List of available licenses. Example: ['GPL', 'LGPL', 'MIT', 'UNLICENSE']
# There must be a folder for each license to use, with a license file inside
LICENSES = [
    folder.name for folder in Path(TEMPLATE_DIR / "licenses").iterdir()
]
