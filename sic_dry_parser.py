"""

the dry parser job is to iterate over the tokens steam and convert the steam to an ast format,
any analysis of the ast won't be done here.

"""

import typing
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

    def is_token_kind(self, kind: tk.TokenKind | list[tk.TokenKind]) -> bool:
        if isinstance(kind, list):
            return self.current_token.kind in kind
        else:
            return self.current_token.kind == kind

    @staticmethod
    def is_node(node_type: typing.Type[node.Node] | list[typing.Type[node.Node]], obj: node.Node) -> bool:
        return isinstance(node_type, obj)

    def fetal_token(self, error_string: str, token: tk.Token = None):
        if token is None:
            raise SyntaxError(error_string + ' ' + f'in {self.current_token.start}')
        else:
            raise SyntaxError(error_string + ' ' + f'in {token.start}')

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
            case tk.TokenKind.SIZEOF:
                assert False, "not implemented yet"

        postfix_expression: node.Node = self.peek_postfix_expression()

        return postfix_expression

    def peek_unary_operator(self):
        pass

    def peek_cast_expression(self):
        pass

    def peek_multiplicative_expression(self):
        pass

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

    def peek_type_specifier(self):
        pass

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

    def peek_type_name(self):
        pass

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
