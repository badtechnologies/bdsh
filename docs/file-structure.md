# System File Structure

This document provides an overview of the file and folder structure of bdsh (Bados Dynamic Shell).

## Root Directory

- **bdsh/**: main directory
  - **core/**: pre-installed system scripts and binaries
  - **cfg/**: configuration files
  - **prf/**: profile-specific home directories
  - **exec/**: non-system scripts and binaries

## Profile-specific files

Profile-specific home directories contain certain local profile files, such as:

- **cfg/**: profile configuration files
- **exec/**: profile scripts and binaries

## Binary execution

bdsh runs binaries in this order:

1. bdsh scripts: e.g. echo, exit
2. core/
3. exec/
4. prf/[username]/exec/
