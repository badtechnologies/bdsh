

# BadOS Dynamic Shell (bdsh)

## Table of Contents

- [BadOS Dynamic Shell Package Library (bpl)](bpl.md)
- [BadOS Package Manager (bpm)](bpm.md)
- [BadBandSSH (bssh)](bssh.md)
- [System File Structure](file-structure.md)
- [BadOS Dynamic Shell (bdsh)](index.md)

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/badtechnologies/bdsh.git
    cd bdsh
    ```

2. **Setup bdsh:**

    ```sh
    python3 config.py
    ```

    Follow the on-screen instructions.

3. **Run the project:**

    ```sh
    python3 bdsh.py
    ```

## Usage

Run the `config.py` script, and follow the on-screen instructions.

> [!NOTE]
> At least ONE user must exist for bdsh to function

Once the `/bdsh` directory and your configs are prepared, you can start bdsh with `bdsh.py` to launch the interactive shell.
