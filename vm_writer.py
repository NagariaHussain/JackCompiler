from enum import Enum # for creating enum classes

class SegmentType(Enum):
    '''Memory Segment Type Enumeration'''
    CONST   = 0
    ARG     = 1
    LOCAL   = 2
    STATIC  = 3
    THIS    = 4
    THAT    = 5
    POINTER = 6
    TEMP    = 7


class CommandType(Enum):
    ADD = 0
    SUB = 1
    NEG = 2
    EQ  = 3
    GT  = 4
    LT  = 5
    AND = 6
    OR  = 7
    NOT = 8


class VMWriter:
    def __init__(self) -> None:
        '''creates a new ouput vm file'''
        pass

    def write_push(self, segement: SegmentType, index: int) -> None:
        '''writes a VM push command'''
        pass

    def write_pop(self, segment: SegmentType, index: int) -> None:
        '''writes a VM pop command'''
        if segment == SegmentType.CONST:
            raise AssertionError("cannot pop into CONST segment")
    
    def write_arithmetic(self, command: CommandType) -> None:
        '''writes a VM arithmetic-logical command'''
        pass

    def write_label(self, label: str) -> None:
        '''writes a VM `label` command'''
        pass

    def write_goto(self, label: str) -> None:
        '''writes a VM `goto` command'''
        pass

    def write_if(self, label: str) -> None:
        '''writes a VM `if-goto` command'''
        pass

    def write_call(self, name: str, nArgs: int) -> None:
        '''writes a VM `call` command'''
        pass

    def write_function(self, name: str, nLocals: int) -> None:
        '''writes a VM `function` command'''
        pass

    def write_return(self) -> None:
        '''writes a VM `return` command'''
        pass



