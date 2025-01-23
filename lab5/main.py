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


    def create_symbol_nfa(self, symbol):
        """Создать НКА для одного символа."""
        start = self.create_state()
        accept = self.create_state()
        start.transitions[symbol] = [accept]
        return NFA(start, accept)

    def create_union_nfa(self, left, right):
        """Создать НКА для операции '|'."""
        start = self.create_state()
        accept = self.create_state()
        start.transitions[None] = [left.start, right.start]  # Пустые переходы
        left.end.transitions[None] = [accept]
        right.end.transitions[None] = [accept]
        return NFA(start, accept)

    def create_kleene_star_nfa(self, nfa):
        """Создать НКА для операции '*'."""
        start = self.create_state()
        medium = self.create_state()
        accept = self.create_state()
        start.transitions[None] = [medium]  # Пустые переходы
        medium.transitions[None] = [nfa.start, accept]
        nfa.end.transitions[None] = [medium]
        return NFA(start, accept)

    def create_plus_nfa(self, nfa):
        """Создать НКА для операции '*'."""
        start = self.create_state()
        accept = self.create_state()
        start.transitions[None] = [nfa.start]  # Пустые переходы
        nfa.end.transitions[None] = [nfa.start, accept]
        return NFA(start, accept)

    def nfa_plus_nfa(self, nfa1: NFA, nfa2: NFA):
        """Создать НКА для операции '*'."""
        start = self.create_state()
        accept = self.create_state()
        nfa1.end.transitions[None] = [nfa2.start]  # Пустые переходы
        nfa2.end.transitions[None] = [accept]
        start.transitions[None] = [nfa1.start]
        return NFA(start, accept)

    def build(self, node):
        if isinstance(node, Literal):
            return self.create_symbol_nfa(node.char)

        elif isinstance(node, Concatenation):
            left_nfa = self.build(node.left)
            right_nfa = self.build(node.right)
            return self.nfa_plus_nfa(left_nfa, right_nfa)
        elif isinstance(node, Alternation):
            left_nfa = self.build(node.left)
            right_nfa = self.build(node.right)
            return self.create_union_nfa(left_nfa, right_nfa)
        elif isinstance(node, Star):
            nfa = self.build(node.node)
            return self.create_kleene_star_nfa(nfa)
        elif isinstance(node, Group):
            return self.build(node.node)
        else:
            raise ValueError(f"Unknown node type: {type(node)}")



def main(args):
    try:
        output_file_name = args[0]
        regex = args[1]
    except Exception:
        output_file_name = "output.csv"
        regex = "(tw|y)*(tq|t)" #FIXME MOCK
    output_file = open(output_file_name, "w+", encoding="utf-8")
    output_file.close()

    parser = RegexParser(regex)
    ast = parser.parse()
    print(ast)

    # Построение НКА
    builder = NFABuilder()
    nfa = builder.build(ast)

    def print_nfa(nfa):
        visited = set()
        stack = [nfa.start]

        print("Состояния и переходы:")
        while stack:
            state = stack.pop()
            if state.id in visited:
                continue
            visited.add(state.id)
            for symbol, targets in state.transitions.items():
                symbol_str = symbol if symbol is not None else "ε"
                for target in targets:
                    print(f"State {state.id} --{symbol_str}--> State {target.id}")
                    stack.append(target)

    print_nfa(nfa)
    with open(output_file_name, 'w', newline='', encoding='utf-8') as file:
        # проверяем какое стартовое состояние и записываем сначала его
        output_dict = dict()
        output_dict[OUTPUT_CH] = []
        output_dict[QS] = []

        # output_dict[OUTPUT_CH].append(";")
        output_dict[QS].append(nfa.start.id)

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
