import sic_lexer
import sic_token
import sys

with open('test.c', 'r') as f:
    source = f.read()

lexer = sic_lexer.Lexer(source)
lexer.lex()

keywords_token_kind = [
    sic_token.TokenKind.UNSIGNED,
    sic_token.TokenKind.CONTINUE,
    sic_token.TokenKind.SIZEOF,
    sic_token.TokenKind.SIGNED,
    sic_token.TokenKind.RETURN,
    sic_token.TokenKind.DOUBLE,
    sic_token.TokenKind.WHILE,
    sic_token.TokenKind.SHORT,
    sic_token.TokenKind.FLOAT,
    sic_token.TokenKind.BREAK,
    sic_token.TokenKind.VOID,
    sic_token.TokenKind.ELSE,
    sic_token.TokenKind.CHAR,
    sic_token.TokenKind.LONG,
    sic_token.TokenKind.FUNC,
    sic_token.TokenKind.INT,
    sic_token.TokenKind.FOR,
    sic_token.TokenKind.IF,
]

for token in lexer.tokens:
    if token.kind not in keywords_token_kind and token.kind != sic_token.TokenKind.END:
        print("The token " + token.string + " is not an identifier", file=sys.stderr)
