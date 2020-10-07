# Import enums
from type_enums import TokenType, KeywordType

# Import jack tokenizer
from jack_tokenizer import JackTokenizer

# Supported data type keywords
data_types = {
    KeywordType.INT,
    KeywordType.BOOLEAN,
    KeywordType.CHAR
}

# Supported statement type keywords
statement_types = {
    KeywordType.LET,
    KeywordType.IF,
    KeywordType.WHILE,
    KeywordType.DO,
    KeywordType.RETURN
}

class CompilationEngine:
    '''The brain of the Jack syntax analyzer'''
    # Constructor
    def __init__(self, tokenizer: JackTokenizer, out_path):
        self.tokenizer = tokenizer
        
        # Open the output file for writing
        self.out_stream = out_path.open('w')

        # Read the first token into memory
        self.tokenizer.has_more_tokens()

        # Start analyzing syntax
        if self.tokenizer.get_token_type() == TokenType.KEYWORD:
            if self.tokenizer.get_keyword_type() == KeywordType.CLASS:
                self.compile_class()
        else:
            print(self.tokenizer.get_token_type())
            raise AttributeError("Not starting with a class")
    
    # Helper method to write terminal XML tags
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
            self.compile_subroutine_dec()

        # Class ending curly brackets
        self.eat("}")
        self.write_terminal_tag(TokenType.SYMBOL, "}")

        # At the end of function call
        self.out_stream.write("</class>\n")

    # ('static'|'field') type varName (',' varName)* ';'
    def compile_class_var_dec(self):
        # Write opening tag
        self.out_stream.write("<classVarDec>\n")

        # Write static/field
        self.write_terminal_tag(TokenType.KEYWORD, self.tokenizer.get_cur_ident())

        # Read the next token
        self.tokenizer.has_more_tokens()

        if self.is_valid_type():
            self.write_terminal_tag(self.tokenizer.get_token_type(), self.tokenizer.get_cur_ident())
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
        # Opening tag
        self.out_stream.write("<subroutineDec>\n")
        
        # Write subroutine type
        self.write_terminal_tag(TokenType.KEYWORD, self.tokenizer.get_cur_ident())

        # Move to next token
        self.tokenizer.has_more_tokens()

        if self.is_valid_type() or (self.tokenizer.get_token_type() == TokenType.KEYWORD and self.tokenizer.get_keyword_type() == KeywordType.VOID):
            self.write_terminal_tag(self.tokenizer.get_token_type(), self.tokenizer.get_cur_ident())
        else:
            raise AssertionError("Not a valid subroutine return type!")

         # Move to next token
        self.tokenizer.has_more_tokens()

        if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            self.write_terminal_tag(TokenType.IDENTIFIER, self.tokenizer.get_cur_ident())
        else:
            raise AssertionError("Invalid Syntax for function name!")
        
        # Move to next token
        self.tokenizer.has_more_tokens()

        self.eat('(')
        self.write_terminal_tag(TokenType.SYMBOL, "(")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # If there are some parameters
        self.out_stream.write("<parameterList>\n")
        if not (self.tokenizer.get_token_type() == TokenType.SYMBOL):
            self.compile_parameter_list()
        self.out_stream.write("</parameterList>\n")

        # Move to next token
        self.eat(')')
        self.write_terminal_tag(TokenType.SYMBOL, ")")
        
        # Move to the next token
        self.tokenizer.has_more_tokens()

        self.compile_subroutine_body()

        # Closing tag
        self.out_stream.write("</subroutineDec>\n")

    # ((type varName) (',' type varName)*)?
    def compile_parameter_list(self):
        if self.is_valid_type():
            self.write_terminal_tag(self.tokenizer.get_token_type(), self.tokenizer.get_cur_ident())
        else:
            raise AssertionError("Invalid syntax in parameter list!")
        
        # Move to next token
        self.tokenizer.has_more_tokens()

        if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            self.write_terminal_tag(TokenType.IDENTIFIER, self.tokenizer.get_cur_ident())
        else:
            raise AssertionError("Invalid Syntax for function parameter name name!")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Handle more than one parameters
        while self.tokenizer.get_token_type() == TokenType.SYMBOL and self.tokenizer.get_symbol() == ",":
            self.write_terminal_tag(TokenType.SYMBOL, ",")

            # Read the next token
            self.tokenizer.has_more_tokens()

            # If the current token is a valid type name
            if self.is_valid_type():
                self.write_terminal_tag(self.tokenizer.get_token_type(), self.tokenizer.get_cur_ident())
            else:
                raise AssertionError("Invalid variable type in parameter list")
            
            # Read the next token
            self.tokenizer.has_more_tokens()

            # If current token is a valid identifier
            if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
                self.write_terminal_tag(TokenType.IDENTIFIER, self.tokenizer.get_cur_ident())
            else:
                raise AssertionError("Invalid variable name in parameter list!!")

            # Read the next token
            self.tokenizer.has_more_tokens()
        
    # '{' varDec* statements '}'
    def compile_subroutine_body(self):
        # Write opening tag
        self.out_stream.write("<subroutineBody>\n")

        # Eat opening curly bracket
        self.eat("{")
        self.write_terminal_tag(TokenType.SYMBOL, "{")
        
        # Move to next token
        self.tokenizer.has_more_tokens()

        # Handle variable declarations
        while self.tokenizer.get_token_type() == TokenType.KEYWORD  \
        and self.tokenizer.get_keyword_type() == KeywordType.VAR:
            # Current token is the 'var' keyword
            self.compile_var_dec()

        # Handle statements
        self.compile_statements()

        # Eat closing curly bracker
        self.eat("}")
        self.write_terminal_tag(TokenType.SYMBOL, "}")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Write closing tag
        self.out_stream.write("</subroutineBody>\n")

    # 'var' type varName (',' varName)* ';'
    def compile_var_dec(self):
        # Write opening tag
        self.out_stream.write("<varDec>\n")

        # Write var keyword tag
        self.write_terminal_tag(TokenType.KEYWORD, "var")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Write the type of variables
        if self.is_valid_type():
            self.write_terminal_tag(self.tokenizer.get_token_type(), self.tokenizer.get_cur_ident())
        else:
            raise AssertionError("Not a valid var type!")

        # Move to next token
        self.tokenizer.has_more_tokens()

        if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            self.write_terminal_tag(TokenType.IDENTIFIER, self.tokenizer.get_cur_ident())
        else:
            raise AssertionError("Invalid Syntax for var name!")

        # Move to next token
        self.tokenizer.has_more_tokens()

        while self.tokenizer.get_token_type() == TokenType.SYMBOL and self.tokenizer.get_symbol() == ",":
            # Write this symbol
            self.write_terminal_tag(TokenType.SYMBOL, ",")

            # Move to the next token
            self.tokenizer.has_more_tokens()

            if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
                self.write_terminal_tag(TokenType.IDENTIFIER, self.tokenizer.get_cur_ident())
            else:
                raise AssertionError("Invalid Syntax for var name!")
            
            # Move to the next token
            self.tokenizer.has_more_tokens()

        self.eat(";")
        self.write_terminal_tag(TokenType.SYMBOL, ";")

        # Move to the next token
        self.tokenizer.has_more_tokens()

        # Write closing tag
        self.out_stream.write("</varDec>\n")
    
    # statement*
    def compile_statements(self):
        # Write open tag
        self.out_stream.write("<statements>\n")

        # Process statements
        while self.tokenizer.get_token_type() == TokenType.KEYWORD and self.tokenizer.get_keyword_type() in statement_types:
            # Statment type is based on the starting keyword
            statement_type = self.tokenizer.get_keyword_type()

            # Call compile method based on type
            if statement_type == KeywordType.LET:
                self.compile_let()
            elif statement_type == KeywordType.IF:
                self.compile_if()
            elif statement_type == KeywordType.WHILE:
                self.compile_while_statement()
            elif statement_type == KeywordType.DO:
                self.compile_do()
            elif statement_type == KeywordType.RETURN:
                self.compile_return()
        
        self.out_stream.write("</statements>\n")
    
    # 'let' varName ('[' expression ']')? '=' expression ';'
    def compile_let(self):
        self.out_stream.write("<letStatement>\n")

        self.write_terminal_tag(TokenType.KEYWORD, "let")

        # Move to next token
        self.tokenizer.has_more_tokens()

        if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            self.write_terminal_tag(TokenType.IDENTIFIER, self.tokenizer.get_cur_ident())
        else:
            raise AssertionError("Invalid Syntax for varName!")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Optional bracket syntax
        if self.tokenizer.get_token_type() == TokenType.SYMBOL \
        and self.tokenizer.get_symbol() == "[":
            self.write_terminal_tag(TokenType.SYMBOL, "[")

            # Move to next token
            self.tokenizer.has_more_tokens()
            
            # Compile the expression
            self.compile_expression()

            self.eat("]")
            self.write_terminal_tag(TokenType.SYMBOL, "]")

            # Move to the next token
            self.tokenizer.has_more_tokens()

        # Eat assignment operator
        self.eat("=")
        self.write_terminal_tag(TokenType.SYMBOL, "=")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.compile_expression()

        self.eat(";")
        self.write_terminal_tag(TokenType.SYMBOL, ";")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.out_stream.write("</letStatement>\n")
    
    # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    def compile_if(self):
        self.out_stream.write("<ifStatement>\n")

        self.write_terminal_tag(TokenType.KEYWORD, "if")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.eat("(")
        self.write_terminal_tag(TokenType.SYMBOL, "(")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.compile_expression()

        self.eat(")")
        self.write_terminal_tag(TokenType.SYMBOL, ")")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.eat("{")
        self.write_terminal_tag(TokenType.SYMBOL, "{")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Compile if-block body
        self.compile_statements()

        self.eat("}")
        self.write_terminal_tag(TokenType.SYMBOL, "}")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # If there is an else statement
        # Handle else block
        if self.tokenizer.get_token_type() == TokenType.KEYWORD \
        and self.tokenizer.get_keyword_type() == KeywordType.ELSE:
            self.write_terminal_tag(TokenType.KEYWORD, "else")
            
            # Move to next token
            self.tokenizer.has_more_tokens()

            self.eat("{")
            self.write_terminal_tag(TokenType.SYMBOL, "{")

            # Move to next token
            self.tokenizer.has_more_tokens()

            self.compile_statements()

            self.eat("}")
            self.write_terminal_tag(TokenType.SYMBOL, "}")

            # Move to next token
            self.tokenizer.has_more_tokens()

        # Write closing tag
        self.out_stream.write("</ifStatement>\n")
    
    # 'while' '(' expression ')' '{' statements '}'
    def compile_while_statement(self):
        self.out_stream.write("<whileStatement>\n")

        self.write_terminal_tag(TokenType.KEYWORD, "while")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.eat("(")
        self.write_terminal_tag(TokenType.SYMBOL, "(")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.compile_expression()

        self.eat(")")
        self.write_terminal_tag(TokenType.SYMBOL, ")")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.eat("{")
        self.write_terminal_tag(TokenType.SYMBOL, "{")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Compile if-block body
        self.compile_statements()

        self.eat("}")
        self.write_terminal_tag(TokenType.SYMBOL, "}")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Write closing tag
        self.out_stream.write("</whileStatement>\n")

    # 'do' subroutineCall ';'
    def compile_do(self):
        # Write opening tag
        self.out_stream.write("<doStatement>\n")

        # Write do keyword tag
        self.write_terminal_tag(TokenType.KEYWORD, "do")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Handle subroutineCall
        if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            self.write_terminal_tag(TokenType.IDENTIFIER, self.tokenizer.get_cur_ident())
        else:
            raise AssertionError("Not a valid subroutine/class name!!!")
        
        # Move to next token
        self.tokenizer.has_more_tokens()

        # Is is a method call
        if self.tokenizer.get_token_type() == TokenType.SYMBOL \
            and self.tokenizer.get_symbol() == ".":
            self.write_terminal_tag(TokenType.SYMBOL, ".")

            # Move to next token
            self.tokenizer.has_more_tokens()

            # Handle subroutineCall
            if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
                self.write_terminal_tag(TokenType.IDENTIFIER, self.tokenizer.get_cur_ident())
            else:
                raise AssertionError("Not a valid subroutine/class name!!!")

            # Move to next token
            self.tokenizer.has_more_tokens()

        self.eat("(")
        self.write_terminal_tag(TokenType.SYMBOL, "(")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.out_stream.write("<expressionList>\n")
        if not (self.tokenizer.get_token_type() == TokenType.SYMBOL and self.tokenizer.get_symbol() == ")"):
            self.compile_expression_list()
        self.out_stream.write("</expressionList>\n")

        self.eat(")")
        self.write_terminal_tag(TokenType.SYMBOL, ")")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.eat(";")
        self.write_terminal_tag(TokenType.SYMBOL, ";")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Write closing tag
        self.out_stream.write("</doStatement>\n")
    
    # 'return' expression? ';'
    def compile_return(self):
        # Write opening tag
        self.out_stream.write("<returnStatement>\n")

        # Write do keyword tag
        self.write_terminal_tag(TokenType.KEYWORD, "return")

        # Move to next token
        self.tokenizer.has_more_tokens()

        if self.tokenizer.get_token_type() == TokenType.SYMBOL \
            and self.tokenizer.get_symbol() == ";":
            self.write_terminal_tag(TokenType.SYMBOL, ";")
        else:
            self.compile_expression()
            self.eat(";")
            self.write_terminal_tag(TokenType.SYMBOL, ";")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Write closing tag
        self.out_stream.write("</returnStatement>\n")

    # term (op term)*
    def compile_expression(self):
        self.out_stream.write("<expression>\n")
        self.out_stream.write("<term>\n")
        
        # TODO: Implement expression handle
        self.write_terminal_tag(TokenType.IDENTIFIER, self.tokenizer.get_cur_ident())
        self.tokenizer.has_more_tokens()

        self.out_stream.write("</term>\n")
        self.out_stream.write("</expression>\n")

    
    # integerConstant | stringConstant | keywordConstant | varName | 
    # varName '[' expression ']' | subroutineCall | '(' expression ')' 
    # | unaryOp term
    def compile_term(self):
        pass

    # (expression (',' expression)*)?
    def compile_expression_list(self):
        self.compile_expression()
    
    # eat the given string, else raise error
    def eat(self, string):
        if self.tokenizer.get_token_type() == TokenType.SYMBOL:
            if not (self.tokenizer.get_symbol() == string):
                raise AssertionError(f"Expected symbol {string}, found: {self.tokenizer.get_symbol()}")
        else:
            raise AssertionError("Symbol not found!!")

    # Utility method to check weather 
    # the current token is a valid data type 
    def is_valid_type(self):
        # If built-in data type
        if self.tokenizer.get_token_type() == TokenType.KEYWORD:
            # if int, char, boolean
            if self.tokenizer.get_keyword_type() in data_types:
                return True
        
        # If custom data type
        elif self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            return True

         # Invalid data type        
        return False

