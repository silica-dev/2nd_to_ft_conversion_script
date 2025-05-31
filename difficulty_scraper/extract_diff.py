import os
import regex as re
import json

FOLDER = "webpages"

pages = os.listdir(FOLDER)
with open("stars_to_level.json", "rt", encoding="utf-8") as file:
    star_conv = json.load(file)
diffs = {}
for page in pages:
    with open(FOLDER + "\\" + page, "rt", encoding="utf-8") as file:
        html = file.readlines()
    difficulties = []
    search_ready = False
    for line in html:
        if len(difficulties) >= 4:
            break
        if (
            line.find('id="Hatsune_Miku:_Project_DIVA_2nd"') > 0
            or line.find('id="Hatsune_Miku:_Project_DIVA_2nd/Extend"') > 0
        ):
            search_ready = True
        if search_ready:
            match = re.search("^[^★]*(★+☆*)$", line)
            if match is not None:
                difficulties.append(star_conv[match.groups(1)[0]])
    diffs[page] = difficulties

with open("star_conv_2nd.json", "wt", encoding="utf-8") as file:
    json.dump(diffs, file)
