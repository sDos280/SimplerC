"""

the emitter job is to emit the ast code

"""
import enum
import sic_node as node
import llvmlite.ir as ir


class StackPackage:
    # this class is used to store the information of the identifiers in the stack
    def __init__(self, declaration: node.Declaration | node.FunctionDefinition, ir_declaration: ir.Function | ir.Value):
        self.declaration = declaration
        self.ir_declaration = ir_declaration

    def to_tuple(self):
        return self.declaration, self.ir_declaration


class Emitter:
    def __init__(self, lexer, translation_unit):
        self.lexer = lexer
        self.translation_unit = translation_unit

        self.module: ir.Module = ir.Module()

        self.current_function_ir: ir.Function | None = None
        self.current_iteration_ir: ir.Block | None = None

        self.cfb: ir.IRBuilder | None = None  # current function builder

        self.identifiers_table: list[StackPackage] = []

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

    def pop_stack_by(self, amount: int) -> None:
        for _ in range(amount):
            self.identifiers_table.pop()

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
            identifier_in_stack: node.Declaration = self.look_for_ed_identifier_in_stack(expression).declaration

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
        identifier_in_stack: node.FunctionDefinition = self.look_for_ed_identifier_in_stack(expression.identifier).declaration

        if identifier_in_stack is None:
            raise SyntaxError("SimplerC : Some Thing Went Wrong: ...")

        return identifier_in_stack.type_name

    def look_for_ed_identifier_in_stack(self, identifier: node.Identifier) -> StackPackage | None:
        for stack_package in self.identifiers_table:
            if stack_package.declaration.identifier.token.string == identifier.token.string:
                return stack_package
        return None

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
            # the caller of emit_declaration is responsible for popping the identifier from the stack
            self.identifiers_table.append(StackPackage(declaration, ir_variable))

            # emit initializer
            if not isinstance(declaration.initializer, node.NoneNode):
                ir_initializer = self.emit_expression(declaration.initializer)
                self.cfb.store(ir_initializer, ir_variable)

        return declaration_block

    def emit_if_statement(self, if_statement: node.If) -> None:
        # inline if statement
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

    def emit_compound_statement(self, compound_statement: node.CompoundStatement) -> ir.Block:
        # create compound block
        compound_block: ir.Block = self.cfb.append_basic_block(name='compound')

        with self.cfb.goto_block(compound_block):
            for declaration in compound_statement.declarations:
                self.emit_declaration(declaration)

            for statement in compound_statement.statements:
                self.emit_statement(statement)

        self.pop_stack_by(len(compound_statement.declarations))

        return compound_block

    def emit_statement(self, statement: node.StatementTypes) -> None:
        # inline statement
        if isinstance(statement, node.CompoundStatement):
            self.emit_compound_statement(statement)
        elif isinstance(statement, node.Expression):
            self.emit_expression(statement)
        elif isinstance(statement, node.If):
            self.emit_if_statement(statement)
        elif isinstance(statement, node.While):
            self.emit_while_statement(statement)
        elif isinstance(statement, node.For):
            self.emit_for_statement(statement)
        elif isinstance(statement, node.Return):
            self.emit_return_statement(statement)
        elif isinstance(statement, node.Break):
            self.emit_break_statement(statement)
        elif isinstance(statement, node.Continue):
            self.emit_continue_statement(statement)
        else:
            raise SyntaxError("SimplerC : Some Thing Went Wrong: ...")

    def emit_expression(self, expression: node.ExpressionTypes) -> ir.Value | None:
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
            return self.look_for_ed_identifier_in_stack(expression).ir_declaration
        else:
            raise SyntaxError("SimplerC : Type Error : the node in not an expression")

    def emit_cast_expression(self, expression: node.CCast) -> ir.Value:
        # get the value of the expression
        expression_value = self.emit_expression(expression.expression)
        expression_value_type: node.CPrimaryType = self.get_expression_type(expression.expression)

        return self.emit_cast_instruction(expression.type_name, expression_value, expression_value_type)

    def emit_cast_instruction(self, cast_to: node.CPrimaryType, what_to_cast_ir: ir.Value, what_to_cast_type: node.CPrimaryType) -> ir.Value:
        match cast_to:
            case node.CPrimaryType.CHAR:  # the default char type is unsigned char
                match what_to_cast_type:
                    case node.CPrimaryType.CHAR:  # char to char
                        return what_to_cast_ir
                    case node.CPrimaryType.SHORT:  # short to char
                        return self.cfb.trunc(what_to_cast_ir, ir.IntType(8))
                    case node.CPrimaryType.INT:  # int to char
                        return self.cfb.trunc(what_to_cast_ir, ir.IntType(8))
                    case node.CPrimaryType.LONG:  # long to char
                        return self.cfb.trunc(what_to_cast_ir, ir.IntType(8))
                    case node.CPrimaryType.FLOAT:  # float to char
                        return self.cfb.fptoui(what_to_cast_ir, ir.IntType(8))
                    case node.CPrimaryType.DOUBLE:  # double to char
                        raise SyntaxError("SimplerC : Type Error : cannot cast double to char")
            case node.CPrimaryType.SHORT:
                match what_to_cast_type:
                    case node.CPrimaryType.CHAR:  # char to short
                        return self.cfb.zext(what_to_cast_ir, ir.IntType(16))
                    case node.CPrimaryType.SHORT:  # short to short
                        return what_to_cast_ir
                    case node.CPrimaryType.INT:  # int to short
                        return self.cfb.trunc(what_to_cast_ir, ir.IntType(16))
                    case node.CPrimaryType.LONG:  # long to short
                        return self.cfb.trunc(what_to_cast_ir, ir.IntType(16))
                    case node.CPrimaryType.FLOAT:  # float to short
                        return self.cfb.fptosi(what_to_cast_ir, ir.IntType(16))
                    case node.CPrimaryType.DOUBLE:  # double to short
                        raise SyntaxError("SimplerC : Type Error : cannot cast double to short")
            case node.CPrimaryType.INT:
                match what_to_cast_type:
                    case node.CPrimaryType.CHAR:  # char to int
                        return self.cfb.zext(what_to_cast_ir, ir.IntType(32))
                    case node.CPrimaryType.SHORT:  # short to int
                        return self.cfb.zext(what_to_cast_ir, ir.IntType(32))
                    case node.CPrimaryType.INT:  # int to int
                        return what_to_cast_ir
                    case node.CPrimaryType.LONG:  # long to int
                        return self.cfb.trunc(what_to_cast_ir, ir.IntType(32))
                    case node.CPrimaryType.FLOAT:  # float to int
                        return self.cfb.fptosi(what_to_cast_ir, ir.IntType(32))
                    case node.CPrimaryType.DOUBLE:  # double to int
                        raise SyntaxError("SimplerC : Type Error : cannot cast double to int")
            case node.CPrimaryType.LONG:  # the default long type is signed long
                match what_to_cast_type:
                    case node.CPrimaryType.CHAR:  # char to long
                        return self.cfb.zext(what_to_cast_ir, ir.IntType(64))
                    case node.CPrimaryType.SHORT:  # short to long
                        return self.cfb.zext(what_to_cast_ir, ir.IntType(64))
                    case node.CPrimaryType.INT:  # int to long
                        return self.cfb.zext(what_to_cast_ir, ir.IntType(64))
                    case node.CPrimaryType.LONG:  # long to long
                        return what_to_cast_ir
                    case node.CPrimaryType.FLOAT:  # float to long
                        return self.cfb.fptosi(what_to_cast_ir, ir.IntType(64))
                    case node.CPrimaryType.DOUBLE:  # double to long
                        raise SyntaxError("SimplerC : Type Error : cannot cast double to long")
            case node.CPrimaryType.FLOAT:
                match what_to_cast_type:
                    case node.CPrimaryType.CHAR:  # char to float
                        return self.cfb.uitofp(what_to_cast_ir, ir.FloatType())
                    case node.CPrimaryType.SHORT:  # short to float
                        return self.cfb.sitofp(what_to_cast_ir, ir.FloatType())
                    case node.CPrimaryType.INT:  # int to float
                        return self.cfb.sitofp(what_to_cast_ir, ir.FloatType())
                    case node.CPrimaryType.LONG:  # long to float
                        return self.cfb.sitofp(what_to_cast_ir, ir.FloatType())
                    case node.CPrimaryType.FLOAT:  # float to float
                        return what_to_cast_ir
                    case node.CPrimaryType.DOUBLE:  # double to float
                        raise self.cfb.fpext(what_to_cast_ir, ir.FloatType())
            case node.CPrimaryType.DOUBLE:
                match what_to_cast_type:
                    case node.CPrimaryType.CHAR:  # char to double
                        return self.cfb.uitofp(what_to_cast_ir, ir.DoubleType())
                    case node.CPrimaryType.SHORT:  # short to double
                        return self.cfb.sitofp(what_to_cast_ir, ir.DoubleType())
                    case node.CPrimaryType.INT:  # int to double
                        return self.cfb.sitofp(what_to_cast_ir, ir.DoubleType())
                    case node.CPrimaryType.LONG:  # long to double
                        return self.cfb.sitofp(what_to_cast_ir, ir.DoubleType())
                    case node.CPrimaryType.FLOAT:  # float to double
                        return self.cfb.fpext(what_to_cast_ir, ir.DoubleType())
                    case node.CPrimaryType.DOUBLE:  # double to double
                        return what_to_cast_ir

    def emit_store(self, store_to: node.Identifier, what_to_store: ir.Value) -> None:
        self.cfb.store(what_to_store, self.look_for_ed_identifier_in_stack(store_to).ir_declaration)

    def emit_binary_operator(self, binary_expression: node.CBinaryOp) -> ir.Value | None:
        # assignment operator
        assignment_operators: list[node.CBinaryOpKind] = [
            node.CBinaryOpKind.Assignment,
            node.CBinaryOpKind.AdditionAssignment,
            node.CBinaryOpKind.SubtractionAssignment,
            node.CBinaryOpKind.MultiplicationAssignment,
            node.CBinaryOpKind.DivisionAssignment,
            node.CBinaryOpKind.ModulusAssignment,
            node.CBinaryOpKind.BitwiseAndAssignment,
            node.CBinaryOpKind.BitwiseOrAssignment,
            node.CBinaryOpKind.BitwiseXorAssignment,
            node.CBinaryOpKind.LeftShiftAssignment,
            node.CBinaryOpKind.RightShiftAssignment,
        ]

        conditional_operators: list[node.CBinaryOpKind] = [
            node.CBinaryOpKind.EqualTo,
            node.CBinaryOpKind.NotEqualTo,
            node.CBinaryOpKind.GreaterThan,
            node.CBinaryOpKind.GreaterThanOrEqualTo,
            node.CBinaryOpKind.LessThan,
            node.CBinaryOpKind.LessThanOrEqualTo,
            node.CBinaryOpKind.LogicalAND,
            node.CBinaryOpKind.LogicalOR,
        ]

        # check if the binary expression is an assignment operator
        if binary_expression.kind in assignment_operators:
            # make sure the left side is an identifier
            if not isinstance(binary_expression.left, node.Identifier):
                raise SyntaxError("SimplerC : Syntax Error : left side of assignment operator must be an identifier")

            match binary_expression.kind:
                case node.CBinaryOpKind.Assignment:
                    self.emit_store(binary_expression.left, self.emit_expression(binary_expression.right))
                case node.CBinaryOpKind.AdditionAssignment:
                    if self.look_for_ed_identifier_in_stack(binary_expression.left).declaration.type_name in [node.CPrimaryType.CHAR,
                                                                                                              node.CPrimaryType.SHORT,
                                                                                                              node.CPrimaryType.INT,
                                                                                                              node.CPrimaryType.LONG]:
                        self.emit_store(binary_expression.left, self.cfb.add(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                    else:  # float or double
                        self.emit_store(binary_expression.left, self.cfb.fadd(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                case node.CBinaryOpKind.SubtractionAssignment:
                    if self.look_for_ed_identifier_in_stack(binary_expression.left).declaration.type_name in [node.CPrimaryType.CHAR,
                                                                                                              node.CPrimaryType.SHORT,
                                                                                                              node.CPrimaryType.INT,
                                                                                                              node.CPrimaryType.LONG]:
                        self.emit_store(binary_expression.left, self.cfb.sub(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                    else:  # float or double
                        self.emit_store(binary_expression.left, self.cfb.fsub(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                case node.CBinaryOpKind.MultiplicationAssignment:
                    if self.look_for_ed_identifier_in_stack(binary_expression.left).declaration.type_name in [node.CPrimaryType.CHAR,
                                                                                                              node.CPrimaryType.SHORT,
                                                                                                              node.CPrimaryType.INT,
                                                                                                              node.CPrimaryType.LONG]:
                        self.emit_store(binary_expression.left, self.cfb.mul(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                    else:  # float or double
                        self.emit_store(binary_expression.left, self.cfb.fmul(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                case node.CBinaryOpKind.DivisionAssignment:
                    if self.look_for_ed_identifier_in_stack(binary_expression.left).declaration.type_name in [node.CPrimaryType.CHAR,
                                                                                                              node.CPrimaryType.SHORT,
                                                                                                              node.CPrimaryType.INT,
                                                                                                              node.CPrimaryType.LONG]:
                        self.emit_store(binary_expression.left, self.cfb.sdiv(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                    else:  # float or double
                        self.emit_store(binary_expression.left, self.cfb.fdiv(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                case node.CBinaryOpKind.ModulusAssignment:
                    if self.look_for_ed_identifier_in_stack(binary_expression.left).declaration.type_name in [node.CPrimaryType.SHORT,
                                                                                                              node.CPrimaryType.INT,
                                                                                                              node.CPrimaryType.LONG]:
                        self.emit_store(binary_expression.left, self.cfb.srem(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                    elif self.look_for_ed_identifier_in_stack(binary_expression.left).declaration.type_name == node.CPrimaryType.CHAR:
                        self.emit_store(binary_expression.left, self.cfb.urem(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                    else:  # float or double
                        self.emit_store(binary_expression.left, self.cfb.frem(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                case node.CBinaryOpKind.BitwiseAndAssignment:
                    if self.look_for_ed_identifier_in_stack(binary_expression.left).declaration.type_name in [node.CPrimaryType.CHAR,
                                                                                                              node.CPrimaryType.SHORT,
                                                                                                              node.CPrimaryType.INT,
                                                                                                              node.CPrimaryType.LONG]:
                        self.emit_store(binary_expression.left, self.cfb.and_(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                    else:  # float or double
                        raise SyntaxError("SimplerC : Syntax Error : bitwise and operator cannot be applied to float or double")
                case node.CBinaryOpKind.BitwiseOrAssignment:
                    if self.look_for_ed_identifier_in_stack(binary_expression.left).declaration.type_name in [node.CPrimaryType.CHAR,
                                                                                                              node.CPrimaryType.SHORT,
                                                                                                              node.CPrimaryType.INT,
                                                                                                              node.CPrimaryType.LONG]:
                        self.emit_store(binary_expression.left, self.cfb.or_(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                    else:  # float or double
                        raise SyntaxError("SimplerC : Syntax Error : bitwise or operator cannot be applied to float or double")
                case node.CBinaryOpKind.BitwiseXorAssignment:
                    if self.look_for_ed_identifier_in_stack(binary_expression.left).declaration.type_name in [node.CPrimaryType.CHAR,
                                                                                                              node.CPrimaryType.SHORT,
                                                                                                              node.CPrimaryType.INT,
                                                                                                              node.CPrimaryType.LONG]:
                        self.emit_store(binary_expression.left, self.cfb.xor(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                    else:  # float or double
                        raise SyntaxError("SimplerC : Syntax Error : bitwise xor operator cannot be applied to float or double")
                case node.CBinaryOpKind.LeftShiftAssignment:
                    if self.look_for_ed_identifier_in_stack(binary_expression.left).declaration.type_name in [node.CPrimaryType.CHAR,
                                                                                                              node.CPrimaryType.SHORT,
                                                                                                              node.CPrimaryType.INT,
                                                                                                              node.CPrimaryType.LONG]:
                        self.emit_store(binary_expression.left, self.cfb.shl(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                    else:  # float or double
                        raise SyntaxError("SimplerC : Syntax Error : left shift operator cannot be applied to float or double")
                case node.CBinaryOpKind.RightShiftAssignment:
                    if self.look_for_ed_identifier_in_stack(binary_expression.left).declaration.type_name in [node.CPrimaryType.CHAR,
                                                                                                              node.CPrimaryType.SHORT,
                                                                                                              node.CPrimaryType.INT,
                                                                                                              node.CPrimaryType.LONG]:
                        self.emit_store(binary_expression.left, self.cfb.ashr(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right)))
                    else:  # float or double
                        raise SyntaxError("SimplerC : Syntax Error : right shift operator cannot be applied to float or double")

        elif binary_expression.kind in conditional_operators:  # conditional operators
            match binary_expression.kind:
                case node.CBinaryOpKind.EqualTo:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.icmp_signed('==', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    elif self.get_expression_type(binary_expression.left) == node.CPrimaryType.CHAR:
                        return self.cfb.icmp_unsigned('==', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        return self.cfb.fcmp_ordered('==', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                case node.CBinaryOpKind.NotEqualTo:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.icmp_signed('!=', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    elif self.get_expression_type(binary_expression.left) == node.CPrimaryType.CHAR:
                        return self.cfb.icmp_unsigned('!=', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        return self.cfb.fcmp_ordered('!=', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                case node.CBinaryOpKind.GreaterThan:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.icmp_signed('>', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    elif self.get_expression_type(binary_expression.left) == node.CPrimaryType.CHAR:
                        return self.cfb.icmp_unsigned('>', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        return self.cfb.fcmp_ordered('>', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                case node.CBinaryOpKind.GreaterThanOrEqualTo:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.icmp_signed('>=', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    elif self.get_expression_type(binary_expression.left) == node.CPrimaryType.CHAR:
                        return self.cfb.icmp_unsigned('>=', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        return self.cfb.fcmp_ordered('>=', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                case node.CBinaryOpKind.LessThan:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.icmp_signed('<', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    elif self.get_expression_type(binary_expression.left) == node.CPrimaryType.CHAR:
                        return self.cfb.icmp_unsigned('<', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        return self.cfb.fcmp_ordered('<', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                case node.CBinaryOpKind.LessThanOrEqualTo:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.icmp_signed('<=', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    elif self.get_expression_type(binary_expression.left) == node.CPrimaryType.CHAR:
                        return self.cfb.icmp_unsigned('<=', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        return self.cfb.fcmp_ordered('<=', self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                case node.CBinaryOpKind.LogicalAND:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.CHAR,
                                                                            node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.and_(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        raise SyntaxError("SimplerC : Syntax Error : bitwise and operator cannot be applied to float or double")
                case node.CBinaryOpKind.LogicalOR:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.CHAR,
                                                                            node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.or_(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        raise SyntaxError("SimplerC : Syntax Error : bitwise or operator cannot be applied to float or double")

        else:  # non-assignment binary operators or conditional operators
            match binary_expression.kind:
                case node.CBinaryOpKind.Addition:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.CHAR,
                                                                            node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.add(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        return self.cfb.fadd(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                case node.CBinaryOpKind.Subtraction:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.CHAR,
                                                                            node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.sub(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        return self.cfb.fsub(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                case node.CBinaryOpKind.Multiplication:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.CHAR,
                                                                            node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.mul(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        return self.cfb.fmul(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                case node.CBinaryOpKind.Division:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.CHAR,
                                                                            node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.sdiv(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        return self.cfb.fdiv(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                case node.CBinaryOpKind.Modulus:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.srem(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    elif self.get_expression_type(binary_expression.left) == node.CPrimaryType.CHAR:
                        return self.cfb.urem(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        return self.cfb.frem(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                case node.CBinaryOpKind.BitwiseOR:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.CHAR,
                                                                            node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.or_(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        raise SyntaxError("SimplerC : Syntax Error : bitwise or operator cannot be applied to float or double")
                case node.CBinaryOpKind.BitwiseAND:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.CHAR,
                                                                            node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.and_(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        raise SyntaxError("SimplerC : Syntax Error : bitwise and operator cannot be applied to float or double")
                case node.CBinaryOpKind.BitwiseXOR:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.CHAR,
                                                                            node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.xor(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        raise SyntaxError("SimplerC : Syntax Error : bitwise xor operator cannot be applied to float or double")
                case node.CBinaryOpKind.LeftShift:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.CHAR,
                                                                            node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.shl(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        raise SyntaxError("SimplerC : Syntax Error : left shift operator cannot be applied to float or double")
                case node.CBinaryOpKind.RightShift:
                    if self.get_expression_type(binary_expression.left) in [node.CPrimaryType.CHAR,
                                                                            node.CPrimaryType.SHORT,
                                                                            node.CPrimaryType.INT,
                                                                            node.CPrimaryType.LONG]:
                        return self.cfb.ashr(self.emit_expression(binary_expression.left), self.emit_expression(binary_expression.right))
                    else:  # float or double
                        raise SyntaxError("SimplerC : Syntax Error : right shift operator cannot be applied to float or double")

    # -------------------------------------------------------

    # -------------------------------------------------------
    # add functions

    # -------------------------------------------------------
