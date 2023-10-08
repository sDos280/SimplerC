import sic_lexer
import sic_dry_parser
import sic_ast_visitor
import sic_emitter
import json

with open('test.c', 'r') as f:
    source = f.read()

lexer = sic_lexer.Lexer(source)
lexer.lex()

parser = sic_dry_parser.DryParser(lexer)
translation_unit = parser.peek_translation_unit()
"""print(json.dumps(
    [external_declaration.to_dict() for external_declaration in translation_unit],
    indent=2), end='\n\n')"""


ast_visitor = sic_ast_visitor.ASTVisitor(lexer, translation_unit)

ast_visitor.visit_translation_unit()

emitter = sic_emitter.Emitter(lexer, translation_unit)
emitter.emit_translation_unit()

print()