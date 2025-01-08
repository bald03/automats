import sys

from mealy import mealy_transform_to_min
from moore import moore_transform_to_min

COMMAND_MEALY = "mealy"
COMMAND_MOORE = "moore"


# program moore-to-mealy moore.csv mealy.csv
# program mealy-to-moore mealy.csv moore.csv
def main(args):
    command = args[0]
    input_file_name = args[1]
    output_file_name = args[2]
    input_file = open(input_file_name, "r")
    output_file = open(output_file_name, "w+")
    if command == COMMAND_MEALY:
        mealy_transform_to_min(input_file, output_file)

    if command == COMMAND_MOORE:
        moore_transform_to_min(input_file, output_file)
    output_file.close()


if __name__ == '__main__':
    main(sys.argv[1:])