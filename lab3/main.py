import sys
import re

#grammar.txt output.csv

NEW_NAME = "Q"
LEFT = r"^\s*<(\w+)>\s*->\s*((?:<\w+>\s+)?[\wε](?:\s*\|\s*(?:<\w+>\s+)?[\wε])*)\s*$"
RIGHT = r"^\s*<(\w+)>\s*->\s*([\wε](?:\s+<\w+>)?(?:\s*\|\s*[\wε](?:\s+<\w+>)?)*)\s*$"

SOSTOYANIE = r"^\s*<(\w+)>\s*->"
PEREHODI = r"([\wε](?:\s+<\w+>)?(?:\s*\|\s*[\wε](?:\s+<\w+>)?)*)$"

SEPARATOR = ";"
END_STATE = "F"

NAME_STATE = "STATE"

EMPTY_TRS = ""

is_left = False

def read_grammar(input_file):
    global is_left
    lines = input_file.readlines()

    current_rule = ""
    rules = []

    old_line = ""
    for k, line in enumerate(lines):
        line = line.replace("\n", "")
        line = line.strip()
        if not line:
            continue
        if current_rule and old_line.endswith("|"):
            current_rule += " " + line
        else:
            if current_rule:
                rules.append(current_rule)
            current_rule = line
        old_line = line
    if current_rule:
        rules.append(current_rule)

    grammar = dict()


    for i, rule in enumerate(rules):
        matches = re.findall(RIGHT, rule)
        if not matches:
            is_left = True
            matches = re.findall(LEFT, rule)
        name = matches[0][0]
        grammar[name] = []
        p = matches[0][1].split("|")
        for s in p:
            grammar[name].append(s.strip())

    return grammar

def prepare_left_grammar(grammar, output_file):
    matrix = dict()
    matrix[NAME_STATE] = dict()

    last_index = 0
    for index, (key, value) in enumerate(reversed(list(grammar.items()))):
        matrix[NAME_STATE][key] = f"{NEW_NAME}{index + 1}"

    final_state = NEW_NAME + str(last_index)
    matrix[NAME_STATE][final_state] = f"{final_state}"
    matrix[NAME_STATE] = dict(sorted(matrix[NAME_STATE].items(), key=lambda item: item[1]))
    for index, line in enumerate(grammar):
        for k, tr in enumerate(grammar[line]):
            transition = tr.strip().split(" ")

            if len(transition) == 1:
                ch = transition[0]
                from_state = final_state
                in_state = matrix[NAME_STATE][line]

                new_index = list(matrix[NAME_STATE].keys()).index(from_state)

                if ch not in matrix:
                    matrix[ch] = []
                    for _ in matrix[NAME_STATE]:
                        matrix[ch].append(EMPTY_TRS)

                if matrix[ch][new_index] == EMPTY_TRS:
                    matrix[ch][new_index] = in_state
                else:
                    matrix[ch][new_index] = f"{matrix[ch][new_index]},{in_state}"

            else:
                ch = transition[1]
                old_name = transition[0].replace("<", "").replace(">", "")
                in_state = matrix[NAME_STATE][line]

                if ch not in matrix:
                    matrix[ch] = []
                    for _ in matrix[NAME_STATE]:
                        matrix[ch].append(EMPTY_TRS)

                new_index = list(matrix[NAME_STATE].keys()).index(old_name)

                if matrix[ch][new_index] == EMPTY_TRS:
                    matrix[ch][new_index] = in_state
                else:
                    matrix[ch][new_index] = f"{matrix[ch][new_index]},{in_state}"

    for index, line in enumerate(matrix[NAME_STATE]):
        if index < len(matrix[NAME_STATE]): output_file.write(SEPARATOR)
    output_file.write(END_STATE)
    output_file.write("\n")

    for line in matrix:
        if line != NAME_STATE: output_file.write(line)
        for k, ch in enumerate(matrix[line]):
            if line == NAME_STATE:
                if k < len(matrix[line]):  output_file.write(SEPARATOR)
                output_file.write(matrix[line][ch])
            else:
                if k < len(matrix[line]): output_file.write(SEPARATOR)
                output_file.write(ch)

        output_file.write("\n")

def prepare_right_grammar(grammar, output_file):
    matrix = dict()
    matrix[NAME_STATE] = dict()

    last_index = 0
    for index, line in enumerate(grammar):
        matrix[NAME_STATE][line] = f"{NEW_NAME}{index}"
        last_index = index

    final_state = NEW_NAME + str(last_index + 1)
    matrix[NAME_STATE][final_state] = f"{final_state}"
    for index, line in enumerate(grammar):
        for k, tr in enumerate(grammar[line]):
            transition = tr.strip().split(" ")

            if len(transition) == 1:
                ch = transition[0]
                state = final_state
                if ch not in matrix:
                    matrix[ch] = []
                    for b in matrix[NAME_STATE]:
                        matrix[ch].append(EMPTY_TRS)

                if matrix[ch][index] == EMPTY_TRS: matrix[ch][index] = state
                else: matrix[ch][index] = f"{matrix[ch][index]},{state}"

            else:
                ch = transition[0]
                state = transition[1].replace("<", "").replace(">", "")
                state = matrix[NAME_STATE][state]

                if ch not in matrix:
                    matrix[ch] = []
                    for _ in matrix[NAME_STATE]:
                        matrix[ch].append(EMPTY_TRS)

                if matrix[ch][index] == EMPTY_TRS: matrix[ch][index] = state
                else: matrix[ch][index] = f"{matrix[ch][index]},{state}"

    for index, line in enumerate(matrix[NAME_STATE]):
        if index < len(matrix[NAME_STATE]): output_file.write(SEPARATOR)
    output_file.write(END_STATE)
    output_file.write("\n")

    for line in matrix:
        if line != NAME_STATE: output_file.write(line)
        for k, ch in enumerate(matrix[line]):
            if line == NAME_STATE:
                if k < len(matrix[line]):  output_file.write(SEPARATOR)
                output_file.write(matrix[line][ch])
            else:
                if k < len(matrix[line]): output_file.write(SEPARATOR)
                output_file.write(ch)

        output_file.write("\n")



def main(args):
    input_file_name = args[0]
    output_file_name = args[1]
    #input_file_name = "lg1.lg"
    #output_file_name = "output.csv"
    input_file = open(input_file_name, "r",  encoding="utf-8")
    output_file = open(output_file_name, "w+", encoding="utf-8")

    grammar = read_grammar(input_file)
    if is_left: prepare_left_grammar(grammar, output_file)
    else: prepare_right_grammar(grammar, output_file)

    output_file.close()

if __name__ == '__main__':
    main(sys.argv[1:])

