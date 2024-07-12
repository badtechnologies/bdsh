[❮ Back](.)

# BDSH Commands

bdsh contains many commands for you to use, packed inside the shell.

Some are self explainatory, others will be explained here.

See the order that bdsh finds and runs commands [here](file-structure.md#binary-execution).

## ld (list directory)

Prints all files and folders in the current directory, or the directory passed as an argument

## def (define)

Binds keywords to definitions. Similar to a shortcut, but for commands.

### Example (`hello -> echo hi`)

```bdsh
/$ def hello echo hi
defined 'hello' to run 'echo hi'
/$ hello
hi
```

## throw

Throws an exception.

## go

Goes to a directory, similar to `cd` on other operating systems.

## peek

Peeks into a file, and prints its contents to the terminal.
