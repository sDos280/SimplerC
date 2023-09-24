import sic_lexer
import sic_token
import sys

with open('test.c', 'r') as f:
    source = f.read()

lexer = sic_lexer.Lexer(source)
lexer.lex()

for token in lexer.tokens:
    if token.kind not in [sic_token.TokenKind.IDENTIFIER, sic_token.TokenKind.END]:
        print("The token " + token.string + " is not an identifier", file=sys.stderr)
