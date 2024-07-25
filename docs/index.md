

# BadOS Dynamic Shell (bdsh)

## Table of Contents

- [BadOS Dynamic Shell Package Library (bpl)](bpl.md)
- [BadOS Package Manager (bpm)](bpm.md)
- [BadBandSSH (bssh)](bssh.md)
- [BDSH Commands](commands.md)
- [System File Structure](file-structure.md)
- [BadOS Dynamic Shell (bdsh)](index.md)


## Quick Install

Run the following command:

```sh
curl -O https://raw.githubusercontent.com/badtechnologies/bdsh/main/install.py
python3 install.py
```

After completing setup, bdsh should be good to go!


## Installation

1. **Download the latest release**

    Or, you can directly download `install.py` from the [repo](https://github.com/badtechnologies/bdsh).

    > #### 💡 Tip
    > The only file needed to create a bdsh installation is `install.py`.<br>
    > Running `install.py` generates, downloads, or installs everything else.

2. **Setup bdsh:**

    ```sh
    python3 install.py
    ```

    Follow the on-screen instructions.

    > #### ℹ️ Note
    > At least ONE user must exist for bdsh to function

    Once the `/bdsh` directory and your configs are prepared, you can start bdsh with `bdsh.py` to launch the interactive shell.

3. **Launch bdsh:**

    ```sh
    bdsh
    ```

    > #### ℹ️ Note
    > This may change depending on how you created your launcher scripts.
