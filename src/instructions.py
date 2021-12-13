class Instruction:
    pass

class MovReg(Instruction):
    def __init__(self, r1, r2) -> None:
        self.reg1 = r1
        self.reg2 = r2

    def __repr__(self) -> str:
        return f"mov_reg({self.reg1}, {self.reg2})"

class MovInt(Instruction):
    def __init__(self, r, n) -> None:
        self.reg = r
        self.value = n

    def __repr__(self) -> str:
        return f"mov_int({self.reg}, {self.value})"

class MovLabel(Instruction):
    def __init__(self, reg, label) -> None:
        self.reg = reg
        self.value = label

    def __repr__(self) -> str:
        return f"mov_label({self.reg}, {self.value})"

class Alloc(Instruction):
    def __init__(self, reg, n) -> None:
        self.reg = reg
        self.slots = n

    def __repr__(self) -> str:
        return f"alloc({self.reg}, {self.slots})"

# r1 := r2[i]
class Load(Instruction):
    def __init__(self, reg1, reg2, index) -> None:
        self.reg1 = reg1
        self.reg2 = reg2
        self.index = index

    def __repr__(self) -> str:
        return f"load({self.reg1}, {self.reg2}, {self.index})"

# r1[i] := r2
class Store(Instruction):
    def __init__(self, reg1, index, reg2) -> None:
        self.reg1 = reg1
        self.index = index
        self.reg2 = reg2

    def __repr__(self) -> str:
        return f"store({self.reg1}, {self.index}, {self.reg2})"

class Print(Instruction):
    def __init__(self, reg) -> None:
        self.reg = reg

    def __repr__(self) -> str:
        return f"print({self.reg})"

class PrintChar(Instruction):
    def __init__(self, reg) -> None:
        self.reg = reg

    def __repr__(self) -> str:
        return f"print_char({self.reg})"

class JumpInstruction(Instruction):
    def __init__(self, reg1 = None, reg2 = None, label = None) -> None:
        self.reg1 = reg1
        self.reg2 = reg2
        self.label = label

class Jump(JumpInstruction):
    def __init__(self, label) -> None:
        super().__init__(label=label)

    def __repr__(self) -> str:
        return f"jump({self.label})"

class JumpEq(JumpInstruction):
    def __repr__(self) -> str:
        return f"jump_eq({self.reg1}, {self.reg2}, {self.label})"

class JumpLt(Instruction):
    def __repr__(self) -> str:
        return f"jump_lt({self.reg1}, {self.reg2}, {self.label})"

class OpInstruction(Instruction):
    def __init__(self, reg1, reg2, reg3, op = None) -> None:
        self.reg1 = reg1
        self.reg2 = reg2
        self.reg3 = reg3
        self.op = op

    def __repr__(self) -> str:
        return f"{self.op}({self.reg1}, {self.reg2}, {self.reg3})"

class Add(OpInstruction):
    def __init__(self, reg1, reg2, reg3) -> None:
        super().__init__(reg1, reg2, reg3, op="add")

class Sub(OpInstruction):
    def __init__(self, reg1, reg2, reg3) -> None:
        super().__init__(reg1, reg2, reg3, op="sub")

class Mul(OpInstruction):
    def __init__(self, reg1, reg2, reg3) -> None:
        super().__init__(reg1, reg2, reg3, op="mul")

class Div(OpInstruction):
    def __init__(self, reg1, reg2, reg3) -> None:
        super().__init__(reg1, reg2, reg3, op="div")

class Mod(OpInstruction):
    def __init__(self, reg1, reg2, reg3) -> None:
        super().__init__(reg1, reg2, reg3, op="mod")

class Call(Instruction):
    def __init__(self, label) -> None:
        self.label = label

    def __repr__(self) -> str:
        return f"call({self.label})"

class ICall(Instruction):
    def __init__(self, reg) -> None:
        self.reg = reg

    def __repr__(self) -> str:
        return f"icall({self.reg})"

class Return(Instruction):
    def __repr__(self) -> str:
        return f"return()"
