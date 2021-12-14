import json
import traceback

from sys import argv

from .compiler import FlechaCompiler
from .env import Env
from .lexer import FlechaLexer
from .parser import FlechaParser
from .serializer import FlechaSerializer


if __name__ == '__main__':

    '''
    python -m src.main tests_parser/test00.input
    '''

    try:
        if len(argv) < 2:
            raise Exception("Pass a filename as argument")

        inputFile = argv[1]
        with open(inputFile, 'r') as inputContent:
            inputData = inputContent.read()

        lexer = FlechaLexer()
        parser = FlechaParser()
        serializer = FlechaSerializer()
        compiler = FlechaCompiler()
        tokenized = lexer.tokenize(inputData)
        parsed = parser.parse(tokenized)
        ast = parsed.ast()
        serialized = serializer.serializeProgram(ast)
        print(serialized)
        exps = json.loads(serialized)
        env = Env()
        reg = "$main"
        insList = compiler.compile(exps, env, reg)
        for ins in insList:
            print(ins)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
