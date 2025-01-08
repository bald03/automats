import sys

from collections import defaultdict
OUTPUT_CH = "OUTPUT_CH"
QS = "QS"


def parse_regex_to_nfa(regex):
    """
    Построение ε-НКА из регулярного выражения с использованием метода Томпсона.
    Возвращает:
        - переходы (dict): Ключ — состояние, значение — словарь {символ: [список следующих состояний]}.
        - начальное состояние (str)
        - конечные состояния (set)
    """
    state_counter = 0

    def new_state():
        nonlocal state_counter
        state = f"q{state_counter}"
        state_counter += 1
        return state

    stack = []
    transitions = defaultdict(lambda: defaultdict(list))

    start_state = new_state()
    end_state = new_state()

    for char in regex:
        if char == '(':  # Группировка
            stack.append((start_state, end_state))
            start_state = new_state()
            end_state = new_state()
        elif char == ')':
            old_start, old_end = stack.pop()  # Извлекаем старые состояния
            transitions[old_end]['ε'].append(start_state)  # Соединяем старый конец с началом подграфа
            transitions[end_state]['ε'].append(old_end)  # Завершаем подграф КАК БУДТО КАКАЯ ТО ХУЙНЯ И ПОЯВЛЯЕТСЯ ЦИКЛ 
            transitions[old_start]['ε'].append(start_state)  # Важное соединение!
            end_state = new_state()
            start_state = old_end
        elif char == '|':  # Альтернатива
            alt_start = new_state()
            alt_end = new_state()
            transitions[alt_start]['ε'].extend([start_state, end_state])
            transitions[end_state]['ε'].append(alt_end)
            start_state, end_state = alt_start, alt_end
        elif char == '*':  # Замыкание Клини
            kleene_start = new_state()
            kleene_end = new_state()
            transitions[kleene_start]['ε'].extend([start_state, kleene_end])
            transitions[end_state]['ε'].extend([start_state, kleene_end])
            start_state, end_state = kleene_start, kleene_end
        elif char == '+':  # Конкатенация
            next_state = new_state()
            transitions[start_state]['ε'].append(next_state)
            start_state = next_state
        else:  # Конкретный символ
            next_state = new_state()
            transitions[start_state][char].append(next_state)
            start_state, end_state = next_state, end_state

    return transitions, start_state, {end_state}

def write_nfa_to_csv(transitions, start_state, final_states, output_file):
    """Записывает NFA в формате CSV."""

    with open(output_file, 'w', newline='', encoding='utf-8'):
        # проверяем какое стартовое состояние и записываем сначала его
        output_dict = dict()
        output_dict[OUTPUT_CH] = []
        output_dict[QS] = []


        output_dict[OUTPUT_CH].append(";")
        output_dict[QS].append(start_state)

        if start_state in final_states:
            output_dict[OUTPUT_CH].append("F")

        for i, item in enumerate(transitions):
            if item == start_state: continue
            output_dict[QS].append(item)
            if item in final_states:
                output_dict[OUTPUT_CH].append("F")
            else:
                output_dict[OUTPUT_CH].append("")
            for item2 in transitions[item]:
                if item2 not in output_dict:
                    output_dict[item2] = []
                    for k, _ in enumerate(transitions):
                        output_dict[item2].append("")


        for i, item in enumerate(transitions):
            if item == start_state: continue
            for item2 in transitions[item]:
                if item2 not in output_dict: output_dict[item2] = []
                if len(item) > 1: tr = ",".join(transitions[item][item2])
                else: tr = ",".join(transitions[item][item2])
                output_dict[item2][i] = tr

        for item in output_dict:
            print(f"{item} {output_dict[item]}")





def main():
    output_file_name = sys.argv[0]
    regex = sys.argv[1]
    #output_file_name = "output.csv"
    #regex = "(r*|su*t)* su*" #FIXME MOCK
    output_file = open(output_file_name, "w+", encoding="utf-8")
    output_file.close()

    transitions, start_state, final_states = parse_regex_to_nfa(regex)
    write_nfa_to_csv(transitions, start_state, final_states, output_file_name)
    print(f"NFA successfully written to {output_file}")

if __name__ == "__main__":
    main()
