"""Store and delete OAuth tokens used by the main program."""
import argparse
import getpass

import keyring

import consts


def check_credential_manager() -> str:
    """Check for an existing system credential manager.

    :returns: keyring backend to be used."""
    try:
        keyring_imp = keyring.get_keyring()
    except keyring.errors.InitError as e:
        print(f"Error initialising the keyring: {e}")
        exit()
    return keyring_imp


def delete_token(username: str):
    """Delete the OAuth Token from the system credential manager.

    :param username: GitHub username."""
    try:
        keyring.delete_password(consts.KEYRING_SYSTEM, username)
    except keyring.errors.PasswordDeleteError:
        print("Error deleting OAuth Token: No token was found "
              f"for {username}@{consts.KEYRING_SYSTEM}.")
    else:
        print(f"OAuth Token for {username}@{consts.KEYRING_SYSTEM} deleted.")


def store_token(username: str):
    """Store the OAuth Token in the system credential manager.

    :param username: GitHub username."""
    token = getpass.getpass(prompt="\nPlease enter GitHub OAuth token: ")

    try:
        keyring.set_password(consts.KEYRING_SYSTEM, username, token)
    except keyring.errors.PasswordSetError as e:
        print(f"Error storing OAuth Token: {e}")
    else:
        print(f"OAuth Token for {username}@{consts.KEYRING_SYSTEM} stored.")


def main(argv: argparse.Namespace):
    keyring_imp = check_credential_manager()
    print(f"Using {keyring_imp}")

    if argv.delete:
        delete_token(argv.username)
    else:
        store_token(argv.username)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Store and delete OAuth tokens using the system "
                    "credential manager.",
        allow_abbrev=False,
    )

    parser.add_argument("username",
                        help="GitHub username")
    parser.add_argument("-d", "--delete", action="store_true",
                        help="delete a previously stored OAuth token")

    args = parser.parse_args()
    main(args)
