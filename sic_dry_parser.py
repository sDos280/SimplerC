"""

the dry parser job is to iterate over the tokens steam and convert the steam to an ast format,
any analysis of the ast won't be done here.

"""

import sic_utils as utils
import sic_token as tk
import sic_lexer as lx
import sic_node as node


class DryParser:
    def __init__(self, lexer: lx.Lexer):
        self.lexer = lexer
        self.index = 0
        self.current_token = lexer.tokens[0]

    # dry parser util methods
    def peek_token(self):
        self.index += 1
        self.current_token = self.lexer.tokens[self.index]

    def drop_token(self):
        self.index -= 1
        self.current_token = self.lexer.tokens[self.index]

    def get_token_by_offset(self, offset: int) -> tk.Token:
        return self.lexer.tokens[self.index + offset]

    def is_token_kind(self, kind: tk.TokenKind | list[tk.TokenKind]) -> bool:
        if isinstance(kind, list):
            return self.current_token.kind in kind
        else:
            return self.current_token.kind == kind

    def expect_token_kind(self, kind: tk.TokenKind | list[tk.TokenKind], error_string: str = "", token: tk.Token | None = None):
        if not self.is_token_kind(kind):
            self.fatal_token(error_string, token)

    def is_token_type_name(self) -> bool:
        return self.is_token_kind([
            tk.TokenKind.VOID,
            tk.TokenKind.CHAR,
            tk.TokenKind.SHORT,
            tk.TokenKind.INT,
            tk.TokenKind.LONG,
            tk.TokenKind.FLOAT,
            tk.TokenKind.DOUBLE,
            tk.TokenKind.SIGNED,
            tk.TokenKind.UNSIGNED
        ])

    def is_token_type_specifier(self) -> bool:
        return self.is_token_type_name()

    def is_assignment_operator(self) -> bool:
        return self.is_token_kind([tk.TokenKind.EQUALS,
                                   tk.TokenKind.MUL_ASSIGN,
                                   tk.TokenKind.DIV_ASSIGN,
                                   tk.TokenKind.MOD_ASSIGN,
                                   tk.TokenKind.ADD_ASSIGN,
                                   tk.TokenKind.SUB_ASSIGN,
                                   tk.TokenKind.LEFT_ASSIGN,
                                   tk.TokenKind.RIGHT_ASSIGN,
                                   tk.TokenKind.AND_ASSIGN,
                                   tk.TokenKind.XOR_ASSIGN,
                                   tk.TokenKind.OR_ASSIGN])

    def is_compound_statement(self) -> bool:
        return self.is_token_kind(tk.TokenKind.OPENING_CURLY_BRACE)

    def is_selection_statement(self) -> bool:
        return self.is_token_kind(tk.TokenKind.IF)

    def is_iteration_statement(self) -> bool:
        return self.is_token_kind([tk.TokenKind.WHILE, tk.TokenKind.FOR])

    def is_jump_statement(self) -> bool:
        return self.is_token_kind([tk.TokenKind.CONTINUE, tk.TokenKind.BREAK, tk.TokenKind.RETURN])

    def fatal_token(self, error_string: str, token: tk.Token = None):
        fetal_token: tk.Token = token if token is not None else self.current_token
        line_index: int = utils.get_line_index_by_char_index(self.lexer.string, fetal_token.start)
        line_string: str = utils.get_line_by_index(self.lexer.string, line_index)

        full_error_string = f"SimplerC : Fetal Token : {error_string}:\n"
        full_error_string += f"    {line_string}\n"
        raise SyntaxError(full_error_string)

    # dry parser non-grammar peek methods
    def peek_identifier(self) -> node.Identifier:
        token: tk.Token = self.current_token

        self.peek_token()  # peek identifier token

        return node.Identifier(token)

    def peek_assignment_operator(self) -> node.CBinaryOpKind:
        if self.is_token_kind(tk.TokenKind.EQUALS):
            self.peek_token()  # peek the = token
            return node.CBinaryOpKind.Assignment
        elif self.is_token_kind(tk.TokenKind.MUL_ASSIGN):
            self.peek_token()  # peek the *= token
            return node.CBinaryOpKind.MultiplicationAssignment
        elif self.is_token_kind(tk.TokenKind.DIV_ASSIGN):
            self.peek_token()  # peek the /= token
            return node.CBinaryOpKind.DivisionAssignment
        elif self.is_token_kind(tk.TokenKind.MOD_ASSIGN):
            self.peek_token()  # peek the %= token
            return node.CBinaryOpKind.ModulusAssignment
        elif self.is_token_kind(tk.TokenKind.ADD_ASSIGN):
            self.peek_token()  # peek the += token
            return node.CBinaryOpKind.AdditionAssignment
        elif self.is_token_kind(tk.TokenKind.SUB_ASSIGN):
            self.peek_token()  # peek the -= token
            return node.CBinaryOpKind.SubtractionAssignment
        elif self.is_token_kind(tk.TokenKind.LEFT_ASSIGN):
            self.peek_token()  # peek the <<= token
            return node.CBinaryOpKind.LeftShiftAssignment
        elif self.is_token_kind(tk.TokenKind.RIGHT_ASSIGN):
            self.peek_token()  # peek the >>= token
            return node.CBinaryOpKind.RightShiftAssignment
        elif self.is_token_kind(tk.TokenKind.AND_ASSIGN):
            self.peek_token()  # peek the &= token
            return node.CBinaryOpKind.BitwiseAndAssignment
        elif self.is_token_kind(tk.TokenKind.XOR_ASSIGN):
            self.peek_token()  # peek the ^= token
            return node.CBinaryOpKind.BitwiseXorAssignment
        elif self.is_token_kind(tk.TokenKind.OR_ASSIGN):
            self.peek_token()  # peek the |= token
            return node.CBinaryOpKind.BitwiseOrAssignment
        else:
            self.fatal_token("Expected assignment operator token")

    # dry parser grammar peek methods
    def peek_primary_expression(self) -> node.Node | list[node.Node]:
        if self.is_token_kind(tk.TokenKind.IDENTIFIER):
            return self.peek_identifier()
        elif self.is_token_kind([tk.TokenKind.INTEGER_LITERAL, tk.TokenKind.FLOAT_LITERAL]):
            token: tk.Token = self.current_token

            self.peek_token()  # peek integer/float literal token

            return node.ConstantLiteral(token)
        elif self.is_token_kind(tk.TokenKind.CHAR_LITERAL):
            token: tk.Token = self.current_token

            self.peek_token()  # peek char literal token

            return node.CharLiteral(token)
        elif self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            self.peek_token()  # peek ( token

            expression: node.Expression = self.peek_expression()

            self.peek_token()  # peek ) token

            return expression
        else:
            self.fatal_token("primary token expected")

    def peek_postfix_expression(self) -> node.Node:
        primary_expression: node.Node = self.peek_primary_expression()

        if self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            self.peek_token()  # peek ( token

            argument_expression_list: list[node.Node] = []

            if not self.is_token_kind(tk.TokenKind.CLOSING_PARENTHESIS):
                argument_expression_list = self.peek_argument_expression_list()

            self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expected ')' in function call")
            self.peek_token()  # peek ) token

            return node.FunctionCall(primary_expression, argument_expression_list)
        elif self.is_token_kind(tk.TokenKind.INC_OP):
            self.peek_token()  # peek ++ token

            return node.CUnaryOp(node.CUnaryOpKind.PostIncrease, primary_expression)
        elif self.is_token_kind(tk.TokenKind.DEC_OP):
            self.peek_token()  # peek -- token

            return node.CUnaryOp(node.CUnaryOpKind.PostDecrease, primary_expression)
        else:
            return primary_expression

    def peek_argument_expression_list(self) -> list[node.Node]:
        argument_expression_list: list[node.Node] = [self.peek_assignment_expression()]

        while self.is_token_kind(tk.TokenKind.COMMA):
            self.peek_token()  # peek , token

            argument_expression_list.append(self.peek_assignment_expression())

        return argument_expression_list

    def peek_unary_expression(self) -> node.Node:
        match self.current_token.kind:
            # INC_OP unary_expression
            # DEC_OP unary_expression
            # unary_operator cast_expression
            # SIZEOF '(' type_name ')'
            # SIZEOF unary_expression

            case tk.TokenKind.INC_OP:
                self.peek_token()  # peek ++ token

                unary_expression: node.Node = self.peek_unary_expression()

                return node.CUnaryOp(node.CUnaryOpKind.PreIncrease, unary_expression)
            case tk.TokenKind.DEC_OP:
                self.peek_token()  # peek -- token

                unary_expression: node.Node = self.peek_unary_expression()

                return node.CUnaryOp(node.CUnaryOpKind.PreDecrease, unary_expression)
            case tk.TokenKind.SIZEOF:
                self.peek_token()  # peek sizeof token

                if self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
                    self.peek_token()  # peek ( token

                    type_name: node.TypeName = self.peek_type_name()

                    self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expected ')' in sizeof expression")
                    self.peek_token()  # peek ) token

                    return node.CUnaryOp(node.CUnaryOpKind.Sizeof, type_name)
                else:
                    unary_expression: node.Node = self.peek_unary_expression()

                    return node.CUnaryOp(node.CUnaryOpKind.Sizeof, unary_expression)
            case tk.TokenKind.PLUS:
                self.peek_token()  # peek + token

                cast_expression: node.Node = self.peek_cast_expression()

                return node.CUnaryOp(node.CUnaryOpKind.Plus, cast_expression)
            case tk.TokenKind.HYPHEN:
                self.peek_token()  # peek - token

                cast_expression: node.Node = self.peek_cast_expression()

                return node.CUnaryOp(node.CUnaryOpKind.Minus, cast_expression)
            case tk.TokenKind.TILDE:
                self.peek_token()  # peek ~ token

                cast_expression: node.Node = self.peek_cast_expression()

                return node.CUnaryOp(node.CUnaryOpKind.BitwiseNOT, cast_expression)
            case tk.TokenKind.EXCLAMATION:
                self.peek_token()  # peek ! token

                cast_expression: node.Node = self.peek_cast_expression()

                return node.CUnaryOp(node.CUnaryOpKind.LogicalNOT, cast_expression)

        return self.peek_postfix_expression()

    def peek_unary_operator(self) -> node.CUnaryOpKind:
        match self.current_token.kind:
            case tk.TokenKind.PLUS:
                self.peek_token()  # peek + token

                return node.CUnaryOpKind.Plus
            case tk.TokenKind.HYPHEN:
                self.peek_token()  # peek - token

                return node.CUnaryOpKind.Minus
            case tk.TokenKind.TILDE:
                self.peek_token()  # peek ~ token

                return node.CUnaryOpKind.BitwiseNOT
            case tk.TokenKind.EXCLAMATION:
                self.peek_token()  # peek ! token

                return node.CUnaryOpKind.LogicalNOT

        self.fatal_token("unary operator expected")

    def peek_cast_expression(self) -> node.Node:
        if self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            self.peek_token()  # peek ( token

            if self.is_token_type_name():
                type_name: node.TypeName = self.peek_type_name()

                self.peek_token()  # peek ) token

                cast_expression: node.Node = self.peek_cast_expression()

                return node.CCast(type_name, cast_expression)
            else:
                self.drop_token()  # drop ( token

        unary_expression: node.Node = self.peek_unary_expression()

        return unary_expression

    def peek_multiplicative_expression(self) -> node.Node:
        cast_expression: node.Node = self.peek_cast_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.ASTERISK):
                self.peek_token()  # peek * token

                sub_cast_expression: node.Node = self.peek_cast_expression()

                cast_expression = node.CBinaryOp(node.CBinaryOpKind.Multiplication, cast_expression, sub_cast_expression)
            elif self.is_token_kind(tk.TokenKind.SLASH):
                self.peek_token()  # peek / token

                sub_cast_expression: node.Node = self.peek_cast_expression()

                cast_expression = node.CBinaryOp(node.CBinaryOpKind.Division, cast_expression, sub_cast_expression)
            elif self.is_token_kind(tk.TokenKind.PERCENTAGE):
                self.peek_token()  # peek % token

                sub_cast_expression: node.Node = self.peek_cast_expression()

                cast_expression = node.CBinaryOp(node.CBinaryOpKind.Modulus, cast_expression, sub_cast_expression)
            else:
                return cast_expression

    def peek_additive_expression(self) -> node.Node:
        multiplicative_expression: node.Node = self.peek_multiplicative_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.PLUS):
                self.peek_token()  # peek + token

                sub_multiplicative_expression: node.Node = self.peek_multiplicative_expression()

                multiplicative_expression = node.CBinaryOp(node.CBinaryOpKind.Addition, multiplicative_expression, sub_multiplicative_expression)
            elif self.is_token_kind(tk.TokenKind.HYPHEN):
                self.peek_token()  # peek - token

                sub_multiplicative_expression: node.Node = self.peek_multiplicative_expression()

                multiplicative_expression = node.CBinaryOp(node.CBinaryOpKind.Subtraction, multiplicative_expression, sub_multiplicative_expression)
            else:
                return multiplicative_expression

    def peek_shift_expression(self) -> node.Node:
        additive_expression: node.Node = self.peek_additive_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.LEFT_OP):
                self.peek_token()  # peek << token

                sub_additive_expression: node.Node = self.peek_additive_expression()

                additive_expression = node.CBinaryOp(node.CBinaryOpKind.LeftShift, additive_expression, sub_additive_expression)
            elif self.is_token_kind(tk.TokenKind.RIGHT_OP):
                self.peek_token()  # peek >> token

                sub_additive_expression: node.Node = self.peek_additive_expression()

                additive_expression = node.CBinaryOp(node.CBinaryOpKind.RightShift, additive_expression, sub_additive_expression)
            else:
                return additive_expression

    def peek_relational_expression(self) -> node.Node:
        shift_expression: node.Node = self.peek_shift_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.LESS_THAN):
                self.peek_token()  # peek the < token

                sub_shift_expression: node.Node = self.peek_shift_expression()

                shift_expression = node.CBinaryOp(node.CBinaryOpKind.LessThan, shift_expression, sub_shift_expression)

            elif self.is_token_kind(tk.TokenKind.GREATER_THAN):
                self.peek_token()  # peek the > token

                sub_shift_expression: node.Node = self.peek_shift_expression()

                shift_expression = node.CBinaryOp(node.CBinaryOpKind.GreaterThan, shift_expression, sub_shift_expression)

            elif self.is_token_kind(tk.TokenKind.LE_OP):
                self.peek_token()  # peek the <= token

                sub_shift_expression: node.Node = self.peek_shift_expression()

                shift_expression = node.CBinaryOp(node.CBinaryOpKind.LessThanOrEqualTo, shift_expression, sub_shift_expression)

            elif self.is_token_kind(tk.TokenKind.GE_OP):
                self.peek_token()  # peek the >= token

                sub_shift_expression: node.Node = self.peek_shift_expression()

                shift_expression = node.CBinaryOp(node.CBinaryOpKind.GreaterThanOrEqualTo, shift_expression, sub_shift_expression)

            else:
                return shift_expression

    def peek_equality_expression(self) -> node.Node:
        relational_expression: node.Node = self.peek_relational_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.EQ_OP):
                self.peek_token()  # peek the == token

                sub_relational_expression: node.Node = self.peek_relational_expression()

                relational_expression = node.CBinaryOp(node.CBinaryOpKind.EqualTo, relational_expression, sub_relational_expression)

            elif self.is_token_kind(tk.TokenKind.NE_OP):
                self.peek_token()  # peek the != token

                sub_relational_expression: node.Node = self.peek_relational_expression()

                relational_expression = node.CBinaryOp(node.CBinaryOpKind.NotEqualTo, relational_expression, sub_relational_expression)

            else:
                return relational_expression

    def peek_and_expression(self) -> node.Node:
        equality_expression: node.Node = self.peek_equality_expression()

        while self.is_token_kind(tk.TokenKind.AMPERSAND):
            self.peek_token()  # peek the & token

            sub_equality_expression: node.Node = self.peek_equality_expression()

            equality_expression = node.CBinaryOp(node.CBinaryOpKind.BitwiseAND, equality_expression, sub_equality_expression)

        return equality_expression

    def peek_exclusive_or_expression(self) -> node.Node:
        and_expression: node.Node = self.peek_and_expression()

        while self.is_token_kind(tk.TokenKind.CIRCUMFLEX):
            self.peek_token()  # peek the ^ token

            sub_and_expression: node.Node = self.peek_and_expression()

            and_expression = node.CBinaryOp(node.CBinaryOpKind.BitwiseXOR, and_expression, sub_and_expression)

        return and_expression

    def peek_inclusive_or_expression(self) -> node.Node:
        exclusive_or_expression: node.Node = self.peek_exclusive_or_expression()

        while self.is_token_kind(tk.TokenKind.VERTICAL_BAR):
            self.peek_token()  # peek the | token

            sub_exclusive_or_expression: node.Node = self.peek_exclusive_or_expression()

            exclusive_or_expression = node.CBinaryOp(node.CBinaryOpKind.BitwiseOR, exclusive_or_expression, sub_exclusive_or_expression)

        return exclusive_or_expression

    def peek_logical_and_expression(self) -> node.Node:
        inclusive_or_expression: node.Node = self.peek_inclusive_or_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.AND_OP):
                self.peek_token()  # peek the && token

                sub_inclusive_or_expression: node.Node = self.peek_inclusive_or_expression()

                inclusive_or_expression = node.CBinaryOp(node.CBinaryOpKind.LogicalAND, inclusive_or_expression, sub_inclusive_or_expression)
            else:
                return inclusive_or_expression

    def peek_logical_or_expression(self) -> node.Node:
        logical_and_expression: node.Node = self.peek_logical_and_expression()

        while self.is_token_kind(tk.TokenKind.OR_OP):
            self.peek_token()  # peek the || token

            sub_logical_and_expression: node.Node = self.peek_logical_and_expression()

            logical_and_expression = node.CBinaryOp(node.CBinaryOpKind.LogicalOR, logical_and_expression, sub_logical_and_expression)

        return logical_and_expression

    def peek_conditional_expression(self) -> node.Node:
        logical_or_expression: node.Node = self.peek_logical_or_expression()

        if self.is_token_kind(tk.TokenKind.QUESTION_MARK):
            self.peek_token()  # peek the ? token

            expression: node.Expression = self.peek_expression()

            self.expect_token_kind(tk.TokenKind.COLON, "Expected ':' in conditional expressions")

            self.peek_token()  # peek the : token

            conditional_expression: node.Node = self.peek_conditional_expression()

            return node.CTernaryOp(logical_or_expression, expression, conditional_expression)

        return logical_or_expression

    def peek_assignment_expression(self) -> node.Node:
        conditional_expression: node.Node = self.peek_conditional_expression()

        if self.is_assignment_operator():
            binary_assignment_op: node.CBinaryOpKind = self.peek_assignment_operator()  # peek assignment operator token

            sub_assignment_expression: node.Node = self.peek_assignment_expression()

            return node.CBinaryOp(binary_assignment_op, conditional_expression, sub_assignment_expression)
        else:
            return conditional_expression

    def peek_expression(self) -> node.Expression:
        expression: node.Expression = node.Expression([self.peek_assignment_expression()])

        while self.is_token_kind(tk.TokenKind.COMMA):
            self.peek_token()  # peek the , token

            expression.expressions.append(self.peek_assignment_expression())

        return expression

    def peek_constant_expression(self) -> node.Node:
        return self.peek_conditional_expression()

    def peek_declaration(self) -> node.Declaration:
        declaration_specifiers: node.TypeName = self.peek_declaration_specifiers()
        init_declarator: node.Declarator = self.peek_init_declarator()

        self.expect_token_kind(tk.TokenKind.SEMICOLON, "Expected ';' in declaration")
        self.peek_token()  # peek the ; token

        return node.Declaration(declaration_specifiers, init_declarator)

    def peek_declaration_specifiers(self) -> node.TypeName:
        return self.peek_specifier_list()

    def peek_init_declarator(self) -> node.Declarator:
        self.expect_token_kind(tk.TokenKind.IDENTIFIER, "Expected identifier in declaration")
        token: tk.Token = self.current_token

        self.peek_token()  # peek identifier token

        identifier: node.Identifier = node.Identifier(token)
        initializer: node.Node = node.NoneNode()

        if self.is_token_kind(tk.TokenKind.EQUALS):
            self.peek_token()  # peek the = token

            initializer: node.Node = self.peek_initializer()

        return identifier, initializer

    def peek_type_specifier(self) -> node.CTypeSpecifier:
        match self.current_token.kind:
            case tk.TokenKind.VOID:
                self.peek_token()  # peek void token

                return node.CTypeSpecifier.VOID
            case tk.TokenKind.CHAR:
                self.peek_token()  # peek char token

                return node.CTypeSpecifier.CHAR
            case tk.TokenKind.SHORT:
                self.peek_token()  # peek short token

                return node.CTypeSpecifier.SHORT
            case tk.TokenKind.INT:
                self.peek_token()  # peek int token

                return node.CTypeSpecifier.INT
            case tk.TokenKind.LONG:
                self.peek_token()  # peek long token

                return node.CTypeSpecifier.LONG
            case tk.TokenKind.FLOAT:
                self.peek_token()  # peek float token

                return node.CTypeSpecifier.FLOAT
            case tk.TokenKind.DOUBLE:
                self.peek_token()  # peek double token

                return node.CTypeSpecifier.DOUBLE
            case tk.TokenKind.SIGNED:
                self.peek_token()  # peek signed token

                return node.CTypeSpecifier.SIGNED
            case tk.TokenKind.UNSIGNED:
                self.peek_token()  # peek unsigned token

                return node.CTypeSpecifier.UNSIGNED

    def peek_parameter_list(self) -> list[node.Declaration]:
        parameter_list: list[node.Declaration] = [self.peek_parameter_declaration()]

        while self.is_token_kind(tk.TokenKind.COMMA):
            self.peek_token()  # peek the , token

            parameter_list.append(self.peek_parameter_declaration())

        return parameter_list

    def peek_parameter_declaration(self) -> node.Declaration:
        declaration_specifiers: node.TypeName = self.peek_declaration_specifiers()

        if self.is_token_kind(tk.TokenKind.IDENTIFIER):
            return node.Declaration(declaration_specifiers, (self.peek_identifier(), node.NoneNode()))
        else:
            return node.Declaration(declaration_specifiers, (node.NoneNode(), node.NoneNode()))

    def peek_specifier_list(self) -> node.CPrimaryType:
        specifier_counter: node.CTypeSpecifier = node.CTypeSpecifier(0)
        c_primary_type: node.CPrimaryType = node.CPrimaryType.VOID

        while self.is_token_type_specifier():
            specifier: node.CTypeSpecifier = self.peek_type_specifier()
            if specifier == node.CTypeSpecifier.UNSIGNED or specifier == node.CTypeSpecifier.SIGNED:
                specifier_counter |= specifier
            else:
                specifier_counter += specifier

            c_primary_type = node.c_type_specifier_counter_to_c_primary_type.get(specifier_counter)

            if c_primary_type is None:
                self.fatal_token("invalid type specifier")

        if specifier_counter == 0:
            self.fatal_token("type specifier expected")

        return c_primary_type

    def peek_type_name(self) -> node.TypeName:
        return self.peek_specifier_list()

    def peek_initializer(self) -> node.Node:
        return self.peek_assignment_expression()

    def peek_statement(self) -> node.Node:
        if self.is_compound_statement():
            return self.peek_compound_statement()
        elif self.is_selection_statement():
            return self.peek_selection_statement()
        elif self.is_iteration_statement():
            return self.peek_iteration_statement()
        elif self.is_jump_statement():
            return self.peek_jump_statement()
        else:
            return self.peek_expression_statement()

    def peek_compound_statement(self) -> node.CompoundStatement:
        compound_statement: node.CompoundStatement = node.CompoundStatement([], [])

        self.expect_token_kind(tk.TokenKind.OPENING_CURLY_BRACE, "Expected '{' in compound statement")
        self.peek_token()  # peek the { token

        # '{' '}'
        if self.is_token_kind(tk.TokenKind.CLOSING_CURLY_BRACE):
            self.peek_token()  # peek the } token

            return compound_statement

        # '{' declaration_list '}'  |  '{' declaration_list '}'  |  '{' declaration_list statement_list '}'
        if self.is_token_type_specifier():
            compound_statement.declarations = self.peek_declaration_list()

        while not self.is_token_kind(tk.TokenKind.CLOSING_CURLY_BRACE):
            compound_statement.statements.append(self.peek_statement())

        self.expect_token_kind(tk.TokenKind.CLOSING_CURLY_BRACE, "Expected '}' in compound statement")
        self.peek_token()  # peek the } token

        return compound_statement

    def peek_declaration_list(self) -> list[node.Declaration]:
        declaration_list: list[node.Declaration] = [self.peek_declaration()]

        while self.is_token_type_specifier():
            declaration_list.append(self.peek_declaration())

        return declaration_list

    def peek_statement_list(self):
        pass

    def peek_expression_statement(self) -> node.Expression | node.NoneNode:
        if self.is_token_kind(tk.TokenKind.SEMICOLON):
            self.peek_token()  # peek the ; token

            return node.NoneNode()
        else:
            expression: node.Expression = self.peek_expression()

            self.expect_token_kind(tk.TokenKind.SEMICOLON, "Expected ';' in expression statement")
            self.peek_token()  # peek the ; token

            return expression

    def peek_selection_statement(self) -> node.If:
        self.expect_token_kind(tk.TokenKind.IF, "Expected 'if' in selection statement")
        self.peek_token()  # peek the if token

        self.expect_token_kind(tk.TokenKind.OPENING_PARENTHESIS, "Expected '(' in selection statement")
        self.peek_token()  # peek the ( token

        decision_expression: node.Expression = self.peek_expression()

        self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expected ')' in selection statement")
        self.peek_token()  # peek the ) token

        if_statement: node.Node = self.peek_statement()

        if self.is_token_kind(tk.TokenKind.ELSE):
            self.peek_token()  # peek the else token

            else_statement: node.Node = self.peek_statement()

            return node.If(decision_expression, if_statement, else_statement)

        return node.If(decision_expression, if_statement, node.NoneNode())

    def peek_iteration_statement(self) -> node.Node:
        if self.is_token_kind(tk.TokenKind.WHILE):
            self.peek_token()  # peek while token

            self.expect_token_kind(tk.TokenKind.OPENING_PARENTHESIS, "Expected '(' in while statement")
            self.peek_token()  # peek ( token

            condition: node.Expression = self.peek_expression()

            self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expected ')' in while statement")
            self.peek_token()  # peek ) token

            statement: node.Node = self.peek_statement()

            return node.While(condition, statement)
        elif self.is_token_kind(tk.TokenKind.FOR):
            self.peek_token()  # peek for token

            self.expect_token_kind(tk.TokenKind.OPENING_PARENTHESIS, "Expected '(' in for statement")
            self.peek_token()  # peek ( token

            initializer: node.Node = self.peek_expression_statement()
            condition: node.Expression = self.peek_expression_statement()
            update: node.Expression = self.peek_expression()

            self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expected ')' in for statement")
            self.peek_token()  # peek ) token

            statement: node.Node = self.peek_statement()

            return node.For(initializer, condition, update, statement)
        else:
            self.fatal_token("Expected iteration statement")

    def peek_jump_statement(self) -> node.Node:
        if self.is_token_kind(tk.TokenKind.CONTINUE):
            continue_node: node.Continue = node.Continue(self.current_token)
            self.peek_token()  # peek continue token

            self.expect_token_kind(tk.TokenKind.SEMICOLON, "Expected ';' in continue statement")
            self.peek_token()  # peek ; token

            return continue_node
        elif self.is_token_kind(tk.TokenKind.BREAK):
            break_node: node.Break = node.Break(self.current_token)
            self.peek_token()  # peek break token

            self.expect_token_kind(tk.TokenKind.SEMICOLON, "Expected ';' in break statement")
            self.peek_token()  # peek ; token

            return break_node
        elif self.is_token_kind(tk.TokenKind.RETURN):
            return_node: node.Return = node.Return(node.NoneNode(), self.current_token)
            self.peek_token()  # peek return token

            return_node.expression = self.peek_expression()

            self.expect_token_kind(tk.TokenKind.SEMICOLON, "Expected ';' in return statement")
            self.peek_token()  # peek ; token

            return return_node
        else:
            self.fatal_token("Expected jump statement")

    def peek_translation_unit(self) -> node.TranslationUnit:
        translation_unit: node.TranslationUnit = []

        while not self.is_token_kind(tk.TokenKind.END):
            translation_unit.append(self.peek_external_declaration())

        return translation_unit

    def peek_external_declaration(self) -> node.ExternalDeclaration:
        if self.is_token_kind(tk.TokenKind.FUNC):
            return self.peek_function_definition()
        elif self.is_token_type_specifier():
            return self.peek_declaration()
        else:
            self.fatal_token("Expected external declaration")

    def peek_function_definition(self) -> node.FunctionDefinition | node.FunctionDeclaration:
        self.expect_token_kind(tk.TokenKind.FUNC, "Expected func keyword in function definition")
        self.peek_token()  # peek func token

        declaration_specifiers: node.TypeName = self.peek_declaration_specifiers()

        self.expect_token_kind(tk.TokenKind.IDENTIFIER, "Expected identifier in function definition")
        identifier: node.Identifier = node.Identifier(self.current_token)
        self.peek_token()  # peek identifier token

        self.expect_token_kind(tk.TokenKind.OPENING_PARENTHESIS, "Expected '(' in function definition")
        self.peek_token()  # peek ( token

        parameter_list: list[node.Declaration] = self.peek_parameter_list()

        self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expected ')' in function definition")
        self.peek_token()  # peek ) token

        if self.is_token_kind(tk.TokenKind.SEMICOLON):
            self.peek_token()  # peek ; token

            return node.FunctionDeclaration(declaration_specifiers, identifier, parameter_list)
        else:
            compound_statement: node.CompoundStatement = self.peek_compound_statement()

            return node.FunctionDefinition(declaration_specifiers, identifier, parameter_list, compound_statement)
