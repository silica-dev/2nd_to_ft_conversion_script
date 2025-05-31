import ext_to_FT
import sys
import os
import re
import json


def get_id(filename):
    base = os.path.basename(filename)
    match = re.search(r"pv_(\d+)_.*", base)
    if match is None:
        return None
    id = int(match.group(1))
    return id


def mm_merge(filename, id=None, ext_commands=None):
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
    mm_commands = []
    if ext_commands is None:
        with open(filename, "rb") as file:
            ext_commands = ext_to_FT.load_dsc(
                file, ft_opcodes, filterlist=["END"], prefix=1
            )
            if ext_commands is None:
                return
    with open(mm_filename, "rb") as file:
        mm_commands = ext_to_FT.load_dsc(
            file,
            ft_opcodes,
            filterlist=[
                "MODE_SELECT",
                "TARGET",
                "TARGET_FLYING_TIME",
                "BAR_TIME_SET",
                "END",
            ],
            prefix=1,
        )
        if mm_commands is None:
            return
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
