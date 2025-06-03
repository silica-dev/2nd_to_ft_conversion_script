import sys
import ext_to_FT
import json
from mm_merge import get_id


# assumes commands only contains TIME, TARGET, and TARGET_FLYING_TIME commands
def get_note_time_by_index(commands, index):
    note_index = -1
    command_index = 0
    cur_time = 0
    cur_note = None
    cur_fly = None
    while note_index <= index:
        if commands[command_index][0] == "TIME":
            cur_time = commands[command_index][1][0]
        elif commands[command_index][0] == "TARGET_FLYING_TIME":
            cur_fly = commands[command_index][1][0]
        elif (
            commands[command_index][0] == "TARGET"
            and commands[command_index - 1][0] != "TARGET"
        ):
            note_index += 1
            cur_note = commands[command_index]
        command_index += 1
    if cur_note is None:
        return (cur_time, 0)
    if cur_fly is None and len(cur_note[1]) >= 10:
        cur_fly = cur_note[1][9]
    elif cur_fly is None:
        cur_fly = 0
    return (cur_time, cur_fly)


def get_delay(sync_commands, ref_commands, sync_index, ref_index):
    sync_time, sync_fly = get_note_time_by_index(sync_commands, sync_index)
    ref_time, ref_fly = get_note_time_by_index(ref_commands, ref_index)
    return sync_time + sync_fly - (ref_time + ref_fly)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        exit(1)
    syncfile = sys.argv[1]
    sync_index = int(sys.argv[2])
    ref_index = int(sys.argv[3])
    with open("2nd_opcodes.json") as file:
        ext_opcodes = json.load(file)
    with open("ft_opcodes.json") as file:
        ft_opcodes = json.load(file)
    with open("2nd_ext_to_ft.json") as file:
        id_conv = json.load(file)
    with open("basegame_to_f2nd.json") as file:
        f2nd_conv = json.load(file)

    ext_id = get_id(syncfile)
    mm_id = id_conv[f"{ext_id}"]
    f2nd_id = f2nd_conv[f"{mm_id}"]
    with open(syncfile, "rb") as file:
        sync_commands = ext_to_FT.load_dsc(
            file, ext_opcodes, filter=False, filterlist=["TIME", "TARGET"]
        )
    with open(f"MM_script_database\\pv_{mm_id:03}_extreme.dsc", "rb") as file:
        mm_commands = ext_to_FT.load_dsc(
            file,
            ft_opcodes,
            filter=False,
            filterlist=["TIME", "TARGET", "TARGET_FLYING_TIME"],
            prefix=1,
        )
    with open(f"F2nd_scripts\\pv_{f2nd_id}_extreme.dsc", "rb") as file:
        f2nd_commands = ext_to_FT.load_dsc(
            file,
            ft_opcodes,
            filter=False,
            filterlist=["TIME", "TARGET", "TARGET_FLYING_TIME"],
            prefix=1,
        )

    mm_delay = get_delay(sync_commands, mm_commands, sync_index, ref_index)
    # mm_delay = 0
    f2nd_delay = get_delay(sync_commands, f2nd_commands, sync_index, ref_index)
    print(
        f"""
          \"{mm_id}\":{{
                \"normal\": {mm_delay},
                \"f2nd\": {f2nd_delay}
              }}
          """
    )
