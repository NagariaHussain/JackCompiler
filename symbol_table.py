from typing import NamedTuple
from enum import Enum

class SymbolKind(Enum):
    STATIC = 0
    FEILD = 1
    ARG = 2
    VAR = 3
    NONE = 4


class SymbolTuple(NamedTuple):
    name: str
    type: str
    kind: SymbolKind
    index: int

class SymbolTable:
    def __init__(self) -> None:
        '''creates a new symbol table'''
        pass

    def start_subroutine(self) -> None:
        '''reset subroutine level symbol table'''
        pass

    def define(self, name: str, type: str, kind: SymbolKind) -> None:
        '''creates a new symbol table entry'''
        pass

    def get_var_count(self, kind: SymbolKind) -> int:
        '''returns number of variables of given `kind`'''
        pass

    def get_kind_of(name: str) -> SymbolKind:
        '''returns the kind of the named identifier'''
        pass
    
    def get_type_of(name: str) -> str:
        '''returns the type of the named identifier'''
        pass

    def get_index_of(name: str) -> int:
        '''returns the index assigned to the named identifier'''
        pass

