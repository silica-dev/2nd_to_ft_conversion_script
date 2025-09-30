import json
import os
import ext_to_FT
import re
import tomlkit

# constants
NO_CHANCE = 0
CHANCE_STAR = 1
FULL_F2ND = 2
CHALLENGE_TIME = 3

# parameters
EXT_FOLDER = "unpacked"
OUT = "2nd and extend chart pack - F2nd Compatible\\rom"
DIFF_LIST = {"easy": 0, "normal": 1, "hard": 2, "extreme": 3, "ex_extreme": 3}
PROFILE = CHALLENGE_TIME
F2ND_COMPAT = True
END_NORMALIZE = [85]
IGNORE_NORMALIZE = [211, 64, 86, 10]

def get_id(filename):
    base = os.path.basename(filename)
    match = re.search(r"pv_(\d+)_.*", base)
    if match is None:
        return None
    id = int(match.group(1))
    return id

def get_difficulty(filename):
    base = os.path.basename(filename)
    match = re.search(r"pv_\d+_(\w+)\.dsc", base)
    if match is None:
        return None
    difficulty = match.group(1)
    return difficulty


if __name__ == "__main__":
    nc_db = {}
    with open("2nd_opcodes.json", "rt") as file:
        ext_opcodes = json.load(file)
    with open("2nd_ext_to_ft.json", "rt") as file:
        id_conv = json.load(file)
    with open("star_conv.json", "rt") as file:
        star_conv = json.load(file)
    with open("f_opcodes_T.json", "rt") as file:
        f_opcodes_T = json.load(file)
    with open("compat_ignore.txt", "rt") as file:
        ex_list = [int(line.strip()) for line in file.readlines()]
    with open("timeshift.json", "rt") as file:
        timeshift = json.load(file)
    mm_scripts = os.listdir("MM_script_database")

    # get all scripts to convert
    dir_list = os.listdir(EXT_FOLDER)
    ext_isolate = ["TIME", "TARGET", "BAR_TIME_SET", "TARGET_FLYING_TIME", "END"]
    if PROFILE != NO_CHANCE:
        ext_isolate.append("MODE_SELECT")
        score_mode = "ARCADE"
    else:
        score_mode = "ARCADE"

    for script in dir_list:
        song_difficulty = get_difficulty(script)
        song_id_ext = f"{get_id(script)}"
        song_id = id_conv[f"{song_id_ext}"]
        if song_id in ex_list and F2ND_COMPAT:
            if song_difficulty == "extreme":
                song_difficulty = "ex_extreme"
            else:
                continue
        # convert script and merge it with megamix script
        with open(EXT_FOLDER + "\\" + script, "rb") as file:
            manual_norm = timeshift.get(f"{song_id}", None)
            if manual_norm is not None:
                manual_norm = (
                    manual_norm["f2nd"] if F2ND_COMPAT else manual_norm["normal"]
                )
            ext = ext_to_FT.load_dsc(
                file,
                ext_opcodes,
                False,
                ext_isolate,
                normalize=(song_id not in IGNORE_NORMALIZE),
                manual_norm=manual_norm,
            )
        ext = ext_to_FT.nc_convert(ext)
        # add to nc_db
        level = (
            star_conv[f"{song_id_ext}"][DIFF_LIST[song_difficulty]]
            if isinstance(song_difficulty, str)
            else "PV_LV_01_0"
        )
        if song_id not in nc_db.keys():
            nc_db[song_id] = {}
        nc_db[song_id][song_difficulty] = [
            {
                "style": "CONSOLE",
                "script_file_name": f"rom/script_nc//pv_{song_id}_{song_difficulty}.dsc",
                "level": level,
                "score_mode": score_mode,
            },
        ]
        if (
            song_difficulty != "ex_extreme"
            or f"pv_{song_id:03}_extreme_1.dsc" in mm_scripts
        ):
            nc_db[song_id][song_difficulty].append({"style": "ARCADE"})

        # write to folder
        with open(
            OUT + f"\\script_nc\\pv_{song_id}_{song_difficulty}.dsc", "wb"
        ) as file:
            ext_to_FT.print_dsc(file, ext, f_opcodes_T)
    # make the final nc_db
    final_db = {"songs": []}
    for id, params in nc_db.items():
        params["id"] = int(id)
        final_db["songs"].append(params)
    with open(OUT + "\\nc_db.toml", "w") as file:
        tomlkit.dump(final_db, file)
