---
title: File Structure
nav_order: 4
---

# System File Structure

The installer creates the bdsh directory tree under the current working directory.

## Root Directory

- **bdsh/**: shell root
  - **app/**: application installs managed by bpm
  - **cfg/**: configuration and package metadata
  - **cfg/bpm/**: package store metadata files
  - **cfg/userman**: user database
  - **exec/**: executable scripts and binaries for the shell
  - **prf/**: profile directories for each user

## Profile directories

Each user gets a folder under `bdsh/prf/<username>`. This is the directory the shell moves into after login.

## Runtime paths

bdsh defines the following runtime paths in `bdsh.__init__`:

- `OSPaths.ROOT`
- `OSPaths.APPLICATIONS`
- `OSPaths.CONFIGS`
- `OSPaths.EXECUTABLES`
- `OSPaths.PROFILES`

## Command resolution

bdsh resolves commands in this order:

1. definitions from the current session
2. built in commands
3. executables in `bdsh/exec/`

The shell does not currently search profile directories for executables during command resolution.
