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

        self.cfb: ir.IRBuilder | None = None  # current function builder

        self.identifiers_table: dict[str, ...] = {}

    # -------------------------------------------------------
    # helper functions
    def sic_type_to_ir_type(self, sic_type: node.TypeName) -> ir.Type:
        match sic_type:
            case node.TypeName.VOID:
                return ir.VoidType()
            case node.TypeName.CHAR:
                return ir.IntType(8)
            case node.TypeName.SHORT:
                return ir.IntType(16)
            case node.TypeName.INT:
                return ir.IntType(32)
            case node.TypeName.LONG:
                return ir.IntType(64)
            case node.TypeName.FLOAT:
                return ir.FloatType()
            case node.TypeName.DOUBLE:
                return ir.DoubleType()

    # -------------------------------------------------------
    # emit functions
    def emit_translation_unit(self):
        for external_declaration in self.translation_unit:
            if isinstance(external_declaration, node.FunctionDefinition):
                self.emit_function_definition(external_declaration)
            elif isinstance(external_declaration, node.Declaration):
                self.emit_declaration(external_declaration)

    def emit_declaration(self, declaration: node.Declaration):
        # create declaration block
        declaration_block = self.cfb.append_basic_block(name=f'{declaration.identifier.token.string}.declaration')

        with self.cfb.goto_block(declaration_block):
            # create declaration variable
            ir_type = self.sic_type_to_ir_type(declaration.type_name)
            ir_variable = self.cfb.alloca(ir_type, name=declaration.identifier.token.string)

            # add to identifiers table
            self.identifiers_table[declaration.identifier.token.string] = ir_variable

            # emit initializer
            if not isinstance(declaration.initializer, node.NoneNode):
                ir_initializer = self.emit_expression(declaration.initializer)
                self.cfb.store(ir_initializer, ir_variable)

        return declaration_block

    def emit_if_statement(self, if_statement: node.If) -> ir.Block:
        # create if block
        if_block: ir.Block = self.cfb.append_basic_block(name='if')

        with self.cfb.goto_block(if_block):
            ir_condition = self.emit_expression(if_statement.condition)

            if isinstance(if_statement.else_body, node.NoneNode):
                # there is no else body
                with self.cfb.if_then(ir_condition):
                    statement = self.emit_compound_statement(if_statement.body)
                    self.cfb.position_at_end(statement)
            else:
                # there is an else body
                with self.cfb.if_else(ir_condition) as (then, otherwise):
                    with then:
                        statement = self.emit_compound_statement(if_statement.body)
                        self.cfb.position_at_end(statement)
                    with otherwise:
                        statement = self.emit_compound_statement(if_statement.else_body)
                        self.cfb.position_at_end(statement)

        return if_block

    # -------------------------------------------------------

    # -------------------------------------------------------
    # add functions

    # -------------------------------------------------------
