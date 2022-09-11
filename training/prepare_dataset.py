import argparse
import os
import uuid
import re

states = ["I", "Q", "A"]


def parse_commandline():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--in", required=True, help="path to raw data files")
    parser.add_argument("-o", "--out", required=True, help="output filename in csv format")

    return vars(parser.parse_args())


def generate_id(filename, qfilename, afilename):
    intent_id = 0
    state = states[0]

    with open(filename) as file:
        q_file = open(qfilename, "a+")
        a_file = open(afilename, "a+")

        for line in file.readlines():
            line = re.sub(",|\r|\n", " ", line.strip())

            if line.startswith("+++"):
                intent_id = 0
                state = states[0]

            elif line.startswith("000"):
                intent_id = uuid.uuid4()
                print("----------------")

            # question lines
            elif state == states[0] and line.startswith("---"):
                state = states[1]

            # answer line
            elif state == states[1] and line.startswith("---"):
                state = states[2]

            elif state == states[1]:
                print(f"Q: {intent_id}, {line}")
                q_file.write(f"\n{intent_id},{line}")

            elif state == states[2]:
                print(f"A: {intent_id}, {line}")
                a_file.write(f"\n{intent_id},{line}")

        file.close()
        q_file.close()
        a_file.close()


def main():
    opts = parse_commandline()  # get command line arguments
    print(opts)

    # delete existing files
    qfilename = opts["in"] + "/q_" + opts["out"]
    afilename = opts["in"] + "/a_" + opts["out"]

    with open(qfilename, "w") as file:
        file.write('"intent_id","keyword"')
        file.close()

    with open(afilename, "w") as file:
        file.write("intent_id,response")
        file.close()

    # list all files in in folder
    for (root, dir, filenames) in os.walk(opts["in"]):
        for filename in filenames:
            generate_id(os.path.join(root, filename), qfilename, afilename)


if __name__ == "__main__":
    main()
