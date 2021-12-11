
def parseParametros(parametros, expresion=None):
    tail = expresion.ast() if expresion is not None else []

    if not parametros or parametros.isEmpty():
        return [tail]
    for parametro in reversed(parametros):
        tail = ["ExprLambda", parametro.ast(), tail]
    return tail

def parseSpecialChar(char):
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

def parseString(s):
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
