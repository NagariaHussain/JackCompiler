from pathlib import Path

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

in_stream = Path('tests/SquareGame.jack').open('r')
xml_out = Path('SquareGameMT.xml').open('w')

# Write XML main tag
xml_out.write("<tokens>\n")

cur_char = in_stream.read(1)

while cur_char:
    # Reset value variables
    cur_symbol = ""
    cur_ident = ""
    cur_intval = ""
    cur_strconst = ""

    # Eat the white spaces
    while (cur_char == " " or cur_char == "\n"):
        cur_char = in_stream.read(1)

    # If current character is alphabet
    if cur_char.isalpha():
        cur_ident = cur_char
        # Eat all consecutive alpha numeric characters
        cur_char = in_stream.read(1)
        while(cur_char.isalnum() or cur_char == "_"):
            cur_ident += cur_char
            cur_char = in_stream.read(1)

        if cur_ident in keywords:
            xml_out.write(f"<keyword> {cur_ident} </keyword>\n")
        else:
            xml_out.write(f"<identifier> {cur_ident} </identifier>\n")


        continue
    
    if cur_char in symbols:
        cur_symbol = cur_char
        if cur_symbol == "<":
            cur_symbol = "&lt;"
        elif cur_symbol == ">":
            cur_symbol = "&gt;"
        elif cur_symbol == "&":
            cur_symbol = "&amp;"
        
       
        if (cur_char == "/"):
            # Read the character ahead
            cur_char = in_stream.read(1)

            # Handle inline comments
            if (cur_char == "/"):
                while cur_char != "\n":
                    cur_char = in_stream.read(1)
                continue

            # Handle block comments
            elif (cur_char == "*"):
                cur_char = in_stream.read(1)
                while True:
                    while cur_char != "*":
                        cur_char = in_stream.read(1)
                    
                    cur_char = in_stream.read(1)

                    if cur_char == "/":
                        cur_char = in_stream.read(1)
                        break
                    else:
                        continue
            
            else:
                cur_char = in_stream.read(1)
                xml_out.write(f"<symbol> {cur_symbol} </symbol>\n")

        else:
            cur_char = in_stream.read(1)
            xml_out.write(f"<symbol> {cur_symbol} </symbol>\n")
    
    if cur_char.isdigit():
        cur_intval = cur_char
        # Eat all consecutive numeric characters
        while((cur_char := in_stream.read(1)).isdigit()):
            cur_intval += cur_char
        
        xml_out.write(f"<integerConstant> {cur_intval} </integerConstant>\n")

        continue

    if cur_char == '"':
        while ((cur_char := in_stream.read(1)) != '"'):
            cur_strconst += cur_char
        
        # Closing `"` occurs 
        # Move one character ahead
        cur_char = in_stream.read(1)
        xml_out.write(f"<stringConstant> {cur_strconst} </stringConstant>\n")

# Write XML closing main tag
xml_out.write("</tokens>\n")