#!/usr/bin/env python3

import subprocess
import re
import sys
import ast
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path
from os import chdir


def bl_info_version() -> tuple[int, int, int] | None:
    try:
        module_fh = open('src/__init__.py', 'r')
        module_file = module_fh.read()
        module_fh.close()
        for node in ast.parse(module_file).body:
            if isinstance(node, ast.Assign) and node.targets[0].id == 'bl_info':
                bl_info = ast.literal_eval(node.value)
                return bl_info['version']
    except:
        return None

# FIND AND VERIFY TAG
try:
    tag_name = subprocess.check_output(["git", "describe", "--tags"], stderr=subprocess.DEVNULL).decode(
        sys.stdout.encoding).strip()
    tag_name = re.sub(r'[^\w._-]+', "_", tag_name)
    if matches := re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)', tag_name):
        bl_vers = bl_info_version()
        tag_vers = tuple([int(g) for g in matches.groups()])
        if bl_vers is not None and bl_vers != tag_vers:
            print(f"<<!>> Version {bl_vers} in the bl_info global in src/__init__.py does not match \"{tag_name}\" in the tag. Setting version to \"latest\".")
            tag_name = "latest"
except subprocess.CalledProcessError:
    tag_name = "latest"

# SETUP
root_dir = "src"  # Start here
toss_ins = ["demo", "README", "README.md", "LICENSE",
            "COPYING", "docs_support"]  # Toss these files in from the super-root directory, too.
exclude_regexes = [r"__pycache__", r"^venv", r"\.git(ignore|modules)?", r"^\.idea",
                   r".blend1$"]  # Exclude anything that matches these
wrap_dir = "mark_sharps"  # Wrap the output in a directory in the ZIP file
output_file = f"mark_sharps_{tag_name}.zip"  # What to call the ZIP file

# EXECUTION
home = str(Path(__file__).parents[0])
chdir(home)


def regex_allows(p: str) -> bool:
    return not [rx for rx in exclude_regexes if re.search(rx, str(p))]


# Get paths
paths = [p for p in Path(root_dir).rglob("**/*")]

# Filter directories
paths = [p for p in paths if not p.is_dir()]

# Filter regex exclusions
paths = [p for p in paths if regex_allows(str(p))]

# Find Git untracked files
try:
    git_lsfiles_output = subprocess.check_output(["git", "ls-files", "--others"]).decode(sys.stdout.encoding)
except subprocess.CalledProcessError:
    git_lsfiles_output = ""
git_untracked = [Path(p) for p in git_lsfiles_output.split("\n") if p]

# Filter untracked out of paths -- Two-step and save the untracked_paths for later display
untracked_paths = [p for p in paths if p in git_untracked]
paths = [p for p in paths if p not in untracked_paths]

# Add toss-in files
tossin_all = [Path(p) for p in toss_ins if Path(p).exists()]
tossin_paths = [p for p in tossin_all if not p.is_dir()]

# Traverse toss-in directories
for dp in tossin_all:
    if dp.is_dir():
        tossin_paths += [p for p in Path(dp).rglob("**/*")]

# Filter out excluded files and untracked files from toss-ins
untracked_tossins = [p for p in tossin_paths if p in git_untracked]
tossin_paths = [p for p in tossin_paths if p not in untracked_tossins and regex_allows(str(p))]

print(
    "\nExclusions ---\n" + "\n".join([f"Excluding untracked file: {p}" for p in (untracked_paths + untracked_tossins)]))
print(f"\nInclusions ---\nIncluding {len(paths)} files from {root_dir}")
print("\n".join([f"Tossing in {p}" for p in tossin_paths]))
print(f"\nOutput ---\n{output_file} at {Path(output_file).absolute()}")

if Path(output_file).exists():
    raise Exception("File already exists")

print("\nCreating archive...\n")
with ZipFile(output_file, mode="w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
    # Write normal files
    for p in paths:
        zip_path = str(Path(wrap_dir, *p.parts[1:]))
        print("rootdir: ", zip_path)
        archive.write(p, arcname=zip_path)
    for p in tossin_paths:
        zip_path = str(Path(wrap_dir, p))
        print("toss-in: ", zip_path)
        archive.write(p, arcname=zip_path)

print(f"Created {output_file} at {Path(output_file).absolute()}")
