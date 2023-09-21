"""

the ast visitor job is to check the ast for errors
like:
* duplicate identifiers
* undeclared identifiers
* type errors

"""

import sic_node as node
import sic_utils as utils
import sic_lexer as lexer


# ed - external declaration
# fd - function definition or declaration
class ASTVisitor:
    def __init__(self, lexer: lexer.Lexer, translation_unit: node.TranslationUnit):
        self.lexer = lexer
        self.translation_unit = translation_unit
        self.external_declaration_stack: list[node.ExternalDeclaration] = []  # a stack of external declaration

    def fatal_duplicate_identifiers(self, duplicate_of: node.Identifier, duplicate: node.Identifier) -> None:
        duplicate_of_line_index: int = utils.get_line_index_by_char_index(self.lexer.string, duplicate_of.token.start)
        duplicate_of_line_string: str = utils.get_line_by_index(self.lexer.string, duplicate_of_line_index)

        duplicate_line_index: int = utils.get_line_index_by_char_index(self.lexer.string, duplicate.token.start)
        duplicate_line_string: str = utils.get_line_by_index(self.lexer.string, duplicate_line_index)

        full_error_string = f"SimplerC : Duplicate Identifiers : the identifier {duplicate.token.string} was declared in :\n"
        full_error_string += f"    {duplicate_of_line_string}\n"
        full_error_string = f"SimplerC : Duplicate Identifiers : but is declared again in:\n"
        full_error_string += f"    {duplicate_line_string}\n"
        raise SyntaxError(full_error_string)

    def fatal_undeclared_identifier(self, identifier: node.Identifier) -> None:
        line_index: int = utils.get_line_index_by_char_index(self.lexer.string, identifier.token.start)
        line_string: str = utils.get_line_by_index(self.lexer.string, line_index)

        full_error_string = f"SimplerC : Undeclared Identifier : the identifier {identifier.token.string} was used in :\n"
        full_error_string += f"    {line_string}\n"
        raise SyntaxError(full_error_string)

    def look_for_ed_identifier_in_stack(self, identifier: node.Identifier) -> node.ExternalDeclaration | None:
        for external_declaration in self.external_declaration_stack:
            if external_declaration.identifier == identifier:
                return external_declaration
        return None

    def pop_stack_by(self, amount: int) -> None:
        for _ in range(amount):
            self.external_declaration_stack.pop()

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
            identifier_in_stack: node.Declaration = self.look_for_ed_identifier_in_stack(expression)

            if identifier_in_stack is None:
                self.fatal_undeclared_identifier(expression)

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
            raise SyntaxError("SimplerC : Type Error : the binary operator must have the same type for both expressions")

        return left_type

    def get_unary_expression_type(self, expression: node.CUnaryOp) -> node.CPrimaryType:
        if expression.kind == node.CUnaryOpKind.Sizeof:
            return node.CPrimaryType.UINT
        else:
            return self.get_expression_type(expression.expression)

    def get_ternary_expression_type(self, expression: node.CTernaryOp) -> node.CPrimaryType:
        if self.get_expression_type(expression.true_value) != self.get_expression_type(expression.false_value):
            raise SyntaxError("SimplerC : Type Error : the ternary operator must have the same type for both expressions")

        return self.get_expression_type(expression.true_value)

    def get_function_call_type(self, expression: node.FunctionCall) -> node.CPrimaryType:
        identifier_in_stack: node.FunctionDeclaration | node.FunctionDefinition = self.look_for_ed_identifier_in_stack(expression.identifier)

        if identifier_in_stack is None:
            self.fatal_undeclared_identifier(expression.identifier)

        return identifier_in_stack.type_name

    def visit_translation_unit(self) -> None:
        for external_declaration in self.translation_unit:
            """# look if the external declaration identifiers is already in the stack

            identifier_in_stack = self.look_for_ed_identifier_in_stack(external_declaration.identifier)

            if identifier_in_stack is not None:
                self.fatal_duplicate_identifiers(identifier_in_stack.identifier, external_declaration.identifier)

            # add the identifier to the stack
            self.external_declaration_stack.append(external_declaration)"""

            if isinstance(external_declaration, node.FunctionDefinition):
                self.visit_fd(external_declaration)
            elif isinstance(external_declaration, node.Declaration):
                self.visit_declaration(external_declaration)

        # pop the stack
        self.pop_stack_by(len(self.translation_unit))

    def visit_declaration(self, declaration: node.Declaration) -> None:
        # look if the declaration identifier is already in the stack

        identifier_in_stack = self.look_for_ed_identifier_in_stack(declaration.identifier)

        if identifier_in_stack is not None:
            self.fatal_duplicate_identifiers(identifier_in_stack.identifier, declaration.identifier)

        # add the identifier to the stack
        self.external_declaration_stack.append(declaration)

        # visit the declarator initializer
        if not isinstance(declaration.initializer, node.NoneNode):
            self.visit_initializer(declaration.initializer)

    def visit_initializer(self, initializer: node.Node) -> None:
        self.visit_expression(initializer)

    def visit_expression(self, expression: node.Node) -> None:
        if isinstance(expression, node.CBinaryOp):
            self.visit_binary_expression(expression)
        else:
            assert False, f"Not implemented yet"

    def visit_binary_expression(self, binary_expression: node.Node) -> None:
        # check if both left and right binary_expression are of the same type
        if self.get_expression_type(binary_expression.left) != self.get_expression_type(binary_expression.right):
            raise SyntaxError("SimplerC : Type Error : the binary operator must have the same type for both expressions")

        # visit the left and the right of the binary_expression
        self.visit_expression(binary_expression.left)
        self.visit_expression(binary_expression.right)
