import sys
import json
import tomlkit
import regex as re
import fix_pv_db

MERGE_DBS = [
    "MM_script_database\\pv_db.txt",
    "MM_script_database\\mdata_pv_db.txt",
    "MM_script_database\\mod_pv_db.txt",
]


def write_missing_diff(difficulty, id, level, out):
    alt_diff = "easy" if difficulty == "normal" else "normal"
    out.write(f"pv_{int(id):03}.difficulty.{difficulty}.0.edition=0\n")
    out.write(f"pv_{int(id):03}.difficulty.{difficulty}.0.level={level}\n")
    out.write(f"pv_{int(id):03}.difficulty.{difficulty}.0.level_sort_index=20\n")
    out.write(
        f"pv_{int(id):03}.difficulty.{difficulty}.0.script_file_name=rom/script/pv_{int(id):03}_{alt_diff}.dsc\n"
    )
    out.write(f"pv_{int(id):03}.difficulty.{difficulty}.0.script_format=0x15122517\n")
    out.write(f"pv_{int(id):03}.difficulty.{difficulty}.0.version=1\n")
    out.write(f"pv_{int(id):03}.difficulty.{difficulty}.length=1\n")


def write_db(diff_list, nc_db, out):
    # make nc_db usable

    nc_dict = {
        item["id"]: [
            item[difficulty][0]["level"] for difficulty in diff_list[f"{item['id']}"]
        ]
        for item in nc_db["songs"]
        if f"{item['id']}" in diff_list.keys()
    }
    for db in MERGE_DBS:
        with open(db, "rt", encoding="utf8") as file:
            lines = file.readlines()
        for line in lines:
            id = re.search(r"^pv_(\d+)\..*$", line)
            if id is None:
                continue
            id = id.group(1)
            if f"{int(id)}" not in diff_list.keys():
                continue
            if line.count("length") > 0 and line.count("difficulty") > 0:
                difficulty = re.search(r"^pv_\d+\.difficulty\.(\w+)\..*$", line)
                if difficulty is None:
                    continue
                difficulty = difficulty.group(1)
                if difficulty not in diff_list[f"{int(id)}"]:
                    out.write(line)
                else:
                    write_missing_diff(difficulty, id, nc_dict[int(id)][0], out)
            else:
                out.write(line)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        exit(1)
    in_file = sys.argv[1]
    out_file = sys.argv[2]
    nc_db_file = sys.argv[3]
    with open(in_file, "rt") as file:
        diff_list = json.load(file)
    with open(nc_db_file, "rt") as file:
        nc_db = tomlkit.load(file)
    with open(out_file, "wt", encoding="utf8") as file:
        write_db(diff_list, nc_db, file)
    fix_pv_db.fix_db(out_file)
