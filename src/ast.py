from .util import parseString

class Expr:
    def ast(self):
        raise "abstract method"
    def isEmpty(self):
        return False

class ExprProgram(Expr):
    def __init__(self, program, definition):
        self.program = program
        self.definition = definition
    def ast(self):
        return self.program.ast() + [self.definition.ast()]

class ExprDefinition(Expr):
    def __init__(self, id, params, exp):
        self.id = id
        self.node = ExprLetParams(params, exp)
    def ast(self):
        return ["Def", self.id] + [self.node.ast()]

class ExprParams(Expr):
    def __init__(self, id=None, values=None):
        self.id = id
        self.values = values
    def ast(self):
        res = []
        if self.id:
            res.append(self.id)
        res += self.values.ast()
        return res

class ExprLetParams(Expr):
    def __init__(self, values, exp):
        self.values = values
        self.exp = exp
    def ast(self):
        tail = self.exp.ast()
        for parametro in reversed(self.values.ast()):
            tail = ["ExprLambda", parametro, tail]
        return tail

class ExprSequence(Expr):
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2
    def ast(self):
        return ["ExprLet", "_", self.expr1.ast(), self.expr2.ast()]

class ExprExpr(Expr):
    def __init__(self, expr):
        self.expr = expr
    def ast(self):
        return self.expr.ast()

class ExprIfThen(Expr):
    def __init__(self, condition, ramaThen, ramaElse):
        self.condition = condition
        self.ramaThen = ramaThen
        self.ramaElse = ramaElse
    def ast(self):
        ramaThen = ["CaseBranch", "True", [], self.ramaThen.ast()]
        ramaElse = ["CaseBranch", "False", [], self.ramaElse.ast()]
        return ['ExprCase', self.condition.ast(), [ramaThen, ramaElse]]

class ExprCase(Expr):
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2
    def ast(self):
        return ['ExprCase', self.expr1.ast(), self.expr2.ast()]

class ExprCases(Expr):
    def __init__(self, branchCase = None, branchesCase = None):
        self.branchCase = branchCase
        self.branchesCase = branchesCase
    def ast(self):
        res = []
        if self.branchCase:
            res = [self.branchCase.ast()]
        if self.branchesCase:
            res += self.branchesCase.ast()
        return res

class ExprCaseBranch(Expr):
    def __init__(self, id, params, exp):
        self.id = id
        self.node = ExprParams(values=params)
        self.exp = exp
    def ast(self):
        return ["CaseBranch", self.id] + [self.node.ast()] + [self.exp.ast()]

class ExprLet(Expr):
    def __init__(self, id, params, exp1, exp2):
        self.id = id
        self.node = ExprLetParams(params, exp1)
        self.exp2 = exp2

    def ast(self):
        return ["ExprLet", self.id] + [self.node.ast()] + [self.exp2.ast()]

class ExprLambda(Expr):
    def __init__(self, params, exp):
        self.node = ExprLetParams(params, exp)

    def ast(self):
        return self.node.ast()

class ExprApply(Expr):
    def __init__(self, exp1, exp2=None):
        self.exp1 = exp1
        self.exp2 = exp2
    def ast(self):
        res = ['ExprApply']
        if self.exp1 and not self.exp1.isEmpty():
            res += [self.exp1.ast()]
        if self.exp2 and not self.exp2.isEmpty():
            res += [self.exp2.ast()]
        return res

class ExprOp(Expr):
    def __init__(self, name):
        self.name = name
    def ast(self):
        return ["ExprVar", self.name]

class ExprBinOp(Expr):
    def __init__(self, exp1, op, exp2):
        self.node = ExprApply(ExprApply(op, exp1), exp2)
    def ast(self):
        return self.node.ast()

class ExprUnOp(Expr):
    def __init__(self, exp, op):
        self.node = ExprApply(op, exp)
    def ast(self):
        return self.node.ast()

class ExprVar(Expr):
    def __init__(self, id):
        self.id = id
    def ast(self):
        return ["ExprVar", self.id]

class ExprCons(Expr):
    def __init__(self, id):
        self.id = id
    def ast(self):
        return ["ExprConstructor", self.id]

class ExprChar(Expr):
    def __init__(self, value):
        self.value = value
    def ast(self):
        return ["ExprChar"] + parseString(self.value)

class ExprString(Expr):
    def __init__(self, value):
        self.value = value
    def ast(self):
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
    def __init__(self, value):
        self.value = value
    def ast(self):
        return ["ExprNumber", int(self.value)]

class ExprAtomic(Expr):
    def __init__(self, exp):
        self.exp = exp
    def ast(self):
        return self.exp.ast()

class ExprEmpty(Expr):
    def ast(self):
        return []
    def isEmpty(self):
        return True
