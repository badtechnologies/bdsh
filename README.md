# BadOS Dynamic Shell (bdsh)

## Usage

Run the `config.py` script, and follow the on-screen instructions.

> [!NOTE]
> At least ONE user must exist for bdsh to function

Once the `/bdsh` directory and your configs are prepared, you can start bdsh with `bdsh.py` to launch the interactive shell.
Or, you can start `badbandssh.py` to host a BadBandSSH server for bdsh.

BadBandSSH runs on port 2200 by default. Connect to a BadBandSSH server with the following command:

```sh
ssh <username>@<hostname> -p 2200
```

## Default Binaries

- BadBandSSH (bssh)
