import tomlkit
import sys
import re
import os
import shutil

if __name__ == "__main__":
    if len(sys.argv) != 4:
        exit(1)
    with open(sys.argv[1], "rt") as file:
        ignore_list = [int(line) for line in file.readlines()]
    # folders
    os.makedirs(sys.argv[3] + "\\rom", exist_ok=True)
    subdirs = os.listdir(sys.argv[2] + "\\script_nc")
    for dir in subdirs:
        id = re.search(r"pv(\d+)", dir)
        if id is None:
            continue
        id = id.group(0)
        if id not in ignore_list:
            shutil.copytree(
                sys.argv[2] + "\\script_nc\\" + dir,
                sys.argv[3] + "\\rom\\script_nc\\" + dir,
                dirs_exist_ok=True,
            )

    # nc_db
    with open(sys.argv[2] + "\\nc_db.toml", "rt") as file:
        nc_db = tomlkit.load(file).unwrap()
    nc_db["songs"] = [pair for pair in nc_db["songs"] if pair["id"] not in ignore_list]
    with open(sys.argv[3] + "\\rom\\nc_db.toml", "wt") as file:
        tomlkit.dump(nc_db, file)
