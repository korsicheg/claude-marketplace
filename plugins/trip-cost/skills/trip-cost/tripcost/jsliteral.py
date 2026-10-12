"""Reads a JavaScript data literal (objects, arrays, strings, numbers, true, false, null) from source
text, without running any JavaScript: the toll dataset is published as a .js file."""
import re

NUMBER_RE = re.compile(r"-?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?")
WORD_RE = re.compile(r"[A-Za-z_$][\w$]*")
WORDS = {"true": True, "false": False, "null": None, "undefined": None}
ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}


class JsLiteralError(ValueError):
    pass


def literal_after(source: str, marker: str) -> object:
    """The literal that follows the marker, e.g. the array after "const TOLL_DATA =" ."""
    position = source.find(marker)
    if position < 0:
        raise JsLiteralError(f"{marker!r} not found")
    return _Reader(source, position + len(marker)).value()


class _Reader:
    def __init__(self, source: str, position: int):
        self.source = source
        self.position = position

    def value(self) -> object:
        self.skip_blanks()
        char = self.peek()
        if char == "{":
            return self.object()
        if char == "[":
            return self.array()
        if char in "\"'`":
            return self.string()
        if char == "-" or char == "." or char.isdigit():
            return self.number()
        word = self.word()
        if word not in WORDS:
            raise self.error(f"not a data literal: {word!r}")
        return WORDS[word]

    def object(self) -> dict:
        self.expect("{")
        result = {}
        while not self.closes("}"):
            key = self.string() if self.peek() in "\"'" else self.word()
            self.skip_blanks()
            self.expect(":")
            result[key] = self.value()
            self.skip_separator("}")
        return result

    def array(self) -> list:
        self.expect("[")
        result = []
        while not self.closes("]"):
            result.append(self.value())
            self.skip_separator("]")
        return result

    def string(self) -> str:
        quote = self.take()
        chars = []
        while (char := self.take()) != quote:
            if char == "\\":
                chars.append(self.escape())
            else:
                chars.append(char)
        return "".join(chars)

    def escape(self) -> str:
        char = self.take()
        if char == "u":
            return chr(int(self.take_count(4), 16))
        if char == "x":
            return chr(int(self.take_count(2), 16))
        if char == "\n":
            return ""
        return ESCAPES.get(char, char)

    def number(self) -> float:
        match = NUMBER_RE.match(self.source, self.position)
        if not match:
            raise self.error("bad number")
        self.position = match.end()
        return float(match.group())

    def word(self) -> str:
        match = WORD_RE.match(self.source, self.position)
        if not match:
            raise self.error("expected a name")
        self.position = match.end()
        return match.group()

    def closes(self, bracket: str) -> bool:
        self.skip_blanks()
        if self.peek() == bracket:
            self.position += 1
            return True
        return False

    def skip_separator(self, bracket: str) -> None:
        self.skip_blanks()
        if self.peek() == ",":
            self.position += 1
        elif self.peek() != bracket:
            raise self.error(f"expected ',' or {bracket!r}")

    def skip_blanks(self) -> None:
        """Whitespace and comments."""
        while self.position < len(self.source):
            if self.source[self.position].isspace():
                self.position += 1
            elif self.source.startswith("//", self.position):
                end = self.source.find("\n", self.position)
                self.position = len(self.source) if end < 0 else end + 1
            elif self.source.startswith("/*", self.position):
                end = self.source.find("*/", self.position + 2)
                if end < 0:
                    raise self.error("unclosed comment")
                self.position = end + 2
            else:
                return

    def expect(self, char: str) -> None:
        if self.take() != char:
            raise self.error(f"expected {char!r}")

    def peek(self) -> str:
        if self.position >= len(self.source):
            raise self.error("unexpected end")
        return self.source[self.position]

    def take(self) -> str:
        char = self.peek()
        self.position += 1
        return char

    def take_count(self, count: int) -> str:
        text = self.source[self.position:self.position + count]
        self.position += count
        return text

    def error(self, message: str) -> JsLiteralError:
        line = self.source.count("\n", 0, self.position) + 1
        return JsLiteralError(f"{message} at line {line}")
