from typing import List

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
