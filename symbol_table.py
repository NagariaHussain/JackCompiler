from typing import NamedTuple
from enum import Enum

class SymbolKind(Enum):
    STATIC = 0
    FEILD = 1
    ARG = 2
    VAR = 3
    NONE = 4


class SymbolTuple(NamedTuple):
    type: str
    kind: SymbolKind
    index: int

class SymbolTable:
    def __init__(self) -> None:
        '''creates a new symbol table'''
        self.hash_map = dict()
        self.kind_index = {
            SymbolKind.STATIC: 0,
            SymbolKind.FEILD: 0,
            SymbolKind.ARG: 0,
            SymbolKind.VAR: 0
        }

    def reset_table(self) -> None:
        '''clear symbol table'''
        self.hash_map.clear()
        self.kind_index = {
            SymbolKind.STATIC: 0,
            SymbolKind.FEILD: 0,
            SymbolKind.ARG: 0,
            SymbolKind.VAR: 0
        }

    def define(self, 
        name: str, 
        type: str, 
        kind: SymbolKind) -> None:
        '''creates a new symbol table entry'''
        # Get index for this kind of var
        run_index = self.kind_index[kind]

        # Create new tuple entry
        entry = SymbolTuple(
            type, kind, run_index
        )

        # Insert entry into hash map
        self.hash_map[name] = entry

        # Increment index
        self.kind_index[kind] += 1

    def get_var_count(self, kind: SymbolKind) -> int:
        '''returns number of variables of given `kind`'''
        return (self.kind_index[kind])

    def get_kind_of(self, name: str) -> SymbolKind:
        '''returns the kind of the named identifier'''
        if name in self.hash_map:
            return self.hash_map[name].kind
        return SymbolKind.NONE
    
    def get_type_of(self, name: str) -> str:
        '''returns the type of the named identifier'''
        return self.hash_map[name].type

    def get_index_of(self, name: str) -> int:
        '''returns the index assigned to the named identifier'''
        return self.hash_map[name].index

