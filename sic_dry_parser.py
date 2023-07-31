"""

the dry parser job is to iterate over the tokens steam and convert the steam to an ast format,
any analysis of the ast won't be done here.

"""

import sic_lexer as lx


class DryParser:
    def __init__(self, lexer: lx.Lexer):
        self.lexer = lexer

    def peek_primary_expression(self):
        pass

    def peek_postfix_expression(self):
        pass

    def peek_argument_expression_list(self):
        pass

    def peek_unary_expression(self):
        pass

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
