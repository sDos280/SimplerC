import sic_lexer
import sic_dry_parser
import sic_ast_visitor
import sic_emitter
import sic_compiler_front_hand
from ctypes import CFUNCTYPE, c_int
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
llvm_ir = emitter.emit_translation_unit()
print(llvm_ir)

engine = sic_compiler_front_hand.create_execution_engine()
mod = sic_compiler_front_hand.compile_ir(engine, llvm_ir)

# Look up the function pointer (a Python int)
func_ptr = engine.get_function_address("fibonacci")

# Run the function via ctypes
cfunc = CFUNCTYPE(c_int)(func_ptr)
for i in range(10):
    print(f"fibonacci({i}) = {cfunc(i)}")
