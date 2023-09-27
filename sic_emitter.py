"""

the emitter job is to emit the ast code

"""
import sic_node as node
import llvmlite.ir as ir


class IrScope:
    def __init__(self):
        self.current_function: ir.Function | None = None
        self.current_block: ir.Block | None = None


class SicScope:
    def __init__(self):
        self.current_function: node.FunctionDefinition | None = None
        self.current_block: node.CompoundStatement | None = None  # a block in SimpleC is a compound statement
        self.current_while: node.While | None = None
        self.current_for: node.For | None = None
        self.current_if: node.If | None = None


class Emitter:
    def __init__(self, lexer, translation_unit):
        self.lexer = lexer
        self.translation_unit = translation_unit
        self.ir_scope = IrScope()
        self.sic_scope = SicScope()

        self.module = ir.Module()

    def emit_translation_unit(self):
        for external_declaration in self.translation_unit:
            self.emit_external_declaration(external_declaration)

    def emit_external_declaration(self, external_declaration: node.ExternalDeclaration):
        if isinstance(external_declaration, node.FunctionDefinition):
            self.emit_function_definition(external_declaration)
        elif isinstance(external_declaration, node.Declaration):
            assert False, "not implemented"
        else:
            assert False, "unknown external declaration"