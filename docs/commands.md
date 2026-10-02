---
title: Commands
nav_order: 3
---

# BDSH Commands

bdsh ships with a small built in command set.

The shell resolves commands in this order: definitions, built in commands, then executable files in `bdsh/exec`.

## help

Shows the available commands or the help text for one command.

## echo

Prints text to the terminal.

## ld

Lists the files and folders in the current directory. `ls` and `dir` resolve to this command.

## def

Creates a command definition. It works like a shortcut for shell commands.

```bdsh
/$ def hello echo hi
defined 'hello' to run 'echo hi'
/$ hello
hi
```

## go

Changes the current directory. `~` resolves to the current user's home folder.

## peek

Prints the contents of a file.

## cwd

Prints the current working directory.

## ver

Prints the shell banner.

## throw

Raises an exception. This is useful for testing shell error handling.

## exit

Exits the shell.

## bpm

Runs the BadOS Package Manager. Supported actions are `install`, `remove`, and `upgrade`.

## net

Shows network interface information. Pass an interface name to limit the output.

## hostname

Prints the current system hostname.

## ping

Pings a host with a configurable timeout and packet count.

## badproc

Starts a registered system service. See [Services](services.md) for more details.
