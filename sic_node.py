from __future__ import annotations
import enum
import sic_token as tk
import typing


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


class StringLiteral:
    def __int__(self, token: tk.Token):
        self.token = token


class ConstantLiteral:
    def __init__(self, token: tk.Token):
        self.token = token


class CUnaryOp:
    def __init__(self, kind: CUnaryOpKind, expression: Node):
        self.kind = kind
        self.expression = expression


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


class CCast:
    def __init__(self, type_name: TypeName, expression: Node):
        self.type_name = type_name
        self.expression = expression


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


class CBinaryOp:
    def __init__(self, kind: CBinaryOpKind, left: Node, right: Node):
        self.kind: CBinaryOpKind = kind
        self.left: Node = left
        self.right: Node = right


class CTernaryOp:
    def __init__(self, condition: Node, true_value: Node, false_value: Node):
        self.condition: Node = condition
        self.true_value: Node = true_value
        self.false_value: Node = false_value


Node = typing.Union[Identifier, StringLiteral, ConstantLiteral, CUnaryOp, CCast, CBinaryOp, CTernaryOp]
TypeName = CPrimaryType
