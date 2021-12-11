from sly import Parser

from .lexer import FlechaLexer

from .ast import ExprApply, ExprAtomic, ExprBinOp, ExprCase, ExprCaseBranch, ExprCases, ExprChar, ExprCons, ExprDefinition, ExprEmpty, ExprExpr, ExprIfThen, ExprLambda, ExprLet, ExprNumber, ExprOp, ExprParams, ExprProgram, ExprSequence, ExprString, ExprUnOp, ExprVar

class FlechaParser(Parser):
    # debugfile = 'parser.out'
    tokens = FlechaLexer.tokens
    start = 'programa'

    precedence = (
        ('left', OR),
        ('left', AND),
        ('right', NOT),
        ('left', EQ, NE, GE, LE, GT, LT),
        ('left', ADD, SUB),
        ('left', MUL),
        ('left', DIV, MOD),
        ('right', UMINUS),
    )

    @_('')
    def empty(self, p):
        return ExprEmpty()

    @_('empty')
    def programa(self, p):
        return ExprEmpty()

    @_('programa definicion')
    def programa(self, p):
        return ExprProgram(p.programa, p.definicion)

    @_('DEF LOWERID parametros DEFEQ expresion')
    def definicion(self, p):
        return ExprDefinition(p.LOWERID, p.parametros, p.expresion)

    @_('empty')
    def parametros(self, p):
        return ExprEmpty()

    @_('LOWERID parametros')
    def parametros(self, p):
        return ExprParams(p.LOWERID, p.parametros)

    @_('expresionExterna')
    def expresion(self, p):
        return ExprExpr(p.expresionExterna)

    @_('expresionExterna SEMICOLON expresion')
    def expresion(self, p):
        return ExprSequence(p.expresionExterna, p.expresion)

    @_('expresionIf', 'expresionCase', 'expresionLet', 'expresionLambda', 'expresionInterna')
    def expresionExterna(self, p):
        return ExprExpr(p[0])

    @_('IF expresionInterna THEN expresionExterna ramasElse')
    def expresionIf(self, p):
        return ExprIfThen(p.expresionInterna, p.expresionExterna, p.ramasElse)

    @_('ELIF expresionInterna THEN expresionInterna ramasElse')
    def ramasElse(self, p):
        return ExprIfThen(p.expresionInterna0, p.expresionInterna1, p.ramasElse)

    @_('ELSE expresionInterna')
    def ramasElse(self, p):
        return ExprExpr(p.expresionInterna)

    @_('CASE expresionInterna ramasCase')
    def expresionCase(self, p):
        return ExprCase(p.expresionInterna, p.ramasCase)

    @_('empty')
    def ramasCase(self, p):
        return ExprEmpty()

    @_('ramaCase ramasCase')
    def ramasCase(self, p):
        return ExprCases(p.ramaCase, p.ramasCase)

    @_('PIPE UPPERID parametros ARROW expresionInterna')
    def ramaCase(self, p):
        return ExprCaseBranch(p.UPPERID, p.parametros, p.expresionInterna)

    @_('LET LOWERID parametros DEFEQ expresionInterna IN expresionExterna')
    def expresionLet(self, p):
        return ExprLet(p.LOWERID, p.parametros, p.expresionInterna, p.expresionExterna)

    @_('LAMBDA parametros ARROW expresionExterna')
    def expresionLambda(self, p):
        return ExprLambda(p.parametros, p.expresionExterna)

    @_('expresionAplicacion')
    def expresionInterna(self, p):
        return ExprExpr(p[0])

    @_('expresionInterna ADD expresionInterna')
    @_('expresionInterna SUB expresionInterna')
    @_('expresionInterna MUL expresionInterna')
    @_('expresionInterna DIV expresionInterna')
    @_('expresionInterna MOD expresionInterna')
    @_('expresionInterna OR expresionInterna')
    @_('expresionInterna AND expresionInterna')
    @_('expresionInterna EQ expresionInterna')
    @_('expresionInterna NE expresionInterna')
    @_('expresionInterna GE expresionInterna')
    @_('expresionInterna LE expresionInterna')
    @_('expresionInterna GT expresionInterna')
    @_('expresionInterna LT expresionInterna')
    def expresionInterna(self, p):
        names = list(p._namemap.keys())
        name = names[1]
        return ExprBinOp(p.expresionInterna0, ExprOp(name), p.expresionInterna1)

    @_('SUB expresionInterna %prec UMINUS')
    @_('NOT expresionInterna')
    def expresionInterna(self, p):
        symb = p[0]
        name = "ERR"
        if symb == "-":
            name = "UMINUS"
        elif symb == "!":
            name = "NOT"
        return ExprUnOp(p.expresionInterna, ExprOp(name))

    @_('expresionAtomica')
    def expresionAplicacion(self, p):
        return ExprExpr(p[0])

    @_('expresionAplicacion expresionAtomica')
    def expresionAplicacion(self, p):
        return ExprApply(p.expresionAplicacion, p.expresionAtomica)

    @_('LOWERID')
    def expresionAtomica(self, p):
        return ExprVar(p[0])

    @_('UPPERID')
    def expresionAtomica(self, p):
        return ExprCons(p[0])

    @_('CHAR')
    def expresionAtomica(self, p):
        return ExprChar(p[0])

    @_('STRING')
    def expresionAtomica(self, p):
        return ExprString(p[0])

    @_('NUMBER')
    def expresionAtomica(self, p):
        return ExprNumber(p[0])

    @_('LPAREN expresion RPAREN')
    def expresionAtomica(self, p):
        return ExprAtomic(p[1])
