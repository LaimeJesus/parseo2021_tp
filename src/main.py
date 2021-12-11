from sys import argv

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
        tokenized = lexer.tokenize(inputData)
        parsed = parser.parse(tokenized)
        ast = parsed.ast()
        serialized = serializer.serializeProgram(ast)
        print(serialized)
    except Exception as e:
        print(e)
