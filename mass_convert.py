import json
import os
import ext_to_FT
import mm_merge
import regex as re
import generate_csv
import tomlkit

# constants
NO_CHANCE = 0
CHANCE_STAR = 1
FULL_F2ND = 2

# parameters
EXT_FOLDER = "unpacked"
OUT = "2nd and extend chart pack - No Chance Time\\rom"
DIFF_LIST = {"easy": 0, "normal": 1, "hard": 2, "extreme": 3}
PROFILE = NO_CHANCE


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
    with open("ft_opcodes_T.json", "rt") as file:
        ft_opcodes_T = json.load(file)
    # get all scripts to convert
    dir_list = os.listdir(EXT_FOLDER)
    ext_isolate = [
        "TIME",
        "TARGET",
        "BAR_TIME_SET",
        "TARGET_FLYING_TIME",
    ]
    if PROFILE != NO_CHANCE:
        ext_isolate.append("MODE_SELECT")
        score_mode = "F2ND"
    else:
        score_mode = "ARCADE"

    for script in dir_list:
        # convert script and merge it with megamix script
        with open(EXT_FOLDER + "\\" + script, "rb") as file:
            ext = ext_to_FT.load_dsc(
                file, ext_opcodes, False, ext_isolate, normalize=True
            )
        ext = ext_to_FT.nc_convert(ext)
        merged = mm_merge.mm_merge(script, ext_commands=ext)
        song_id_ext = f"{mm_merge.get_id(script)}"
        song_id = id_conv[f"{song_id_ext}"]
        song_difficulty = get_difficulty(script)
        if merged is None:
            print(
                f"WARNING: PV_{song_id}_{song_difficulty} could not be converted or merged"
            )
            continue
        # add to nc_db
        level = (
            star_conv[f"{song_id_ext}"][DIFF_LIST[song_difficulty]]
            if isinstance(song_difficulty, str)
            else "PV_LV_01_0"
        )
        if song_id not in nc_db.keys():
            nc_db[song_id] = {}
        nc_db[song_id][song_difficulty] = [
            {"style": "ARCADE"},
            {
                "style": "CONSOLE",
                "script_file_name": f"rom/script_nc/pv{song_id}/pv_{song_id}_{song_difficulty}.dsc",
                "level": level,
                "score_mode": score_mode,
            },
        ]
        # write to folder
        os.makedirs(OUT + f"\\script_nc\\pv{song_id}", exist_ok=True)
        with open(
            OUT + f"\\script_nc\\pv{song_id}\\pv_{song_id}_{song_difficulty}.dsc", "wb"
        ) as file:
            ext_to_FT.print_dsc(file, merged, ft_opcodes_T)
        generate_csv.make_lengths(
            merged,
            OUT + f"\\script_nc\\pv{song_id}\\pv_{song_id:}_{song_difficulty}.csv",
        )

    # make the final nc_db
    final_db = {"songs": []}
    for id, params in nc_db.items():
        params["id"] = int(id)
        final_db["songs"].append(params)
    with open(OUT + "\\nc_db.toml", "w") as file:
        tomlkit.dump(final_db, file)
