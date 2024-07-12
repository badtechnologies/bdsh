[❮ Back](.)

# System File Structure

This document provides an overview of the file and folder structure of bdsh (Bados Dynamic Shell).

The system file structure will be created automatically with the bdsh configuration tool (config.py).

## Root Directory

- **bdsh/**: main directory
  - **cfg/**: configuration files
  - **prf/**: profile-specific home directories
  - **exec/**: scripts and binaries

## Profile-specific files

Profile-specific home directories contain certain local profile files, such as:

- **cfg/**: profile configuration files
- **exec/**: profile scripts and binaries

## Binary execution

bdsh runs binaries in this order:

1. definitions (set with `def` command)
2. bdsh scripts: e.g. echo, exit
3. exec/
4. prf/[username]/exec/
