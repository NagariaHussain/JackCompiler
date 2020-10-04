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
    pass
elif in_path.is_dir():
    # Path points to a directory
    pass

# Initialize tokenizer
tokenizer = JackTokenizer(in_path)

# Initialize compilation engine
compilationEngine = CompilationEngine(tokenizer)