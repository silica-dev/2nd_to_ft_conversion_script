# Project DIVA 2nd/Extend to Future Tone Converter
This repository contains the scripts I used to port every song from 2nd/extend to MegaMix+ with the [New Classics mod](https://gamebanana.com/mods/596416). In total, the following scripts are provided:
* **fix_packaged.py**: fixes the Project DIVA 2nd scripts for *Packaged* to not use a double note.
* **create_transpose.py:** takes in a json database of script opcodes in the format of `"<id>":{"opcode":"<name>", "len": "<len>"}`, then converts it to one with entries in the format of `"<name>":{"opcode":"<id>", "len": "<len>"}` (internally called a "transpose").
* **ext_to_FT.py**: contains functions for loading and saving .dsc files when provided opcode databases as described above, as well as converting 2nd/extend style .dsc files to MM+ new classics style ones. When run as a script, it takes in a 2nd/extend .dsc file, strips all commands related to the PV rather than the chart, and outputs a converted file in MM+ new classics style.
* **generate_csv.py**: contains functions for generating the csv database of long note hold times required for New Classics to function. When run as a script, takes in a New Classics-style .dsc and generates a corresponding csv database.
* **mass_convert.py**: performs all required conversion steps for generating a New Classics-style mod of all 2nd/extend .dsc scripts in a given directory. Further details are explained in the [Usage](#usage) section.
* **mm_merge.py**: provides functions for merging two MegaMix+ .dsc files. when run as a script, takes in a script file (and optionally a manually-specific pv_id), then merges it with its corresponding script in `MM_script_database/`
* **difficulty_scraper**: contains two scripts, **download_list.py** and **extract_diff.py** which were used to scrape the Project DIVA fandom wiki for song difficulties

## Usage
The following parameters can be defined in **mass_convert.py** to change the behavior of mod generation:
* `EXT_FOLDER`: the folder which stores the files to be converted
* `OUT`: the folder to generate the mod in
* `DIFF_LIST`: a dictionary of difficulty names and their corresponding indicies in each entry of `star_conv.json`
* `PROFILE`: the conversion profile. currently, only `NO_CHANCE` is implemented
* `F2ND_COMPAT`: whether to generate the mod with compatibility with the F2nd song pack in mind. For this to work, the F2nd mod pack extreme chart of each overlapping song must be present in `F2nd_scripts`
* `IGNORE_NORMALIZE`: by default, every song is normalized such that the music starts playing at time zero. If that causes issues, add the song's MM+ id to this list.

To generate the mod with **mass_convert.py**, the following must be present for each chart to be converted:
* a 2nd/extend-styled chart in `EXT_FOLDER` titled in the format `pv_{song_id}_{song_difficulty}.dsc`
* the extreme MM+ script for that song in the `MM_script_database/` folder
* a conversion between that song's 2nd/ext ids to its MM+ id in `2nd_ext_to_ft.json`
* the star level for that chart's difficulty (organized by MM+ id) in `star_conv.json`, following the convention defined by `DIFF_LIST`.

## Manual Time Sync
You can specify manual time syncs in `timeshift.json`. A negative number increases the delay on notes, while a positive number decreases it. To Sync from two note times manually:
- Find two notes that occur on the same "beat" in a song
- Add the note start time and flight time together for the **2nd/extend** chart
- Add the note start time and flight time together for the **MM+/F2nd Pack** chart
- Subtract the latter from the former.

Some useful timeshifts have already been specified in this repository

## Limitations
* The F2nd compatible version *must* be loaded before the F2nd song pack to function properly.
* `mass_convert.py` does not generate a `config.toml` as is required by DivaModManager. There are no plans to change this
* If the MM+ script starts playing music after time 0, the produced script will very likely be off sync. This may be changed in the future if such a case is found
* many 2nd/extend charts are slightly off-sync. Manual adjustment is required.
* Some Ex. Extremes in the F2nd compatible version end their PVs at odd times. This is still being investigated

## Future Plans
| Item                                                                              | Planned Timeline                     | Current Progress |
|-----------------------------------------------------------------------------------|--------------------------------------|------------------|
| Better error handling and command line behavior                                   | Short-term goal                      | In Progress      |
| Better Code Documentation                                                         | Short-term goal                      | In Progress      |
| Compatibility with F/F2nd/X Chart Packs                                           | Short-term goal                      | Finished         |
| Fix Electric Angel                                                                | Short-term goal                      | Finished         |
| Fix Sync Errors                                                                   | Short-term goal                      | In Progress      |
| Fix PV End Times                                                                  | Short-term goal                      | In Progress      |
| YouTube Preview                                                                   | Short-term goal                      | to start soon    |
| GameBanana & DivaModArchive Publishing                                            | Short-term goal                      | Finished         |
| Chance Time version                                                               | Long-term goal                       | Finished    |
| Project DIVA 1st charts                                                           | Long-term goal                       | Not Started      |
| Port charts from 2nd DLC that do not have MM+ PVs (GO MY WAY!! & Relations)       | Long-term goal                       | Not Started      |

## Credits
`ft_opcodes.json` and `2nd_opcodes.json` were adapted from [nastys' DSC Studio](https://github.com/nastys/nastys.github.io/tree/master/dsceditor). The codebase was also used as reference for some functions in `ext_to_FT.py`. [Samyuu's](https://github.com/samyuu) ScriptEditor was also helpful in determining the implementation differences between some 2nd/extend opcodes and MM+ opcodes. Chart difficulty information in `star_conv.json` was largely provided by [The Project DIVA wiki on Fandom](project-diva.fandom.com).
