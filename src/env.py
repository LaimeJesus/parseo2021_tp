
class Binding:
    def value(self) -> str:
        raise Exception("Metodo Abstracto")

class BindingRegister(Binding):
    def __init__(self, var: str, reg: str) -> None:
        self.var = var
        self.reg = reg

    def value(self) -> str:
        return self.reg

class BindingEnclosed(Binding):
    def __init__(self, var: str, n: str) -> None:
        self.var = var
        self.index = n

    def value(self) -> str:
        return str(self.index)

class Env:
    def __init__(self) -> None:
        self.elements = {}
        self.lastReg = 0

    # BRegister(Reg)
    def bindRegister(self, var: str, reg: str) -> str:
        self.elements[var] = BindingRegister(var, reg)
        return reg

    # BEnclosed(Int)
    def bindEnclosed(self, var: str, n: int) -> int:
        self.elements[var] = BindingEnclosed(var, n)
        return n

    def exists(self, name: str) -> bool:
        return name in self.elements

    def get(self, name: str) -> Binding:
        if self.exists(name):
            return self.elements[name]
        raise Exception("No existe {name} en entorno")

    def fresh(self):
        self.lastReg += 1
        reg = self.lastReg
        return f"$r{reg}"
