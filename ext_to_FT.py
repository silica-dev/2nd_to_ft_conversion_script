import sys
import json


# loads a dsc file as plaintext. adapted from nastys' editor
# arguments:
#   - input: input file pointer
#   - filter=True: whether to filter (True) or isolate (False)
#   - filterList=[]: list of items to filter/isolate
#   - opcode_dict: dict of opcode names and parameter numbers
def load_dsc(
    input,
    opcode_dict,
    filter=True,
    filterlist=[],
    prefix=0,
    normalize=False,
    manual_norm=None,
):
    for _ in range(prefix):
        input.read(4)
    output = []
    opcode = input.read(4)
    cur_time = 0
    music_start = 0
    while opcode != b"":
        opnum = int.from_bytes(opcode, byteorder="little", signed=True)
        if f"{opnum}" not in opcode_dict.keys():
            return None
        args = [
            int.from_bytes(input.read(4), byteorder="little", signed=True)
            for _ in range(opcode_dict[f"{opnum}"]["len"])
        ]
        name = opcode_dict[f"{opnum}"]["opcode"]
        if name == "TIME":
            cur_time = args[0]
        if name == "MUSIC_PLAY":
            music_start = cur_time
        if filter ^ (name in filterlist):
            output.append([name, args])
        opcode = input.read(4)
    if manual_norm == None:
        manual_norm = music_start
    if normalize:
        return normalize_times(output, manual_norm)
    return output


def normalize_times(commands, start_time):
    new_list = []
    for command in commands:
        if command[0] == "TIME":
            command[1][0] -= start_time
            if command[1][0] >= 0:
                new_list.append(command)
        else:
            new_list.append(command)
    return new_list


def convert_2nd_target(command):
    command[1][1] = command[1][3]
    command[1][2] = command[1][4]
    command[1][3] = command[1][5]
    command[1][4] = command[1][7]
    command[1][5] = command[1][8]
    command[1].pop()
    command[1].pop()
    command[1].pop()
    command[1].pop()
    return command


def print_dsc(fp, script, opcode_dict_T, prefix=bytearray([23, 37, 18, 21])):
    # version specifier
    fp.write(prefix)
    for command in script:
        opcode = opcode_dict_T[command[0]]["opcode"]
        fp.write(int(opcode).to_bytes(4, "little", signed=True))
        for i in range(opcode_dict_T[command[0]]["len"]):
            fp.write(command[1][i].to_bytes(4, "little", signed=True))


# converts 2nd/extend charts to new classics style and strips unused times
def nc_convert(input):
    output = []
    prev_command = [None, None]
    cur_flight_time = 0
    for command in input:
        match command[0]:
            case "TIME":
                if prev_command[0] == "TIME":
                    output.pop()
                output.append(command)
                prev_command = command
                pass
            case "TARGET":
                if command[1][9] != cur_flight_time:
                    cur_flight_time = command[1][9]
                    output.append(["TARGET_FLYING_TIME", [cur_flight_time]])
                match command[1][0]:
                    # arrows
                    case 6:
                        command[1][0] = 31
                    case 4:
                        command[1][0] = 29
                    case 5:
                        command[1][0] = 30
                    case 7:
                        command[1][0] = 32
                    # longs
                    case 8:
                        command[1][0] = 33
                    case 9:
                        command[1][0] = 34
                    case 10:
                        command[1][0] = 35
                    case 11:
                        command[1][0] = 36
                command = convert_2nd_target(command)
                output.append(command)
                prev_command = command
            case "MODE_SELECT":
                match command[1]:
                    case [3, 1]:
                        command[1] = [31, 1]
                    case [3, 3]:
                        command[1] = [31, 3]
                    case _:
                        continue
                output.append(command)
                prev_command = command
            case _:
                output.append(command)
                prev_command = command
    return output


if __name__ == "__main__":
    if len(sys.argv) < 3:
        exit()
    # load the 2nd/extend opcode list
    second_db = {}
    with open("2nd_opcodes.json", "rt") as file:
        second_db = json.load(file)
    parsed_input = []

    # load the 2nd/extend chart
    with open(sys.argv[1], "rb") as input:
        parsed_input = load_dsc(
            input,
            second_db,
            False,
            [
                "TIME",
                "MODE_SELECT",
                "TARGET",
                "END",
                "BAR_TIME_SET",
                "TARGET_FLYING_TIME",
            ],
            normalize=True,
        )
    # convert target numbers and chance time to new classics style
    # also filters unused times
    classic_ver = nc_convert(parsed_input)

    ft_db_T = {}
    with open("ft_opcodes_T.json", "rt") as file:
        ft_db_T = json.load(file)

    with open(sys.argv[2], "wb") as file:
        print_dsc(file, classic_ver, ft_db_T)
