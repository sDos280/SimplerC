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

        self.identifiers_table = {}

    def emit_translation_unit(self):
        for external_declaration in self.translation_unit:
            self.emit_external_declaration(external_declaration)

    def emit_external_declaration(self, external_declaration: node.ExternalDeclaration):
        if isinstance(external_declaration, node.FunctionDefinition):
            function_ir = self.emit_function_definition(external_declaration)
        elif isinstance(external_declaration, node.Declaration):
            assert False, "not implemented"
        else:
            assert False, "unknown external declaration"

    def emit_function_definition(self, function_definition: node.FunctionDefinition) -> ir.Function:
        function_type = self.emit_function_type(function_definition)
        function_ir = ir.Function(self.module, function_type, name=function_definition.identifier.token.string)
        self.ir_scope.current_function = function_ir
        self.sic_scope.current_function = function_definition
        self.emit_function_body(function_definition)

        self.ir_scope.current_function = None
        self.sic_scope.current_function = None
        return function_ir
