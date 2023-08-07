from __future__ import annotations
import enum
import sic_token as tk
import typing


class CPrimaryType(enum.IntEnum):
    VOID = 1 << 0  # 'void'
    CHAR = 1 << 2  # 'char' or 'signed char'
    UCHAR = 1 << 4  # 'unsigned char'
    SHORT = 1 << 6  # 'short' or 'short int' or 'signed short' or 'signed short int'
    USHORT = 1 << 8  # 'unsigned short'
    INT = 1 << 10  # 'int' or 'signed' or 'signed int'
    UINT = 1 << 12  # 'unsigned' or 'unsigned int'
    LONG = 1 << 14  # 'long' or 'long int' or 'signed long' or 'signed long int'
    ULONG = 1 << 16  # 'unsigned long'
    FLOAT = 1 << 18  # 'float'
    DOUBLE = 1 << 20  # 'double'


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
