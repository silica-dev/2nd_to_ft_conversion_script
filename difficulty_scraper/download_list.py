import regex as re

with open("in.html", "rt") as file:
    li = file.readlines()
out = []
for line in li:
    match = re.search(r'<a href="([^=]+)"', line)
    if match is not None:
        out.append("https://project-diva.fandom.com" + match.group(1) + "\n")
out = set(out)

with open("out.txt", "wt") as file:
    file.writelines(out)
