# For accessing command line args
from sys import argv

# For handling file/dir paths
from pathlib import Path

# Import Analyzer components
from compilation_engine import CompilationEngine
from jack_tokenizer import JackTokenizer

# Get input path
in_path = Path(argv[1])

if in_path.is_file():
    # Path points to a file
    # Initialize tokenizer
    tokenizer = JackTokenizer(in_path)
    # Initialize compilation engine
    compilationEngine = CompilationEngine(tokenizer, in_path.with_suffix(".xml"))

    # Start compilation
    compilationEngine.start_compilation()

elif in_path.is_dir():
    # Path points to a directory
    for item in in_path.iterdir():
        if item.is_file():
            # Compile every jack file
            if item.suffix == ".jack":
                tokenizer = JackTokenizer(item)
                ci = CompilationEngine(tokenizer, item.with_suffix(".xml"))
                ci.start_compilation()


# END OF FILE
