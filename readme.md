<h2 align='center'>pyghusk</h2>

<p align="center">
    <img src="docs/assets/pyghusk.png" width="200" />
    <br />
    <i>Command-line program to start a new <b>Py</b>thon <b>G</b>it<b>H</b>ub project in <b>VSC</b>ode.</i>
</p>

#### Table of contents:
- [What does this program do?](#functionality)
- [How can I install it?](#installation)
- [How can I execute it?](#syntax)
- [How do I configure the program?](#configuration)
- [How can I use the program?](#how-to-use)
- [Changelog](#changelog)
- [License](#license)

---

### Functionality
This program was created so that I can start new Python projects in a faster and more comfortable way.

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
- (opt) Rebuild pages of the personal blog (`{USERNAME}`.github.io).

---

### Installation
Requires Python 3.6+ (with pip).

Clone the repository or download and extract the zip or tarball file in an empty folder on your computer.

Navigate until the recently created folder and install dependencies:

- Pipenv:

        pipenv install

- Pip:

        pip install -r requirements.txt

---

### Syntax
    pyghusk.py [-h] [-V] [-v] [-f FOLDER] [-n NAME]
               [-d DESCRIPTION] [-l {LICENSES}]

Options:

        -h, --help: show help message and exit.
        -V, --version: show program's version number and exit.
        -v, --verbose: set logging level to DEBUG.
        -f FOLDER, --folder FOLDER: local project folder.
        -n NAME, --name NAME: name for the remote repo.
        -d DESCRIPTION, --description DESCRIPTION: description for the remote repo.
        -l {LICENSES}, --license {LICENSES}: license to use for the project.

For executing the program, run it with `pipenv run` or `python3`.

---

### Configuration
Before running the program, you need to configure some options in the `config.json` file:
- PYTHON_VERSION: Python version for the virtual environment. You need to have it installed in your system.
- LINTER: Linter to use with VSCode (pep8, pylint, flake8...).
- USERNAME: Your GitHub username.
- README_CONTENT: Sections for your `readme.md` file.
- ENABLE_GH_PAGES: Set it to True if you want to activate GitHub pages for your project. They will be deployed from the `docs` folder in your master branch.

The following option is only needed if you set ENABLE_GH_PAGES to True:
- JEKILL_CONFIG: Content of the `_config.yml` file for your GitHub pages.

Once you finished editing it, you need to move it to `~/.config/pyghusk/`.

---

### How to use
First of all, this program assumes you want to write Python code using Visual Studio Code, and want to create a new public remote repository in GitHub platform. If you use other tools, feel free to modify this program to your own needs.

For some parameters that are likely to not change frequenly in between projects there is a configuration file called `config.json`, so they don't need to be specified every time the program is executed. Remember to configure them to your own needs. Then move it to `~/.config/pyghusk/`, which is the directory this program uses for getting config files, templates, and write logs.

If `--folder` option is not supplied, the current directory will be used as the local project folder. If any other argument is missing, an interactive prompt will try to get it from the user.

In `LICENSES` directory there must be a folder for each license to be used, whose name will identify the license. Inside each folder there must be a file called `LICENSE` with the text of such license, unless it is the Unlicense, in which case both the file and the folder must be called `UNLICENSE`.

You can execute `create_templates.py` to create the directory structure and templates for licenses and `.gitignore` files. The program checks GitHub to get these template files. You will still need to move your own GitHub page documents inside `~/.config/pyghusk/templates/docs` folder if you want to use that feature.

An Oauth token for GitHub can be set in the system's credential manager. For creating a personal access token, please refer to this article: https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line. It is enough with "public_repo" scope.

You can execute `manage_tokens.py` to set an OAuth token to be used by this program. You can delete such token running the same program with `--delete` option. Under Windows 7/8/10, the program will use Windows Credential Manager. Under GNU/Linux, if the program doesn't detect any keyring, please check keyring documentation at https://keyring.readthedocs.io/en/latest/ since you could need additional packages. It is untested under Mac OS (it should use macOS Keychain).

If no OAuth token is found, the program will ask users for their GitHub password. This password is not stored and it is only used to make requests to the GitHub API under HTTPS.

The events happening during the execution of the program are logged in a log file in `~/.config/pyghusk/logs/`. If the program was executed with the `--verbose` option, debug information will be added to the log file.

Directory structure for `~/.config/pyghusk/` folder:

    ├──  /templates
    │    ├──  /docs
    │    │    └── <content you want for your GitHub pages>
    │    ├──  /licenses
    │    │    ├── /GPL-3.0
    │    │    │   └── LICENSE
    │    │    ├── /LGPL-3.0
    │    │    └── LICENSE
    ...  ...  ...
    │    │    ├── /<any license you want to be able to use>
    │    │    │   └── LICENSE
    │    │    └── /UNLICENSE
    │    │        └── UNLICENSE
    │    └──  .gitignore
    └──  /logs

---

### Changelog
**Version 0.1.0 - 2019/08/29**
- Divided the program in smaller modules.
- Tokens are stored in system's keyring backend.
- `manage_tokens.py` program to set tokens into the keyring backend (and delete them).
- `create_templates.py` program to create directory structure and template files.
- JSON configuration file stores user preferences.
- `readme.md`, `docs/index.md`, and `docs/_config.yml` files are generated from the configuration file.
- GitHub pages are now optional.
- Logs moved to their own directory.

**Version 0.0.1 - 2019/08/23**
- Initial release

---

### License
This program is under the UNLICENSE license. This means that it is "free and unencumbered software released into the public domain". Feel free to use it and modify it as you want.