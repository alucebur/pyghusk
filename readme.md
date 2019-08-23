<h2 align='center'>pyghusk</h2>

<p align="center">
    <img src="docs/assets/pyghusk.png" width="200" />
    <br />
    <i>Command-line script to start a new <b>Py</b>thon <b>G</b>it<b>H</b>ub project in <b>VSC</b>ode.</i>
</p>

#### Table of contents:
- [What does this script do?](#functionality)
- [How can I install it?](#installation)
- [How can I execute it?](#syntax)
- [How can I use the script?](#how-to-use)
- [License](#license)

---

### Functionality
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

---

### How to use
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

Example of structure for ~/.config/pyghusk/ folder:

        /templates
        ├──  /docs
        │    ├── /layouts
        │    │   └── default.html
        │    ├── /screenshots
        │    └── 404.html
        ├──  /licenses
        │    ├── /GPL
        │    │   └── LICENSE
        │    ├── /LGPL
        │    │   └── LICENSE
        │    ├── /MIT
        │    │   └── LICENSE
        │    └── /UNLICENSE
        │        └── UNLICENSE
        └──  .gitignore

---

### License
This program is under the UNLICENSE license. This means that it is "free and unencumbered software released into the public domain". Feel free to use it and modify it as you want.