
from sys import flags


class Binding:
    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value

    def isRegister(self) -> bool:
        return False

class BindingRegister(Binding):
    def isRegister(self) -> bool:
        return True

class BindingEnclosed(Binding):
    pass

class Env:
    def __init__(self) -> None:
        self.elements = {}
        self.lastReg = 0

    # BRegister(Reg)
    def bindRegister(self, var: str, reg: str) -> str:
        binding = BindingRegister(var, reg)
        self.elements[var] = binding
        return binding

    def unbindRegister(self, var: str) -> None:
        del self.elements[var]

    # BEnclosed(Int)
    def bindEnclosed(self, var: str, n: int) -> int:
        binding = BindingEnclosed(var, n)
        self.elements[var] = binding
        return binding

    def exists(self, name: str) -> bool:
        return name in self.elements

    def get(self, name: str) -> Binding:
        if self.exists(name):
            return self.elements[name]
        raise Exception(f"No existe {name} en entorno")

    def fresh(self):
        self.lastReg += 1
        reg = self.lastReg
        return f"$r{reg}"
