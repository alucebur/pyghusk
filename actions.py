"""Functions for every step pyghusk executes."""
import base64
import getpass
import json
import logging
import shutil
from pathlib import Path, PurePath
from subprocess import CalledProcessError

import keyring
import requests

import consts
import helpers


def build_pages(username: str, headers: dict):
    """Request page build to include the new project in personal blog.

    :param username: GitHub username.
    :param headers: http request headers."""
    # We need a custom media type to access the endpoint during the preview
    blog_repo = f"{username}.github.io"
    url = consts.GH_API_URL + f"/repos/{username}/{blog_repo}/pages/builds"
    headers["Accept"] = ("application/vnd.github.mister-fantastic-"
                         "preview+json")

    response = requests.post(url, headers=headers)
    if 200 <= response.status_code < 300:  # Usually 201
        message = f"Personal blog `{blog_repo}` pages rebuilt."
        logging.info(message)
        logging.debug(f"Raw response:\n{response.text}")
        print(message)

    else:
        error = (f"Error {response.status_code}. API request failed when "
                 "rebuilding gh-pages.")
        logging.critical(error)
        print(error)
        server_message = json.loads(response.text)["message"]
        logging.critical(f"Error {response.status_code}: "
                         f"{response.reason} ({server_message})")
        logging.debug(f"Raw response:\n{response.text}")
        logging.debug(f"Response headers:\n{str(response.headers)}")
        print("\nCancelling...")
        exit()


def enable_pages(headers: dict, remote_path: str):
    """Enable GitHub pages in the remote repository.

    :param headers: http request headers.
    :param remote_path: remote repository path."""
    # Warning: The Pages API is being tested and may change in the future
    # We need a custom media type to access the endpoint during the preview
    url = consts.GH_API_URL + f"/repos/{remote_path}/pages"
    headers["Accept"] = "application/vnd.github.switcheroo-preview+json"

    # Set source for pages
    pages_config = {
        "source": {
            "branch": "master",
            "path": "/docs"
        }
    }

    response = requests.post(url, json=pages_config, headers=headers)
    if 200 <= response.status_code < 300:  # Usually 201
        message = f"GitHub pages enabled in {remote_path}."
        logging.info(message)
        logging.debug(f"Raw response:\n{response.text}")
        print(f"\n{message}")

    else:
        error = (f"Error {response.status_code}. API request failed when "
                 "enabling gh-pages.")
        logging.critical(error)
        print(f"\n{error}")
        server_message = json.loads(response.text)["message"]
        logging.critical(f"Error {response.status_code}: "
                         f"{response.reason} ({server_message})")
        logging.debug(f"Raw response:\n{response.text}")
        logging.debug(f"Response headers:\n{str(response.headers)}")
        print("\nCancelling...")
        exit()


def update_remote(folder: PurePath):
    """Update remote repository.

    :param folder: project folder."""
    print("\nUpdating remote repository...")
    try:
        output = helpers.execute_subprocess(
            ["git", "push", "-u", "origin", "master"],
            folder,
        )

    except (OSError, CalledProcessError) as e:
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


def add_origin(folder: PurePath, remote_path: str):
    """Add a remote pointing to GitHub repository.

    :param folder: project repository.
    :param remote_path: remote repository path."""
    remote_repo = f"https://github.com/{remote_path}"
    try:
        helpers.execute_subprocess(
            ["git", "remote", "add", "origin", f"{remote_repo}.git"],
            folder,
        )

    except (OSError, CalledProcessError) as e:
        error = f"Subprocess error: {e}"
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    else:
        logging.info("Remote repository added.")


def create_remote_repository(name: str, description: str,
                             headers: dict) -> str:
    """Create a remote repository in GitHub.

    :param name: name for remote repository.
    :param description: short description for remote repository.
    :param headers: http request headers.
    :returns: final remote repository path."""
    print("\nConnecting to GitHub...")
    github_config = {
        "name": f"{name}",
        "description": f"{description}",
        "private": False,
        "has_projects": False,
    }

    url = consts.GH_API_URL + "/user/repos"
    response = requests.post(url, json=github_config, headers=headers)
    if 200 <= response.status_code < 300:  # Usually 201
        repo_final_name = json.loads(response.text)['full_name']
        message = f"Remote repository {repo_final_name} created."
        logging.info(message)
        logging.debug(f"Raw response:\n{response.text}")
        print(message)

    else:
        error = (f"API request failed when creating the remote repository.")
        logging.critical(error)
        print(error)
        server_message = json.loads(response.text)["message"]
        logging.critical(f"Error {response.status_code}: {response.reason} "
                         f"({server_message})")
        logging.debug(f"Raw response:\n{response.text}")
        logging.debug(f"Response headers:\n{str(response.headers)}")
        print("\nCancelling...")
        exit()

    return repo_final_name


def build_headers(username: str) -> dict:
    """Get authentication and create http headers.

    :param username: GitHub username.
    :returns: http request headers."""
    # Try to get an OAuth token from the system keyring
    token = None
    try:
        token = keyring.get_password(consts.KEYRING_SYSTEM, username)
    except keyring.errors.InitError:
        logging.warning("No credential manager was found in the system.")

    #  Ask for credentials if no token was retrieved
    if token is None:
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

    # requests uses HTTPBasicAuth internally when auth is a tuple like this:
    # auth = (username, password)
    # But there is a bug in requests.auth.HTTPBasicAuth when using special
    # characters (issue #4649) so let's build the basic auth by ourselves
    if token is None:
        logging.debug("Asking for credentials.")
        bauth = f"{username}:{password}".encode()
        authorization = f"Basic {base64.b64encode(bauth).decode()}"
    else:
        logging.debug(f"OAuth token retrieved from {keyring.get_keyring()}.")
        authorization = f"token {token}"

    headers = {
        "User-Agent": f"{username} using {consts.PROGRAM}/"
                      f"{consts.VERSION}",
        "Authorization": authorization,
        "Accept": "application/vnd.github.v3+json",
    }

    return headers


def commit_files(folder: PurePath):
    """Save staged files to the local repository.

    :param folder: project folder."""
    print("\nCommiting files...")
    try:
        output = helpers.execute_subprocess(
            ["git", "commit", "-m", "initial commit", "-m",
             f"by `{consts.PROGRAM}/{consts.VERSION}`"],
            folder,
        )

    except (OSError, CalledProcessError) as e:
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


def stage_files(folder: PurePath):
    """Add files in the folder to the stage area.

    :param folder: project folder."""
    print("\nStaging files...")
    try:
        helpers.execute_subprocess(
            ["git", "add", "-A"],
            folder,
        )

    except (OSError, CalledProcessError) as e:
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


def initialise_git(folder: PurePath):
    """Initialise local repository.

    :param folder: project folder."""
    print("\nInitialising git...")
    try:
        output = helpers.execute_subprocess(
            ["git", "init"],
            folder,
        )

    except (OSError, CalledProcessError) as e:
        error = f"Subprocess error: {e}"
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    else:
        message = output.strip()
        logging.info(message)
        print(message)


def build_vscode_settings(folder: PurePath, linter: str, interpreter: str):
    """Create settings file for Visual Studio Code.

    :param folder: project folder.
    :param linter: installed linter.
    :param interpreter: path to Python interpreter."""
    try:
        Path.mkdir(folder / ".vscode")
    except FileExistsError:
        pass

    settings = {
        "python.linting.enabled": True,
        f"python.linting.{linter}Enabled": True,
        "python.pythonPath": interpreter,
    }

    # Overwrite settings.json file just in case the interpreter path changed
    with open(folder / ".vscode/settings.json", "w") as f:
        json.dump(settings, f, indent=4)
    message = "A `settings.json` file was created in `/.vscode`."
    logging.info(message)
    print(f"\n{message}")


def get_interpreter_path(folder: str) -> str:
    """Get interpreter path inside the virtual environment.

    :param folder: project folder.
    :returns: path to Python interpreter."""
    try:
        output = helpers.execute_subprocess(
            ["pipenv", "--py"],
            folder,
        )

    except (OSError, CalledProcessError) as e:
        error = f"Subprocess error: {e}"
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    else:
        interpreter = output.strip()
        logging.debug(f"Interpreter path: `{interpreter}`")

    return interpreter


def install_linter(folder: PurePath, linter: str):
    """Install linter as a dev package in the current virtual environment.

    :param folder: project folder.
    :param linter: linter to install."""
    print("\nThis can take a while...")
    try:
        helpers.execute_subprocess(
            ["pipenv", "install", linter, "--dev"],
            folder,
        )

    except (OSError, CalledProcessError) as e:
        error = f"Subprocess error: {e}"
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    else:
        message = f"`{linter}` linter installed."
        logging.info(message)
        print(message)


def build_environment(folder: PurePath, python_version: str):
    """Create Python virtual environment.

    :param folder: project folder.
    :param pytyhon_version: Python version to install."""
    print("\nThis can take a while...")
    try:
        helpers.execute_subprocess(
            ["pipenv", "--python", f"{python_version}"],
            folder,
        )

    except (OSError, CalledProcessError) as e:
        error = f"Subprocess error: {e}"
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    else:
        message = f"Python {python_version} virtual environment created."
        logging.info(message)
        print(message)


def build_gh_pages(description: str, folder: PurePath, content: dict):
    """Build index and configuration page for GitHub pages.

    :param description: short description for the project.
    :param folder: project folder.
    :param content: content for _config.yml file."""
    # if a docs/index.md file already exists, overwrite it
    shutil.copy(folder / "readme.md", folder / "docs/index.md")
    message = ("An `index.md` file was created in `/docs`.")
    logging.info(message)
    print(message)

    content["description"] = description
    try:
        with open(folder / "docs/_config.yml", "x") as f:
            for key, value in content.items():
                f.write(f"{key}: {value}\n")
    except FileExistsError:
        message = "A `_config.yml` file was found. Skipping step."
    else:
        message = "A `_config.yml` file was created in `/docs`."
    finally:
        logging.info(message)
        print(message)


def copy_templates(licence: str, folder: PurePath, gh_pages: bool):
    """Copy template files to the project folder.

    :param licence: license for the project.
    :param folder: project folder.
    :param gh_pages: if True, copy GitHub pages templates."""
    if gh_pages:
        try:
            shutil.copytree(consts.TEMPLATE_DIR / "docs",
                            folder / "docs")
        except FileExistsError:
            logging.debug("A `/docs` folder was found. Skipping step.")
        else:
            logging.debug(f"A `/docs` folder was copied to `{folder}`.")

    # If a .gitignore file already exists, overwrite it
    shutil.copy(consts.TEMPLATE_DIR / ".gitignore", folder)
    logging.debug(f"A `.gitignore` file was copied to `{folder}`.")

    # If a license file already exists, overwrite it
    license_file = "UNLICENSE" if licence.upper() == "UNLICENSE" else "LICENSE"
    shutil.copy(
        consts.TEMPLATE_DIR / f"licenses/{licence}/{license_file}",
        folder
    )
    logging.debug(f"A `{licence}` license file was copied to "
                  f"`{folder}`.")

    message = f"Template files were copied to `{folder}`."
    logging.info(message)
    print(message)


def build_readme(name: str, description: str, licence: str, folder: PurePath,
                 content: dict):
    """Create readme.md file from a dictionary.

    :param name: name for the project.
    :param description: short description for the project.
    :param licence: license for the project.
    :param folder: project folder.
    :param content: sections for the readme file."""
    content["License"] = f"This project is under the {licence} license.\n\n"
    try:
        with open(folder / "readme.md", "x") as f:
            # Title and short description
            f.write(
                f"<h2 align='center'>{name.upper()}</h2>\n\n"
                "<p align='center'>\n"
                f"  <i>{description}</i>\n"
                "</p>\n\n"
                "#### Table of contents:\n"
            )

            # Table of contents
            for key in content.keys():
                f.write(f"- [{key}](#{helpers.validate_name(key)})\n")

            # Sections
            for key, value in content.items():
                f.write(f"\n---\n\n### {key}\n")
                f.write(f"{value}\n")

            # Footer
            f.write(
                f"\n###### This file was generated by "
                f"`{consts.PROGRAM}/{consts.VERSION}`"
            )

    except FileExistsError:
        message = "A `readme.md` file was found. Skipping step."
    else:
        message = f"A `readme.md` file was created in `{folder}`."
    logging.info(message)
    print(message)
