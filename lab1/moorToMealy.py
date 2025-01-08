NAME_POINTS = "Q"
NAME_NEW_POINTS = "S"
NAME_OUTPUT_CH = "Y"
NUMBER_OUTPUT_CH = 0
NUMBER_POINTS = 1
SEPARATOR = ";"

reachable_points = dict()
class Ptr:
    def __init__(self, value):
        self.value: str = value
        self.next = dict()
        self.prev = dict()

def moore_to_mealy(input_file, output_file):
    lines = input_file.readlines()

    moore_mass = get_moore_mass(lines)
    points_with_transition = dict()

    #составляем переходы
    for i, point in enumerate(moore_mass[NAME_POINTS]):
        points_with_transition[point] = moore_mass[NAME_OUTPUT_CH][i]

    mealy_mass = dict()
    mealy_mass[NAME_POINTS] = []

    for i, line in enumerate(moore_mass):
        if line == NAME_OUTPUT_CH: continue
        if line == NAME_POINTS:
            for k, point in enumerate(moore_mass[line]):
                mealy_mass[line].append(point)
            continue
        for b, transition in enumerate(moore_mass[line]):
            if line not in mealy_mass: mealy_mass[line] = []
            mealy_mass[line].append(f"{transition}/{points_with_transition[transition]}")

    graph = dict()

    for i, ch in enumerate(mealy_mass[NAME_POINTS]):
        graph[ch] = Ptr(ch)

    for i, new_point in enumerate(mealy_mass[NAME_POINTS]):
        for k, ch in enumerate(mealy_mass):
            if k in range(0, 1): continue
            else:
                s = mealy_mass[ch][i]
                if get_q(s) not in graph: graph[get_q(s)] = Ptr(get_q(s))
                graph[new_point].next[get_q(s)] = graph[get_q(s)]
                graph[get_q(s)].prev[new_point] = graph[new_point]

    has_unreach = True
    while has_unreach:
        has_unreach = False
        new_graph = dict()
        for i, ptr in enumerate(graph):
            if ptr != mealy_mass[NAME_POINTS][0] and is_all_prev_not_valid(graph[ptr].prev, ptr):
                has_unreach = True
                for b, nextPtr in enumerate(graph[ptr].next):
                    del graph[nextPtr].prev[ptr]
            else:
                new_graph[ptr] = graph[ptr]
        graph = new_graph

    new_mealy_mass = dict()
    new_mealy_mass[NAME_POINTS] = []
    for i, ch in enumerate(mealy_mass[NAME_POINTS]):
        if ch not in graph: continue
        for k, line in enumerate(mealy_mass):
            if line not in new_mealy_mass: new_mealy_mass[line] = list()
            new_mealy_mass[line].append(mealy_mass[line][i])

    mealy_mass = new_mealy_mass

    for i, line in enumerate(mealy_mass):
        if line == NAME_POINTS:
            output_file.write(";")
        else: output_file.write(f"{line};")
        for k, ch in enumerate(mealy_mass[line]):
            if line == NAME_POINTS:
                output_file.write(ch)
                if k < len(mealy_mass[line]) - 1:
                    output_file.write(SEPARATOR)
                continue
            output_file.write(ch)
            if k < len(mealy_mass[line]) - 1:
                    output_file.write(SEPARATOR)
        output_file.write("\n")


def get_moore_mass(lines):
    mass = dict()
    output_ch_line = lines[NUMBER_OUTPUT_CH]
    points_line = lines[NUMBER_POINTS]

    temp = output_ch_line.strip().split(SEPARATOR)
    mass[NAME_OUTPUT_CH] = []
    for i, item in enumerate(temp):
        if item != "":
         mass[NAME_OUTPUT_CH].append(item)


    temp = points_line.strip().split(SEPARATOR)
    mass[NAME_POINTS] = []
    for i, item in enumerate(temp):
        if item != "":
            mass[NAME_POINTS].append(item)

    for i, line in enumerate(lines):
        if i in range(0,2): continue
        temp = line.strip().split(SEPARATOR)
        mass[temp[0]] = []
        for k, item in enumerate(temp):
            if k != 0:
                mass[temp[0]].append(item)
                reachable_points[item] = ""
    return mass

def get_q(tr: str):
    result = tr.split('/')[0]
    return result

def is_all_prev_not_valid(prevs, q):
    if len(prevs) == 0 or len(prevs) == 1 and q in prevs: return True
    return False