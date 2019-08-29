"""Functions used by pyghusk."""
import logging
import re
import subprocess
import unicodedata
from pathlib import Path, PurePath

import consts


def get_repo_name(name: str = None) -> str:
    """Get a valid remote repository name.

    :param name: candidate name for the remote repository.
    :returns: valid remote repository name.

    >>> get_repo_name(" déjà  vu! ")
    'deja-vu'"""
    if name:
        repo_name = validate_name(name)
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
    return repo_name


def get_repo_description(description: str = None) -> str:
    """Get remote repository description.

    :param description: candidate short description for the project.
    :returns: short description for the project.

    >>> get_repo_description("This is a test.")
    'This is a test.'"""
    if description:
        repo_description = description
    else:
        repo_description = input("Repository description (optional): ")

    logging.info(f"Repo description will be `{repo_description}`")
    return repo_description


def get_license(licence: str = None) -> str:
    """Get a valid license for the project.

    :param license: candidate license for the project.
    :returns: license for the project.

    >>> get_license("MIT")
    'MIT'"""
    if licence:
        project_license = licence

    else:
        while True:
            print(f"\nAvailable licenses: {', '.join(consts.LICENSES)}")
            project_license = input(f"License for the project: ")
            if project_license in consts.LICENSES:
                break
            else:
                error = (f" - Error: `{project_license}` license is not "
                         "available.")
                logging.debug(error)
                print(error)

    logging.info(f"Project will be under `{project_license}` license")
    return project_license


def empty_folder(folder: PurePath) -> bool:
    """Check if folder is empty.

    :param folder: folder to check.
    :returns: True if folder is empty.

    >>> empty_folder(Path("."))
    False"""
    try:
        next(folder.iterdir())
    except StopIteration:
        return True
    else:
        return False


def get_user_approval():
    """Ask user for permission to continue."""
    response = input("\nIs this info correct? (y/N): ").lower()
    if response not in ["y", "yes"]:
        logging.info("Program cancelled by the user.")
        print("\nCancelling...")
        exit()


def get_project_folder(folder: str = None) -> PurePath:
    """Get a valid project folder.

    :param folder: candidate directory for the project.
    :returns: project folder."""
    if folder:
        project_folder = Path(folder)
    else:
        project_folder = consts.CURRENT_DIR

    if project_folder.exists():
        logging.info(f"Local project directory will be `{project_folder}`")
    else:
        error = f"Error: directory `{project_folder}` doesn't exist."
        logging.critical(error)
        print(error)
        print("\nCancelling...")
        exit()

    return project_folder


def start_logging(verbose: bool = False):
    """Initialise logger.

    :params verbose: when True, set level to debug mode."""
    log_format = "%(asctime)-15s %(levelname)s: %(message)s"
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format=log_format,
        level=log_level,
        filename=consts.LOG_FILE,
    )


def execute_subprocess(command: list, direct: str) -> str:
    """Execute subprocess and return output.

    :param command: list of command arguments.
    :param direct: working directory.
    :returns: output of the subprocess.

    >>> execute_subprocess(["python", "-V"], ".")  # doctest: +ELLIPSIS
    'Python 3...'"""
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
