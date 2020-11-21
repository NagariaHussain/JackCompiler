# Import enums
from vm_writer import VMWriter
from type_enums import TokenType, KeywordType

# Import jack tokenizer
from jack_tokenizer import JackTokenizer

# Import symbol table 
from symbol_table import SymbolKind, SymbolTable

from vm_writer import VMWriter, SegmentType, ArithmeticCType
from pathlib import Path

# Supported built-in data type keywords
data_types = {
    KeywordType.INT,
    KeywordType.BOOLEAN,
    KeywordType.CHAR
}

# Supported keyword constants
keyword_constants = {
    KeywordType.TRUE,
    KeywordType.FALSE,
    KeywordType.NULL,
    KeywordType.THIS
}

# Supported statement type keywords
statement_types = {
    KeywordType.LET,
    KeywordType.IF,
    KeywordType.WHILE,
    KeywordType.DO,
    KeywordType.RETURN
}

# Supported binary operations
allowed_op = {
    "+": ArithmeticCType.ADD,
    "-": ArithmeticCType.SUB,
    "*": ArithmeticCType.MULT, 
    "/": ArithmeticCType.DIV, 
    "&": ArithmeticCType.AND,
    "&amp;": ArithmeticCType.AND,
    "|": ArithmeticCType.OR,
    "<": ArithmeticCType.LT,
    "&lt;": ArithmeticCType.LT,
    ">": ArithmeticCType.GT,
    "&gt;": ArithmeticCType.GT,
    "=": ArithmeticCType.EQ
}

# Supported unary operations
allowed_unary_op = { 
    "-": ArithmeticCType.NEG, 
    "~": ArithmeticCType.NOT
}

class CompilationEngine:
    '''The brain of the Jack syntax analyzer'''
    # Constructor
    def __init__(self, tokenizer: JackTokenizer, out_path : Path):
        self.tokenizer = tokenizer
        
        # Create symbol tables
        self.class_level_st = SymbolTable()
        self.subroutine_level_st = SymbolTable()

        # class's name
        self.class_name = None

        # Open the output file for writing
        self.out_stream = out_path.open('w')

        # Create a new VM writer for writing
        self.vm_writer = VMWriter(out_path.with_suffix(".vm"))

        # For generating labels
        self.label_count = {
            "if": 0,
            "while": 0
        }
    
    def get_if_labels(self):
        self.label_count["if"] += 1
        return (
            f"LABEL_IF_{self.label_count['if'] - 1}_1", 
            f"LABEL_IF_{self.label_count['if'] - 1}_2"
        )
    
    def get_while_labels(self):
        self.label_count["while"] += 1
        return (
            f"LABEL_WHILE_{self.label_count['while'] - 1}_1", 
            f"LABEL_WHILE_{self.label_count['while'] - 1}_2"
        )

    def start_compilation(self):
        # Read the first token into memory
        self.tokenizer.has_more_tokens()

        # Start analyzing syntax
        if self.tokenizer.get_token_type() == TokenType.KEYWORD:
            if self.tokenizer.get_keyword_type() == KeywordType.CLASS:
                self.compile_class()
        else:
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
            self.class_name = self.tokenizer.get_cur_ident()
            self.write_terminal_tag(
                self.tokenizer.get_token_type(), 
                self.class_name
            )
            self.out_stream.write("\n===DECLARED===\nclass name\n=======")
        else:
            raise AttributeError("Not a valid class name!")
        
        # Read the next token
        self.tokenizer.has_more_tokens()

        self.eat('{')
        self.write_terminal_tag(self.tokenizer.get_token_type(), self.tokenizer.get_symbol())

        # Handle class variable declaration (classVarDec*)
        # Proceed to next token
        self.tokenizer.has_more_tokens()

        # While there are field/static declarations
        while \
        (self.tokenizer.get_token_type() == TokenType.KEYWORD) and\
        (
            self.tokenizer.get_keyword_type() in (KeywordType.FIELD, KeywordType.STATIC) 
        ):
            self.compile_class_var_dec()

        while \
        (self.tokenizer.get_token_type() == TokenType.KEYWORD) and\
        (
            self.tokenizer.get_keyword_type() in (KeywordType.CONSTRUCTOR, KeywordType.FUNCTION, KeywordType.METHOD)
        ):
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
        self.write_terminal_tag(
            TokenType.KEYWORD, 
            self.tokenizer.get_cur_ident())

        # To store variable properties
        var_kind = None
        var_type = None
        var_index = None
        var_name = None

        if self.tokenizer.get_cur_ident() == "static":
            var_kind = SymbolKind.STATIC
        elif self.tokenizer.get_cur_ident() == "field":
            var_kind = SymbolKind.FEILD
        else:
            raise Exception(
                "Other than static or feild:" +  
                self.tokenizer.get_cur_ident()
            )

        # Read the next token
        self.tokenizer.has_more_tokens()

        if self.is_valid_type():
            self.write_terminal_tag(
                self.tokenizer.get_token_type(), 
                self.tokenizer.get_cur_ident())

            var_type = self.tokenizer.get_cur_ident()
        else:
            raise AssertionError("Invalid class variable type!")
        
        # Move to next token
        self.tokenizer.has_more_tokens()

        if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            var_name = self.tokenizer.get_cur_ident()

            # Write varible tag to XML file
            self.write_terminal_tag(
                self.tokenizer.get_token_type(), 
                var_name)

            # Define new class level variable
            self.class_level_st.define(var_name, var_type, var_kind)
            var_index = self.class_level_st.get_index_of(var_name)

            # Write variable properties
            self.out_stream.write(
                f"\n===DECLARED===\nkind: {var_kind}, type: {var_type}, index: {var_index}\n=======")
        else:
            raise AssertionError("Invalid class variable name!")

        # Move to the next token
        self.tokenizer.has_more_tokens()

        # If has more than one varibles: E.g. field int x, y, z;
        while self.tokenizer.get_token_type() == TokenType.SYMBOL \
            and self.tokenizer.get_symbol() == ",":
            self.write_terminal_tag(TokenType.SYMBOL, ",")

            # Move to next token
            self.tokenizer.has_more_tokens()

            if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
                var_name = self.tokenizer.get_cur_ident()

                # Write varible tag to XML file
                self.write_terminal_tag(
                    self.tokenizer.get_token_type(), 
                    var_name)

                # Define new class level variable
                self.class_level_st.define(var_name, var_type, var_kind)
                var_index = self.class_level_st.get_index_of(var_name)

                # Write variable properties
                self.out_stream.write(
                    f"\n===DECLARED===\nkind: {var_kind}, type: {var_type}, index: {var_index}\n=======")
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
        
        # To store function parameters 
        func_params = {}

        # Write subroutine type
        sub_type = self.tokenizer.get_cur_ident()
        self.write_terminal_tag(TokenType.KEYWORD, sub_type)

        # Reset subroutine level symbol table
        self.subroutine_level_st.reset_table()

        # Insert `this`, if method
        if sub_type == "method":
            self.subroutine_level_st.define(
                "this", self.class_name, SymbolKind.ARG
            )

        # Move to next token
        self.tokenizer.has_more_tokens()

        if self.is_valid_type() or \
            (self.tokenizer.get_token_type() == TokenType.KEYWORD \
            and self.tokenizer.get_keyword_type() == KeywordType.VOID):
            self.write_terminal_tag(
                self.tokenizer.get_token_type(), 
                self.tokenizer.get_cur_ident()
            )
        else:
            raise AssertionError("Not a valid subroutine return type!")

         # Move to next token
        self.tokenizer.has_more_tokens()

        if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            func_params["name"] = self.tokenizer.get_cur_ident()
            self.write_terminal_tag(
                TokenType.IDENTIFIER, 
                func_params["name"]
            )

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
        
        func_params["n_lcls"] = self.subroutine_level_st.get_var_count(
                                    SymbolKind.ARG
                                )
        # Write function VM command
        self.vm_writer.write_function(
            f"{self.class_name}.{func_params['name']}",
            func_params["n_lcls"]
        )

        # Move to the next token
        self.tokenizer.has_more_tokens()

        self.compile_subroutine_body()        
        # Closing tag
        self.out_stream.write("</subroutineDec>\n")

    # ((type varName) (',' type varName)*)?
    def compile_parameter_list(self):
        # For storing varible params
        var_name = None
        var_type = None
        var_kind = SymbolKind.ARG  # Argument list
        var_index = None

        if self.is_valid_type():
            var_type = self.tokenizer.get_cur_ident()
            self.write_terminal_tag(
                self.tokenizer.get_token_type(), 
                var_type)
        else:
            raise AssertionError("Invalid syntax in parameter list!")
        
        # Move to next token
        self.tokenizer.has_more_tokens()

        if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            var_name = self.tokenizer.get_cur_ident()
            self.write_terminal_tag(
                TokenType.IDENTIFIER, 
                var_name)
        else:
            raise AssertionError(
                "Invalid Syntax for function parameter name name!")

        # Define the argument variable
        self.subroutine_level_st.define(
            var_name, var_type, var_kind
        )

        # Get the index of the newly created variable
        var_index = self.subroutine_level_st.get_index_of(var_name)

        # Write variable properties
        self.out_stream.write(
            f"\n===DECLARED===\nkind: {var_kind}, type: {var_type}, index: {var_index}\n=======")
        # Move to next token
        self.tokenizer.has_more_tokens()

        # Handle more than one parameters
        while self.tokenizer.get_token_type() == TokenType.SYMBOL \
            and self.tokenizer.get_symbol() == ",":
            self.write_terminal_tag(TokenType.SYMBOL, ",")

            # Read the next token
            self.tokenizer.has_more_tokens()

            # If the current token is a valid type name
            if self.is_valid_type():
                var_type = self.tokenizer.get_cur_ident()
                self.write_terminal_tag(
                    self.tokenizer.get_token_type(), 
                    var_type)
            else:
                raise AssertionError("Invalid variable type in parameter list")
            
            # Read the next token
            self.tokenizer.has_more_tokens()

            # If current token is a valid identifier
            if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
                var_name = self.tokenizer.get_cur_ident()
                self.write_terminal_tag(
                    TokenType.IDENTIFIER, 
                    var_name)
            else:
                raise AssertionError(
                        "Invalid variable name in parameter list!!")

            self.subroutine_level_st.define(
                var_name, var_type, var_kind
            )

            var_index = self.subroutine_level_st.get_index_of(var_name)

             # Write variable properties
            self.out_stream.write(
                f"\n===DECLARED===\nkind: {var_kind}, type: {var_type}, index: {var_index}\n=======")
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

        # For storing variable params
        var_name = None
        var_type = None
        var_kind = SymbolKind.VAR
        var_index = None

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Write the type of variables
        if self.is_valid_type():
            var_type = self.tokenizer.get_cur_ident()
            self.write_terminal_tag(
                self.tokenizer.get_token_type(), 
                var_type)
        else:
            raise AssertionError("Not a valid var type!")

        # Move to next token
        self.tokenizer.has_more_tokens()

        if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            var_name = self.tokenizer.get_cur_ident()
            self.write_terminal_tag(
                TokenType.IDENTIFIER, 
                var_name)
        else:
            raise AssertionError("Invalid Syntax for var name!")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.subroutine_level_st.define(
            var_name, var_type, var_kind
        )

        var_index = self.subroutine_level_st.get_index_of(var_name)

        # Write variable properties
        self.out_stream.write(
            f"\n===DECLARED===\nkind: {var_kind}, type: {var_type}, index: {var_index}\n=======")

        while self.tokenizer.get_token_type() == TokenType.SYMBOL and self.tokenizer.get_symbol() == ",":
            # Write this symbol
            self.write_terminal_tag(TokenType.SYMBOL, ",")

            # Move to the next token
            self.tokenizer.has_more_tokens()

            if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
                var_name = self.tokenizer.get_cur_ident()
                self.write_terminal_tag(
                    TokenType.IDENTIFIER, 
                    var_name)
            else:
                raise AssertionError("Invalid Syntax for var name!")
            
            self.subroutine_level_st.define(var_name, var_type, var_kind)
            var_index = self.subroutine_level_st.get_index_of(var_name)

            # Write variable properties
            self.out_stream.write(
                f"\n===DECLARED===\nkind: {var_kind}, type: {var_type}, index: {var_index}\n=======")

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
            var_name = self.tokenizer.get_cur_ident()
            self.write_terminal_tag(
                TokenType.IDENTIFIER, 
                var_name)
            
            var_props = self.lookup_st(var_name)
            # Write variable properties
            self.out_stream.write(
                f"\n===USED===\nkind: {var_props['kind']}, type: {var_props['type']}, index: {var_props['index']}\n=======")
            
            # Finding segment type
            var_props["seg_type"] = self.var_t_to_segment_t(
                                        var_props["kind"]
                                    )
            
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

        self.vm_writer.write_pop(
                var_props["seg_type"], 
                var_props["index"])

        self.out_stream.write("</letStatement>\n")
    
    # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    def compile_if(self):
        self.out_stream.write("<ifStatement>\n")
        self.vm_writer.write_comment("if statement")

        self.write_terminal_tag(TokenType.KEYWORD, "if")

        # get the next labels
        L1, L2 = self.get_if_labels()

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.eat("(")
        self.write_terminal_tag(TokenType.SYMBOL, "(")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # write code for the expression
        self.compile_expression()

        self.eat(")")
        self.write_terminal_tag(TokenType.SYMBOL, ")")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # not, the condition inside if
        self.vm_writer.write_arithmetic(ArithmeticCType.NOT)

        self.vm_writer.write_if(L1)

        self.eat("{")
        self.write_terminal_tag(TokenType.SYMBOL, "{")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Compile if-block body
        self.compile_statements()

        self.vm_writer.write_goto(L2)

        self.vm_writer.write_label(L1)

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

        self.vm_writer.write_label(L2)

        # Write closing tag
        self.out_stream.write("</ifStatement>\n")
    
    # 'while' '(' expression ')' '{' statements '}'
    def compile_while_statement(self):
        self.out_stream.write("<whileStatement>\n")

        self.write_terminal_tag(TokenType.KEYWORD, "while")
        L1, L2 = self.get_while_labels()

        self.vm_writer.write_label(L1)

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.eat("(")
        self.write_terminal_tag(TokenType.SYMBOL, "(")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.compile_expression()

        self.eat(")")
        self.write_terminal_tag(TokenType.SYMBOL, ")")

        self.vm_writer.write_arithmetic(ArithmeticCType.NOT)
        self.vm_writer.write_if(L2)
        # Move to next token
        self.tokenizer.has_more_tokens()

        self.eat("{")
        self.write_terminal_tag(TokenType.SYMBOL, "{")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Compile block body
        self.compile_statements()

        self.eat("}")
        self.write_terminal_tag(TokenType.SYMBOL, "}")

        # Move to next token
        self.tokenizer.has_more_tokens()
        self.vm_writer.write_goto(L1)
        self.vm_writer.write_label(L2)
        # Write closing tag
        self.out_stream.write("</whileStatement>\n")

    # 'do' subroutineCall ';'
    def compile_do(self):
        # To store first and second parts of subroutine call
        first_part, second_part = None, None
        # To store nArgs passed to the subroutine
        nArgs = 0

        # Write opening tag
        self.out_stream.write("<doStatement>\n")

        # Write do keyword tag
        self.write_terminal_tag(TokenType.KEYWORD, "do")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Handle subroutineCall
        if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            first_part = self.tokenizer.get_cur_ident()
            self.write_terminal_tag(
                TokenType.IDENTIFIER, 
                first_part
            )
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
                second_part = self.tokenizer.get_cur_ident()
                self.write_terminal_tag(
                    TokenType.IDENTIFIER, 
                    second_part
                )
            else:
                raise AssertionError(
                    "Not a valid subroutine/class name!!!"
                )

            # Move to next token
            self.tokenizer.has_more_tokens()

        self.eat("(")
        self.write_terminal_tag(TokenType.SYMBOL, "(")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.out_stream.write("<expressionList>\n")
        if not (self.tokenizer.get_token_type() == TokenType.SYMBOL \
            and self.tokenizer.get_symbol() == ")"):
            nArgs = self.compile_expression_list()
        self.out_stream.write("</expressionList>\n")

        self.eat(")")
        self.write_terminal_tag(TokenType.SYMBOL, ")")

        # Move to next token
        self.tokenizer.has_more_tokens()

        self.eat(";")
        self.write_terminal_tag(TokenType.SYMBOL, ";")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Write method call
        if second_part:
            # Of some other class
            self.vm_writer.write_call(
                f"{first_part}.{second_part}",
                nArgs
            )
        else:
            # Of this class
            self.vm_writer.write_call(
                f"{self.class_name}.{first_part}",
                nArgs
            )
        
        # call-and-return contract
        self.vm_writer.write_pop(SegmentType.TEMP, 0)
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
            # the subroutine void return type
            self.vm_writer.write_push(SegmentType.CONST, 0)
        else:
            self.compile_expression()
            self.eat(";")
            self.write_terminal_tag(TokenType.SYMBOL, ";")

        # Move to next token
        self.tokenizer.has_more_tokens()

        # Write return command
        self.vm_writer.write_return()
        # Write closing tag
        self.out_stream.write("</returnStatement>\n")

    # term (op term)*
    def compile_expression(self):
        self.out_stream.write("<expression>\n")

        # Compile term
        self.compile_term()

        # Handle (op term)*
        while self.tokenizer.get_token_type() == TokenType.SYMBOL \
            and self.tokenizer.get_symbol() in allowed_op:
            symbol = self.tokenizer.get_symbol()
            # Write tag for operation symbol
            self.write_terminal_tag(
                TokenType.SYMBOL, 
                self.tokenizer.get_symbol())

            # Move to next token 
            self.tokenizer.has_more_tokens()

            # Compile term
            self.compile_term()

            # Apply operation
            self.vm_writer.write_arithmetic(
                allowed_op[symbol]
            )
        
        # Write closing tag
        self.out_stream.write("</expression>\n")

    # integerConstant | stringConstant | keywordConstant | varName | 
    # varName '[' expression ']' | subroutineCall | '(' expression ')' 
    # | unaryOp term
    def compile_term(self):
        self.out_stream.write("<term>\n")
        
        if self.tokenizer.get_token_type() == TokenType.INT_CONST:
            self.write_terminal_tag(
                TokenType.INT_CONST, 
                self.tokenizer.get_int_val()
            )
            self.vm_writer.write_push(
                SegmentType.CONST, 
                self.tokenizer.get_int_val()
            )
            self.tokenizer.has_more_tokens()
        
        elif self.tokenizer.get_token_type() == TokenType.STRING_CONST:
            self.write_terminal_tag(
                TokenType.STRING_CONST, 
                self.tokenizer.get_string_val()
            )
            self.tokenizer.has_more_tokens()
        
        elif self.tokenizer.get_token_type() == TokenType.KEYWORD \
            and self.tokenizer.get_keyword_type() in keyword_constants:
            # keyword constant
            kc = self.tokenizer.get_cur_ident()
            self.write_terminal_tag(
                TokenType.KEYWORD, 
                kc
            )

            if kc == "null" or kc == "false":
                # push const 0
                self.vm_writer.write_push(SegmentType.CONST, 0)
            
            elif kc == "true":
                # push const -1
                self.vm_writer.write_push(SegmentType.CONST, 1)
                self.vm_writer.write_arithmetic(ArithmeticCType.NEG)

            self.tokenizer.has_more_tokens()
        
        elif self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
            first_part, second_part = None, None
            nArgs = 0
            var_name = self.tokenizer.get_cur_ident()
            first_part = var_name
            var_props = self.lookup_st(var_name)

            self.write_terminal_tag(
                TokenType.IDENTIFIER, 
                var_name)

            # Move to next token
            self.tokenizer.has_more_tokens()

            if self.tokenizer.get_token_type() == TokenType.SYMBOL:
                # Handle varName '[' expression ']'
                if self.tokenizer.get_symbol() == "[":
                    self.eat("[")
                    self.write_terminal_tag(TokenType.SYMBOL, "[")
                    self.tokenizer.has_more_tokens()

                    self.compile_expression()

                    self.eat(']')
                    self.write_terminal_tag(TokenType.SYMBOL, "]")

                    # Move to next token
                    self.tokenizer.has_more_tokens()

                # Handle subroutineCall
                elif self.tokenizer.get_symbol() == "(" \
                    or self.tokenizer.get_symbol() == ".":
                    # Is a method call
                    if self.tokenizer.get_symbol() == ".":
                        self.write_terminal_tag(TokenType.SYMBOL, ".")
                        # Move to next token
                        self.tokenizer.has_more_tokens()

                        # Handle subroutineCall
                        if self.tokenizer.get_token_type() == TokenType.IDENTIFIER:
                            second_part = self.tokenizer.get_cur_ident()
                            self.write_terminal_tag(
                                TokenType.IDENTIFIER, 
                                second_part
                            )
                        else:
                            raise AssertionError(
                                "Not a valid subroutine/class name!!!"
                            )
                        
                        # Move to next token
                        self.tokenizer.has_more_tokens()
                    
                    self.eat("(")
                    self.write_terminal_tag(TokenType.SYMBOL, "(")

                    # Move to next token
                    self.tokenizer.has_more_tokens()
                    self.out_stream.write("<expressionList>\n")
                    if not (self.tokenizer.get_token_type() == TokenType.SYMBOL \
                        and self.tokenizer.get_symbol() == ")"):
                        nArgs = self.compile_expression_list()
                    self.out_stream.write("</expressionList>\n")

                    self.eat(")")
                    self.write_terminal_tag(TokenType.SYMBOL, ")")

                    # Move to next token
                    self.tokenizer.has_more_tokens()

            if var_props:
                # Write variable properties
                self.out_stream.write(
                    f"\n===USED===\nkind: {var_props['kind']}, type: {var_props['type']}, index: {var_props['index']}\n=======")

                self.vm_writer.write_push(
                    self.var_t_to_segment_t(var_props['kind']),
                    var_props['index']
                ) 
            else:
                if second_part:
                    # Of some other class
                    self.vm_writer.write_call(
                    f"{first_part}.{second_part}",
                    nArgs
                    )
                else:
                    # Of this class
                    self.vm_writer.write_call(
                    f"{self.class_name}.{first_part}",
                    nArgs
                    )  
        
        elif self.tokenizer.get_token_type() == TokenType.SYMBOL:
            # Handle '(' expression ')'
            if self.tokenizer.get_symbol() == '(':
                self.eat("(")
                self.write_terminal_tag(TokenType.SYMBOL, "(")
                self.tokenizer.has_more_tokens()

                self.compile_expression()

                self.eat(")")
                self.write_terminal_tag(TokenType.SYMBOL, ")")
                self.tokenizer.has_more_tokens()
            # Handle unaryOp term
            elif self.tokenizer.get_symbol() in allowed_unary_op:
                unary_op = self.tokenizer.get_symbol()
                self.write_terminal_tag(
                    TokenType.SYMBOL, 
                    self.tokenizer.get_symbol()
                )

                self.tokenizer.has_more_tokens()
                self.compile_term()

                self.vm_writer.write_arithmetic(
                    allowed_unary_op[unary_op]
                )

            else:
                raise AssertionError("( or unary Op expected!!")

        self.out_stream.write("</term>\n")

    # expression (',' expression)*
    def compile_expression_list(self):
        self.compile_expression()
        arg_count = 1

        while (self.tokenizer.get_token_type() == TokenType.SYMBOL) \
            and (self.tokenizer.get_symbol() == ","):
            self.write_terminal_tag(TokenType.SYMBOL, ",")
            self.tokenizer.has_more_tokens()
            self.compile_expression()
            arg_count += 1

        return arg_count

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

    # Lookup variable in symbol table
    def lookup_st(self, v_name):
        '''return variable properties'''
        # FOR DEBUGGING
        from pprint import pprint
        pprint(self.subroutine_level_st.hash_map)
        pprint(self.class_level_st.hash_map)

        # To store looked up props
        v_props = {}

        # lookup subroutine level table
        v_kind = self.subroutine_level_st.get_kind_of(v_name)
        
        # var not found in subroutine level st
        if v_kind == SymbolKind.NONE:
            # lookup class level table
            v_kind = self.class_level_st.get_kind_of(v_name)

            if v_kind == SymbolKind.NONE:
                return False

            v_props["kind"] = v_kind
            v_props["type"] = self.class_level_st.get_type_of(v_name)
            v_props["index"] = self.class_level_st.get_index_of(v_name)

            # return class level variable data
            return v_props
        
        # Data found for subroutine level table
        v_props["kind"] = v_kind
        v_props["type"] = self.subroutine_level_st.get_type_of(v_name)
        v_props["index"] = self.subroutine_level_st.get_index_of(v_name)

        return v_props

    def var_t_to_segment_t(self, v_kind: SymbolKind) -> SegmentType:
        if v_kind == SymbolKind.STATIC:
            return SegmentType.STATIC
        elif v_kind == SymbolKind.FEILD:
            # TODO
            return SegmentType.STATIC
        elif v_kind == SymbolKind.ARG:
            return SegmentType.ARG
        elif v_kind == SymbolKind.VAR:
            return SegmentType.LOCAL
        else:
            raise AssertionError("No segment kind for given v_kind!!")
        


