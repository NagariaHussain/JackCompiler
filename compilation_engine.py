# Import enums
from type_enums import TokenType, KeywordType
from jack_tokenizer import JackTokenizer

data_types = {
    KeywordType.INT,
    KeywordType.BOOLEAN,
    KeywordType.CHAR
}

class CompilationEngine:
    # Constructor
    def __init__(self, tokenizer: JackTokenizer, out_path):
        self.tokenizer = tokenizer
        self.out_stream = out_path.open('w')
        self.tokenizer.has_more_tokens()

        if self.tokenizer.get_token_type() == TokenType.KEYWORD:
            if self.tokenizer.get_keyword_type() == KeywordType.CLASS:
                self.compile_class()
        else:
            raise AttributeError("Not starting with a class")

    def write_terminal_tag(self, t, v):
        if t == TokenType.KEYWORD:
            self.out_stream.write(f"<keyword> {v} </keyword>\n")
        elif t == TokenType.IDENTIFIER:
            self.out_stream.write(f"<identifier> {v} </identifier>\n")
        elif t == TokenType.SYMBOL:
            self.out_stream.write(f"<symbol> {v} </symbol>\n")
        elif t == TokenType.INT_CONST:
            self.out_stream.write(f"<integerConstant> {v} </integerConstant>\n")
        elif t == TokenType.STRING_CONST:
            self.out_stream.write(f"<stringConstant> {v} </stringConstant>\n")


    # 'class' className '{' classVarDec* subroutineDec* '}'
    def compile_class(self):
        # Write opening tag
        self.out_stream.write("<class>\n")
        self.write_terminal_tag(self.tokenizer.get_token_type(), 'class')

        # Read the next token
        self.tokenizer.has_more_tokens()

        if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            self.write_terminal_tag(self.tokenizer.get_token_type(), self.tokenizer.get_cur_ident())
        else:
            raise AttributeError("Not a valid class name!")
            return
        
        # Read the next token
        self.tokenizer.has_more_tokens()

        self.eat('{')
        self.write_terminal_tag(self.tokenizer.get_token_type(), self.tokenizer.get_symbol())

        # Handle class variable declaration (classVarDec*)
        # Proceed to next token
        self.tokenizer.has_more_tokens()

        # While there are field/static declarations
        while (self.tokenizer.get_token_type() == TokenType.KEYWORD) and (self.tokenizer.get_keyword_type() in  (KeywordType.FIELD, KeywordType.STATIC) ):
            self.compile_class_var_dec()

        while (self.tokenizer.get_token_type() == TokenType.KEYWORD) and (self.tokenizer.get_keyword_type() in (KeywordType.CONSTRUCTOR, KeywordType.FUNCTION, KeywordType.METHOD)):
            pass

        # At the end of function call
        self.out_stream.write("</class>\n")

    
    # ('static'|'field') type varName (',' varName)* ';'
    def compile_class_var_dec(self):
        # Write opening tag
        self.out_stream.write("\n\n<classVarDec>\n")

        # Write static/field
        self.write_terminal_tag(TokenType.KEYWORD, self.tokenizer.get_cur_ident())

        # Read the next token
        self.tokenizer.has_more_tokens()

        # If built-in data type
        if self.tokenizer.get_token_type() == TokenType.KEYWORD:
            # if int, char, boolean
            if self.tokenizer.get_keyword_type() in data_types:
                self.write_terminal_tag(self.tokenizer.get_token_type(), self.tokenizer.get_cur_ident())
        
        # If custom data type
        elif self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            self.write_terminal_tag(self.tokenizer.get_token_type(), self.tokenizer.get_cur_ident())
         # Invalid data type
        else:
            raise AssertionError("Invalid class variable type!")
        
        # Move to next token
        self.tokenizer.has_more_tokens()

        if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            self.write_terminal_tag(self.tokenizer.get_token_type(), self.tokenizer.get_cur_ident())
        else:
            raise AssertionError("Invalid class variable name!")

        # Move to the next token
        self.tokenizer.has_more_tokens()

        # If has more than one varibles: E.g. field int x, y, z;
        while self.tokenizer.get_token_type() == TokenType.SYMBOL and self.tokenizer.get_symbol() == ",":
            self.write_terminal_tag(TokenType.SYMBOL, ",")

            # Move to next token
            self.tokenizer.has_more_tokens()

            if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
                self.write_terminal_tag(TokenType.IDENTIFIER, self.tokenizer.get_cur_ident())
            else:
                raise AssertionError("Invalid Syntax for class varible declaration!")

            # Move to next token
            self.tokenizer.has_more_tokens()

        # Must end with ";"
        self.eat(";")
        self.write_terminal_tag(TokenType.SYMBOL, ";")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Write closing tag
        self.out_stream.write("</classVarDec>\n")
    
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
        if self.tokenizer.get_token_type() == TokenType.SYMBOL:
            if not (self.tokenizer.get_symbol() == string):
                raise AssertionError(f"Expected symbol {string}, found: {self.tokenizer.get_symbol()}")
            


