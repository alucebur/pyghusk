#!/usr/bin/env python3
"""Command-line script to create a new Python GitHub project in VSCode.

This script will:
- create a `readme.md` file in the local project folder
- copy template files to the local project folder
- create `/docs/index.md` and `/docs/_config.yml` files for GitHub pages
- set a new virtual environment with pipenv in the local project folder
- install the specified version of Python in the virtual environment
- install the chosen linter in the virtual environment
- create `settings.json` file for VSCode with linter and interpreter set
- initialise git in the local project folder
- commit all the content of the local project folder to the local repository
- create a public remote repository in GitHub
- push to the remote repository
- Enable GitHub pages in the remote repository
- Rebuild pages of the personal blog (`{USERNAME}`.github.io)

This script assumes you want to write Python code using Visual Studio Code,
and want to create a new public remote repository in GitHub platform. If you
use other tools, feel free to modify this script to your needs.

For some parameters that are likely to not change frequenly in between
projects there are some constants at the start of the script, so they don't
need to be specified every time the script is executed. Remember to configure
them to your needs.

If `--folder` option is not supplied, the current directory will be used as
the local project folder. If any other argument is missing, an interactive
prompt will ask the user.

In `LICENSES` directory there must be a folder for each license to be used,
whose name will identify the license. Inside each folder there must be a file
called `LICENSE` with the text of such license, unless it is the unlicense, in
which case both the file and the folder must be called `UNLICENSE`.

A token auth for GitHub can be set in an environment variable called `GitHub`.
For creating a personal access token, please refer to this article:
https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line

The script will ask for a GitHub password if `GitHub` environment variable is
not set. This password is not stored and it is only used to make requests to
the GitHub API under HTTPS.

The events happening during the execution of the script are logged in a log
file in the `LOG_FILE` directory.

Usage: pyghusk.py [-h] [-V] [-v] [-f FOLDER] [-n NAME]
                  [-d DESCRIPTION] [-l {`LICENSES`}]

Options:
-h, --help: show help message and exit.
-V, --version: show program's version number and exit.
-v, --verbose: set logging level to DEBUG.
-f FOLDER, --folder FOLDER: local project folder.
-n NAME, --name NAME: name for the remote repo.
-d DESCRIPTION, --description DESCRIPTION: description for the remote repo.
-l {LICENSES}, --license {LICENSES}: license to use for the project.

For executing the script, run it with `pipenv run` or `python3`.
Under GNU/Linux, you can make the script executable with `chmod +x pyghusk.py`.
"""
import argparse
import base64
import getpass
import json
import logging
import os
import re
import shutil
import subprocess
import unicodedata
from datetime import datetime
from pathlib import Path

import requests

# =====================================================================
# CONSTANTS USED IN THE SCRIPT THAT YOU SHOULD CONFIGURE             /
# ===================================================================

# Python version for the virtual environment
# You need to have it installed in your system
PYTHON_VERSION = "3.6"

# Linter to use with VSCode
LINTER = "flake8"

# Configure and activate GitHub pages
GH_PAGES = True

# Title for gh-pages (_config.yml)
DOCS_TITLE = "Alucebur Was Here"

# GitHub username
USERNAME = None

# GitHub pages configuration
# - `branch` can be either "master" or "gh-pages"
# - Usually `path` is "/", but when `branch` is "master" you can choose "/docs"
GH_PAGES_CONFIG = {
    "source": {
        "branch": "master",
        "path": "/docs",
    }
}

# =====================================================================
# CONSTANTS USED IN THE SCRIPT THAT YOU CAN SAFELY IGNORE            /
# ===================================================================

# GitHub API url. If you are using GitHub Enterprise with a custom hostname,
# the format should be "https://{hostname}/api/v3" for using the API v3
# More information about API v3 in https://developer.github.com/v3/
GH_API_URL = "https://api.github.com"

# Logfile name format. Example: 2019_08_21_08_35_59
CURRENT_DATE = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

# How the script identifies itself
SCRIPT_NAME = "pyghusk"
SCRIPT_VER = "0.0.1"

# Directory used by the script to save its logs
SCRIPT_DIR = Path.home() / f".config/{SCRIPT_NAME}/"

# Directory with template documents (`/docs`, `.gitignore`, `/licenses`)
TEMPLATE_DIR = SCRIPT_DIR / "templates/"

# Logfile path
LOG_FILE = SCRIPT_DIR / f"{CURRENT_DATE}.log"

# Current directory, used as default local project folder
CURRENT_DIR = Path.cwd()

# List of available licenses. Example: ['GPL', 'LGPL', 'MIT', 'UNLICENSE']
# There must be a folder for each license to use, with a license file inside
LICENSES = [
    folder.name for folder in Path(TEMPLATE_DIR / "licenses").iterdir()
]


# =====================================================================
# FUNCTIONS USED BY THE SCRIPT                                       /
# ===================================================================

def execute_subprocess(command: list, direct: str) -> bytes:
    """Execute subprocess and return output.

    :param command: list of command arguments.
    :param direct: working directory.
    :returns: output of the subprocess.

    >>> execute_subprocess(["python", "-V"], ".")  # doctest: +ELLIPSIS
    b'Python 3...'"""
    process = subprocess.check_output(
        command,
        cwd=direct,
        universal_newlines=True,
    )
    return process


def validate_name(name: str) -> str:
    """Return a valid repository name.

    :param name: string to validate.
    :returns: filtered string with only [a-z0-9_-] characters.

    >>> validate_name(" déjà  vu! ")
    'deja-vu'"""
    # Replace non-ascii characters by ascii characters if possible
    normalized_name = unicodedata.normalize("NFKD", name)
    normalized_name = normalized_name.encode("ascii", "ignore").decode()

    # Replace any character that doesn't match [a-zA-Z0-9_] by a space
    clean_name = re.sub(r"[^\w]", " ", normalized_name, flags=re.ASCII)

    # Strip and replace consecutive spaces by a hyphen
    split_name = "-".join(clean_name.split())

    # Turn all characters into lowercase
    validated_name = split_name.lower()

    return validated_name


def main(argv: argparse.Namespace):
    """Executes script.

    :param argv: object holding attributes parsed from command-line args."""
    # =====================================================================
    # SCRIPT GATHERS MISSING ARGUMENTS BELOW                             /
    # ===================================================================

    # TL;DR trap
    if USERNAME is None:
        print("\nBefore using the script, please take some time to read the "
              "documentation and configure the necessary constants.")
        exit()

    # Initialise logging
    # In verbose mode set level to DEBUG. If not, set level to INFO
    format = "%(asctime)-15s %(levelname)s: %(message)s"
    log_level = logging.DEBUG if argv.verbose else logging.INFO
    logging.basicConfig(
        format=format,
        level=log_level,
        filename=LOG_FILE,
    )

    # Path to the project directory
    if argv.folder:
        project_folder = Path(argv.folder)
    else:
        project_folder = CURRENT_DIR

    if project_folder.exists():
        logging.info(f"Local project directory will be `{project_folder}`")
    else:
        error = f"Error: directory `{project_folder}` doesn't exist."
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    # Path to the template directory
    if not TEMPLATE_DIR.exists():
        error = f"Error: directory `{TEMPLATE_DIR}` doesn't exist."
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    # Name for the remote repository
    if argv.name:
        repo_name = validate_name(argv.name)
        if not repo_name:
            error = "Repository name can't be empty."
            logging.critical(error)
            print(error)
            print("\nCancelling...")
            exit()

    else:
        while True:
            repo_name = input("\nRepository name (keep it short): ")
            repo_name = validate_name(repo_name)
            if repo_name:
                break
            else:
                error = " - Error: repository name can't be empty."
                logging.debug(error)
                print(error)

    logging.info(f"Repo name will be `{repo_name}`")

    # Description for the remote repository
    if argv.description:
        repo_description = argv.description

    else:
        repo_description = input("Repository description (optional): ")

    logging.info(f"Repo description will be `{repo_description}`")

    # License for the project
    if argv.license:
        project_license = argv.license

    else:
        while True:
            print(f"\nAvailable licenses: {', '.join(LICENSES)}")
            project_license = input(f"License for the project: ")
            project_license = project_license.upper()
            if project_license in LICENSES:
                break
            else:
                error = (f" - Error: `{project_license}` license is not "
                         "available.")
                logging.debug(error)
                print(error)

    logging.info(f"Project will be under `{project_license}` license")

    # Checking that everything is ok
    print(f"\n{'Repository name:':>25} {repo_name}")
    print(f"{'Repository description:':>25} {repo_description}")
    print(f"{'Project license:':>25} {project_license}")
    print(f"{'Project folder:':>25} {project_folder}")

    try:
        next(project_folder.iterdir())
    except StopIteration:
        pass  # Empty directory
    else:
        print("\n   *** WARNING: project folder is not empty!! ***")
        print("Make sure there is no confidential information inside")

    response = input("\nIs this info correct? (y/N): ").lower()
    if response not in ["y", "yes"]:
        logging.info("Script cancelled by the user.")
        print("\nCancelling...")
        exit()

    print("\nStarting...\n")

    # =====================================================================
    # SCRIPT STARTS DOING THINGS BELOW                                   /
    # ===================================================================

    # [Step-1] Build readme.md
    # ===================================================================
    readme_content = (
        f"<h2 align='center'>{repo_name}</h2>\n\n"
        f"{repo_description}.\n\n"
        "#### Table of contents:\n"
        "- [License](#license)\n\n"
        "---\n\n"
        "### License\n"
        f"This project is under the {project_license} license.\n\n"
        f"This file was generated by `{SCRIPT_NAME}/{SCRIPT_VER}` script."
    )

    try:
        with open(project_folder / "readme.md", "x") as f:
            f.write(readme_content)
    except FileExistsError:
        message = "A `readme.md` file was found. Skipping step."
    else:
        message = f"A `readme.md` file was created in `{project_folder}`."
    finally:
        logging.info(message)
        print(message)

    # [Step-2] Copy template files
    # ===================================================================
    if GH_PAGES:
        try:
            shutil.copytree(TEMPLATE_DIR / "docs", project_folder / "docs")
        except FileExistsError:
            logging.debug("A `/docs` folder was found. Skipping step.")
        else:
            logging.debug(f"A `/docs` folder was copied to "
                          "`{project_folder}`.")

    try:
        shutil.copy(TEMPLATE_DIR / ".gitignore", project_folder)
    except FileExistsError:
        logging.debug("A `.gitignore` file was found. Skipping step.")
    else:
        logging.debug(f"A `.gitignore` file was copied to `{project_folder}`.")

    # If a license file already exists, it will be overwritten
    license_file = "UNLICENSE" if project_license == "UNLICENSE" else "LICENSE"
    shutil.copy(TEMPLATE_DIR / f"licenses/{project_license}/{license_file}",
                project_folder)
    logging.debug(f"A `{project_license}` license file was copied to "
                  f"`{project_folder}`.")

    message = f"Template files were copied to `{project_folder}`."
    logging.info(message)
    print(message)

    # [Step-3] Build index.md and _config.yml files
    # ===================================================================
    if GH_PAGES:
        try:
            with open(project_folder / "docs/index.md", "x") as f:
                f.write(readme_content)
        except FileExistsError:
            message = "An `index.md` file was found. Skipping step."
        else:
            message = ("An `index.md` file was created in `/docs`.")
        finally:
            logging.info(message)
            print(message)

        config_content = (
            "theme: jekyll-theme-slate\n"
            f"title: {DOCS_TITLE}\n"
            f"description: {repo_description}\n"
            "show_downloads: ['true']"
        )

        try:
            with open(project_folder / "docs/_config.yml", "x") as f:
                f.write(config_content)
        except FileExistsError:
            message = "A `_config.yml` file was found. Skipping step."
        else:
            message = "A `_config.yml` file was created in `/docs`."
        finally:
            logging.info(message)
            print(message)

    # [Step-4] Create a virtual environment for the project
    # ===================================================================
    print("\nThis can take a while...")
    try:
        output = execute_subprocess(
            ["pipenv", "--python", f"{PYTHON_VERSION}"],
            project_folder,
        )

    except (OSError, subprocess.CalledProcessError) as e:
        error = f"Subprocess error: {e}"
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    else:
        message = f"Python {PYTHON_VERSION} virtual environment created."
        logging.info(message)
        print(message)

    # [Step-5] Install linter
    # ===================================================================
    print("\nThis can take a while...")
    try:
        output = execute_subprocess(
            ["pipenv", "install", LINTER, "--dev"],
            project_folder,
        )

    except (OSError, subprocess.CalledProcessError) as e:
        error = f"Subprocess error: {e}"
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    else:
        message = f"`{LINTER}` linter installed."
        logging.info(message)
        print(message)

    # [Step-6] Get the virtual environment path
    # ===================================================================
    try:
        output = execute_subprocess(
            ["pipenv", "--py"],
            project_folder,
        )

    except (OSError, subprocess.CalledProcessError) as e:
        error = f"Subprocess error: {e}"
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    else:
        interpreter = output.strip()
        logging.debug(f"Interpreter path: `{interpreter}`")

    # [Step-7] Building VSCode settings file
    # ===================================================================
    Path.mkdir(project_folder / ".vscode")
    settings = {
        "python.linting.enabled": True,
        f"python.linting.{LINTER}Enabled": True,
        "python.pythonPath": interpreter,
    }

    # Overwrite settings.json file just in case the interpreter path changed
    with open(project_folder / ".vscode/settings.json", "w") as f:
        json.dump(settings, f, indent=4)
    message = "A `settings.json` file was created in `/.vscode`."
    logging.info(message)
    print(f"\n{message}")

    # [Step-8] Initialise git in project directory
    # ===================================================================
    print("\nInitialising git...")
    try:
        output = execute_subprocess(
            ["git", "init"],
            project_folder,
        )

    except (OSError, subprocess.CalledProcessError) as e:
        error = f"Subprocess error: {e}"
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    else:
        message = output.strip()
        logging.info(message)
        print(message)

    # [Step-9] Add all not .gitignored files to the stage area
    # ===================================================================
    print("\nStaging files...")
    try:
        output = execute_subprocess(
            ["git", "add", "-A"],
            project_folder,
        )

    except (OSError, subprocess.CalledProcessError) as e:
        error = f"Subprocess error: {e}"
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    else:
        message = ("All not ignored files in project directory have been "
                   "staged.")
        logging.info(message)
        print(message)

    # [Step-10] Commit files to the local repository
    # ===================================================================
    print("\nCommiting files...")
    try:
        output = execute_subprocess(
            ["git", "commit", "-m", "initial commit", "-m",
             f"by `{SCRIPT_NAME}/{SCRIPT_VER}` script"],
            project_folder,
        )

    except (OSError, subprocess.CalledProcessError) as e:
        error = f"Subprocess error: {e}"
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    else:
        message = "Local commit completed."
        logging.info(message)
        logging.debug(f"Local commit output:\n{output}")
        print(message)

    # [Step-11] Authentication for GitHub API v3
    # ===================================================================
    password = os.getenv('GitHub')
    if password is None:
        while True:
            password = getpass.getpass(
                prompt="\nPlease enter your GitHub password: ")
            password_bis = getpass.getpass(
                prompt="Please re-enter your GitHub password: ")
            if password == password_bis:
                break
            else:
                error = " - Error: passwords do not match."
                logging.debug(error)
                print(error)

    # requests uses HTTPBasicAuth internally when auth is a tuple like this one
    # auth = (USERNAME, password)
    # But there is a bug in requests.auth.HTTPBasicAuth when using special
    # characters (issue #4649) so let's build the basic auth by ourselves
    bauth = f"{USERNAME}:{password}".encode()
    headers = {
        "User-Agent": f"{USERNAME} using {SCRIPT_NAME}/{SCRIPT_VER}",
        "Authorization": f"Basic {base64.b64encode(bauth).decode()}",
        "Accept": "application/vnd.github.v3+json",
    }

    # [Step-12] Create the remote repository in GitHub
    # ===================================================================
    print("Connecting to GitHub...")
    github_config = {
        "name": f"{repo_name}",
        "description": f"{repo_description}",
        "private": False,
        "has_projects": False,
    }

    url = GH_API_URL + "/user/repos"
    response = requests.post(url, json=github_config, headers=headers)
    if 200 <= response.status_code < 300:  # Usually 201
        repo_final_name = json.loads(response.text)['full_name']
        message = f"Remote repository {repo_final_name} created."
        logging.info(message)
        logging.debug(response.text)
        print(message)

    else:
        error = (f"Error {response.status_code}. API request failed when "
                 "creating the remote repository.")
        logging.critical(error)
        logging.debug(response.text)
        print(error)
        print("\nCancelling...")
        exit()

    # [Step-13] Add a remote pointing to GitHub repository
    # ===================================================================
    remote_repo = f"https://github.com/{repo_final_name}"
    try:
        output = execute_subprocess(
            ["git", "remote", "add", "origin", f"{remote_repo}.git"],
            project_folder,
        )

    except (OSError, subprocess.CalledProcessError) as e:
        error = f"Subprocess error: {e}"
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    else:
        logging.info("Remote repository added.")

    # [Step-14] Push local commit to remote repository
    # ===================================================================
    try:
        output = execute_subprocess(
            ["git", "push", "-u", "origin", "master"],
            project_folder,
        )

    except (OSError, subprocess.CalledProcessError) as e:
        error = f"Subprocess error: {e}"
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    else:
        message = "Push to remote repository completed."
        logging.info(message)
        logging.debug(output)
        print(message)

    # [Step-15] Enable GitHub pages
    # ===================================================================
    # Warning: The Pages API is being tested and may change in the future
    # We need a custom media type to access the endpoint during the preview
    if GH_PAGES:
        url = GH_API_URL + f"/repos/{repo_final_name}/pages"
        headers["Accept"] = "application/vnd.github.switcheroo-preview+json"

        response = requests.post(url, json=GH_PAGES_CONFIG, headers=headers)
        if 200 <= response.status_code < 300:  # Usually 201
            message = f"GitHub pages enabled in {repo_final_name}."
            logging.info(message)
            logging.debug(response.text)
            print(message)

        else:
            error = (f"Error {response.status_code}. API request failed when "
                     "enabling gh-pages.")
            logging.critical(error)
            logging.debug(response.text)
            print(error)
            print("\nCancelling...")
            exit()

    # [Step-16] Request page build to include the new project in personal blog
    # ===================================================================
    # We need a custom media type to access the endpoint during the preview
    if GH_PAGES:
        blog_repo = f"{USERNAME}.github.io"
        url = GH_API_URL + f"/repos/{USERNAME}/{blog_repo}/pages/builds"
        headers["Accept"] = ("application/vnd.github.mister-fantastic-"
                             "preview+json")

        response = requests.post(url, headers=headers)
        if 200 <= response.status_code < 300:  # Usually 201
            message = f"Personal blog {blog_repo} pages rebuilt."
            logging.info(message)
            logging.debug(response.text)
            print(message)

        else:
            error = (f"Error {response.status_code}. API request failed when "
                     "rebuilding gh-pages.")
            logging.critical(error)
            logging.debug(response.text)
            print(error)
            print("\nCancelling...")
            exit()

    # [Feedback]
    # ===================================================================
    print(f"\nWork successfully finished!")
    print(f" - Check the log file at `{LOG_FILE}`")
    print(f" - Check the project files at `{project_folder}`")
    print(f" - Check the remote repository at `{remote_repo}`")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        prog=f"{SCRIPT_NAME}",
        description="Command-line program to create a new Python3 GitHub "
                    "project in VSCode.",
        allow_abbrev=False,
    )

    parser.add_argument("-V", "--version", action="version",
                        version=f"%(prog)s {SCRIPT_VER}")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="set logging level to DEBUG")
    parser.add_argument("-f", "--folder",
                        help="local project folder (current directory by "
                             "default).")
    parser.add_argument("-n", "--name",
                        help="name for the remote repository")
    parser.add_argument("-d", "--description",
                        help="description for the remote repository")
    parser.add_argument("-l", "--license",
                        choices=LICENSES,
                        help="license to use for the project")

    args = parser.parse_args()
    main(args)
