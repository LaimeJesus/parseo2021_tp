
from sys import flags


class Binding:
    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value

    def isRegister(self) -> bool:
        return False

    def __repr__(self) -> str:
        return str(self.value)

class BindingRegister(Binding):
    def isRegister(self) -> bool:
        return True

class BindingEnclosed(Binding):
    def __init__(self, name: str, value: int) -> None:
        self.name = name
        self.value = value

    def isRegister(self) -> bool:
        return False

class Env:
    def __init__(self, elements = {}, globals = []) -> None:
        self.elements = elements
        self.globals = globals
        self.primitives = ['unsafePrintInt', 'unsafePrintChar']
        self.lastReg = 0

    # BRegister(Reg)
    def bindRegister(self, var: str, reg: str) -> str:
        binding = BindingRegister(var, reg)
        self.elements[var] = binding
        if '@' == var[0]:
            self.globals += var[0]
        return binding

    def unbindRegister(self, var: str) -> None:
        del self.elements[var]

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

    def isGlobal(self, var: str) -> bool:
        return var in self.globals

    def isPrimitive(self, var: str) -> bool:
        return var in self.primitives
