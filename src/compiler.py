import json
import traceback

from sys import argv
from typing import List

from .env import Binding, Env
from .instructions import Alloc, ICall, Instruction, Jump, JumpEq, Load, MovInt, MovLabel, MovReg, Print, PrintChar, Return, Store
from .util import isExprConstructor, isExprDef, isExprVar, getExprConstructor

class Tag:
    def __init__(self, tag: int, size: int = 1) -> None:
        self.tag = tag
        self.size = size

    def __repr__(self) -> str:
        return str(self.tag)

class FlechaCompiler:
    def __init__(self) -> None:
        self.env = Env()
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

    def freshLabel(self):
        self.lastLabel += 1
        label = self.lastLabel
        return f"Label_{label}"

    def tag(self, name: str, size: int = 1) -> Tag:
        if name not in self.tags:
            self.lastId += 1
            self.tags[name] = Tag(self.lastId, size)
        tag = self.tags[name]
        return tag

    def compileDef(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        name = exp[1]
        defReg = env.get(name).value
        r0 = env.fresh()
        base = [f"{name}:", MovLabel(defReg, name)]
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
        if name == "unsafePrintChar":
            r1 = self.env.fresh()
            return [
                Load(r1, reg, 1),
                PrintChar(r1),
            ]
        elif name == "unsafePrintInt":
            r1 = self.env.fresh()
            return [
                Load(r1, reg, 1),
                Print(r1),
            ]
        else:
            bindingValue = env.get(name)
            r0 = bindingValue.value
            return [MovReg(reg, r0)]

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
        consName = exp[1] # usar params size
        olds: Binding = []
        regs: str = []
        ins = []
        for id, param in enumerate(exp[2]): # chequear args size
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

    def compileLambda(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        name = exp[1]
        fun = env.fresh()
        arg = env.fresh()
        res = env.fresh()
        r0 = env.fresh()
        t = env.fresh()

        expBody = self.compileExpressionWithNewScope(exp[2], env, res, name, arg)

        label = f"rtn_{str(self.lastRoutine)}"
        self.lastRoutine += 1
        ins = [
            f"{label}:",
            MovReg(fun, "@fun"),
            MovReg(arg, "@arg")
        ]
        # TODO buscar las variables libres del scope y guardarlas como enclosed binding
        paramSize = 5
        ins += [
            Alloc(r0, paramSize + 2),
            MovInt(t, 3),
            Store(r0, 0, t),
            MovLabel(t, label),
            Store(r0, 1, t),
        ]
        ins += expBody
        ins += [
            MovReg("@res", res),
            Return()
        ]
        return ins


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

    def compileApply(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        if isExprConstructor(exp[1]):
            ins = self.compileApplyCons(exp, env, reg)
        elif isExprVar(exp[1]):

            insExp1 = self.compileVar(exp[1], env, reg)
            insExp2 = self.compileExpression(exp[2], env, reg)
            ins = insExp2 + insExp1
        else:
            reg1 = env.fresh()
            reg2 = env.fresh()
            reg3 = env.fresh()
            res = env.fresh()
            ins = []
            ins += self.compileExpression(exp[1], env, reg1)
            ins += self.compileExpression(exp[2], env, reg2)
            ins += [
                Load(reg3, reg1, 1),
                MovReg("@fun", reg1),
                MovReg("@arg", reg2),
                ICall(reg3),
                MovReg(res, "@res")
            ]
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
        for exp in exps:
            if isExprDef(exp):
                definition = exp[1]
                reg = f"@G_{definition}"
                env.bindRegister(definition, reg)

    def compileExpressions(self, exps: List, env: Env, reg: str) -> List[Instruction]:
        instructions = []
        self.registerDefinitions(exps, env)
        for exp in exps:
            res = self.compileExpression(exp, env, reg)
            instructions += res
        return instructions

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
        env = Env()
        reg = "$main"
        exps = json.loads(inputData)
        insList = compiler.compileExpressions(exps, env, reg)
        for ins in insList:
            print(ins)
    except Exception as e:
        print(e)
        print(traceback.format_exc())

