from sly import Lexer


class FlechaLexer(Lexer):
    tokens = {
        LPAREN,
        RPAREN,

        LOWERID,
        DEF,
        IF,
        THEN,
        ELIF,
        ELSE,
        CASE,
        LET,
        IN,

        DIV,
        MUL,
        ADD,
        SUB,
        MOD,
        NOT,
        # UMINUS,

        OR,
        AND,

        SEMICOLON,
        LAMBDA,
        PIPE,
        ARROW,

        EQ,
        DEFEQ,
        NE,
        GE,
        LE,
        GT,
        LT,

        UPPERID,
        NUMBER,
        CHAR,
        STRING,
    }

    # Ignored pattern
    ignore_whitespaces = '\s'
    ignore_tabs = '\t+'
    ignore_newline = r'\n+'
    ignore_carry = r'\r+'

    # order is important! it was collisioning with MINUS
    ignore_comment = r'--.*'

    # Tokens
    LPAREN = r'\('
    RPAREN = r'\)'

    DIV = r'/'
    MUL = r'\*'
    ADD = r'\+'
    MOD = r'%'
    ARROW = r'->'
    SUB = r'-'
    # UMINUS = r'-'

    NE = r'!='
    NOT = r'!'
    AND = r'&&'
    OR = r'\|\|'

    EQ = r'=='
    DEFEQ = r'='
    SEMICOLON = r';'
    LAMBDA = r'\\'
    PIPE = r'\|'

    GE = r'>='
    LE = r'<='
    GT = r'>'
    LT = r'<'

    LOWERID = r'[a-z][_a-zA-Z0-9]*'
    LOWERID['def'] = DEF
    LOWERID['if'] = IF
    LOWERID['then'] = THEN
    LOWERID['elif'] = ELIF
    LOWERID['else'] = ELSE
    LOWERID['case'] = CASE
    LOWERID['let'] = LET
    LOWERID['in'] = IN
    UPPERID = r'[A-Z][_a-zA-Z0-9]*'
    NUMBER  = '\\d+'
    CHAR    = r'\'(.\'|.|\\.)\''
    STRING = r'\"(?:[^\"\\]|\\.)*\"'

    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

    def tokenize(self, s: str) -> Lexer.tokenize:
        return super().tokenize(s)
