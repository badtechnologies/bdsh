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
python3 -m pip install bdsh
python3 -m bdsh.install
```

After completing setup, bdsh should be good to go!

## Installation (Manual)

1. **Download the latest release**

   Or, you can directly download the `bdsh` module from PyPI.

2. **Setup bdsh:**

    ```sh
    python3 -m bdsh.install
    ```

   Follow the on-screen instructions.

   Once the `/bdsh` directory and your configs are prepared, you can start bdsh with `bdsh` to launch the interactive
   shell.

3. **Launch bdsh:**

    ```sh
    bdsh
    ```

   > #### ℹ️ Note
   > This may change depending on how you created your launcher scripts.
