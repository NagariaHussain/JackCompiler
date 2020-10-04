from type_enums import TokenType, KeywordType

class CompilationEngine:
    # Constructor
    def __init__(self, tokenizer, out_path):
        self.tokenizer = tokenizer
        self.out_stream = out_path.open('w')
    
    # 'class' className '{' classVarDec* subroutineDec* '}'
    def compile_class(self):
        pass
    
    # ('static'|'field') type varName (',' varName)* ';'
    def compile_class_var_dec(self):
        pass
    
    # ('constructor' | 'function' | 'method') ('void' | 'type') subroutineName
    def compile_subroutine_dec(self):
        pass

    # ((type varName) (',' type varName)*)?
    def compile_parameter_list(self):
        pass
    
    # '{' varDec* statements '}'
    def compile_subroutine_body(self):
        pass

    # 'var' type varName (',' varName)* ';'
    def compile_var_dec(self):
        pass
    
    # statement*
    def compile_statements(self):
        pass
    
    # 'let' varName ('[' expression ']')? '=' expression ';'
    def compile_let(self):
        pass
    
    # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    def compile_if(self):
        pass
    
    # 'while' '(' expression ')' '{' statements '}'
    def compile_while_statement(self):
        pass
    
    # 'do' subroutineCall ';'
    def compile_do(self):
        pass
    
    # 'return' expression? ';'
    def compile_return(self):
        pass

    # term (op term)*
    def compile_expression(self):
        pass
    
    # integerConstant | stringConstant | keywordConstant | varName | 
    # varName '[' expression ']' | subroutineCall | '(' expression ')' 
    # | unaryOp term
    def compile_term(self):
        pass

    # (expression (',' expression)*)?
    def compile_expression_list(self):
        pass
    
    # eat the given string, else raise error
    def eat(self, string):
        pass

