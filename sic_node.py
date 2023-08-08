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


class CTypeSpecifier(enum.IntEnum):
    VOID = 1 << 0
    CHAR = 1 << 2
    SHORT = 1 << 4
    INT = 1 << 6
    LONG = 1 << 8
    FLOAT = 1 << 10
    DOUBLE = 1 << 12
    SIGNED = 1 << 14
    UNSIGNED = 1 << 16


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


Node = typing.Union[Identifier, StringLiteral, ConstantLiteral]
TypeName = CPrimaryType
