import ext_to_FT
import sys
import os
import re
import json

GLOBAL = 0
FAILURE = 1
SUCCESS = 2


def get_id(filename):
    base = os.path.basename(filename)
    match = re.search(r"pv_(\d+)_.*", base)
    if match is None:
        return None
    id = int(match.group(1))
    return id


def isolate_failure(commands):
    cur_branch = GLOBAL
    out = []
    for command in commands:
        if command[0] == "PV_BRANCH_MODE":
            cur_branch = command[1][0]
            if command[1][0] == 0:
                out.append(command)
        elif cur_branch == GLOBAL or cur_branch == FAILURE:
            out.append(command)
    return out


def mm_merge(filename, id=None, ext_commands=None, f2nd_id=None, end_normalize=False):
    if id is None:
        id = get_id(filename)
    # predefined jsons
    id_conv = {}
    ft_opcodes = {}
    with open("2nd_ext_to_ft.json") as file:
        id_conv = json.load(file)
    with open("ft_opcodes.json") as file:
        ft_opcodes = json.load(file)

    id = id_conv[f"{id}"]

    mm_filename = f"MM_script_database\\pv_{id:03}_extreme.dsc"
    if f2nd_id is not None:
        mm_filename = f"F2nd_scripts\\pv_{f2nd_id}_extreme.dsc"
    mm_commands = []
    if ext_commands is None:
        with open(filename, "rb") as file:
            ext_commands = ext_to_FT.load_dsc(
                file, ft_opcodes, filterlist=["END"], prefix=1
            )
            if ext_commands is None:
                return
    with open(mm_filename, "rb") as file:
        filterlist = [
            "MODE_SELECT",
            "TARGET",
            "TARGET_FLYING_TIME",
            "END",
        ]
        if end_normalize:
            filterlist.append("PV_END_FADEOUT")

        mm_commands = ext_to_FT.load_dsc(
            file,
            ft_opcodes,
            filterlist=filterlist,
            prefix=1,
        )
        if mm_commands is None:
            return
    # isolate failure branch
    mm_commands = isolate_failure(mm_commands)
    # convert to stacks
    ext_commands.reverse()
    mm_commands.reverse()
    out = []
    while len(ext_commands) > 0 or len(mm_commands) > 0:
        if len(ext_commands) == 0:
            out.append(mm_commands.pop())
        elif len(mm_commands) == 0:
            out.append(ext_commands.pop())
        elif mm_commands[-1][0] != "TIME":
            out.append(mm_commands.pop())
        elif ext_commands[-1][0] != "TIME":
            out.append(ext_commands.pop())
        elif mm_commands[-1][1][0] <= ext_commands[-1][1][0]:
            out.append(mm_commands.pop())
        else:
            out.append(ext_commands.pop())
    if end_normalize:
        pv_end_index = out.index(["PV_END", []])
        time_index = pv_end_index
        while out[time_index][0] != "TIME":
            time_index -= 1
        time = out[time_index][1][0]
        temp = out[time_index:]
        out = out[:time_index]
        out.append(["TIME", [time - 100000]])
        out.append(["PV_END_FADEOUT", [1000, 0]])
        out.extend(temp)
    out.append(["END", []])
    return out


if __name__ == "__main__":
    merged = []
    if len(sys.argv) == 3:
        merged = mm_merge(sys.argv[1])
    elif len(sys.argv) == 4:
        merged = mm_merge(sys.argv[1], int(sys.argv[3]))
    else:
        exit(1)
    ft_opcodes_T = {}
    with open("ft_opcodes_T.json") as file:
        ft_opcodes_T = json.load(file)
    with open(sys.argv[2], "wb") as file:
        ext_to_FT.print_dsc(file, merged, ft_opcodes_T)
