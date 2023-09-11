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


class ASTVisitor:
    def __init__(self, lexer: lexer.Lexer, translation_unit: node.TranslationUnit):
        self.lexer = lexer
        self.translation_unit = translation_unit
        self.identifiers_stack: list[node.FunctionDefinition | node.FunctionDeclaration | node.Declarator] = []  # a stack of identifiers

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

    def look_for_identifier_in_stack(self, identifier: node.Identifier) -> node.FunctionDefinition | node.FunctionDeclaration | node.Declarator | None:
        for identifier_ in self.identifiers_stack:
            if isinstance(identifier_, tuple):  # declarator
                if identifier_[0] == identifier.token.string:
                    return identifier_
            else:  # function definition or declaration
                if identifier_.identifier.token.string == identifier.token.string:
                    return identifier_
        return None

    def pop_stack_by(self, amount: int) -> None:
        for _ in range(amount):
            self.identifiers_stack.pop()

    def visit_translation_unit(self) -> None:
        for external_declaration in self.translation_unit:
            # look if the identifier is already in the stack
            if isinstance(external_declaration, (node.FunctionDefinition, node.FunctionDeclaration)):
                identifier_in_stack = self.look_for_identifier_in_stack(external_declaration.identifier)

                if identifier_in_stack is not None:
                    self.fatal_duplicate_identifiers(identifier_in_stack, external_declaration.identifier)
            else:  # Variable Declaration
                for declarator in external_declaration.declarators:
                    identifier_in_stack = self.look_for_identifier_in_stack(declarator[0])

                    if identifier_in_stack is not None:
                        self.fatal_duplicate_identifiers(identifier_in_stack, declarator[0])

            # add the identifier to the stack
            if isinstance(external_declaration, (node.FunctionDefinition, node.FunctionDeclaration)):
                self.identifiers_stack.append(external_declaration)
            else:  # Variable Declaration
                self.identifiers_stack.extend(external_declaration.declarators)  # add each identifier in the declaration to the stack

            if isinstance(external_declaration, node.FunctionDefinition):
                self.visit_function_definition(external_declaration)
            elif isinstance(external_declaration, node.Declaration):
                self.visit_declaration(external_declaration)

        # pop the stack
        self.pop_stack_by(len(self.translation_unit))
