

# BadOS Dynamic Shell (bdsh)

## Table of Contents

- [BadOS Dynamic Shell Package Library (bpl)](bpl.md)
- [BadOS Package Manager (bpm)](bpm.md)
- [BadBandSSH (bssh)](bssh.md)
- [BDSH Commands](commands.md)
- [System File Structure](file-structure.md)
- [BadOS Dynamic Shell (bdsh)](index.md)


## Installation

1. **Download the latest release**

    Or, you can directly download `config.py` and `bdsh.py` from the [repo](https://github.com/badtechnologies/bdsh).

2. **Setup bdsh:**

    ```sh
    python3 config.py
    ```

    Follow the on-screen instructions.

    > #### ℹ️ Note
    > At least ONE user must exist for bdsh to function

    Once the `/bdsh` directory and your configs are prepared, you can start bdsh with `bdsh.py` to launch the interactive shell.

3. **Launch bdsh:**

    ```sh
    python3 bdsh.py
    ```
