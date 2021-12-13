from typing import List

from .util import parseString

class Expr:
    def ast(self) -> List:
        raise "abstract method"

    def isEmpty(self) -> bool:
        return False

class ExprProgram(Expr):
    def __init__(self, program: Expr, definition: Expr) -> None:
        self.program = program
        self.definition = definition

    def ast(self) -> List:
        return self.program.ast() + [self.definition.ast()]

class ExprDefinition(Expr):
    def __init__(self, id: str, params: Expr, exp: Expr) -> None:
        self.id = id
        self.node = ExprLetParams(params, exp)

    def ast(self) -> List:
        return ["Def", self.id] + [self.node.ast()]

class ExprParams(Expr): 
    def __init__(self, id: str = None, values: Expr = None) -> None:
        self.id = id
        self.values = values

    def ast(self) -> List:
        res = []
        if self.id:
            res.append(self.id)
        res += self.values.ast()
        return res

class ExprLetParams(Expr):
    def __init__(self, values: Expr, exp: Expr) -> None:
        self.values = values
        self.exp = exp

    def ast(self) -> List:
        tail = self.exp.ast()
        for parametro in reversed(self.values.ast()):
            tail = ["ExprLambda", parametro, tail]
        return tail

class ExprSequence(Expr):
    def __init__(self, expr1: Expr, expr2: Expr) -> None:
        self.expr1 = expr1
        self.expr2 = expr2

    def ast(self) -> List:
        return ["ExprLet", "_", self.expr1.ast(), self.expr2.ast()]

class ExprExpr(Expr):
    def __init__(self, expr: Expr) -> None:
        self.expr = expr

    def ast(self) -> List:
        return self.expr.ast()

class ExprIfThen(Expr):
    def __init__(self, condition: Expr, ramaThen: Expr, ramaElse: Expr) -> None:
        self.condition = condition
        self.ramaThen = ramaThen
        self.ramaElse = ramaElse

    def ast(self) -> List:
        ramaThen = ["CaseBranch", "True", [], self.ramaThen.ast()]
        ramaElse = ["CaseBranch", "False", [], self.ramaElse.ast()]
        return ['ExprCase', self.condition.ast(), [ramaThen, ramaElse]]

class ExprCase(Expr):
    def __init__(self, expr1: Expr, expr2: Expr) -> None:
        self.expr1 = expr1
        self.expr2 = expr2

    def ast(self) -> List:
        return ['ExprCase', self.expr1.ast(), self.expr2.ast()]

class ExprCases(Expr):
    def __init__(self, branchCase: Expr = None, branchesCase: Expr = None) -> None:
        self.branchCase = branchCase
        self.branchesCase = branchesCase

    def ast(self) -> List:
        res = []
        if self.branchCase:
            res = [self.branchCase.ast()]
        if self.branchesCase:
            res += self.branchesCase.ast()
        return res

class ExprCaseBranch(Expr):
    def __init__(self, id: str, params: Expr, exp: Expr) -> None:
        self.id = id
        self.node = ExprParams(values=params)
        self.exp = exp

    def ast(self) -> List:
        return ["CaseBranch", self.id] + [self.node.ast()] + [self.exp.ast()]

class ExprLet(Expr):
    def __init__(self, id: str, params: Expr, exp1: Expr, exp2: Expr) -> None:
        self.id = id
        self.node = ExprLetParams(params, exp1)
        self.exp2 = exp2

    def ast(self) -> List:
        return ["ExprLet", self.id] + [self.node.ast()] + [self.exp2.ast()]

class ExprLambda(Expr):
    def __init__(self, params: Expr, exp: Expr) -> None:
        self.node = ExprLetParams(params, exp)

    def ast(self) -> List:
        return self.node.ast()

class ExprApply(Expr):
    def __init__(self, exp1: Expr, exp2: Expr = None) -> None:
        self.exp1 = exp1
        self.exp2 = exp2

    def ast(self) -> List:
        res = ['ExprApply']
        if self.exp1 and not self.exp1.isEmpty():
            res += [self.exp1.ast()]
        if self.exp2 and not self.exp2.isEmpty():
            res += [self.exp2.ast()]
        return res

class ExprOp(Expr):
    def __init__(self, name: str) -> None:
        self.name = name

    def ast(self) -> List:
        return ["ExprVar", self.name]

class ExprBinOp(Expr):
    def __init__(self, exp1: Expr, op: Expr, exp2: Expr) -> None:
        self.node = ExprApply(ExprApply(op, exp1), exp2)

    def ast(self) -> List:
        return self.node.ast()

class ExprUnOp(Expr):
    def __init__(self, exp: Expr, op: Expr) -> None:
        self.node = ExprApply(op, exp)

    def ast(self) -> List:
        return self.node.ast()

class ExprVar(Expr):
    def __init__(self, id: str) -> None:
        self.id = id

    def ast(self) -> List:
        return ["ExprVar", self.id]

class ExprCons(Expr):
    def __init__(self, id: str) -> None:
        self.id = id

    def ast(self) -> List:
        return ["ExprConstructor", self.id]

class ExprChar(Expr):
    def __init__(self, value: str) -> None:
        self.value = value

    def ast(self) -> List:
        return ["ExprChar"] + parseString(self.value)

class ExprString(Expr):
    def __init__(self, value: str) -> None:
        self.value = value

    def ast(self) -> List:
        parsedList = parseString(self.value)
        tail = ['ExprConstructor', 'Nil']
        if len(parsedList) > 0:
            for ordinal in reversed(parsedList):
                newCons = ['ExprConstructor', 'Cons']
                newChar = ['ExprChar', ordinal]
                head = ['ExprApply', newCons, newChar]
                tail = ['ExprApply', head, tail]
        return tail

class ExprNumber(Expr):
    def __init__(self, value: str) -> None:
        self.value = value

    def ast(self) -> List:
        return ["ExprNumber", int(self.value)]

class ExprAtomic(Expr):
    def __init__(self, exp: Expr) -> None:
        self.exp = exp

    def ast(self) -> List:
        return self.exp.ast()

class ExprEmpty(Expr):
    def ast(self) -> List:
        return []

    def isEmpty(self):
        return True
