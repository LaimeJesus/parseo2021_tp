from typing import List, Tuple, Optional

def parseSpecialChar(char: str) -> int:
    charList = list(char)
    character = charList[1]
    if character == "t":
        parsed = 9
    elif character == 'r':
        parsed = 13
    elif character == 'n':
        parsed = 10
    else:
        parsed = ord(character)
    return parsed

def parseString(s: str) -> List:
    resultList = []
    if len(s) == 1:
        resultList = [ord(s)]
    else:
        slashed = False
        stringList = list(s)[1:-1]
        for c in stringList:
            if slashed:
                value = parseSpecialChar(f'\\{c}')
                resultList.append(value)
                slashed = False
            elif c == '\\':
                slashed = True
            else:
                value = ord(c)
                resultList.append(value)
                slashed = False
    return resultList

def isNotEmptyList(expr: List) -> bool:
    return isinstance(expr, list) and len(expr) > 0

def createExprConstructor(exprApplyList: List) -> Tuple[int, Optional[List]]:
    if isNotEmptyList(exprApplyList) and len(exprApplyList) == 3:
        dep, cons = createExprConstructor(exprApplyList[1])
        return 1 + dep, cons
    if exprApplyList[0] == "ExprConstructor":
        return 0, exprApplyList
    return 0, None

def isExprConstructor(exprApplyList: List) -> bool:
    if isNotEmptyList(exprApplyList):
        if exprApplyList[0] == "ExprApply":
            return isExprConstructor(exprApplyList[1])
        elif exprApplyList[0] == "ExprConstructor":
            return True
    return False

def isExprVar(expr: List) -> bool:
    return isNotEmptyList(expr) and expr[0] == "ExprVar"

def isExprDef(expr: List) -> bool:
    return isNotEmptyList(expr) and expr[0] == "Def"
