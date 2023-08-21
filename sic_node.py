from __future__ import annotations
import enum
import sic_token as tk
import typing


class NoneNode:
    def __init__(self):
        pass

    def to_dict(self):
        return {}


class CPrimaryType(enum.Enum):
    VOID = enum.auto()  # 'void'
    CHAR = enum.auto()  # 'char' or 'signed char'
    UCHAR = enum.auto()  # 'unsigned char'
    SHORT = enum.auto()  # 'short' or 'short int' or 'signed short' or 'signed short int'
    USHORT = enum.auto()  # 'unsigned short'
    INT = enum.auto()  # 'int' or 'signed' or 'signed int'
    UINT = enum.auto()  # 'unsigned' or 'unsigned int'
    LONG = enum.auto()  # 'long' or 'long int' or 'signed long' or 'signed long int'
    ULONG = enum.auto()  # 'unsigned long'
    FLOAT = enum.auto()  # 'float'
    DOUBLE = enum.auto()  # 'double'

    def to_dict(self):
        return {
            "node": "CPrimaryType",
            "value": self.name
        }


class CTypeSpecifier(enum.IntFlag):
    VOID = 1 << 0
    CHAR = 1 << 2
    SHORT = 1 << 4
    INT = 1 << 6
    LONG = 1 << 8
    FLOAT = 1 << 10
    DOUBLE = 1 << 12
    SIGNED = 1 << 14
    UNSIGNED = 1 << 16


c_type_specifier_counter_to_c_primary_type: dict[CTypeSpecifier, CPrimaryType] = {
    CTypeSpecifier.VOID: CPrimaryType.VOID,

    CTypeSpecifier.CHAR: CPrimaryType.CHAR,
    CTypeSpecifier.CHAR + CTypeSpecifier.SIGNED: CPrimaryType.CHAR,
    CTypeSpecifier.CHAR + CTypeSpecifier.UNSIGNED: CPrimaryType.UCHAR,

    CTypeSpecifier.SHORT: CPrimaryType.SHORT,
    CTypeSpecifier.SHORT + CTypeSpecifier.INT: CPrimaryType.SHORT,
    CTypeSpecifier.SIGNED + CTypeSpecifier.SHORT: CPrimaryType.SHORT,
    CTypeSpecifier.SHORT + CTypeSpecifier.INT + CTypeSpecifier.SIGNED: CPrimaryType.SHORT,
    CTypeSpecifier.UNSIGNED + CTypeSpecifier.SHORT: CPrimaryType.USHORT,

    CTypeSpecifier.INT: CPrimaryType.INT,
    CTypeSpecifier.SIGNED: CPrimaryType.INT,
    CTypeSpecifier.SIGNED + CTypeSpecifier.INT: CPrimaryType.INT,
    CTypeSpecifier.UNSIGNED: CPrimaryType.UINT,
    CTypeSpecifier.UNSIGNED + CTypeSpecifier.INT: CPrimaryType.UINT,

    CTypeSpecifier.LONG: CPrimaryType.LONG,
    CTypeSpecifier.LONG + CTypeSpecifier.INT: CPrimaryType.LONG,
    CTypeSpecifier.SIGNED + CTypeSpecifier.LONG: CPrimaryType.LONG,
    CTypeSpecifier.SIGNED + CTypeSpecifier.LONG + CTypeSpecifier.INT: CPrimaryType.LONG,
    CTypeSpecifier.UNSIGNED + CTypeSpecifier.LONG: CPrimaryType.ULONG,

    CTypeSpecifier.FLOAT: CPrimaryType.FLOAT,
    CTypeSpecifier.DOUBLE: CPrimaryType.DOUBLE,
}


class Identifier:
    def __init__(self, token: tk.Token):
        self.token = token

    def to_dict(self):
        return {
            "node": "Identifier",
            "name": self.token.string
        }


class CharLiteral:
    def __init__(self, token: tk.Token):
        self.token = token

    def to_dict(self):
        return {
            "node": "CharLiteral",
            "value": self.token.string
        }


class ConstantLiteral:
    def __init__(self, token: tk.Token):
        self.token = token

    def to_dict(self):
        return {
            "node": "ConstantLiteral",
            "value": self.token.string
        }


class CUnaryOp:
    def __init__(self, kind: CUnaryOpKind, expression: Node):
        self.kind = kind
        self.expression = expression

    def to_dict(self):
        return {
            "node": "CUnaryOp",
            "kind": self.kind.to_dict(),
            "expression": self.expression.to_dict()
        }


class CUnaryOpKind(enum.Enum):
    """"""
    # https://www.scaler.com/topics/pre-increment-and-post-increment-in-c/
    # increase/increase then return
    PreIncrease = enum.auto()
    PreDecrease = enum.auto()
    # return then increase/increase
    PostIncrease = enum.auto()
    PostDecrease = enum.auto()
    Plus = enum.auto()  # '+'
    Minus = enum.auto()  # '-'
    BitwiseNOT = enum.auto()  # '~'
    LogicalNOT = enum.auto()  # '!'
    Sizeof = enum.auto()  # 'sizeof'

    def to_dict(self):
        return {
            "node": "CUnaryOpKind",
            "value": self.name
        }


class CCast:
    def __init__(self, type_name: TypeName, expression: Node):
        self.type_name = type_name
        self.expression = expression

    def to_dict(self):
        return {
            "node": "CCast",
            "type_name": self.type_name.to_dict(),
            "expression": self.expression.to_dict()
        }


class CBinaryOpKind(enum.Enum):
    Addition = enum.auto()
    Subtraction = enum.auto()
    Multiplication = enum.auto()
    Division = enum.auto()
    Modulus = enum.auto()
    Assignment = enum.auto()
    EqualTo = enum.auto()
    NotEqualTo = enum.auto()
    GreaterThan = enum.auto()
    LessThan = enum.auto()
    GreaterThanOrEqualTo = enum.auto()
    LessThanOrEqualTo = enum.auto()
    BitwiseAND = enum.auto()
    BitwiseOR = enum.auto()
    BitwiseXOR = enum.auto()
    LeftShift = enum.auto()
    RightShift = enum.auto()
    LogicalAND = enum.auto()
    LogicalOR = enum.auto()
    MultiplicationAssignment = enum.auto()
    DivisionAssignment = enum.auto()
    ModulusAssignment = enum.auto()
    AdditionAssignment = enum.auto()
    SubtractionAssignment = enum.auto()
    LeftShiftAssignment = enum.auto()
    RightShiftAssignment = enum.auto()
    BitwiseAndAssignment = enum.auto()
    BitwiseXorAssignment = enum.auto()
    BitwiseOrAssignment = enum.auto()

    def to_dict(self):
        return {
            "node": "CBinaryOpKind",
            "value": self.name
        }


class CBinaryOp:
    def __init__(self, kind: CBinaryOpKind, left: Node, right: Node):
        self.kind: CBinaryOpKind = kind
        self.left: Node = left
        self.right: Node = right

    def to_dict(self):
        return {
            "node": "CBinaryOp",
            "kind": self.kind.to_dict(),
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


class CTernaryOp:
    def __init__(self, condition: Node, true_value: Node, false_value: Node):
        self.condition: Node = condition
        self.true_value: Node = true_value
        self.false_value: Node = false_value

    def to_dict(self):
        return {
            "node": "CTernaryOp",
            "condition": self.condition.to_dict(),
            "true_value": self.true_value.to_dict(),
            "false_value": self.false_value.to_dict()
        }


class Expression:
    def __init__(self, sub_expression: list[Node]):
        self.expressions = sub_expression

    def to_dict(self):
        return {
            "node": "Expression",
            "expressions": [expression.to_dict() for expression in self.expressions]
        }


class Declaration:
    def __init__(self, type_name: TypeName, declarators: list[Declarator]):
        self.type_name = type_name
        self.declarators = declarators

    def to_dict(self):
        return {
            "node": "Declaration",
            "type_name": self.type_name.to_dict(),
            "declarators": [[declarator[0].to_dict(), declarator[1].to_dict()] for declarator in self.declarators]
        }


class Continue:
    def __init__(self):
        pass

    def to_dict(self):
        return {
            "node": "Continue",
        }


class Break:
    def __init__(self):
        pass

    def to_dict(self):
        return {
            "node": "Break",
        }


class Return:
    def __init__(self, expression: Node):
        self.expression = expression

    def to_dict(self):
        return {
            "node": "Return",
            "expression": self.expression.to_dict()
        }


class While:
    def __init__(self, condition: Node, body: Node):
        self.condition = condition
        self.body = body

    def to_dict(self):
        return {
            "node": "While",
            "condition": self.condition.to_dict(),
            "body": self.body.to_dict()
        }


class For:
    def __init__(self, init: Node, condition: Node, update: Node, body: Node):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

    def to_dict(self):
        return {
            "node": "For",
            "init": self.init.to_dict(),
            "condition": self.condition.to_dict(),
            "update": self.update.to_dict(),
            "body": self.body.to_dict()
        }


class CompoundStatement:
    def __init__(self, declarations: list[Declaration], statements: list[Node]):
        self.declarations = declarations
        self.statements = statements

    def to_dict(self):
        return {
            "node": "CompoundStatement",
            "declarations": [declaration.to_dict() for declaration in self.declarations],
            "statements": [statement.to_dict() for statement in self.statements]
        }


TypeName = CPrimaryType
Node = typing.Union[NoneNode,
                    Identifier,
                    CharLiteral,
                    ConstantLiteral,
                    CUnaryOp, CCast,
                    CBinaryOp,
                    CTernaryOp,
                    Expression,
                    TypeName,
                    Continue,
                    Break,
                    Return,
                    While,
                    For,
                    CompoundStatement]
Declarator = typing.Union[typing.Tuple[Identifier, Node]]
