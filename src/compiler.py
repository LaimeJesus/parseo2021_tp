import json
import traceback

from sys import argv
from typing import List

from .env import Env
from .instructions import Alloc, ICall, Instruction, Load, MovInt, MovLabel, MovReg, Print, PrintChar, Return, Store
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

    def tag(self, name: str, size: int = 1) -> Tag:
        if name not in self.tags:
            self.lastId += 1
            self.tags[name] = Tag(self.lastId, size)
        tag = self.tags[name]
        return tag

    def compileDef(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        name = exp[1]
        defReg = env.get(name).value()
        r0 = env.fresh()
        expIns = self.compileExpression(exp[2], env, r0)
        return [
            f"{name}:",
            MovLabel(defReg, name)
        ] + expIns + [
            MovReg(defReg, r0),
        ]

    def compileTagCharOrNumber(self, tag: Tag, exp: List, env: Env, reg: str) -> List[Instruction]:
        value = exp[1]
        slots = tag.size
        tmp = env.fresh()
        return [
            Alloc(reg, slots),
            MovInt(tmp, tag.tag),
            Store(reg, 0, tmp), # slot 0 tag
            MovInt(tmp, value),
            Store(reg, 1, tmp), # slot 1 char
        ]

    def compileNumber(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        tag = self.tag("Num")
        return self.compileTagCharOrNumber(tag, exp, env, reg)

    def compileChar(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        tag = self.tag("Char")
        return self.compileTagCharOrNumber(tag, exp, env, reg)

    def compileConstructor(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        value = exp[1]
        r0 = env.fresh()
        tmp = env.fresh()
        tag = self.tag(value)
        slots = tag.size
        return [
            Alloc(r0, slots),
            MovInt(tmp, tag),
            Store(r0, 0, tmp)
        ]

    def compileVar(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        name = exp[1]
        bindingValue = env.get(name)
        r0 = bindingValue.value()
        if bindingValue.isRegister():
            return [
                MovReg(reg, r0)
            ]
        else:
            return []

    def compileCase(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        pass

    def compileLet(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        name = exp[1]
        tmp = env.fresh()
        insE1 = self.compileExpression(exp[2], env, tmp)
        env.bindRegister(name, tmp)
        insE2 = self.compileExpression(exp[3], env, reg)
        return insE1 + insE2

    def compileLambda(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        pass

    # tiene un costructor al final en exp[1]
    def compileApplyCons(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        paramSize, expCons = getExprConstructor(exp)
        regs = []
        for _ in range(paramSize + 1):
            regs += env.fresh()
        name = expCons[1]
        self.tag(name, paramSize)
        constructorIns = self.compileExpression(expCons, env, regs[0])
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
        res = "$r"
        while curr < paramSize:
            instructions += [Store(res, curr, regs[curr])]
            curr += 1
        return instructions

    def compileApply(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        name = exp[0]
        if isExprConstructor(exp[1]):
            ins = self.compileApplyCons(exp, env, reg)
        elif isExprVar(exp[1]):
            r0 = self.env.fresh()
            r1 = self.env.fresh()
            varName = exp[1][1]
            if varName == "unsafePrintChar":
                varIns = [
                    Load(r1, r0, 1),
                    PrintChar(r1),
                ]
            elif varName == "unsafePrintInt":
                varIns = [
                    Load(r1, r0, 1),
                    Print(r1),
                ]
            else:
                varIns = self.compileVar(exp[1], env, r0)
            ins = self.compileExpression(exp[2], env, r0)
            ins += varIns
        else:
            res = "$r"
            reg1 = "$r1"
            reg2 = "$r2"
            reg3 = "$r3"
            insExp1 = self.compileExpression(exp[1], env, reg1)
            insExp2 = self.compileExpression(exp[1], env, reg2)
            ins = insExp1 + insExp2
            ins += [
                Load(reg3, reg1, 1),
                MovReg("@fun", reg1),
                MovReg("@arg", reg2),
                ICall(reg3),
                MovReg(res, "@res")
            ]
        return ins

    def compileCaseBranch(self, exp: List, env: Env, reg: str) -> List[Instruction]:
        pass

    # compileExpresion :: Env -> Expr -> Reg -> [Instruccion]
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
        elif expName == "ExprLet":
            return self.compileLet(exp, env, reg)
        elif expName == "ExprLambda":
            return self.compileLambda(exp, env, reg)
        elif expName == "ExprApply":
            return self.compileApply(exp, env, reg)
        elif expName == "CaseBranch":
            return self.compileCaseBranch(exp, env, reg)

    def registerDefinitions(self, exps: List, env: Env) -> None:
        for exp in exps:
            if isExprDef(exp):
                definition = exp[1]
                reg = f"@_{definition}"
                env.bindRegister(definition, reg)

    # compile :: Env -> [Expr] -> Reg -> [Instruccion]
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

