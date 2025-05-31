import ext_to_FT
import sys
import json


def make_lengths(input, filename):
    with open(filename, "wt", newline="\n") as file:
        # generate header
        file.write("index,sub_index,length,end\n")
        input.reverse()
        cur_time = 0
        index_counter = 0
        while len(input) > 0:
            new = input.pop()
            if new[0] == "TIME":
                cur_time = new[1][0]
            elif new[0] == "TARGET" and new[1][0] in [33, 34, 35, 36]:
                # seek to end target
                end = input.pop()
                end_time = cur_time
                while end[0] != "TARGET":
                    if end[0] == "TIME":
                        end_time = end[1][0]
                    end = input.pop()
                file.write(f"{index_counter},0,{(end_time - cur_time) / 100},0\n")
                file.write(f"{index_counter + 1},0,0.0,1\n")
                index_counter += 2
            elif new[0] == "TARGET":
                index_counter += 1
    pass


if __name__ == "__main__":
    if len(sys.argv) != 3:
        exit(1)
    ft_dict = {}
    with open("ft_opcodes.json", "rt") as file:
        ft_dict = json.load(file)
    input = []
    with open(sys.argv[1], "rb") as file:
        input = ext_to_FT.load_dsc(
            file, ft_dict, filter=False, filterlist=["TIME", "TARGET"], prefix=1
        )
    make_lengths(input, sys.argv[2])
