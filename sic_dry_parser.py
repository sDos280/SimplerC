"""

the dry parser job is to iterate over the tokens steam and convert the steam to an ast format,
any analysis of the ast won't be done here.

"""

import typing
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

    def is_token_kind(self, kind: tk.TokenKind | list[tk.TokenKind]) -> bool:
        if isinstance(kind, list):
            return self.current_token.kind in kind
        else:
            return self.current_token.kind == kind

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

    @staticmethod
    def is_node(node_type: typing.Type[node.Node] | list[typing.Type[node.Node]], obj: node.Node) -> bool:
        return isinstance(node_type, obj)

    def fetal_token(self, error_string: str, token: tk.Token = None):
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

    # dry parser grammar peek methods
    def peek_primary_expression(self) -> node.Node:
        if self.is_token_kind(tk.TokenKind.IDENTIFIER):
            return self.peek_identifier()
        elif self.is_token_kind([tk.TokenKind.INTEGER_LITERAL, tk.TokenKind.FLOAT_LITERAL]):
            token: tk.Token = self.current_token

            self.peek_token()  # peek integer/float literal token

            return node.ConstantLiteral(token)
        elif self.is_token_kind(tk.TokenKind.STRING_LITERAL):
            token: tk.Token = self.current_token

            self.peek_token()  # peek string literal token

            return node.StringLiteral(token)
        elif self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            self.peek_token()  # peek ( token

            expression: node.Node = self.peek_expression()

            self.peek_token()  # peek ) token

            return expression
        else:
            self.fetal_token("primary token expected")

    def peek_postfix_expression(self):
        primary_expression: node.Node = self.peek_primary_expression()

        if self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            assert False, "not implemented yet"
        elif self.is_token_kind(tk.TokenKind.INC_OP):
            self.peek_token()  # peek ++ token

            return node.CUnaryOp(node.CUnaryOpKind.PostIncrease, primary_expression)
        elif self.is_token_kind(tk.TokenKind.DEC_OP):
            self.peek_token()  # peek -- token

            return node.CUnaryOp(node.CUnaryOpKind.PostDecrease, primary_expression)
        else:
            return primary_expression

    def peek_argument_expression_list(self):
        pass

    def peek_unary_expression(self):
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
                assert False, "not implemented yet"
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

    def peek_unary_operator(self):
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

        self.fetal_token("unary operator expected")

    def peek_cast_expression(self):
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

    def peek_multiplicative_expression(self):
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

    def peek_additive_expression(self):
        pass

    def peek_shift_expression(self):
        pass

    def peek_relational_expression(self):
        pass

    def peek_equality_expression(self):
        pass

    def peek_and_expression(self):
        pass

    def peek_exclusive_or_expression(self):
        pass

    def peek_inclusive_or_expression(self):
        pass

    def peek_logical_and_expression(self):
        pass

    def peek_logical_or_expression(self):
        pass

    def peek_conditional_expression(self):
        pass

    def peek_assignment_expression(self):
        pass

    def peek_assignment_operator(self):
        pass

    def peek_expression(self):
        pass

    def peek_constant_expression(self):
        pass

    def peek_declaration(self):
        pass

    def peek_declaration_specifiers(self):
        pass

    def peek_init_declarator_list(self):
        pass

    def peek_init_declarator(self):
        pass

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

    def peek_struct_or_union_specifier(self):
        pass

    def peek_struct_or_union(self):
        pass

    def peek_struct_declaration_list(self):
        pass

    def peek_struct_declaration(self):
        pass

    def peek_specifier_qualifier_list(self):
        pass

    def peek_struct_declarator_list(self):
        pass

    def peek_struct_declarator(self):
        pass

    def peek_enum_specifier(self):
        pass

    def peek_enumerator_list(self):
        pass

    def peek_enumerator(self):
        pass

    def peek_type_qualifier(self):
        pass

    def peek_declarator(self):
        pass

    def peek_direct_declarator(self):
        pass

    def peek_pointer(self):
        pass

    def peek_type_qualifier_list(self):
        pass

    def peek_parameter_type_list(self):
        pass

    def peek_parameter_list(self):
        pass

    def peek_parameter_declaration(self):
        pass

    def peek_identifier_list(self):
        pass

    def peek_type_name(self) -> node.TypeName:
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
                self.fetal_token("invalid type specifier")

        if specifier_counter == 0:
            self.fetal_token("type specifier expected")

        return c_primary_type

    def peek_abstract_declarator(self):
        pass

    def peek_direct_abstract_declarator(self):
        pass

    def peek_initializer(self):
        pass

    def peek_initializer_list(self):
        pass

    def peek_statement(self):
        pass

    def peek_compound_statement(self):
        pass

    def peek_declaration_list(self):
        pass

    def peek_statement_list(self):
        pass

    def peek_expression_statement(self):
        pass

    def peek_selection_statement(self):
        pass

    def peek_iteration_statement(self):
        pass

    def peek_jump_statement(self):
        pass

    def peek_translation_unit(self):
        pass

    def peek_external_declaration(self):
        pass

    def peek_function_definition(self):
        pass
