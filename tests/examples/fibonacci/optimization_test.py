import sic_lexer
import sic_dry_parser
import sic_ast_visitor
import sic_emitter
import sic_compiler_front_hand
from ctypes import CFUNCTYPE, c_int
import llvmlite.binding as llvm


def optimize(mod, opt=3, loop_vectorize=False, slp_vectorize=False):
    with llvm.create_module_pass_manager() as pm:
        with llvm.create_pass_manager_builder() as pmb:
            pmb.opt_level = opt
            pmb.loop_vectorize = loop_vectorize
            pmb.slp_vectorize = slp_vectorize
            pmb.inlining_threshold = 1
            pmb.populate(pm)
        pm.run(mod)


with open('test.c', 'r') as f:
    source = f.read()

# ----------------------------------------------
# lexer
lexer = sic_lexer.Lexer(source)
lexer.lex()

# ----------------------------------------------

# ----------------------------------------------
# parser
parser = sic_dry_parser.DryParser(lexer)
translation_unit = parser.peek_translation_unit()

ast_visitor = sic_ast_visitor.ASTVisitor(lexer, translation_unit)

ast_visitor.visit_translation_unit()
# ----------------------------------------------

# ----------------------------------------------
# emitter
emitter = sic_emitter.Emitter(lexer, translation_unit)
llvm_ir = emitter.emit_translation_unit()

# ----------------------------------------------

# ----------------------------------------------
# optimizer


engine = sic_compiler_front_hand.create_execution_engine()
mod = sic_compiler_front_hand.compile_ir(engine, llvm_ir)
print(str(mod))
optimize(mod)
print(str(mod))

# ----------------------------------------------

# Look up the function pointer (a Python int)
func_ptr = engine.get_function_address("fibonacci")

# Run the function via ctypes
cfunc = CFUNCTYPE(c_int)(func_ptr)
for i in range(10):
    print(f"fibonacci({i}) = {cfunc(i)}")
