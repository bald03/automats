NAME_POINTS = "Q"
SEPARATOR = ";"
NAME_CLASS = "CLASS"
NAME_UNDERCLASS = "UNDERCLASS"
TAG_CLASS_A = "A"
TAG_CLASS_C = "C"
visited = set()
class Ptr:
    def __init__(self, value):
        self.value: str = value
        self.next = dict()
        self.prev = dict()


def mealy_transform_to_min(input_file, output_file):
    mealy_mass = get_mealy_mass(input_file)
    mealy_mass = remove_unreacheble_state(mealy_mass)
    min_mealy_mass = minimize_mealy_mass(mealy_mass)
    print_mealy(min_mealy_mass, output_file)



def remove_unreacheble_state(mealy_mass):
    graph = dict()

    for i, ch in enumerate(mealy_mass[NAME_POINTS]):
        graph[ch] = Ptr(ch)

    for i, new_point in enumerate(mealy_mass[NAME_POINTS]):
        for k, ch in enumerate(mealy_mass):
            if k in range(0, 1):
                continue
            else:
                s = mealy_mass[ch][i]
                if s[0] not in graph: graph[s[0]] = Ptr(s[0])
                graph[new_point].next[s[0]] = graph[s[0]]
                graph[s[0]].prev[new_point] = graph[new_point]

    first_q:Ptr
    for i, item in enumerate(graph):
        first_q = graph[item]
        break
    visited.add(first_q.value)
    dfs(first_q)

    new_mealy_mass = dict()
    new_mealy_mass[NAME_POINTS] = []
    for i, ch in enumerate(mealy_mass[NAME_POINTS]):
        if ch not in visited: continue
        for k, line in enumerate(mealy_mass):
            if line not in new_mealy_mass: new_mealy_mass[line] = list()
            new_mealy_mass[line].append(mealy_mass[line][i])

    return new_mealy_mass


def dfs(node: Ptr):
    for item in node.next:
        ptr = node.next[item]
        if item not in visited:
            visited.add(ptr.value)
            dfs(ptr)



def get_mealy_mass(input_file):
    lines = input_file.readlines()
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

def print_mealy(mealy_mass, output_file):
    for i, line in enumerate(mealy_mass):
        if line == NAME_POINTS:
            output_file.write(";")
        else:
            output_file.write(f"{line};")
        for k, ch in enumerate(mealy_mass[line]):
            if line == NAME_POINTS:
                output_file.write(ch)
                if k < len(mealy_mass[line]) - 1:
                    output_file.write(SEPARATOR)
                continue
            output_file.write(f"{ch[0]}/{ch[1]}")
            if k < len(mealy_mass[line]) - 1:
                output_file.write(SEPARATOR)
        output_file.write("\n")

def create_g_map(map_classes):
    g_map = dict()
    for index, line in enumerate(map_classes):
        clazz = f"{TAG_CLASS_C}{index}"
        for q in map_classes[line]:
            g_map[q] = clazz
    return g_map

def get_map_classes(mealy_mass, g_map):
    new_mealy_mass = dict()
    new_mealy_mass[NAME_POINTS] = []
    for index, line in enumerate(mealy_mass):
        for kIndex, p in enumerate(mealy_mass[line]):
            if line == NAME_POINTS:
                new_mealy_mass[NAME_POINTS].append(p)
                continue
            if line not in new_mealy_mass: new_mealy_mass[line] = []
            new_mealy_mass[line].append(g_map[p[0]])
    map_classes = dict()
    for column_index, point in enumerate(new_mealy_mass[NAME_POINTS]):
        line = ""
        for line_index, ch_line in enumerate(new_mealy_mass):
            if ch_line == NAME_POINTS: continue
            transition = new_mealy_mass[ch_line][column_index]
            line += f"{transition}/{mealy_mass[ch_line][column_index][1]};"
        if line not in map_classes: map_classes[line] = dict()
        map_classes[line][point] = ""

    return map_classes

def get_finish_map_classes(mealy_mass, g_map):
    find_finish = False
    map_classes = get_map_classes(mealy_mass, g_map)
    while not find_finish:
        new_g_map = create_g_map(map_classes)
        new_map_classes = get_map_classes(mealy_mass, new_g_map)
        if len(map_classes) == len(new_map_classes):
            find_finish = True
        map_classes = new_map_classes


    return map_classes

def minimize_mealy_mass(mealy_mass):
    map_classes = dict()
    for column_index, point in enumerate(mealy_mass[NAME_POINTS]):
        line = ""
        for line_index, ch_line in enumerate(mealy_mass):
            if ch_line == NAME_POINTS: continue
            transition = mealy_mass[ch_line][column_index]
            line += f"{transition[1]};"
        if line not in map_classes: map_classes[line] = dict()
        map_classes[line][point] = ""
    g_map = create_g_map(map_classes)

    map_classes = get_finish_map_classes(mealy_mass, g_map)

    g_map = create_g_map(map_classes)

    g_map_classes = dict()
    for index, line in enumerate(map_classes):
        clazz = f"{TAG_CLASS_C}{index}"
        for q in map_classes[line]:
            if clazz not in g_map_classes: g_map_classes[clazz] = []
            g_map_classes[clazz].append(q)

    min_mealy_mass = dict()
    min_mealy_mass[NAME_POINTS] = []
    for g_q in g_map_classes:
        min_mealy_mass[NAME_POINTS].append(g_q)
        first_q = g_map_classes[g_q][0]
        for index, line in enumerate(mealy_mass):
            for kIndex, p in enumerate(mealy_mass[line]):
                if line == NAME_POINTS: continue
                if mealy_mass[NAME_POINTS][kIndex] != first_q: continue
                q = p[0]
                s = p[1]
                if line not in min_mealy_mass: min_mealy_mass[line] = []
                c = [g_map[q], s]
                min_mealy_mass[line].append(c)

    return min_mealy_mass

def is_all_prev_not_valid(prevs, q):
    if len(prevs) == 0 or len(prevs) == 1 and q in prevs: return True
    return False