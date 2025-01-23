import re
import sys

# Регулярные выражения для токенов
TOKEN_PATTERNS = {
    "WHITESPACE": r"\s",
    "LINE_COMMENT": r"//.*",
    "BLOCK_COMMENT": r"\{(?:.|\n)*?\}",  # Многострочные комментарии в одной строке
    "START_BLOCK_COMMENT": r"\{\s*.*",  # Многострочные комментарии
    "END_BLOCK_COMMENT": r"(?:.|\n)*?\}",  # Многострочные комментарии
    "IDENTIFIER": r"[a-zA-Z_][a-zA-Z0-9_]*",
    "STRING": r"'(?:[^'\\]|\\.)*'",
    "INTEGER": r"^(?<![\d.])\b\d+\b(?![\d.])$",  # Окончательная версия для целых чисел
    "FLOAT": r"^\d+\.\d+([eE][+-]?\d+)?$|^\d+[e|E][+-]?\d+$",  # Числа с плавающей точкой или экспонентой
    "PLUS": r"\+",
    "MINUS": r"-",
    "DIVIDE": r"/",
    "SEMICOLON": r";",
    "COMMA": r",",
    "LEFT_PAREN": r"\(",
    "RIGHT_PAREN": r"\)",
    "LEFT_BRACKET": r"\[",
    "RIGHT_BRACKET": r"\]",
    "EQ": r"=",
    "GREATER": r">",
    "LESS": r"<",
    "LESS_EQ": r"<=",
    "GREATER_EQ": r">=",
    "NOT_EQ": r"<>",
    "COLON": r":",
    "ASSIGN": r":=",
    "DOT": r"\.",
}

KEYS_PATTERNS = {
    "ARRAY": r"(?i)\bARRAY\b",
    "BEGIN": r"(?i)\bBEGIN\b",
    "ELSE": r"(?i)\bELSE\b",
    "END": r"(?i)\bEND\b",
    "IF": r"(?i)\bIF\b",
    "OF": r"(?i)\bOF\b",
    "OR": r"(?i)\bOR\b",
    "PROGRAM": r"(?i)\bPROGRAM\b",
    "PROCEDURE": r"(?i)\bPROCEDURE\b",
    "THEN": r"(?i)\bTHEN\b",
    "TYPE": r"(?i)\bTYPE\b",
    "VAR": r"(?i)\bVAR\b",
    "IDENTIFIER": r"[a-zA-Z_][a-zA-Z0-9_]*"
}

delimeters = {"\""," ", "(", ")", "+", "-", "\t", "\n", ";", ":", ",", ".", "[", "]", "{", "}", "*", "/", "'", "\xa0"}

operators = {
    "+": "PLUS",
    "-": "MINUS",
    "/": "DIVIDE",
    "=": "EQ",
    ">": "GREATER",
    "<": "LESS",
    "<=": "LESS_EQ",
    ">=": "GREATER_EQ",
    "<>": "NOT_EQ",
    ":": "COLON",
    ":=": "ASSIGN",
}


class Token:
    def __init__(self, name, line_number, start_position, value, ):
        self.name = name
        self.value = value
        self.line_number = line_number
        self.start_position = start_position


class PascalLexer:
    def __init__(self, input_file_name):
        self.file = open(input_file_name, 'r', encoding='utf-8')
        self.line_number = 0
        self.current_line = ''
        self.position = -1
        self.line = 1
        self.current_char = None
        self.buffer = ''  # Буфер для текущей строки
        self.next_line()  # Инициализируем первый символ
        self.current_value = None
        self.start_position =  -1
        self.start_line = 0

    def next_line(self):
        self.current_line = next(self.file, None)  # Возвращает None на конце файла

        if not self.current_line is None:
            self.current_line = self.current_line.replace("\xa0", " ")
            self.line_number += 1
            self.position = -1

            return True
        self.current_line = ""
        return False

    def try_get_next_char(self):
        self.position += 1
        if self.position >= len(self.current_line):
            return False

        self.current_char = self.current_line[self.position]
        return True

    def go_back(self):
        self.position -= 1
        self.current_char = self.current_line[self.position]

    def show_next_char(self):
        try:
            char = self.current_line[self.position + 1]
            return char
        except Exception as e:
            return None

    def create_token(self, name):
        value = self.current_value
        self.current_value = None
        start = self.start_position
        self.start_position = self.position
        return Token(name, self.start_line, start + 1, value)

    def parse_block_comment(self):
        self.start_position = self.position
        self.start_line = self.line_number
        self.current_value = self.current_char
        while True:
            if not self.try_get_next_char():
                while True:
                    if not self.next_line():
                        return self.create_token("BAD")
                    if len(self.current_line) > 0:
                        break
                self.try_get_next_char()

            self.current_value += self.current_char
            if self.current_char == "}":
                return self.create_token("BLOCK_COMMENT")

    def parse_string(self, end_char):
        self.current_value = self.current_char
        self.start_position = self.position
        self.start_line = self.line_number
        while True:
            if self.try_get_next_char():
                self.current_value += self.current_char
                if self.current_char == end_char:
                    return self.create_token("STRING")

            else:
                return self.create_token("BAD")

    def parse_divide(self):
        self.current_value = self.current_char
        self.start_position = self.position
        self.start_line = self.line_number

        next_char = self.show_next_char()

        if not next_char is None:
            if next_char == "/":
                while self.try_get_next_char():
                    self.current_value += self.current_char
                return self.create_token("LINE_COMMENT")
            else:
                return self.create_token("DIVIDE")
        else:
            return self.create_token("DIVIDE")

    def parse_digit(self):
        self.current_value = self.current_char
        self.start_position = self.position
        self.start_line = self.line_number
        regexF = re.compile(TOKEN_PATTERNS["FLOAT"])
        regexI = re.compile(TOKEN_PATTERNS["INTEGER"])

        while True:
            if self.try_get_next_char():
                if self.current_char.isdigit():
                    self.current_value += self.current_char
                    continue
                if self.current_char == ".":
                    next_char = self.show_next_char()
                    if not next_char is None:
                        if next_char == ".":
                            self.go_back()

                            match = regexF.fullmatch(self.current_value)
                            if match:
                                return self.create_token("FLOAT")

                            match = regexI.fullmatch(self.current_value)
                            if match:
                                if len(self.current_value) > 20:#fixme mock
                                    return self.create_token("BAD")
                                return self.create_token("INTEGER")
                            return self.create_token("BAD")
                        else:
                            self.current_value += self.current_char
                            continue
                    else:
                        self.current_value += self.current_char
                        break
                elif self.current_char in delimeters:
                    if (self.current_value[-1] == "e" or (self.current_value[-1] == "E")) and (self.current_char == "-" or self.current_char == "+"):
                        self.current_value += self.current_char
                        continue

                    self.go_back()
                    break
                elif self.current_char in operators:
                    self.go_back()
                    break
                else:
                    self.current_value += self.current_char
                    continue
            else:
                self.go_back()
                break
        match = regexF.fullmatch(self.current_value)
        if match:
            return self.create_token("FLOAT")

        match = regexI.fullmatch(self.current_value)
        if match:
            if len(self.current_value) > 20:
                return self.create_token("BAD")
            return self.create_token("INTEGER")#fixme mock

        return self.create_token("BAD")

    def parse_identifier(self):
        self.current_value = self.current_char
        self.start_position = self.position
        self.start_line = self.line_number

        while True:
            if self.try_get_next_char():
                if self.current_char in delimeters:
                    self.go_back()
                    break
                if self.current_char in operators:
                    self.go_back()
                    break
                else:
                    self.current_value += self.current_char

            else:
                break

        if len(self.current_value) > 256:
            return self.create_token("BAD")
        for key in KEYS_PATTERNS:
            regex = re.compile(KEYS_PATTERNS[key], re.IGNORECASE)
            if regex.fullmatch(self.current_value):
                return self.create_token(key)
        return self.create_token("BAD")

    def next_token(self):
        while True:
            if not self.try_get_next_char():
                while True:
                    if not self.next_line():
                        return None
                    if len(self.current_line) > 0:
                        break
                self.try_get_next_char()

            if self.current_char == "{":
                return self.parse_block_comment()

            if self.current_char.isspace():
                continue

            if self.current_char.isdigit():
                return self.parse_digit()

            if self.current_char.isalpha() or self.current_char == "_":
                return self.parse_identifier()

            if self.current_char == " ":
                continue

            if self.current_char == '"' or self.current_char == "'" :
                return self.parse_string(self.current_char)

            if self.current_char == '+':
                self.current_value = self.current_char
                self.start_position = self.position
                self.start_line = self.line_number
                return self.create_token("PLUS")

            if self.current_char == '-':
                self.current_value = self.current_char
                self.start_position = self.position
                self.start_line = self.line_number
                return self.create_token("MINUS")

            if self.current_char == '/':
                self.start_line = self.line_number
                return self.parse_divide()

            if self.current_char == ';':
                self.current_value = self.current_char
                self.start_position = self.position
                self.start_line = self.line_number
                return self.create_token("SEMICOLON")

            if self.current_char == ',':
                self.current_value = self.current_char
                self.start_position = self.position
                self.start_line = self.line_number
                return self.create_token("COMMA")

            if self.current_char == '(':
                self.current_value = self.current_char
                self.start_position = self.position
                self.start_line = self.line_number
                return self.create_token("LEFT_PAREN")

            if self.current_char == ')':
                self.current_value = self.current_char
                self.start_position = self.position
                self.start_line = self.line_number
                return self.create_token("RIGHT_PAREN")

            if self.current_char == '[':
                self.current_value = self.current_char
                self.start_position = self.position
                self.start_line = self.line_number
                return self.create_token("LEFT_BRACKET")

            if self.current_char == ']':
                self.current_value = self.current_char
                self.start_position = self.position
                self.start_line = self.line_number
                return self.create_token("RIGHT_BRACKET")

            if self.current_char == '=':
                self.start_position = self.position
                self.current_value = self.current_char
                self.start_line = self.line_number
                return self.create_token("EQ")

            if self.current_char == '*':
                self.start_position = self.position
                self.current_value = self.current_char
                self.start_line = self.line_number
                return self.create_token("MULTIPLICATION")

            if self.current_char == '<':
                self.start_position = self.position
                self.start_line = self.line_number
                next_char = self.show_next_char()
                if not next_char is None:
                    if next_char == "=":
                        char = self.current_char + next_char
                        self.try_get_next_char()
                        return Token("LESS_EQ", self.line_number, self.start_position + 1, char)
                    if next_char == '>':
                        char = self.current_char + next_char
                        self.try_get_next_char()
                        return Token("NOT_EQ", self.line_number, self.start_position + 1, char)
                self.current_value = self.current_char
                return self.create_token("LESS")

            if self.current_char == '>':
                self.start_position = self.position
                self.start_line = self.line_number
                next_char = self.show_next_char()
                if next_char == "=":
                    char = self.current_char + next_char
                    pos = self.position
                    self.try_get_next_char()
                    return Token("GREATER_EQ", self.line_number, self.start_position + 1, char)
                self.current_value = self.current_char
                return self.create_token("GREATER")

            if self.current_char == ':':
                self.start_position = self.position
                self.start_line = self.line_number
                if not self.show_next_char() is None and self.show_next_char() == "=":
                    self.current_value = self.current_char + self.show_next_char()
                    self.try_get_next_char()
                    return self.create_token("ASSIGN")
                else:
                    self.current_value = self.current_char
                    return self.create_token("COLON")

            if self.current_char == '.':
                self.start_position = self.position
                self.start_line = self.line_number
                self.current_value = self.current_char
                return self.create_token("DOT")

            else:
                return Token("BAD", self.line_number, self.position, self.current_char)

    def close(self):
        self.file.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python PascalLexer.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    lexer = PascalLexer(input_file)

    with open(output_file, 'w', encoding='utf-8') as output:
        while True:
            token = lexer.next_token()

            if token is None:
                break
            if token.name == "LINE_COMMENT" or token.name == "BLOCK_COMMENT":
                continue

            print(f"{token.name} ({token.line_number}, {token.start_position}) \"{token.value}\"")
            output.write(f"{token.name} ({token.line_number}, {token.start_position}) \"{token.value}\"\n")
    lexer.close()
