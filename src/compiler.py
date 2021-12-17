import json
import traceback

from sys import argv
from typing import List, Set

from .env import Binding, Env
from .instructions import Alloc, Comment, ICall, Instruction, Jump, JumpEq, Load, MovInt, MovLabel, MovReg, Print, PrintChar, Return, Store
from .util import isExprConstructor, isExprDef, isExprLambda, isExprVar, getExprConstructor

class Tag:
    def __init__(self, tag: int, size: int = 1) -> None:
        self.tag = tag
        self.size = size

    def __repr__(self) -> str:
        return str(self.tag)

class FlechaCompiler:
    def __init__(self) -> None:
        self.tags = {
            "Num": Tag(1, 2),
            "Char": Tag(2, 2),
            "Closure": Tag(3),
            "True": Tag(4),
            "False": Tag(5),
            "Nil": Tag(6),
            "Cons": Tag(7, 3),
        }
        self.lastId = 7
        self.lastRoutine = 0
        self.lastLabel = 0
        self.lambdas = []

    def freshLabel(self):
        self.lastLabel += 1
        label = self.lastLabel
        return f"{label}"

    def tag(self, name: str, size: int = 1) -> Tag:
        if name not in self.tags:
            self.lastId += 1
            self.tags[name] = Tag(self.lastId, size)
        tag = self.tags[name]
        return tag

    def compileDef(self, exp: List, env: Env, _: str) -> List[Instruction]:
        name = exp[1]
        defReg = env.get(name).value
        r0 = env.fresh()
        base = [
            f"{name}:"
        ]
        # env.bindRegister(name, r0)
        expIns = self.compileExpression(exp[2], env, r0)
        return base + expIns + [MovReg(defReg, r0)]

    def compileTagCharOrNumber(self, tag: Tag, exp: List, env: Env, reg: str) -> List[Instruction]:
        value = exp[1]
        slots = tag.size
        tmp = env.fresh()
        r0 = env.fresh()
        return [
            Alloc(r0, slots),
            MovInt(tmp, tag.tag),
            Store(r0, 0, tmp),
            MovInt(tmp, value),
            Store(r0, 1, tmp),
            MovReg(reg, r0),
        ]

    def compileNumber(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        tag = self.tag("Num")
        return self.compileTagCharOrNumber(tag, exp, env, reg)

    def compileChar(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        tag = self.tag("Char")
        return self.compileTagCharOrNumber(tag, exp, env, reg)

    def compileConstructor(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        value = exp[1]
        tmp = env.fresh()
        r0 = env.fresh()
        t = self.tag(value)
        tag = t.tag
        slots = tag.size
        return [
            Alloc(r0, slots),
            MovInt(tmp, tag),
            Store(r0, 0, tmp),
            MovReg(reg, r0),
        ]

    def compileVar(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        name = exp[1]
        if env.isPrimitive(name):
            r1 = env.fresh()
            ins = [Load(r1, reg, 1)]
            if name == "unsafePrintChar":
                ins += [PrintChar(r1)]
            else:
                ins += [Print(r1)]
            return ins
        else:
            bindingValue = env.get(name)
            ins = []
            if bindingValue.isRegister():
                r0 = bindingValue.value
                ins += [MovReg(reg, r0)]
            else:
                r0 = bindingValue.value
                ins += [Load(reg, "@fun", r0 + 2)]
            return ins

    def compileCase(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        val = env.fresh()
        tagReg = env.fresh()
        test = env.fresh()
        label = self.freshLabel()
        endLabel = f"FIN_CASE_{label}" 

        ins = self.compileExpression(exp[1], env, val)
        ins += [Load(tagReg, val, 0)]
        for id, branch in enumerate(exp[2]):
            branchName = f"RAMA_{str(id)}_{label}"
            ins += [
                MovInt(test, id),
                JumpEq(tagReg, test, branchName),
            ]
        for id, branch in enumerate(exp[2]):
            branchName = f"RAMA_{str(id)}_{label}"
            ins += [f"{branchName}:"]
            ins += self.compileCaseBranch(branch, env, val)
            ins += [Jump(endLabel)]
        ins += [f"{endLabel}:"]
        return ins

    def compileCaseBranch(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        consName = exp[1]
        olds: Binding = []
        regs: str = []
        ins = []
        for id, param in enumerate(exp[2]):
            tmp = env.fresh()
            regs += [tmp]
            if env.exists(param):
                olds += [env.get(param)]
            env.bindRegister(param, tmp)
            ins += [Load(tmp, reg, id)]
        ins += self.compileExpression(exp[3], env, reg)
        for old in olds:
            env.bindRegister(old.name, old.value)
        return ins

    def compileLet(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        name = exp[1]
        tmp = env.fresh()

        insE1 = self.compileExpression(exp[2], env, tmp)
        insE2 = self.compileExpressionWithNewScope(exp[3], env, reg, name, tmp)
        return insE1 + insE2

    def compileRoutine(self, exp: List, env: Env, name: str) -> List:
        fun = env.fresh()
        arg = env.fresh()
        res = env.fresh()
        label = f"rtn_{str(self.lastRoutine)}"
        self.lastRoutine += 1

        oldBinding = None
        if env.exists(name):
            oldBinding = env.get(name)
        env.bindRegister(name, arg)

        freeVars = self.freeVars(exp, env)

        routine = [
            f"{label}:",
            MovReg(fun, "@fun"),
            MovReg(arg, "@arg"),
        ]
        routine += self.compileExpression(exp, env, res)
        routine += [
            MovReg("@res", res),
            Return(),
        ]
        env.unbindRegister(name)
        if oldBinding:
            env.bindRegister(oldBinding.name, oldBinding.value)

        return label, routine, freeVars

    def isFree(self, env: Env, var: str):
        return not env.isGlobal(var) and not env.isPrimitive(var) and not env.exists(var)

    def freeVars(self, exp: List, env: Env) -> List:
        expName = exp[0]
        if expName == "ExprVar":
            var = exp[1]
            if self.isFree(env, var):
                return [var]
            return []
        elif expName in ["ExprConstructor", "ExprNumber", "ExprChar"]:
            return []
        elif expName == "CaseBranch":
            return []
        elif expName == "ExprLet":
            var = exp[1]
            s1 = self.freeVars(exp[2], env)
            s2 = self.freeVars(exp[3], env)
            if self.isFree(env, var):
                s2 = list(filter(lambda a: a != var, s2))
            return s1 + s2
        elif expName == "ExprLambda":
            var = exp[1]
            s1 = self.freeVars(exp[2], env)
            if self.isFree(env, var):
                s1 = list(filter(lambda a: a != var, s1))
            return s1
        elif expName == "ExprApply":
            s1 = self.freeVars(exp[1], env)
            s2 = self.freeVars(exp[2], env)
            return s1 + s2
        elif expName == "Def":
            var = exp[1]
            s1 = self.freeVars(exp[2], env)
            if self.isFree(env, var):
                s1 = list(filter(lambda a: a != var, s1))
            return s1
        return []

    def compileLambda(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        name = exp[1]
        r0 = env.fresh()
        t = env.fresh()

        label, routine, freeVars = self.compileRoutine(exp[2], env, name)
        self.lambdas += routine

        paramSize = len(freeVars)
        ins = [
            Alloc(r0, paramSize + 2),
            MovInt(t, 3),
            Store(r0, 0, t),
            MovLabel(t, label),
            Store(r0, 1, t),
        ]
        for ind, freeVar in enumerate(freeVars):
            freeVarReg = env.get(freeVar).value
            ins += [
                MovReg(t, freeVarReg),
                Store(r0, ind + 2, t),
            ]

        return ins + [
            MovReg(reg, r0),
        ]


    def compileApplyCons(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        paramSize, expCons = getExprConstructor(exp)
        name = expCons[1]
        self.tag(name, paramSize)

        regs = []
        for _ in range(paramSize + 1):
            regs += env.fresh()
        res = regs[0]

        constructorIns = self.compileExpression(expCons, env, res)

        instructions = []
        curr = 1
        currExp = exp
        while curr < paramSize:
            instruction = self.compileExpression(currExp[2], env, regs[curr])
            instructions = instruction + instructions
            currExp = currExp[1]
            curr += 1
        instructions += constructorIns

        curr = 0
        while curr < paramSize:
            instructions += [Store(res, curr, regs[curr])]
            curr += 1

        return instructions

    def compileLambdaCalls(self, exp, env, fun, arg, res):
        tmp = env.fresh()
        calls = [
            Load(tmp, fun, 1),
            MovReg("@fun", fun),
            MovReg("@arg", arg),
            ICall(tmp),
            MovReg(res, "@res"),
        ]
        return calls

    def compileApply(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        if isExprConstructor(exp[1]):
            ins = self.compileApplyCons(exp, env, reg)
        elif isExprVar(exp[1]):
            insExp1 = self.compileVar(exp[1], env, reg)
            insExp2 = self.compileExpression(exp[2], env, reg)
            ins = insExp2 + insExp1
        else:
            fun = env.fresh()
            arg = env.fresh()
            res = env.fresh()
            ins = []
            lambdaIns = self.compileExpression(exp[1], env, fun)
            calls = self.compileLambdaCalls(exp[1], env, fun, arg, res)
            argIns = self.compileExpression(exp[2], env, arg)
            ins = lambdaIns + argIns + calls + [MovReg(reg, res)]
        return ins

    # agrega nueva var a scope guardando la anterior si existiera
    def compileExpressionWithNewScope(self, exp: List, env: Env, reg: str, newName: str, newReg: str) -> List[Instruction]:
        oldBinding = None
        if env.exists(newName):
            oldBinding = env.get(newName)
        env.bindRegister(newName, newReg)

        expBody = self.compileExpression(exp, env, reg)

        env.unbindRegister(newName)
        if oldBinding:
            env.bindRegister(oldBinding.name, oldBinding.value)
        return expBody

    def compileExpression(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        expName = exp[0]
        if expName == "Def":
            return self.compileDef(exp, env, reg)
        elif expName == "ExprVar":
            return self.compileVar(exp, env, reg)
        elif expName == "ExprConstructor":
            return self.compileConstructor(exp, env, reg)
        elif expName == "ExprNumber":
            return self.compileNumber(exp, env, reg)
        elif expName == "ExprChar":
            return self.compileChar(exp, env, reg)
        elif expName == "ExprCase":
            return self.compileCase(exp, env, reg)
        elif expName == "CaseBranch":
            return self.compileCaseBranch(exp, env, reg)
        elif expName == "ExprLet":
            return self.compileLet(exp, env, reg)
        elif expName == "ExprLambda":
            return self.compileLambda(exp, env, reg)
        elif expName == "ExprApply":
            return self.compileApply(exp, env, reg)

    def registerDefinitions(self, exps: List, env: Env) -> None:
        firstDefinition = None
        for exp in exps:
            if isExprDef(exp):
                definition = exp[1]
                reg = f"@G_{definition}"
                env.bindRegister(definition, reg)
                if not firstDefinition:
                    firstDefinition = definition
        return firstDefinition

    def compileExpressions(self, exps: List) -> List[Instruction]:
        instructions = []
        env = Env()
        reg = "$main"
        firstDefinition = self.registerDefinitions(exps, env)
        for exp in exps:
            instructions += self.compileExpression(exp, env, reg)
        header = [Jump(firstDefinition)] + self.lambdas
        return header + instructions

if __name__ == '__main__':

    '''
    python -m src.compiler test_codegen_v2/test_codegen/test01.fl.ast
    '''

    try:
        if len(argv) < 2:
            raise Exception("Pass a filename as argument")

        inputFile = argv[1]
        with open(inputFile, 'r') as inputContent:
            inputData = inputContent.read()

        compiler = FlechaCompiler()
        exps = json.loads(inputData)
        insList = compiler.compileExpressions(exps)
        for ins in insList:
            print(ins)
    except Exception as e:
        print(e)
        print(traceback.format_exc())

