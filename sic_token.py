import enum


# note: TK => Token Type

class TokenKind(enum.Enum):
    COMMENT = enum.auto()  # // ... \n or /* ... */

    # Keywords
    UNSIGNED = enum.auto()  # unsigned
    SIZEOF = enum.auto()  # sizeof
    SIGNED = enum.auto()  # signed
    RETURN = enum.auto()  # return
    DOUBLE = enum.auto()  # double
    WHILE = enum.auto()  # while
    SHORT = enum.auto()  # short
    FLOAT = enum.auto()  # float
    BREAK = enum.auto()  # break
    VOID = enum.auto()  # void
    ELSE = enum.auto()  # else
    CHAR = enum.auto()  # char
    LONG = enum.auto()  # long
    FUNC = enum.auto()  # func
    INT = enum.auto()  # int
    FOR = enum.auto()  # for
    IF = enum.auto()  # if

    # Literals
    INTEGER_LITERAL = enum.auto()
    FLOAT_LITERAL = enum.auto()
    STRING_LITERAL = enum.auto()

    # CIdentifier
    IDENTIFIER = enum.auto()

    # Separators and Operators
    ELLIPSIS = enum.auto()  # ...
    RIGHT_ASSIGN = enum.auto()  # >>=
    LEFT_ASSIGN = enum.auto()  # <<=
    ADD_ASSIGN = enum.auto()  # +=
    AND_ASSIGN = enum.auto()  # &=
    SUB_ASSIGN = enum.auto()  # -=
    MUL_ASSIGN = enum.auto()  # *=
    DIV_ASSIGN = enum.auto()  # /=
    MOD_ASSIGN = enum.auto()  # %=
    XOR_ASSIGN = enum.auto()  # ^=
    OR_ASSIGN = enum.auto()  # |=
    RIGHT_OP = enum.auto()  # >>
    LEFT_OP = enum.auto()  # <<
    INC_OP = enum.auto()  # ++
    DEC_OP = enum.auto()  # --
    PTR_OP = enum.auto()  # ->
    AND_OP = enum.auto()  # &&
    OR_OP = enum.auto()  # ||
    LE_OP = enum.auto()  # <=
    GE_OP = enum.auto()  # >=
    EQ_OP = enum.auto()  # ==
    NE_OP = enum.auto()  # !=
    SEMICOLON = enum.auto()  # ;
    OPENING_CURLY_BRACE = enum.auto()  # {
    CLOSING_CURLY_BRACE = enum.auto()  # }
    COMMA = enum.auto()  # ,
    COLON = enum.auto()  # :
    EQUALS = enum.auto()  # =
    OPENING_PARENTHESIS = enum.auto()  # (
    CLOSING_PARENTHESIS = enum.auto()  # )
    OPENING_BRACKET = enum.auto()  # [
    CLOSING_BRACKET = enum.auto()  # ]
    PERIOD = enum.auto()  # .
    AMPERSAND = enum.auto()  # &
    EXCLAMATION = enum.auto()  # !
    TILDE = enum.auto()  # ~
    HYPHEN = enum.auto()  # -
    PLUS = enum.auto()  # +
    ASTERISK = enum.auto()  # *
    SLASH = enum.auto()  # /
    PERCENTAGE = enum.auto()  # %
    LESS_THAN = enum.auto()  # <
    GREATER_THAN = enum.auto()  # >
    CIRCUMFLEX = enum.auto()  # ^
    QUESTION_MARK = enum.auto()  # ?
    VERTICAL_BAR = enum.auto()  # |

    END = enum.auto()  # End Of Tokens stream token


# string to keyword dictionary
string_to_keyword: dict[str, TokenKind] = {
    # the token hierarchy is by string length
    "unsigned": TokenKind.UNSIGNED,
    "sizeof": TokenKind.SIZEOF,
    "signed": TokenKind.SIGNED,
    "return": TokenKind.RETURN,
    "double": TokenKind.DOUBLE,
    "while": TokenKind.WHILE,
    "short": TokenKind.SHORT,
    "float": TokenKind.FLOAT,
    "break": TokenKind.BREAK,
    "void": TokenKind.VOID,
    "else": TokenKind.ELSE,
    "char": TokenKind.CHAR,
    "long": TokenKind.LONG,
    "func": TokenKind.FUNC,
    "int": TokenKind.INT,
    "for": TokenKind.FOR,
    "if": TokenKind.IF,
}

# string to separator or_operator dictionary
string_to_separator_or_operator: dict[str, TokenKind] = {
    # the token hierarchy is by string length
    '>>=': TokenKind.RIGHT_ASSIGN,
    '<<=': TokenKind.LEFT_ASSIGN,
    '&=': TokenKind.AND_ASSIGN,
    '+=': TokenKind.ADD_ASSIGN,
    '-=': TokenKind.SUB_ASSIGN,
    '*=': TokenKind.MUL_ASSIGN,
    '/=': TokenKind.DIV_ASSIGN,
    '%=': TokenKind.MOD_ASSIGN,
    '^=': TokenKind.XOR_ASSIGN,
    '|=': TokenKind.OR_ASSIGN,
    '>>': TokenKind.RIGHT_OP,
    '<<': TokenKind.LEFT_OP,
    '++': TokenKind.INC_OP,
    '--': TokenKind.DEC_OP,
    '->': TokenKind.PTR_OP,
    '&&': TokenKind.AND_OP,
    '||': TokenKind.OR_OP,
    '<=': TokenKind.LE_OP,
    '>=': TokenKind.GE_OP,
    '==': TokenKind.EQ_OP,
    '!=': TokenKind.NE_OP,
    ';': TokenKind.SEMICOLON,
    '{': TokenKind.OPENING_CURLY_BRACE,
    '}': TokenKind.CLOSING_CURLY_BRACE,
    ',': TokenKind.COMMA,
    ':': TokenKind.COLON,
    '=': TokenKind.EQUALS,
    '(': TokenKind.OPENING_PARENTHESIS,
    ')': TokenKind.CLOSING_PARENTHESIS,
    '[': TokenKind.OPENING_BRACKET,
    ']': TokenKind.CLOSING_BRACKET,
    '.': TokenKind.PERIOD,
    '&': TokenKind.AMPERSAND,
    '!': TokenKind.EXCLAMATION,
    '~': TokenKind.TILDE,
    '-': TokenKind.HYPHEN,
    '+': TokenKind.PLUS,
    '*': TokenKind.ASTERISK,
    '/': TokenKind.SLASH,
    '%': TokenKind.PERCENTAGE,
    '<': TokenKind.LESS_THAN,
    '>': TokenKind.GREATER_THAN,
    '^': TokenKind.CIRCUMFLEX,
    '?': TokenKind.QUESTION_MARK,
    '|': TokenKind.VERTICAL_BAR
}


class Token:
    def __init__(self, kind: TokenKind, start: int, string: str):
        self.kind: TokenKind = kind
        self.start: int = start  # the start char index
        self.string: str = string  # the string of the token in the file

    def to_dict(self):
        return {
            self.string,
        }
