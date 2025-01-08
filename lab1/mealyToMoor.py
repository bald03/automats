NAME_POINTS = "Q"
NAME_NEW_POINTS = "S"
NAME_OUTPUT_CH = "Y"
NAME_TRANSITION = "QT"
NUMBER_TRANSITION = 0
NUMBER_OUTPUT_CH = 2
NUMBER_POINTS = 1

SEPARATOR = ";"

class Ptr:
    def __init__(self, value):
        self.value: str = value
        self.next = dict()
        self.prev = dict()


def mealy_to_moore(input_file, output_file):
    lines = input_file.readlines()
    mealy_mass = get_mealy_mass(lines)
    input_characters, transitions = get_input_characters_with_transitions(mealy_mass)
    offset = 4
    moore_mass = dict()

    moore_mass[NAME_TRANSITION] = []
    moore_mass[NAME_POINTS] = []
    moore_mass[NAME_OUTPUT_CH] = []
    moore_mass[NAME_NEW_POINTS] = []

    count = 0
    for i, q in enumerate(mealy_mass[NAME_POINTS]):
        if q in transitions:
            for k, t in enumerate(transitions[q]):
                moore_mass[NAME_TRANSITION].append([q, t])
                moore_mass[NAME_POINTS].append(q)
                moore_mass[NAME_OUTPUT_CH].append(t)
                if count == 0: moore_mass[NAME_NEW_POINTS].append(q)
                else: moore_mass[NAME_NEW_POINTS].append("R" + str(count))
                count += 1

    for i, ch in enumerate(input_characters):
        moore_mass[ch] = []
    for i, line in enumerate(moore_mass):
        if i in range(0, offset): continue
        for k, _ in enumerate(moore_mass[NAME_TRANSITION]):
            moore_q = moore_mass[NAME_POINTS][k]
            moore_input_ch = line
            gq = get_q(
                    mealy_mass=mealy_mass,
                    moore_q=moore_q,
                    moore_input_ch=moore_input_ch
                )
            index = moore_mass[NAME_TRANSITION].index(gq)
            new_tr = moore_mass[NAME_NEW_POINTS][index]
            moore_mass[line].append(new_tr)


    graph = dict()

    for i, ch in enumerate(moore_mass[NAME_NEW_POINTS]):
        graph[ch] = Ptr(ch)

    for i, new_point in enumerate(moore_mass[NAME_NEW_POINTS]):
        for k, ch in enumerate(moore_mass):
            if k in range(0, offset):
                continue
            else:
                s = moore_mass[ch][i]
                if s not in graph: graph[s] = Ptr(s)
                graph[new_point].next[s] = graph[s]
                graph[s].prev[graph[new_point].value] = graph[new_point]


    has_unreach = True
    while has_unreach:
        has_unreach = False
        new_graph = dict()
        for i, ptr in enumerate(graph):
            if ptr != moore_mass[NAME_NEW_POINTS][0] and is_all_prev_not_valid(graph[ptr].prev, ptr):
                has_unreach = True
                for b, nextPtr in enumerate(graph[ptr].next):
                    del graph[nextPtr].prev[ptr]
            else: new_graph[ptr] = graph[ptr]
        graph = new_graph

    new_moore_mass = dict()
    new_moore_mass[NAME_TRANSITION] = []
    new_moore_mass[NAME_POINTS] = []
    new_moore_mass[NAME_OUTPUT_CH] = []
    new_moore_mass[NAME_NEW_POINTS] = []
    for i, ch in enumerate(moore_mass[NAME_NEW_POINTS]):
        if ch not in graph: continue
        for k, line in enumerate(moore_mass):
            if line not in new_moore_mass: new_moore_mass[line] = list()
            new_moore_mass[line].append(moore_mass[line][i])

    moore_mass = new_moore_mass


    for i, line in enumerate(moore_mass):
        if i in range(0, 2): continue
        if i in range(2, 4): output_file.write(SEPARATOR)
        else:
            output_file.write(line)
            output_file.write(SEPARATOR)
        count_separator = 0
        for k, ch in enumerate(moore_mass[line]):
            if line == NAME_OUTPUT_CH or line == NAME_NEW_POINTS:
                output_file.write(ch)
                count_separator += 1
                if count_separator < len(moore_mass[NAME_NEW_POINTS]):
                    output_file.write(SEPARATOR)
                continue
            output_file.write(ch)
            count_separator += 1
            if count_separator < len(moore_mass[NAME_NEW_POINTS]):
                output_file.write(SEPARATOR)
        output_file.write("\n")

def get_q(mealy_mass, moore_q, moore_input_ch):
    i = mealy_mass[NAME_POINTS].index(moore_q)
    q = mealy_mass[moore_input_ch][i]
    return q

def get_mealy_mass(lines):
    mass = dict()
    mass[NAME_POINTS] = []
    temp = lines[0].strip().split(SEPARATOR)
    for i, item in enumerate(temp):
        if item != "": mass[NAME_POINTS].append(item)

    for i, line in enumerate(lines):
        if i == 0: continue
        temp = line.strip().split(SEPARATOR)
        for k, t in enumerate(temp):
            if i > 0 and k > 0:
                temp[k] = t.strip().split("/")
            else: temp[k] = t
        mass[temp[0]] = []
        mass[temp[0]] = temp[1:]
    return mass

def get_input_characters_with_transitions(mass):
    input_characters = []
    transitions = dict()
    for i, key in enumerate(mass):
        if key_is_system_ch(key): continue
        input_characters.append(key)
        for k, transition in enumerate(mass[key]):
            if transition[0] not in transitions:
                transitions[transition[0]] = dict()
            transitions[transition[0]][transition[1]] = ""

    new_transitions = dict()

    first_q = mass[NAME_POINTS][0]

    if first_q not in transitions:
        new_transitions[first_q] = dict()
        new_transitions[first_q][""] = ""


    for k, transition in enumerate(transitions):
        new_transitions[transition] = dict()
        new_transitions[transition] = transitions[transition]

    return [input_characters, new_transitions]

def key_is_system_ch(key):
    if key in [NAME_NEW_POINTS, NAME_OUTPUT_CH, NAME_POINTS]: return True
    else: return False

def is_all_prev_not_valid(prevs, q):
    if len(prevs) == 0 or len(prevs) == 1 and q in prevs: return True
    return False