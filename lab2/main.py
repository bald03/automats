import sys

from mealy import mealy_transform_to_min
from moore import moore_transform_to_min

COMMAND_MEALY = "mealy"
COMMAND_MOORE = "moore"


# program moore-to-mealy moore.csv mealy.csv
# program mealy-to-moore mealy.csv moore.csv
def main(args):
    command = COMMAND_MOORE
    input_file_name = "9_moore.csv"
    output_file_name = "1result.csv"
    input_file = open(input_file_name, "r")
    output_file = open(output_file_name, "w+")
    if command == COMMAND_MEALY:
        mealy_transform_to_min(input_file, output_file)
    if command == COMMAND_MOORE:
        moore_transform_to_min(input_file, output_file)


if __name__ == '__main__':
    main(sys.argv[1:])