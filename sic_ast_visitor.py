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

        self.current_function_definition: node.FunctionDefinition | None = None
        self.current_iteration_statement: node.For | node.While | None = None

    def fatal_duplicate_identifiers(self, duplicate_of: node.Identifier, duplicate: node.Identifier) -> None:
        duplicate_of_line_index: int = utils.get_line_index_by_char_index(self.lexer.string, duplicate_of.token.start)
        duplicate_of_line_string: str = utils.get_line_by_index(self.lexer.string, duplicate_of_line_index)

        duplicate_line_index: int = utils.get_line_index_by_char_index(self.lexer.string, duplicate.token.start)
        duplicate_line_string: str = utils.get_line_by_index(self.lexer.string, duplicate_line_index)

        full_error_string = f"SimplerC : Duplicate Identifiers : the identifier {duplicate.token.string} was declared in :\n"
        full_error_string += f"    {duplicate_of_line_string}\n"
        full_error_string += f"SimplerC : Duplicate Identifiers : but is declared again in:\n"
        full_error_string += f"    {duplicate_line_string}\n"
        raise SyntaxError(full_error_string)

    def fatal_undeclared_identifier(self, identifier: node.Identifier) -> None:
        line_index: int = utils.get_line_index_by_char_index(self.lexer.string, identifier.token.start)
        line_string: str = utils.get_line_by_index(self.lexer.string, line_index)

        full_error_string = f"SimplerC : Undeclared Identifier : the identifier {identifier.token.string} was used in :\n"
        full_error_string += f"    {line_string}\n"
        raise SyntaxError(full_error_string)

    def fatal_function_return_type_mismatch(self, function: node.FunctionDefinition, return_type: node.CPrimaryType) -> None:
        line_index: int = utils.get_line_index_by_char_index(self.lexer.string, function.identifier.token.start)
        line_string: str = utils.get_line_by_index(self.lexer.string, line_index)

        full_error_string = f"SimplerC : Function Return Type Mismatch : the function {function.identifier.token.string} was declared with return type {function.type_name} but returns {return_type} in :\n"
        full_error_string += f"    {line_string}\n"
        raise SyntaxError(full_error_string)

    def fatal_continue_outside_of_iteration_statement(self, continue_statement: node.Continue) -> None:
        line_index: int = utils.get_line_index_by_char_index(self.lexer.string, continue_statement.token.start)
        line_string: str = utils.get_line_by_index(self.lexer.string, line_index)

        full_error_string = f"SimplerC : Continue Outside of Iteration Statement : the continue statement was used outside of an iteration statement in :\n"
        full_error_string += f"    {line_string}\n"
        raise SyntaxError(full_error_string)

    def fatal_break_outside_of_iteration_statement(self, break_statement: node.Break) -> None:
        line_index: int = utils.get_line_index_by_char_index(self.lexer.string, break_statement.token.start)
        line_string: str = utils.get_line_by_index(self.lexer.string, line_index)

        full_error_string = f"SimplerC : Break Outside of Iteration Statement : the break statement was used outside of an iteration statement in :\n"
        full_error_string += f"    {line_string}\n"
        raise SyntaxError(full_error_string)

    def fatal_return_type_mismatch(self, return_statement: node.Return) -> None:
        function_line_index: int = utils.get_line_index_by_char_index(self.lexer.string, self.current_function_definition.identifier.token.start)
        function_line_string: str = utils.get_line_by_index(self.lexer.string, function_line_index)

        return_line_index: int = utils.get_line_index_by_char_index(self.lexer.string, return_statement.token.start)
        return_line_string: str = utils.get_line_by_index(self.lexer.string, return_line_index)

        full_error_string = f"SimplerC : Return Type Mismatch : mismatch return type of the function:\n"
        full_error_string += f"    {function_line_string}\n"
        full_error_string += f"SimplerC : Return Type Mismatch : the return:\n"
        full_error_string += f"    {return_line_string}\n"
        raise SyntaxError(full_error_string)

    def look_for_ed_identifier_in_stack(self, identifier: node.Identifier) -> node.ExternalDeclaration | None:
        for external_declaration in self.external_declaration_stack:
            if external_declaration.identifier.token.string == identifier.token.string:
                return external_declaration
        return None

    def look_for_all_ed_identifier_in_stack(self, identifier: node.Identifier) -> list[node.ExternalDeclaration]:
        external_declaration_list: list[node.ExternalDeclaration] = []
        for external_declaration in self.external_declaration_stack:
            if external_declaration.identifier.token.string == identifier.token.string:
                external_declaration_list.append(external_declaration)

        return external_declaration_list

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
            return node.CPrimaryType.INT
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
            if isinstance(external_declaration, node.FunctionDeclaration):
                # make sure that there is only one function declaration with the same identifier
                # (we won't care here about duplicate function definitions)
                # we don't care here about the function parameters, only the function identifier
                identifiers_in_stack: list[node.FunctionDefinition | node.FunctionDeclaration] = self.look_for_all_ed_identifier_in_stack(external_declaration.identifier)

                if len(identifiers_in_stack) != 0:
                    for identifier_in_stack in identifiers_in_stack:
                        if isinstance(identifier_in_stack, node.FunctionDeclaration):
                            self.fatal_duplicate_identifiers(identifier_in_stack.identifier, external_declaration.identifier)

                # add the identifier to the stack
                self.external_declaration_stack.append(external_declaration)

                self.visit_fd(external_declaration)

            elif isinstance(external_declaration, node.FunctionDefinition):
                # make sure that there is only one function definition with the same identifier
                identifiers_in_stack: list[node.FunctionDefinition | node.FunctionDeclaration] = self.look_for_all_ed_identifier_in_stack(external_declaration.identifier)

                if len(identifiers_in_stack) != 0:
                    for identifier_in_stack in identifiers_in_stack:
                        if isinstance(identifier_in_stack, node.FunctionDefinition):
                            self.fatal_duplicate_identifiers(identifier_in_stack.identifier, external_declaration.identifier)

                # add the identifier to the stack
                self.external_declaration_stack.append(external_declaration)

                self.visit_fd(external_declaration)
            else:  # node.Declaration
                self.visit_declaration(external_declaration)

        # pop the stack
        self.pop_stack_by(len(self.translation_unit))

    def visit_fd(self, df: node.FunctionDefinition | node.FunctionDeclaration) -> None:
        if isinstance(df, node.FunctionDeclaration):
            pass
        else:
            self.current_function_definition = df
            # add the parameters to the stack
            for parameter in df.parameters_declaration:
                identifier_in_stack = self.look_for_ed_identifier_in_stack(parameter.identifier)

                if identifier_in_stack is not None:
                    self.fatal_duplicate_identifiers(identifier_in_stack.identifier, parameter.identifier)

                self.external_declaration_stack.append(parameter)

            # visit the function body
            self.visit_compound_statement(df.body)

            # pop the stack
            # we only pop the parameters, the function identifier will be popped in the visit_translation_unit
            self.pop_stack_by(len(df.parameters_declaration))
            self.current_function_definition = None

    def visit_compound_statement(self, compound_statement: node.CompoundStatement) -> None:
        # if check_for_return is true, return the function return type
        # make sure there are no duplicate identifiers in the compound statement
        for declaration in compound_statement.declarations:
            identifier_in_stack = self.look_for_ed_identifier_in_stack(declaration.identifier)

            if identifier_in_stack is not None:
                self.fatal_duplicate_identifiers(identifier_in_stack.identifier, declaration.identifier)

            self.external_declaration_stack.append(declaration)

            self.visit_declaration(declaration)

        for statement in compound_statement.statements:
            self.visit_statement(statement)

        # pop the stack
        self.pop_stack_by(len(compound_statement.declarations))

    def visit_statement(self, statement: node.StatementTypes) -> None:
        if isinstance(statement, node.CompoundStatement):
            self.visit_compound_statement(statement)
        elif isinstance(statement, node.Continue):
            if self.current_iteration_statement is None:
                self.fatal_continue_outside_of_iteration_statement(statement)

            return None
        elif isinstance(statement, node.Break):
            if self.current_iteration_statement is None:
                self.fatal_break_outside_of_iteration_statement(statement)

            return None
        elif isinstance(statement, node.Return):
            if not isinstance(statement.expression, node.NoneNode):
                return_type: node.CPrimaryType = self.visit_expression(statement.expression)

                if return_type != self.current_function_definition.type_name:
                    self.fatal_return_type_mismatch(statement)
        elif isinstance(statement, node.While):
            self.visit_while(statement)
        elif isinstance(statement, node.For):
            self.visit_for(statement)
        elif isinstance(statement, node.If):
            self.visit_if(statement)
        elif isinstance(statement, node.ExpressionTypes):
            self.visit_expression(statement)
        else:
            raise SyntaxError("SimplerC : Internal Error : unknown statement type")

    def visit_while(self, while_statement: node.While) -> None:
        self.current_iteration_statement = while_statement

        self.visit_expression(while_statement.condition)

        self.visit_statement(while_statement.body)

        self.current_iteration_statement = None

    def visit_for(self, for_statement: node.For) -> None:
        self.current_iteration_statement = for_statement

        self.visit_expression(for_statement.init)
        self.visit_expression(for_statement.condition)
        self.visit_expression(for_statement.update)

        self.visit_statement(for_statement.body)

        self.current_iteration_statement = None

    def visit_if(self, if_statement: node.If) -> None:
        self.visit_expression(if_statement.condition)

        self.visit_statement(if_statement.body)

        if not isinstance(if_statement.else_body, node.NoneNode):
            self.visit_statement(if_statement.else_body)

    def visit_declaration(self, declaration: node.Declaration) -> None:
        # we shouldn't check for duplicate identifiers here, because it's the job the compound statement
        """# look if the declaration identifier is already in the stack

        identifier_in_stack = self.look_for_ed_identifier_in_stack(declaration.identifier)

        if identifier_in_stack is not None:
            self.fatal_duplicate_identifiers(identifier_in_stack.identifier, declaration.identifier)

        # add the identifier to the stack
        self.external_declaration_stack.append(declaration)"""

        # visit the declarator initializer
        if not isinstance(declaration.initializer, node.NoneNode):
            initializer_type = self.visit_initializer(declaration.initializer)

            if initializer_type != declaration.type_name:
                raise SyntaxError("SimplerC : Type Error : the initializer type must be the same as the declaration type")

    def visit_initializer(self, initializer: node.ExpressionTypes) -> node.CPrimaryType:
        return self.visit_expression(initializer)

    def visit_expression(self, expression: node.ExpressionTypes) -> node.CPrimaryType:
        """recursive function to visit an expression, return the type of the expression"""
        if isinstance(expression, node.CBinaryOp):
            return self.visit_binary_expression(expression)
        elif isinstance(expression, node.CharLiteral):
            return self.get_expression_type(expression)
        elif isinstance(expression, node.ConstantLiteral):
            return self.get_expression_type(expression)
        elif isinstance(expression, node.Identifier):
            return self.get_expression_type(expression)  # the identifier type is in checked in the get_expression_type function
        elif isinstance(expression, node.CUnaryOp):
            self.visit_unary_expression(expression)
            return self.get_expression_type(expression)  # same as here
        elif isinstance(expression, node.CCast):
            self.visit_expression(expression.expression)
            return self.get_expression_type(expression)  # same as here
        elif isinstance(expression, node.CTernaryOp):
            return self.visit_ternary_expression(expression)
        elif isinstance(expression, node.FunctionCall):
            return self.visit_function_call(expression)
        else:
            raise SyntaxError("SimplerC : Type Error : the node in not an expression")

    def visit_binary_expression(self, binary_expression: node.CBinaryOp) -> node.CPrimaryType:
        # check if both left and right binary_expression are of the same type
        left_type: node.CPrimaryType = self.get_expression_type(binary_expression.left)
        if left_type != self.get_expression_type(binary_expression.right):
            raise SyntaxError("SimplerC : Type Error : the binary operator must have the same type for both expressions")

        # visit the left and the right of the binary_expression
        self.visit_expression(binary_expression.left)
        self.visit_expression(binary_expression.right)

        return left_type

    def visit_unary_expression(self, unary_expression: node.CUnaryOp) -> node.CPrimaryType:
        # visit the unary_expression
        self.visit_expression(unary_expression.expression)

        match unary_expression.kind:
            case node.CUnaryOpKind.PreDecrease | node.CUnaryOpKind.PostDecrease | node.CUnaryOpKind.PreIncrease | node.CUnaryOpKind.PostIncrease:
                if not isinstance(unary_expression.expression, node.Identifier):  # in --/++ the expression must be an identifier
                    raise SyntaxError("SimplerC : Type Error : the expression in the unary operator must be an identifier")

                return self.get_expression_type(unary_expression.expression)
            case _:
                return self.get_expression_type(unary_expression)

    def visit_ternary_expression(self, ternary_expression: node.CTernaryOp) -> node.CPrimaryType:
        # check if both true and false ternary_expression are of the same type
        true_type: node.CPrimaryType = self.get_expression_type(ternary_expression.true_value)
        if true_type != self.get_expression_type(ternary_expression.false_value):
            raise SyntaxError("SimplerC : Type Error : the ternary operator must have the same type for both expressions")

        # visit the true and the false value of the ternary_expression
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
