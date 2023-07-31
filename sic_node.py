from __future__ import annotations
import sic_token as tk
import typing


class Identifier:
    def __init__(self, token: tk.Token):
        self.token = token


class StringLiteral:
    def __int__(self, token: tk.Token):
        self.token = token


class ConstantLiteral:
    def __init__(self, token: tk.Token):
        self.token = token


Node = typing.Union[Identifier, StringLiteral, ConstantLiteral]
