#!/usr/bin/env python3
"""Command-line program to create a new Python GitHub project in VSCode.

This program will:
- create a `readme.md` file in the local project folder;
- copy template files to the local project folder;
- (opt) create `docs/index.md` and `docs/_config.yml` files for GitHub pages;
- set a new virtual environment with pipenv in the local project folder;
- install the specified version of Python in the virtual environment;
- install the chosen linter in the virtual environment;
- create and configure `.vscode/settings.json` file for VSCode;
- initialise git in the local project folder;
- commit the content of the local project folder to the local repository;
- create a public remote repository in GitHub;
- update remote repository with local changes;
- (opt) Enable GitHub pages in the remote repository;
- (opt) Rebuild pages of the personal blog (`{USERNAME}`.github.io)."""
import argparse
import json

import actions
import consts
import helpers


def main(argv: argparse.Namespace):
    """Executes program.

    :param argv: object holding attributes parsed from command-line args."""
    # Check everything is properly configured (Anti-TL;DR)
    error = False
    if not consts.TEMPLATE_DIR.exists():
        print(f"Error: directory `{consts.TEMPLATE_DIR}` doesn't exist.")
        error = True

    else:
        with open(consts.PROGRAM_DIR / "config.json") as f:
            config = json.load(f)

        if config["USERNAME"] is None:
            print("Error: A GitHub username was not configured.")
            error = True

    if error:
        print("\nBefore using the program, please take some time to read the "
              "documentation and configure the needed files.")
        exit()

    # Initialise logging
    helpers.start_logging(argv.verbose)

    # If a folder is not provided, set project folder to current folder
    project_folder = helpers.get_project_folder(argv.folder)

    # Gather rest of information
    repo_name = helpers.get_repo_name(argv.name)
    repo_description = helpers.get_repo_description(argv.description)
    project_license = helpers.get_license(argv.license)

    # Check out
    print(f"\n{'Repository name:':>25} {repo_name}")
    print(f"{'Repository description:':>25} {repo_description}")
    print(f"{'Project license:':>25} {project_license}")
    print(f"{'Project folder:':>25} {project_folder}")

    if not helpers.empty_folder(project_folder):
        print("\n   *** WARNING: project folder is not empty!! ***")
        print("Make sure there is no confidential information inside")

    helpers.get_user_approval()
    print("\nStarting...\n")

    # [Step-1] Build readme.md
    # ===================================================================
    actions.build_readme(repo_name, repo_description, project_license,
                         project_folder, config["README_CONTENT"])

    # [Step-2] Copy template files
    # ===================================================================
    actions.copy_templates(project_license, project_folder,
                           config["ENABLE_GH_PAGES"])

    # [Step-3] Build index.md and _config.yml files
    # ===================================================================
    if config["ENABLE_GH_PAGES"]:
        actions.build_gh_pages(repo_description, project_folder,
                               config["JEKILL_CONFIG"])

    # [Step-4] Create a virtual environment for the project
    # ===================================================================
    actions.build_environment(project_folder, config["PYTHON_VERSION"])

    # [Step-5] Install linter
    # ===================================================================
    actions.install_linter(project_folder, config["LINTER"])

    # [Step-6] Get interpreter path inside the virtual environment
    # ===================================================================
    interpreter_path = actions.get_interpreter_path(project_folder)

    # [Step-7] Building VSCode settings file
    # ===================================================================
    actions.build_vscode_settings(project_folder, config["LINTER"],
                                  interpreter_path)

    # [Step-8] Initialise git in project directory
    # ===================================================================
    actions.initialise_git(project_folder)

    # [Step-9] Add all not .gitignored files to the stage area
    # ===================================================================
    actions.stage_files(project_folder)

    # [Step-10] Commit files to the local repository
    # ===================================================================
    actions.commit_files(project_folder)

    # [Step-11] Authentication for GitHub API v3
    # ===================================================================
    headers = actions.build_headers(config["USERNAME"])

    # [Step-12] Create the remote repository in GitHub
    # ===================================================================
    remote_path = actions.create_remote_repository(repo_name,
                                                   repo_description, headers)

    # [Step-13] Add a remote pointing to GitHub repository
    # ===================================================================
    actions.add_origin(project_folder, remote_path)

    # [Step-14] Push local commit to remote repository
    # ===================================================================
    actions.update_remote(project_folder)

    # [Step-15] Enable GitHub pages
    # ===================================================================
    if config["ENABLE_GH_PAGES"]:
        actions.enable_pages(headers, remote_path)

    # [Step-16] Request page build to include the new project in personal blog
    # ===================================================================
    if config["ENABLE_GH_PAGES"]:
        actions.build_pages(config["USERNAME"], headers)

    # [Finished]
    # ===================================================================
    print(f"\nWork successfully finished!")
    print(f" - Check the log file at `{consts.LOG_FILE}`")
    print(f" - Check the project files at `{project_folder}`")
    print(" - Check the remote repository at `https://github.com/"
          f"{remote_path}`")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        prog=f"{consts.PROGRAM}",
        description="Command-line program to create a new Python3 GitHub "
                    "project in VSCode.",
        allow_abbrev=False,
    )

    parser.add_argument("-V", "--version", action="version",
                        version=f"%(prog)s {consts.VERSION}")
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
                        choices=consts.LICENSES,
                        help="license to use for the project")

    args = parser.parse_args()
    main(args)
