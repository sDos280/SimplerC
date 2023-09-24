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
            if external_declaration.identifier.token.string == identifier.token.string:
                return external_declaration
        return None

    def look_for_all_ed_identifier_in_stack(self, identifier: node.Identifier) -> list[node.ExternalDeclaration]:
        for external_declaration in self.external_declaration_stack:
            if external_declaration.identifier.token.string == identifier.token.string:
                yield external_declaration

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
            if isinstance(external_declaration, node.FunctionDefinition):
                self.visit_fd(external_declaration)
            elif isinstance(external_declaration, node.Declaration):
                self.visit_declaration(external_declaration)

        # pop the stack
        self.pop_stack_by(len(self.translation_unit))

    def visit_fd(self, df: node.FunctionDefinition | node.FunctionDeclaration) -> None:
        if isinstance(df, node.FunctionDeclaration):
            # make sure that there is only one function declaration with the same identifier
            # (we won't care here about duplicate function definitions)
            # we don't care here about the function parameters, only the function identifier
            identifiers_in_stack: list[node.FunctionDefinition | node.FunctionDeclaration] = self.look_for_all_ed_identifier_in_stack(df.identifier)

            if len(identifiers_in_stack) != 0:
                for identifier_in_stack in identifiers_in_stack:
                    if isinstance(identifier_in_stack, node.FunctionDeclaration):
                        self.fatal_duplicate_identifiers(identifier_in_stack.identifier, df.identifier)

            # add the identifier to the stack
            self.external_declaration_stack.append(df)
        else:
            # make sure that there is only one function definition with the same identifier
            identifiers_in_stack: list[node.FunctionDefinition | node.FunctionDeclaration] = self.look_for_all_ed_identifier_in_stack(df.identifier)

            if len(identifiers_in_stack) != 0:
                for identifier_in_stack in identifiers_in_stack:
                    if isinstance(identifier_in_stack, node.FunctionDefinition):
                        self.fatal_duplicate_identifiers(identifier_in_stack.identifier, df.identifier)

            # add the identifier to the stack
            self.external_declaration_stack.append(df)

            # add the parameters to the stack
            for parameter in df.parameters_declaration:
                identifier_in_stack = self.look_for_ed_identifier_in_stack(parameter.identifier)

                if identifier_in_stack is not None:
                    self.fatal_duplicate_identifiers(identifier_in_stack.identifier, parameter.identifier)

                self.external_declaration_stack.append(parameter)

            # visit the function body
            self.visit_compound_statement(df.body, check_for_return=True)

    def visit_compound_statement(self, compound_statement: node.CompoundStatement, check_for_return: bool = False) -> None:
        # make sure there are no duplicate identifiers in the compound statement
        for declaration in compound_statement.declarations:
            identifier_in_stack = self.look_for_ed_identifier_in_stack(declaration.identifier)

            if identifier_in_stack is not None:
                self.fatal_duplicate_identifiers(identifier_in_stack.identifier, declaration.identifier)

            self.external_declaration_stack.append(declaration)

        is_return_statement_found = False
        # visit the statements
        for statement in compound_statement.statements:
            if isinstance(statement, node.Return):
                is_return_statement_found = True

            self.visit_statement(statement, check_for_return)

        if check_for_return and not is_return_statement_found:
            raise SyntaxError("SimplerC : Type Error : the compound statement must contain return statement")

        # pop the stack
        self.pop_stack_by(len(compound_statement.declarations))

    def visit_declaration(self, declaration: node.Declaration) -> None:
        # look if the declaration identifier is already in the stack

        identifier_in_stack = self.look_for_ed_identifier_in_stack(declaration.identifier)

        if identifier_in_stack is not None:
            self.fatal_duplicate_identifiers(identifier_in_stack.identifier, declaration.identifier)

        # add the identifier to the stack
        self.external_declaration_stack.append(declaration)

        # visit the declarator initializer
        if not isinstance(declaration.initializer, node.NoneNode):
            initializer_type = self.visit_initializer(declaration.initializer)

            if initializer_type != declaration.type_name:
                raise SyntaxError("SimplerC : Type Error : the initializer type must be the same as the declaration type")

    def visit_initializer(self, initializer: node.Node) -> node.CPrimaryType:
        return self.visit_expression(initializer)

    def visit_expression(self, expression: node.Node) -> node.CPrimaryType:
        """recursive function to visit an expression, return the type of the expression"""
        if isinstance(expression, node.CBinaryOp):
            self.visit_binary_expression(expression)
        elif isinstance(expression, node.CharLiteral):
            return self.get_expression_type(expression)
        elif isinstance(expression, node.ConstantLiteral):
            return self.get_expression_type(expression)
        elif isinstance(expression, node.Identifier):
            return self.get_expression_type(expression)  # the identifier type is in checked in the get_expression_type function
        elif isinstance(expression, node.CUnaryOp):
            return self.get_expression_type(expression)  # same as here
        elif isinstance(expression, node.CCast):
            return self.get_expression_type(expression)  # same as here
        elif isinstance(expression, node.CTernaryOp):
            return self.visit_ternary_expression(expression)
        elif isinstance(expression, node.FunctionCall):
            return self.visit_function_call(expression)
        else:
            raise SyntaxError("SimplerC : Type Error : the node in not an expression")

    def visit_binary_expression(self, binary_expression: node.Node) -> node.CPrimaryType:
        # check if both left and right binary_expression are of the same type
        left_type: node.CPrimaryType = self.get_expression_type(binary_expression.left)
        if left_type != self.get_expression_type(binary_expression.right):
            raise SyntaxError("SimplerC : Type Error : the binary operator must have the same type for both expressions")

        # visit the left and the right of the binary_expression
        self.visit_expression(binary_expression.left)
        self.visit_expression(binary_expression.right)

        return left_type

    def visit_ternary_expression(self, ternary_expression: node.Node) -> node.CPrimaryType:
        # check if both true and false ternary_expression are of the same type
        true_type: node.CPrimaryType = self.get_expression_type(ternary_expression.true_value)
        if true_type != self.get_expression_type(ternary_expression.false_value):
            raise SyntaxError("SimplerC : Type Error : the ternary operator must have the same type for both expressions")

        # visit the true and the false of the ternary_expression
        self.visit_expression(ternary_expression.true_value)
        self.visit_expression(ternary_expression.false_value)

        return true_type

    def visit_function_call(self, function_call: node.FunctionCall) -> node.CPrimaryType:
        # look if the function call identifier is already in the stack

        identifier_in_stack: node.FunctionDeclaration | node.FunctionDefinition = self.look_for_ed_identifier_in_stack(function_call.identifier)

        if identifier_in_stack is None:
            self.fatal_undeclared_identifier(function_call.identifier)

        # check if the function call has the same number of arguments as the function definition
        if len(function_call.arguments) != len(identifier_in_stack.parameters_declaration):
            raise SyntaxError("SimplerC : Type Error : the function call must have the same number of arguments as the function definition")

        # visit the arguments
        for index, argument in enumerate(function_call.arguments):
            argument_type = self.visit_expression(argument)

            # check if the argument type is the same as the parameter type
            if argument_type != identifier_in_stack.parameters_declaration[index].type_name:
                raise SyntaxError("SimplerC : Type Error : the function call argument type must be the same as the function definition parameter type")

        return identifier_in_stack.type_name
