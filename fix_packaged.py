import ext_to_FT
import json

with open("2nd_opcodes.json", "rt") as file:
    opcodes = json.load(file)
with open("2nd_opcodes_T.json", "rt") as file:
    opcodes_T = json.load(file)

for difficulty in ["normal", "hard", "extreme"]:

    with open("unpacked\\pv_09_" + difficulty + ".dsc", "rb") as file:
        commands = ext_to_FT.load_dsc(file, opcodes)
    if commands is None:
        continue
    out = []
    command_ptr = 0
    while command_ptr < len(commands):
        if (
            commands[command_ptr][0] == "TARGET"
            and commands[command_ptr + 1][0] == "TARGET"
        ):
            # found the double target
            time_cmd = out.pop()
            commands[command_ptr][1][9] += 10
            new_first_time = ["TIME", [time_cmd[1][0] - 10]]
            out.append(new_first_time)
            out.append(commands[command_ptr])
            out.append(time_cmd)
        else:
            out.append(commands[command_ptr])
        command_ptr += 1
    with open("unpacked\\pv_09_" + difficulty + ".dsc", "wb") as file:
        ext_to_FT.print_dsc(file, out, opcodes_T, prefix=bytearray())
