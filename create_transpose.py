import json
import sys

if len(sys.argv) < 3:
    print("USAGE: create_transpose.py [input db] [output transpose db]")
    exit()

input = {}
with open(sys.argv[1]) as file:
    input = json.load(file)
output = {}
for name in input:
    new_key = input[name]["opcode"]
    new_value = {}
    new_value["opcode"] = name
    new_value["len"] = input[name]["len"]
    output[new_key] = new_value

with open(sys.argv[2], "wt") as file:
    json.dump(output, file)
