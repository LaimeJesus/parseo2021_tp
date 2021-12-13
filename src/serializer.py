from typing import List

class FlechaSerializer:
    def spaced(self, ss: str, depth: int) -> str:
        spaces = " " * depth
        return """{spaces}{s}{spaces}""".format(s=ss, spaces=spaces)

    def serializeList(self, ls: List, depth: int) -> str:
        space = " " * depth
        if len(ls) == 0:
            return """{space}[]""".format(space=space)
        ss = """{space}[\n""".format(space=space)
        last = len(ls) - 1
        for idx, d in enumerate(ls):
            s = self.serializeExp(d, depth + 1)
            ss += s
            if idx < last:
              ss += ","
            ss += "\n"
        ss += """{space}]""".format(space=space)
        return ss

    def serializeDef(self, expDef: List, depth: int) -> str:
        spaces = " " * depth
        body = self.serializeExp(expDef[2], depth + 1)
        s = """{spaces}["{expName}", "{name}",\n{body}\n{spaces}]""".format(expName=expDef[0], name=expDef[1], body=body, spaces=spaces)
        return s

    def serializeUnQuoted(self, exp: List, depth: int) -> str:
        spaces = " " * depth
        s = """{spaces}["{expName}", {value}]""".format(expName=exp[0], value=exp[1], spaces=spaces)
        return s

    def serializeQuoted(self, exp: List, depth: int) -> str:
        spaces = " " * depth
        s = """{spaces}["{expName}", "{value}"]""".format(expName=exp[0], value=exp[1], spaces=spaces)
        return s

    def serializeNumber(self, exp: List, depth: int) -> str:
        return self.serializeUnQuoted(exp, depth)

    def serializeChar(self, exp: List, depth: int) -> str:
        return self.serializeUnQuoted(exp, depth)

    def serializeVar(self, exp: List, depth: int) -> str:
        return self.serializeQuoted(exp, depth)

    def serializeConstructor(self, exp: List, depth: int) -> str:
        return self.serializeQuoted(exp, depth)

    def serializeApply(self, exp: List, depth: int) -> str:
        spaces = " " * depth
        sign = self.serializeExp(exp[1], depth + 1)
        body = self.serializeExp(exp[2], depth + 1)
        s = """{spaces}["{expName}",\n{sign},\n{body}\n{spaces}]""".format(expName=exp[0], sign=sign, body=body, spaces=spaces)
        return s

    def serializeExprCase(self, exp: List, depth: int) -> str:
        spaces = " " * depth
        sign = self.serializeExp(exp[1], depth + 1)
        cases = self.serializeList(exp[2], depth + 1)
        s = """{spaces}["{expName}",\n{sign},\n{cases}\n{spaces}]""".format(expName=exp[0], sign=sign, cases=cases, spaces=spaces)
        return s

    def serializeCaseBranch(self, exp: List, depth: int) -> str:
        spaces = " " * depth
        params = str(exp[2]).replace("'", '"')
        body = self.serializeExp(exp[3], depth + 1)
        s = """{spaces}["{expName}", "{name}", {params},\n{body}\n{spaces}]""".format(expName=exp[0], name=exp[1], params=params, body=body, spaces=spaces)
        return s

    def serializeLambda(self, exp: List, depth: int) -> str:
        spaces = " " * depth
        body = self.serializeExp(exp[2], depth + 1)
        s = """{spaces}["{expName}", "{name}",\n{body}\n{spaces}]""".format(expName=exp[0], name=exp[1], body=body, spaces=spaces)
        return s

    def serializeLet(self, exp: List, depth: int) -> str:
        spaces = " " * depth
        sign = self.serializeExp(exp[2], depth + 1)
        body = self.serializeExp(exp[3], depth + 1)
        s = """{spaces}["{expName}", "{name}",\n{sign},\n{body}\n{spaces}]""".format(expName=exp[0], name=exp[1], params=exp[2], sign=sign, body=body, spaces=spaces)
        return s

    def serializeExp(self, exp: List, depth: int) -> str:
        name = exp[0]
        if name == "Def":
            return self.serializeDef(exp, depth)
        elif name == "ExprNumber":
            return self.serializeNumber(exp, depth)
        elif name == "ExprChar":
            return self.serializeChar(exp, depth)
        elif name == "ExprVar":
            return self.serializeVar(exp, depth)
        elif name == "ExprConstructor":
            return self.serializeConstructor(exp, depth)
        elif name == "ExprApply":
            return self.serializeApply(exp, depth)
        elif name == "ExprCase":
            return self.serializeExprCase(exp, depth)
        elif name == "CaseBranch":
            return self.serializeCaseBranch(exp, depth)
        elif name == "ExprLambda":
            return self.serializeLambda(exp, depth)
        elif name == "ExprLet":
            return self.serializeLet(exp, depth)
        return ""

    def serializeProgram(self, ast: List, depth: int = 0) -> str:
        return self.serializeList(ast, depth)
