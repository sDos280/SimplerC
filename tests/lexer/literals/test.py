import sic_lexer
import sic_token
import sys

with open('test.c', 'r') as f:
    source = f.read()

lexer = sic_lexer.Lexer(source)
lexer.lex()

constants_token_kind = [
    sic_token.TokenKind.INTEGER_LITERAL,
    sic_token.TokenKind.FLOAT_LITERAL,
    sic_token.TokenKind.CHAR_LITERAL,
]

for token in lexer.tokens:
    if token.kind not in constants_token_kind and token.kind != sic_token.TokenKind.END:
        print("The token " + token.string + " is not an literal", file=sys.stderr)
