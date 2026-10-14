---
title: Commands
nav_order: 3
---

# Commands

bdsh resolves an input name in this order: session command definitions, built-in commands, then files under `bdsh/exec`. Definitions are expanded before execution. The shell splits input on spaces; it does not implement quoting or general shell syntax such as pipes and redirection.

## Built-in commands

| Command    | Usage                         | Description                                               |
| ---------- | ----------------------------- | --------------------------------------------------------- |
| `help`     | `help [command]`              | List commands or show one command's help.                 |
| `echo`     | `echo [text ...]`             | Print the arguments.                                      |
| `ld`       | `ld [directory]`              | List a directory's entries.                               |
| `def`      | `def <keyword> <command ...>` | Define a command shortcut for this session.               |
| `go`       | `go <directory>`              | Change directory; `go ~` returns to the user's profile.   |
| `peek`     | `peek <file>`                 | Print a text file.                                        |
| `cwd`      | `cwd`                         | Print the current directory.                              |
| `ver`      | `ver`                         | Print the shell name and version.                         |
| `throw`    | `throw [message ...]`         | Raise an exception, useful for exercising error handling. |
| `exit`     | `exit`                        | End the interactive shell session.                        |
| `net`      | `net [interface]`             | Show network interfaces and addresses.                    |
| `hostname` | `hostname`                    | Print the system hostname.                                |

## Aliases

`ls` and `dir` are definitions for `ld`; `cd` is a definition for `go`. A definition can be overridden in the current session with `def`.

## External commands

An executable installed under `bdsh/exec` can be run by its filename. bdsh loads it as a Python module and calls its `main` function with `session` and `args` keyword arguments. The function is expected to accept those two parameters. The standalone `boss` program is an installed entry point, not a built-in shell command.
