from enum import Enum # for creating enum classes 
from pathlib import Path

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

def segment_type_to_string(st: SegmentType) -> str:
    if st == SegmentType.CONST:
        return "constant"
    if st == SegmentType.ARG:
        return "argument"
    if st == SegmentType.LOCAL:
        return "local"
    if st == SegmentType.STATIC:
        return "static"
    if st == SegmentType.THIS:
        return "this"
    if st == SegmentType.THAT:
        return "that"
    if st == SegmentType.POINTER:
        return "pointer"
    if st == SegmentType.TEMP:
        return "temp"

class ArithmeticCType(Enum):
    ADD = 0
    SUB = 1
    NEG = 2
    EQ  = 3
    GT  = 4
    LT  = 5
    AND = 6
    OR  = 7
    NOT = 8
    MULT = 9
    DIV = 10

def arithmetic_ct_to_string(t: ArithmeticCType) -> str:
    if t == ArithmeticCType.ADD:
        return "add"
    if t == ArithmeticCType.SUB:
        return "sub"
    if t == ArithmeticCType.NEG:
        return "neg"
    if t == ArithmeticCType.EQ:
        return "eq"
    if t == ArithmeticCType.GT:
        return "gt"
    if t == ArithmeticCType.LT:
        return "lt"
    if t == ArithmeticCType.AND:
        return "and"
    if t == ArithmeticCType.OR:
        return "or"
    if t == ArithmeticCType.NOT:
        return "not"
    if t == ArithmeticCType.MULT:
        return "call Math.multiply 2"
    if t == ArithmeticCType.DIV:
        return "call Math.divide 2"

class VMWriter:
    def __init__(self, file_path: Path) -> None:
        '''creates a new ouput vm file'''
        self.out_stream = file_path.open("w")

    def write_push(self, segment: SegmentType, index: int) -> None:
        '''writes a VM push command'''
        self.write_command(
            "push",
            segment_type_to_string(segment),
            str(index)
        )
    
    def write_pop(self, segment: SegmentType, index: int) -> None:
        '''writes a VM pop command'''
        if segment == SegmentType.CONST:
            raise AssertionError("cannot pop into CONST segment")
        
        self.write_command(
            "pop",
            segment_type_to_string(segment),
            str(index)
        )
    
    def write_arithmetic(self, command: ArithmeticCType) -> None:
        '''writes a VM arithmetic-logical command'''
        self.write_command(
            arithmetic_ct_to_string(command)
        )

    def write_label(self, label: str) -> None:
        '''writes a VM `label` command'''
        self.write_command("label", label)

    def write_goto(self, label: str) -> None:
        '''writes a VM `goto` command'''
        self.write_command("goto", label)

    def write_if(self, label: str) -> None:
        '''writes a VM `if-goto` command'''
        self.write_command("if-goto", label)

    def write_call(self, name: str, nArgs: int) -> None:
        '''writes a VM `call` command'''
        self.write_command(
            "call",
            name,
            str(nArgs)
        )

    def write_function(self, name: str, nLocals: int) -> None:
        '''writes a VM `function` command'''
        self.write_command(
            "function",
            name,
            str(nLocals)
        )

    def write_return(self) -> None:
        '''writes a VM `return` command'''
        self.write_command("return")
        self.out_stream.write("\n--------------\n")
    
    def write_command(self, *words) -> None:
        '''helper method to write command to vm file'''
        for word in words:
            self.out_stream.write(word + " ")
        # add a newline
        self.out_stream.write("\n")
    
    def write_comment(self, comment: str) -> None:
        '''writes a line comment to the VM file'''
        self.write_command("//", comment)

# TESTING ===========================================
if __name__ == "__main__":    
    # Test writer
    writer = VMWriter(Path("test0.vm"))

    # Test push 
    writer.write_push(SegmentType.CONST, 0)
    writer.write_push(SegmentType.STATIC, 8)
    writer.write_push(SegmentType.LOCAL, 10)

    # Test pop
    writer.write_pop(SegmentType.TEMP, 1)
    writer.write_pop(SegmentType.ARG, 5)

    # Test arithmetic logical commands
    writer.write_arithmetic(ArithmeticCType.NOT)
    writer.write_arithmetic(ArithmeticCType.AND)
    writer.write_arithmetic(ArithmeticCType.OR)
    writer.write_arithmetic(ArithmeticCType.ADD)

    # Test commenting
    writer.write_comment("This are some branching commands")

    # Test branching commands
    writer.write_label("loop2190")
    writer.write_label("loop_another")
    writer.write_if("branch786")
    writer.write_goto("branch789")

    # Test function commands
    writer.write_function("Sys.init", 9)
    writer.write_function("doSomething", 3)
    writer.write_function("malloc", 0)
    writer.write_return()
    writer.write_call("alloc", 1)
    writer.write_call("free", 2)
    writer.write_return()
