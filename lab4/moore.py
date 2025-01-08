NAME_POINTS = "Q"
NAME_OUTPUT_CH = "Y"
NUMBER_OUTPUT_CH = 0
NUMBER_POINTS = 1
SEPARATOR = ";"
NAME_CLASS = "CLASS"
NAME_UNDERCLASS = "UNDERCLASS"
TAG_CLASS = "C"


class Ptr:
    def __init__(self, value):
        self.value: str = value
        self.next = dict()
        self.prev = dict()


def moore_transform_to_min(input_file, output_file):
    lines = input_file.readlines()
    moore_mass = get_moore_mass(lines)
    moore_mass = remove_unreacheble_state(moore_mass)
    moore_mass = minimize_moore_mass(moore_mass)

    print_moore(moore_mass, output_file)

visited = set()
def remove_unreacheble_state(moore_mass, is_uniq = True):
    graph = dict()

    for i, ch in enumerate(moore_mass[NAME_POINTS]):
        graph[ch] = Ptr(ch)

    for i, new_point in enumerate(moore_mass[NAME_POINTS]):
        for k, ch in enumerate(moore_mass):
            if k in range(0, 1):
                continue
            else:
                s = moore_mass[ch][i]
                if s != "":
                    temp = s.split(",")
                    if len(temp) > 1 and is_uniq:
                        if s not in graph: graph[s] = Ptr(s)
                        for item in temp:
                            if item not in graph: graph[item] = Ptr(item)
                            graph[new_point].next[item] = graph[item]
                            graph[item].prev[new_point] = graph[new_point]
                            graph[new_point].next[s] = graph[s]
                            graph[s].prev[new_point] = graph[new_point]
                    if s not in graph: graph[s] = Ptr(s)
                    graph[new_point].next[s] = graph[s]
                    graph[s].prev[new_point] = graph[new_point]


    first_q: Ptr

    for i, item in enumerate(graph):
        first_q = graph[item]
        break
    visited.add(first_q.value)
    dfs(first_q)

    new_moore_mass = dict()
    new_moore_mass[NAME_OUTPUT_CH] = []
    new_moore_mass[NAME_POINTS] = []
    for i, ch in enumerate(moore_mass[NAME_POINTS]):
        if ch not in visited or ch in new_moore_mass[NAME_POINTS]: continue
        for k, line in enumerate(moore_mass):
            if line not in new_moore_mass: new_moore_mass[line] = list()
            new_moore_mass[line].append(moore_mass[line][i])
    visited.clear()
    return  new_moore_mass

def dfs(node: Ptr):
    for item in node.next:
        if item not in visited:
            visited.add(item)
            dfs(node.next[item])

def minimize_moore_mass(moore_mass):
    map_classes = dict()
    for column_index, output_ch in enumerate(moore_mass[NAME_OUTPUT_CH]):
        if output_ch not in map_classes: map_classes[output_ch] = dict()
        map_classes[output_ch][moore_mass[NAME_POINTS][column_index]] = ""

    g_map = create_g_map(map_classes)

    map_classes = get_finish_map_classes(moore_mass, g_map)

    g_map = create_g_map(map_classes)

    g_map_classes = dict()
    for index, line in enumerate(map_classes):
        clazz = f"{TAG_CLASS}{index}"
        for q in map_classes[line]:
            if clazz not in g_map_classes: g_map_classes[clazz] = []
            g_map_classes[clazz].append(q)

    min_moore_mass = dict()
    min_moore_mass[NAME_OUTPUT_CH] = []
    min_moore_mass[NAME_POINTS] = []
    for g_q in g_map_classes:
        min_moore_mass[NAME_POINTS].append(g_q)
        first_q = g_map_classes[g_q][0]
        min_moore_mass[NAME_OUTPUT_CH].append(moore_mass[NAME_OUTPUT_CH][moore_mass[NAME_POINTS].index(first_q)])

        for index, line in enumerate(moore_mass):
            for kIndex, p in enumerate(moore_mass[line]):
                if line == NAME_POINTS or line == NAME_OUTPUT_CH: continue
                if moore_mass[NAME_POINTS][kIndex] != first_q: continue
                if line not in min_moore_mass: min_moore_mass[line] = []
                if p == "":
                    min_moore_mass[line].append(p)
                    continue
                c = g_map[p]
                min_moore_mass[line].append(c)


    return min_moore_mass

def get_finish_map_classes(moore_mass, g_map):
    find_finish = False
    map_classes = get_map_classes(moore_mass, g_map)
    count_finish = 0
    expected_count_finish = 3
    while count_finish != expected_count_finish:
        new_g_map = create_g_map(map_classes)
        new_map_classes = get_map_classes(moore_mass, new_g_map)
        if len(map_classes) == len(new_map_classes):
            count_finish += 1
        map_classes = new_map_classes

    return map_classes

def get_map_classes(moore_mass, g_map):
    new_moore_mass = dict()
    new_moore_mass[NAME_OUTPUT_CH] = []
    new_moore_mass[NAME_POINTS] = []
    for index, line in enumerate(moore_mass):
        for kIndex, p in enumerate(moore_mass[line]):
            if p == "":
                if line not in new_moore_mass: new_moore_mass[line] = []
                new_moore_mass[line].append(p)
                continue
            if line == NAME_OUTPUT_CH:
                new_moore_mass[NAME_OUTPUT_CH].append(p)
                continue
            if line == NAME_POINTS:
                new_moore_mass[NAME_POINTS].append(p)
                continue
            if line not in new_moore_mass: new_moore_mass[line] = []
            new_moore_mass[line].append(g_map[p])
    map_classes = dict()
    for column_index, point in enumerate(new_moore_mass[NAME_POINTS]):
        line = ""
        for line_index, ch_line in enumerate(new_moore_mass):
            if ch_line == NAME_POINTS: continue
            transition = new_moore_mass[ch_line][column_index]
            line += f"{transition};"
        if line not in map_classes: map_classes[line] = dict()
        map_classes[line][point] = ""
    return map_classes

def create_g_map(map_classes):
    g_map = dict()
    for index, line in enumerate(map_classes):
        clazz = f"{TAG_CLASS}{index}"
        for q in map_classes[line]:
            g_map[q] = clazz
    return g_map

def get_moore_mass(lines):
    mass = dict()
    output_ch_line = lines[NUMBER_OUTPUT_CH]
    points_line = lines[NUMBER_POINTS]

    temp = output_ch_line.strip().split(SEPARATOR)
    mass[NAME_OUTPUT_CH] = []
    for i, item in enumerate(temp):
        if i != 0:
            mass[NAME_OUTPUT_CH].append(item)

    temp = points_line.strip().split(SEPARATOR)
    mass[NAME_POINTS] = []
    for i, item in enumerate(temp):
        if item != "":
            mass[NAME_POINTS].append(item)

    for i, line in enumerate(lines):
        if i in range(0, 2): continue
        temp = line.strip().split(SEPARATOR)
        mass[temp[0]] = []
        for k, item in enumerate(temp):
            if k != 0:
                mass[temp[0]].append(item)
    return mass

def print_moore(moore_mass, output_file):
    file = open(output_file, "w+", encoding="utf-8")
    for i, line in enumerate(moore_mass):
        if i in range(0, 2): file.write(SEPARATOR)
        else:
            file.write(line)
            file.write(SEPARATOR)
        count_separator = 0
        for k, ch in enumerate(moore_mass[line]):
            if line == NAME_OUTPUT_CH or line == NAME_POINTS:
                file.write(ch)
                count_separator += 1
                if count_separator < len(moore_mass[NAME_POINTS]):
                    file.write(SEPARATOR)
                continue
            file.write(ch)
            count_separator += 1
            if count_separator < len(moore_mass[NAME_POINTS]):
                file.write(SEPARATOR)
        file.write("\n")

def is_all_prev_not_valid(prevs, q):
    if len(prevs) == 0 or len(prevs) == 1 and q in prevs: return True
    return False