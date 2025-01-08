import sys

from moore import moore_transform_to_min, remove_unreacheble_state, SEPARATOR

LINE_END = "Y"
LINE_STATES = "Q"
LINE_CH = "LINE_CH"
EMPTY_CH = "ε"
NAME_END = "F"
Q_SEPARATOR = ","
NAME_NEW_Q = "S"
end_state = []


def mockOutput(table):
    for i, b in enumerate(table):
        print(i, b, table[b])

def read_nfa(input_file):
    global end_state
    lines = input_file.readlines()
    automat = dict()
    automat[LINE_END] = []
    automat[LINE_STATES] = []
    index_end_state = []
    for index, line in enumerate(lines):
        if index == 0:
            for i, ch in enumerate(line.strip().split(";")):
                if i != 0: automat[LINE_END].append(ch)
                if ch == NAME_END:
                    index_end_state.append(i)
        else:
            if index == 1:
                for i, ch in enumerate(line.strip().split(";")):
                    if i != 0: automat[LINE_STATES].append(ch)
                    if i in index_end_state: end_state.append(ch)
            else:
                first_ch = line.strip().split(";")[0]
                for i, ch in enumerate(line.strip().split(";")):
                    if i == 0: automat[first_ch] = []
                    else: automat[first_ch].append(ch)
    automat =  remove_unreacheble_state(automat)
    new_automat = dict()
    for line in automat:
        if line == LINE_END or line == LINE_STATES:
            new_automat[line] = automat[line]
            continue
        delete = True
        for tr in automat[line]:
            if tr != "":
                delete = False
        if not delete:
            new_automat[line] = automat[line]
    automat = new_automat
    return automat

def add_empty_tr(qs, empty_transition):
    find_new_q = True
    new_qs = qs.copy()
    while find_new_q:
        find_new_q = False
        for i in qs:
            if i in empty_transition:
                for b in empty_transition[i]:
                    if b not in new_qs:
                        new_qs.append(b)
                        find_new_q = True
        qs = new_qs
    return qs


def determinate(nfa_automat, output_file):
    empty_transitions = dict()
    global end_state
    start_q = nfa_automat[LINE_STATES][0]
    if EMPTY_CH in nfa_automat:
        for index, ch in enumerate(nfa_automat[LINE_STATES]):
            empty_transitions[ch] = []
            empty_transitions[ch].append(ch)
            empty_tr = nfa_automat[EMPTY_CH][index]
            if empty_tr != "":
                empty_tr = empty_tr.split(Q_SEPARATOR)
                for tr in empty_tr:
                    if tr != "":
                        if tr not in empty_transitions[ch]: empty_transitions[ch].append(tr)
                        for i in empty_transitions:
                            if ch in empty_transitions[i] and tr not in empty_transitions[i]:
                                empty_transitions[i].append(tr)
        for item in empty_transitions:
            for item2 in empty_transitions[item]:
                if item2 in end_state: end_state.append(item)
        start_q = list(empty_transitions.items())[0][1]
        start_q = Q_SEPARATOR.join(map(str, start_q))
    table = dict()
    table[LINE_CH] = []

    for ch in nfa_automat:
        if ch == LINE_END or ch == LINE_STATES or ch == EMPTY_CH: continue
        table[LINE_CH].append(ch)

    table[start_q] = []
    
    find_new_q = True
    finded_q = dict()
    finded_q[start_q] = False
    while find_new_q:
        find_new_q = False
        new_finded_q = finded_q.copy()
        for index, item in enumerate(finded_q):
            if finded_q[item]: continue
            table[item] = []
            for i in range(0, len(table[LINE_CH])):
                table[item].append("")
            qs = item.split(Q_SEPARATOR)
            qs = add_empty_tr(qs.copy(), empty_transitions)
            for q in qs:
                for kindex, ch in enumerate(table[LINE_CH]):
                    if ch == EMPTY_CH: continue
                    tr = nfa_automat[ch][nfa_automat[LINE_STATES].index(q)]
                    if tr != "":
                        new_tr = tr
                        mk = table[item][kindex]
                        if len(mk) > 0:
                            new_tr = table[item][kindex]
                            s = table[item][kindex].split(Q_SEPARATOR)
                            q_in_new_tr = tr.split(Q_SEPARATOR)
                            for itemK in q_in_new_tr:
                                if itemK not in s:
                                    new_tr = f"{new_tr},{itemK}"
                        table[item][kindex] = new_tr

                        if new_tr not in finded_q:
                            new_finded_q[new_tr] = False
                            find_new_q = True
            new_finded_q[item] = True
        finded_q = new_finded_q

    rewrite_table = dict()
    rewrite_table[LINE_END] = []
    rewrite_table[LINE_STATES] = []

    for yandex, line in enumerate(table):
        if line == LINE_CH:
            for kindex, ch in enumerate(table[LINE_CH]):
                rewrite_table[ch] = []
                for i in range(1, len(table)):
                    rewrite_table[ch].append("")
        else:
            s = line.split(Q_SEPARATOR)
            s.sort()
            s = list(dict.fromkeys(s))
            s = Q_SEPARATOR.join(s)
            rewrite_table[LINE_STATES].append(s)

    for states in rewrite_table[LINE_STATES]:
        temp = states.split(Q_SEPARATOR)
        for state in temp:
            if state in end_state:
                rewrite_table[LINE_END].append(f";{NAME_END}")
                break
        else: rewrite_table[LINE_END].append(";")

    for yandex, ch in enumerate(table[LINE_CH]):
        for kindex, q in enumerate(table):
            if q == LINE_CH: continue
            s = table[q][yandex]
            s = s.split(Q_SEPARATOR)
            s.sort()
            s = list(dict.fromkeys(s))
            s = Q_SEPARATOR.join(s)
            rewrite_table[ch][kindex - 1] = s

    rewrite_table = remove_unreacheble_state(rewrite_table, False)
    for i, b in enumerate(rewrite_table):
        if b == LINE_END:
            print(";", end = "")
            for k, c in enumerate(rewrite_table[b]):
                print(f"{c}", end ="")
            print()
        else:
            if b == LINE_STATES:
                for k, c in enumerate(rewrite_table[b]):
                    print(f";{c}", end ="")
                print()
            else:
                print(b, end="")
                for k, c in enumerate(rewrite_table[b]):
                    print(f";{c}", end="")
                print()


    temp_file = open("temp.csv", "w+", encoding="utf-8")
    for i, b in enumerate(rewrite_table):
        if b == LINE_END:
            for k, c in enumerate(rewrite_table[b]):
                temp_file.write(c)
            temp_file.write("\n")
        else:
            if b == LINE_STATES:
                for k, c in enumerate(rewrite_table[b]):
                    temp_file.write(f";{c}")
                temp_file.write("\n")
            else:
                temp_file.write(b)
                for k, c in enumerate(rewrite_table[b]):
                    temp_file.write(f";{c}")
                temp_file.write("\n")

    temp_file.close()
    temp_file =  open("temp.csv", "r", encoding="utf-8")
    moore_transform_to_min(temp_file, output_file)

def main(args):
    input_file_name = args[0]
    output_file_name = args[1]

    input_file = open(input_file_name, "r",  encoding="utf-8")
    output_file = open(output_file_name, "w+", encoding="utf-8")

    nfa_automat = read_nfa(input_file)

    determinate(nfa_automat, output_file_name)

    output_file.close()

if __name__ == '__main__':
    main(sys.argv[1:])