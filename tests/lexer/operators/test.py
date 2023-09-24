import sic_lexer
import sic_token
import sys

with open('test.c', 'r') as f:
    source = f.read()

lexer = sic_lexer.Lexer(source)
lexer.lex()

operators_token_kind = [
    sic_token.TokenKind.ELLIPSIS,
    sic_token.TokenKind.RIGHT_ASSIGN,
    sic_token.TokenKind.LEFT_ASSIGN,
    sic_token.TokenKind.ADD_ASSIGN,
    sic_token.TokenKind.AND_ASSIGN,
    sic_token.TokenKind.SUB_ASSIGN,
    sic_token.TokenKind.MUL_ASSIGN,
    sic_token.TokenKind.DIV_ASSIGN,
    sic_token.TokenKind.MOD_ASSIGN,
    sic_token.TokenKind.XOR_ASSIGN,
    sic_token.TokenKind.OR_ASSIGN,
    sic_token.TokenKind.RIGHT_OP,
    sic_token.TokenKind.LEFT_OP,
    sic_token.TokenKind.INC_OP,
    sic_token.TokenKind.DEC_OP,
    sic_token.TokenKind.PTR_OP,
    sic_token.TokenKind.AND_OP,
    sic_token.TokenKind.OR_OP,
    sic_token.TokenKind.LE_OP,
    sic_token.TokenKind.GE_OP,
    sic_token.TokenKind.EQ_OP,
    sic_token.TokenKind.NE_OP,
    sic_token.TokenKind.SEMICOLON,
    sic_token.TokenKind.OPENING_CURLY_BRACE,
    sic_token.TokenKind.CLOSING_CURLY_BRACE,
    sic_token.TokenKind.COMMA,
    sic_token.TokenKind.COLON,
    sic_token.TokenKind.EQUALS,
    sic_token.TokenKind.OPENING_PARENTHESIS,
    sic_token.TokenKind.CLOSING_PARENTHESIS,
    sic_token.TokenKind.OPENING_BRACKET,
    sic_token.TokenKind.CLOSING_BRACKET,
    sic_token.TokenKind.PERIOD,
    sic_token.TokenKind.AMPERSAND,
    sic_token.TokenKind.EXCLAMATION,
    sic_token.TokenKind.TILDE,
    sic_token.TokenKind.HYPHEN,
    sic_token.TokenKind.PLUS,
    sic_token.TokenKind.ASTERISK,
    sic_token.TokenKind.SLASH,
    sic_token.TokenKind.PERCENTAGE,
    sic_token.TokenKind.LESS_THAN,
    sic_token.TokenKind.GREATER_THAN,
    sic_token.TokenKind.CIRCUMFLEX,
    sic_token.TokenKind.QUESTION_MARK,
    sic_token.TokenKind.VERTICAL_BAR,
]

for token in lexer.tokens:
    if token.kind not in operators_token_kind and token.kind != sic_token.TokenKind.END:
        print("The token " + token.string + " is not an operator", file=sys.stderr)
