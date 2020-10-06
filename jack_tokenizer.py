# Token type constants
from type_enums import TokenType, KeywordType

# Set of reserved keywords
keywords = {
    "class",
    "constructor",
    "function",
    "method",
    "field",
    "static",
    "var",
    "int",
    "char",
    "boolean",
    "void",
    "true",
    "false",
    "null",
    "this",
    "let",
    "do",
    "if",
    "else",
    "while",
    "return"
}

# Set of Allowed Symbols
symbols = {
    "{",
    "}",
    "(",
    ")",
    "[",
    "]",
    ".",
    ",",
    ";",
    "+",
    "-",
    "*",
    "/",
    "&",
    "|",
    "<",
    ">",
    "=",
    "~"
}

class JackTokenizer:
    '''Tokenizes the given Jack Source File'''
    # Constructor
    def __init__(self, in_path):
        # Open file for reading
        self.in_stream = in_path.open('r', encoding="utf-8")
        
        # Store the current character 
        self.cur_char = self.in_stream.read(1)

        # Current token type
        self.cur_token_type = None

    
    # Are there more tokens?
    # Also, updates the current 
    # token params
    def has_more_tokens(self):
        # Reset value variables
        self.cur_symbol = ""
        self.cur_ident = ""
        self.cur_intval = ""
        self.cur_strconst = ""

        # Eat the white spaces
        while (self.cur_char == " " or self.cur_char == "\n"):
            self.cur_char = self.in_stream.read(1)

        # If current character is alphabet
        if self.cur_char.isalpha():
            self.cur_ident = self.cur_char
            # Eat all consecutive alpha numeric characters
            self.cur_char = self.in_stream.read(1)
            while(self.cur_char.isalnum() or self.cur_char == "_"):
                self.cur_ident += self.cur_char
                self.cur_char = self.in_stream.read(1)

            if self.cur_ident in keywords:
                self.cur_token_type = TokenType.KEYWORD
            else:
                self.cur_token_type = TokenType.IDENTIFIER

            return True
        
        if self.cur_char in symbols:
            self.cur_symbol = self.cur_char
            if self.cur_symbol == "<":
                self.cur_symbol = "&lt;"
            elif self.cur_symbol == ">":
                self.cur_symbol = "&gt;"
            elif self.cur_symbol == "&":
                self.cur_symbol = "&amp;"
            
        
            if (self.cur_char == "/"):
                # Read the character ahead
                self.cur_char = self.in_stream.read(1)

                # Handle inline comments
                if (self.cur_char == "/"):
                    while self.cur_char != "\n":
                        self.cur_char = self.in_stream.read(1)

                    return self.has_more_tokens()

                # Handle block comments
                elif (self.cur_char == "*"):
                    self.cur_char = self.in_stream.read(1)
                    while True:
                        while self.cur_char != "*":
                            self.cur_char = self.in_stream.read(1)
                        
                        self.cur_char = self.in_stream.read(1)

                        if self.cur_char == "/":
                            self.cur_char = self.in_stream.read(1)
                            break
                        else:
                            continue
                
                else:
                    self.cur_char = self.in_stream.read(1)
                    self.cur_token_type = TokenType.SYMBOL
                    return True

            else:
                self.cur_char = self.in_stream.read(1)
                self.cur_token_type = TokenType.SYMBOL
                return True
        
        if self.cur_char.isdigit():
            self.cur_intval = self.cur_char
            # Eat all consecutive numeric characters
            self.cur_char = self.in_stream.read(1)
            while(self.cur_char.isdigit()):
                self.cur_intval += self.cur_char
                self.cur_char = self.in_stream.read(1)
            
            self.cur_token_type = TokenType.INT_CONST

            return True

        if self.cur_char == '"':
            self.cur_char = self.in_stream.read(1)
            while (self.cur_char != '"'):
                self.cur_strconst += self.cur_char
                self.cur_char = self.in_stream.read(1)
            
            # Closing `"` occurs 
            # Move one character ahead
            self.cur_char = self.in_stream.read(1)
            self.cur_token_type = TokenType.STRING_CONST

            return True

        return False
    

    # Returns the type of token
    def get_token_type(self):
        return self.cur_token_type
    
    # Returns the keyword which in current token
    def get_keyword_type(self):
        if self.cur_ident == "class":
            return KeywordType.CLASS
        
        if self.cur_ident == "method":
            return KeywordType.METHOD

        if self.cur_ident == "function":
            return KeywordType.FUNCTION

        if self.cur_ident == "constructor":
            return KeywordType.CONSTRUCTOR

        if self.cur_ident == "int":
            return KeywordType.INT

        if self.cur_ident == "boolean":
            return KeywordType.BOOLEAN

        if self.cur_ident == "char":
            return KeywordType.CHAR
        
        if self.cur_ident == "void":
            return KeywordType.VOID

        if self.cur_ident == "var":
            return KeywordType.VAR

        if self.cur_ident == "static":
            return KeywordType.STATIC

        if self.cur_ident == "field":
            return KeywordType.FIELD

        if self.cur_ident == "let":
            return KeywordType.LET

        if self.cur_ident == "do":
            return KeywordType.DO

        if self.cur_ident == "if":
            return KeywordType.IF

        if self.cur_ident == "else":
            return KeywordType.ELSE

        if self.cur_ident == "while":
            return KeywordType.WHILE

        if self.cur_ident == "return":
            return KeywordType.RETURN

        if self.cur_ident == "true":
            return KeywordType.TRUE

        if self.cur_ident == "false":
            return KeywordType.FALSE

        if self.cur_ident == "null":
            return KeywordType.NULL

        if self.cur_ident == "this":
            return KeywordType.THIS
    
    # Returns the character which 
    # is the current token
    def get_symbol(self):
        return self.cur_symbol

    # Returns the integer value 
    # of the current token
    def get_int_val(self):
        return int(self.cur_intval)

    # Returns the string value
    # of the current token
    def get_string_val(self):
        return self.cur_strconst

    def get_cur_ident(self):
        return self.cur_ident

# TESTING THE TOKENIZER
# from pathlib import Path


# tz = JackTokenizer(Path('test.jack'))

# while tz.has_more_tokens():
#     print(tz.get_token_type())

#     if (tz.get_token_type() == TokenType.STRING_CONST):
#         print(tz.get_string_val())

#     if (tz.get_token_type() == TokenType.INT_CONST):
#         print(tz.get_int_val())

#     if (tz.get_token_type() == TokenType.KEYWORD):
#         print(tz.get_keyword_type())