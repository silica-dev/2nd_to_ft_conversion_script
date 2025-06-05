import sys
import regex as re


def fix_db(filename):
    with open(filename, "rt", encoding="utf8") as file:
        lines = file.readlines()
    props_db = {}
    for line in lines:
        id = re.search(r"^pv_(\d+)\..*$", line)
        if id is None:
            # should be impossible
            return
        id = int(id.group(1))
        if id not in props_db.keys():
            props_db[id] = [line]
        else:
            props_db[id].append(line)
    # print in order
    with open(filename, "wt", encoding="utf8") as file:
        for id in sorted(props_db.keys()):
            file.writelines(props_db[id])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        exit(1)
    filename = sys.argv[1]
    fix_db(filename)
