import sys
OUTPUT_CH = "OUTPUT_CH"
QS = "QS"

OPERATORS = ["(",")", "|"]

class RegexNode:
    pass

class Literal(RegexNode):
    def __init__(self, char):
        self.char = char

    def __repr__(self):
        return f"Literal('{self.char}')"

class Epsilon(RegexNode):
    def __repr__(self):
        return "Epsilon()"

class Concatenation(RegexNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Concatenation({self.left}, {self.right})"

class Alternation(RegexNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Alternation({self.left}, {self.right})"

class Star(RegexNode):
    def __init__(self, node):
        self.node = node

    def __repr__(self):
        return f"Star({self.node})"

class Group(RegexNode):
    def __init__(self, node):
        self.node = node

    def __repr__(self):
        return f"Group({self.node})"

class RegexParser:
    def __init__(self, regex):
        self.regex = regex
        self.pos = 0

    def parse(self):
        return self._parse_alternation()

    def _parse_alternation(self):
        left = self._parse_concatenation()
        while self._current_char() == '|':
            self.pos += 1
            right = self._parse_concatenation()
            left = Alternation(left, right)
        return left

    def _parse_concatenation(self):
        nodes = []
        while self._current_char() and self._current_char() not in '|)':
            nodes.append(self._parse_star())
        if not nodes:
            return Literal("ε")
        result = nodes[0]
        for node in nodes[1:]:
            result = Concatenation(result, node)
        return result

    def _parse_star(self):
        node = self._parse_group_or_literal()
        while self._current_char() == '*':
            self.pos += 1
            node = Star(node)
        return node

    def _parse_group_or_literal(self):
        char = self._current_char()
        if char == '(':
            self.pos += 1
            node = self._parse_alternation()
            if self._current_char() != ')':
                raise ValueError(f"Unmatched parenthesis at position {self.pos}")
            self.pos += 1
            return Group(node)
        else:
            self.pos += 1
            return Literal(char)

    def _current_char(self):
        return self.regex[self.pos] if self.pos < len(self.regex) else None


class State:
    def __init__(self, id):
        self.id = id
        self.transitions = {}  # {symbol: [state1, state2]}


class NFA:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __repr__(self):
        return f"NFA(start={self.start}, end={self.end})"


class NFABuilder:
    def __init__(self):
        self.state_count = 0

    def create_state(self):
        state = State(self.state_count)
        self.state_count += 1
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


        visited = set()
        end = nfa.end
        output_dict[QS].append(end.id)
        output_dict[OUTPUT_CH].append(""),
        output_dict[OUTPUT_CH].append("F")
        stack = [nfa.start]
        max_size = 1
        while stack:
            state = stack.pop()
            if state.id in visited:
                continue
            visited.add(state.id)
            for symbol, targets in state.transitions.items():
                symbol_str = symbol if symbol is not None else "ε"
                for target in targets:
                    if symbol_str not in output_dict:
                        output_dict[symbol_str] = []
                    if state.id not in output_dict[QS]:
                        output_dict[QS].append(state.id)
                        if state.id == end.id:
                            output_dict[OUTPUT_CH].append("F")
                        else:
                            output_dict[OUTPUT_CH].append("")
                    state_index = output_dict[QS].index(state.id)
                    if max_size <= state_index: max_size = state_index + 1
                    print()
                    if len(output_dict[symbol_str]) <= max_size:
                        for item in output_dict:
                            if item == QS or item == OUTPUT_CH: continue
                            if len(output_dict[item]) < max_size:
                                for i in range(len(output_dict[item]), max_size):
                                    output_dict[item].append("")
                    print(len(output_dict[symbol_str]), max_size, state_index)
                    if len(output_dict[symbol_str][state_index]) == 0:
                        output_dict[symbol_str][state_index] = f"{target.id}"
                    else:
                        output_dict[symbol_str][state_index] += f",{target.id}"
                    print(f"State {state.id} --{symbol_str}--> State {target.id}")
                    stack.append(target)

        for symbol in output_dict:
            if symbol == QS or symbol == OUTPUT_CH: continue
            if len(output_dict[symbol]) < len(output_dict[QS]):
                for i in range(len(output_dict[symbol]), len(output_dict[QS])):
                    output_dict[item].append("")

        for item in output_dict:
            # if item == OUTPUT_CH:
            #     file.write(";")
            if item != QS and item != OUTPUT_CH:
                file.write(f"{item}")
            for k in output_dict[item]:
                file.write(f";{k}")
            file.write("\n")
if __name__ == "__main__":
    main(sys.argv[1:])