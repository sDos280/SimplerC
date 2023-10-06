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


class StackPackage:
    # this class is used to store the information of the identifiers in the stack
    def __init__(self, identifier_str: str, declaration: node.Declaration | node.FunctionDefinition, ir_declaration: ir.Function | ir.Value):
        self.identifier_str = identifier_str
        self.declaration = declaration
        self.ir_declaration = ir_declaration

    def to_dict(self):
        return {
            f'{self.identifier_str}': (self.declaration, self.ir_declaration)
        }


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
    @staticmethod
    def sic_type_to_ir_type(sic_type: node.TypeName) -> ir.Type:
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

    def get_expression_type(self, expression: node.Node) -> node.CPrimaryType:
        if isinstance(expression, node.CBinaryOp):
            return self.get_binary_expression_type(expression)
        elif isinstance(expression, node.CharLiteral):
            return node.CPrimaryType.CHAR
        elif isinstance(expression, node.ConstantLiteral):
            if expression.token.string.find('.') == 1:
                return node.CPrimaryType.FLOAT
            else:
                return node.CPrimaryType.INT
        elif isinstance(expression, node.Identifier):
            identifier_in_stack: node.Declaration = self.look_for_ed_string_in_stack(expression.token.string)[0]

            if identifier_in_stack is None:
                raise SyntaxError("SimplerC : Some Thing Went Wrong: ...")

            return identifier_in_stack.type_name
        elif isinstance(expression, node.CUnaryOp):
            return self.get_unary_expression_type(expression)
        elif isinstance(expression, node.CCast):
            return expression.type_name
        elif isinstance(expression, node.CTernaryOp):
            return self.get_ternary_expression_type(expression)
        elif isinstance(expression, node.FunctionCall):
            return self.get_function_call_type(expression)
        else:
            raise SyntaxError("SimplerC : Type Error : the node in not an expression")

    def get_binary_expression_type(self, expression: node.CBinaryOp) -> node.CPrimaryType:
        left_type: node.CPrimaryType = self.get_expression_type(expression.left)
        right_type: node.CPrimaryType = self.get_expression_type(expression.right)

        if left_type != right_type:
            raise SyntaxError("SimplerC : Some Thing Went Wrong: ...")

        return left_type

    def get_unary_expression_type(self, expression: node.CUnaryOp) -> node.CPrimaryType:
        if expression.kind == node.CUnaryOpKind.Sizeof:
            return node.CPrimaryType.INT
        else:
            return self.get_expression_type(expression.expression)

    def get_ternary_expression_type(self, expression: node.CTernaryOp) -> node.CPrimaryType:
        if self.get_expression_type(expression.true_value) != self.get_expression_type(expression.false_value):
            raise SyntaxError("SimplerC : Some Thing Went Wrong: ...")

        return self.get_expression_type(expression.true_value)

    def get_function_call_type(self, expression: node.FunctionCall) -> node.CPrimaryType:
        identifier_in_stack: node.FunctionDefinition = self.look_for_ed_string_in_stack(expression.identifier.token.string)[0]

        if identifier_in_stack is None:
            raise SyntaxError("SimplerC : Some Thing Went Wrong: ...")

        return identifier_in_stack.type_name

    def look_for_ed_string_in_stack(self, identifier_str: str):
        return self.identifiers_table[identifier_str]

    # -------------------------------------------------------
    # emit functions
    def emit_translation_unit(self):
        for external_declaration in self.translation_unit:
            if isinstance(external_declaration, node.FunctionDefinition):
                self.emit_function_definition(external_declaration)
            elif isinstance(external_declaration, node.Declaration):
                self.emit_declaration(external_declaration)

    def emit_expression(self, expression: node.ExpressionTypes, create_block: False):

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
                ir_initializer = self.emit_expression(declaration.initializer, create_block=False)
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

    def emit_expression(self, expression: node.ExpressionTypes) -> ir.Value:
        # assignment expression will be inlined to the block

        if isinstance(expression, node.CBinaryOp):
            return self.emit_binary_operator(expression)
        elif isinstance(expression, node.Expression):
            for expression in expression.expressions:
                return self.emit_expression(expression)
        elif isinstance(expression, node.CUnaryOp):
            assert False, "not implemented"
        elif isinstance(expression, node.CCast):
            return self.emit_cast_expression(expression)
        elif isinstance(expression, node.CTernaryOp):
            assert False, "not implemented"
        elif isinstance(expression, node.FunctionCall):
            assert False, "not implemented"
        elif isinstance(expression, node.CharLiteral):
            return ir.Constant(ir.IntType(8), ord(expression.token.string[1]))
        elif isinstance(expression, node.ConstantLiteral):
            if expression.token.string.find('.') == 1:  # a constant float literal
                return ir.Constant(ir.FloatType(), float(expression.token.string))
            else:  # a constant int literal
                return ir.Constant(ir.IntType(32), int(expression.token.string))
        elif isinstance(expression, node.Identifier):
            # return the ir variable of the identifier
            return self.identifiers_table[expression.token.string]
        else:
            raise SyntaxError("SimplerC : Type Error : the node in not an expression")

    """def emit_cast_expression(self, expression: node.CCast):
        "
        # -----------------------------------------
        CHAR = enum.auto()  # 'char' or 'signed char'
        # UCHAR = enum.auto()  # 'unsigned char'
        SHORT = enum.auto()  # 'short' or 'short int' or 'signed short' or 'signed short int'
        # USHORT = enum.auto()  # 'unsigned short'
        INT = enum.auto()  # 'int' or 'signed' or 'signed int'
        # UINT = enum.auto()  # 'unsigned' or 'unsigned int'
        LONG = enum.auto()  # 'long' or 'long int' or 'signed long' or 'signed long int'
        # ULONG = enum.auto()  # 'unsigned long'
        # -----------------------------------------
        FLOAT = enum.auto()  # 'float'
        DOUBLE = enum.auto()  # 'double'
        # -----------------------------------------
        "

        # get the type of the expression
        expression_cast_type = self.sic_type_to_ir_type(expression.type_name)

        # get the value of the expression
        expression_value = self.emit_expression(expression.expression)
        expression_value_type = self.cfb."""

    def emit_store(self, store_to: node.Identifier, what_to_store: ir.Value):
        self.cfb.store(what_to_store, self.identifiers_table[store_to.token.string])

    # -------------------------------------------------------

    # -------------------------------------------------------
    # add functions

    # -------------------------------------------------------
