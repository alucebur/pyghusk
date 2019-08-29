"""Program to create template files for pyghusk."""
import json

import requests

import consts


def create_program_directory():
    """Create directory structure for pyghusk."""
    try:
        (consts.TEMPLATE_DIR / "docs").mkdir(parents=True)
        print(f"Directory `{consts.TEMPLATE_DIR / 'docs'}` created.")

    except FileExistsError:
        print(f"Directory `{consts.TEMPLATE_DIR / 'docs'}` already exists. "
              "Skippping step.")

    try:
        (consts.PROGRAM_DIR / "logs").mkdir()
        print(f"Directory `{consts.PROGRAM_DIR / 'logs'}` created.")

    except FileExistsError:
        print(f"Directory `{consts.PROGRAM_DIR / 'logs'}` already exists. "
              "Skippping step.")


def get_gitigore_file(headers: dict) -> str:
    """Request a Python gitignore file from GitHub.

    :param headers: http request headers.
    :returns: content for Python `.gitignore` file."""
    headers["Accept"] = "application/vnd.github.v3.raw"

    url = consts.GH_API_URL + "/gitignore/templates/Python"
    response = requests.get(url, headers=headers)
    if 200 <= response.status_code < 300:  # Usually 200
        ignore_content = response.text

    else:
        print(f"\nAPI request failed when getting `.gitignore` file.")
        server_message = json.loads(response.text)["message"]
        print(f"Error {response.status_code}: {response.reason} "
              f"({server_message})")
        exit()

    return ignore_content


def get_license_urls(headers: dict) -> dict:
    """Get urls for the most commonly used licenses from GitHub.

    :param headers: http request headers.
    :returns: license names with urls to download."""
    url = consts.GH_API_URL + "/licenses"
    response = requests.get(url, headers=headers)
    if 200 <= response.status_code < 300:  # Usually 200
        content = json.loads(response.text)
        licenses = {
            licence['spdx_id']: licence['url'] for licence in content
        }

    else:
        print(f"\nAPI request failed when getting license urls.")
        server_message = json.loads(response.text)["message"]
        print(f"Error {response.status_code}: {response.reason} "
              f"({server_message})")
        exit()

    return licenses


def get_license_file(headers: dict, name: str, url: str):
    """Get license file and create subfolders.

    :param headers: http request headers.
    :param name: license name.
    :param url: license url."""
    response = requests.get(url, headers=headers)
    if 200 <= response.status_code < 300:  # Usually 200
        content = json.loads(response.text)['body']

    else:
        print(f"\nAPI request failed when getting license file.")
        server_message = json.loads(response.text)["message"]
        print(f"Error {response.status_code}: {response.reason} "
              f"({server_message})")
        exit()

    try:
        (consts.TEMPLATE_DIR / "licenses" / name).mkdir(parents=True)
        print(f"\nDirectory `{consts.TEMPLATE_DIR / 'licenses' / name}` "
              "created.")

    except FileExistsError:
        print(f"\nDirectory `{consts.TEMPLATE_DIR / 'licenses' / name}` "
              "already exists. Skippping step.")

    try:
        file_name = "UNLICENSE" if name.upper() == "UNLICENSE" else "LICENSE"
        with open(
            consts.TEMPLATE_DIR / "licenses" / name / file_name, "x"
        ) as f:
            f.write(content)
        print(f"`{name}` license file created.")

    except FileExistsError:
        print(f"`{name}` license file already exists. Skippping step.")


def main():
    create_program_directory()

    headers = {
        "User-Agent": f"{consts.PROGRAM}/{consts.VERSION}",
        "Accept": "application/vnd.github.v3+json"
    }

    content = get_gitigore_file(headers)
    try:
        with open(consts.TEMPLATE_DIR / ".gitignore", "x") as f:
            f.write(content)
        print(f"\n`.gitignore` file created.")

    except FileExistsError:
        print("\nA `.gitignore` file already exists. Skipping step.")

    licenses = get_license_urls(headers)
    for name, url in licenses.items():
        get_license_file(headers, name, url)

    print("\nTemplate files created.\nPlease remember to edit and move "
          f"`config.json` file to `{consts.PROGRAM_DIR}`")


if __name__ == "__main__":
    main()
