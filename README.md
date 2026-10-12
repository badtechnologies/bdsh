# BadOS Dynamic Shell (bdsh)

Read the docs at [badtechnologies.github.io/bdsh](https://badtechnologies.github.io/bdsh).

## Quick Install

Run the following command:

```sh
python3 -m pip install bdsh
python3 -m bdsh.install
```

The installer creates the shell root, config directory, and first user.

## Installation (Manual)

1. Download the latest release.

   Or, install the package from PyPI.

2. Set up bdsh:

   ```sh
   python3 -m bdsh.install
   ```

   Follow the prompts. The setup script creates the `bdsh/` directory tree and config files.

3. Start bdsh:

   ```sh
   bdsh
   ```

The shell prompts for a username and password, then starts an interactive session.

## Minimal boot profile

For a minimal boot prompt that does not start services or request a BadLogon
login, run:

```sh
bdsh-init
```

The same entry point is available as `python3 -m bdsh.init`. It uses a fixed
`/` starting directory and only standard-library shell commands. The `exit`
and `quit` commands are disabled so the init process remains alive.
