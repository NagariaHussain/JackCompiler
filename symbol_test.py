from symbol_table import SymbolTable, SymbolKind

# Create a new symbol table
s1 = SymbolTable()

# Insert some test data
s1.define("a", "int", SymbolKind.ARG)
s1.define("b", "int", SymbolKind.ARG)
s1.define("c", "String", SymbolKind.FEILD)
s1.define("d", "Point", SymbolKind.ARG)

# Test var index
assert s1.get_index_of("a") == 0
assert s1.get_index_of("b") == 1
assert s1.get_index_of("c") == 0
assert s1.get_index_of("d") == 2

# Test var kind
assert s1.get_kind_of("d") == SymbolKind.ARG
assert s1.get_kind_of("c") == SymbolKind.FEILD
# When symbol is not defined
assert s1.get_kind_of("e") == SymbolKind.NONE
assert s1.get_kind_of("spam") == SymbolKind.NONE

# Test var type
assert s1.get_type_of("a") == "int"
assert s1.get_type_of("c") == "String"
assert s1.get_type_of("d") == "Point"

print("All assertions are True!")
