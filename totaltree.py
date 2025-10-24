import os
import sys
from pathlib import Path

with open('diokl.txt', 'w') as file:
    # --- Configuration ---
    def print(statement):
        file.write(statement)
    # Directories to completely ignore during traversal
    IGNORED_DIR_NAMES = {'.git', '.idea', '.vscode', '__pycache__', 'node_modules', 'dist', 'build'}

    # File extensions that are highly likely to be binary (skips content reading)
    COMMON_BINARY_EXTENSIONS = {
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', 
        '.mp3', '.wav', '.ogg', '.mp4', '.avi', '.mov', 
        '.zip', '.tar', '.gz', '.7z', '.rar', 
        '.exe', '.dll', '.so', '.dylib', '.bin',
        '.db', '.sqlite', '.sqlite3', 
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
        '.class', '.pyc',
        '.woff', '.woff2', '.ttf', '.otf'
    }

    # Number of bytes to check for the presence of a null byte (\x00), 
    # which is a strong indicator of a binary file.
    NULL_BYTE_THRESHOLD = 1024 

    # ANSI Color Codes for better output readability
    C_DIR = '\033[94m'   # Blue
    C_FILE = '\033[92m'  # Green
    C_SEPARATOR = '\033[93m' # Yellow
    C_SKIP = '\033[91m'  # Red
    C_END = '\033[0m'    # Reset

    def is_text_file(filepath: Path) -> bool:
        """
        Heuristic to determine if a file is likely text or binary based on
        extension and the presence of null bytes.
        """
        # 1. Check extension against known binary types
        if filepath.suffix.lower() in COMMON_BINARY_EXTENSIONS:
            return False
        
        # 2. Check for null bytes in the file's header
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(NULL_BYTE_THRESHOLD)
                if b'\x00' in chunk:
                    return False
        except IOError:
            # Cannot read the file (e.g., permissions issue), treat as non-text/unreadable
            return False
        
        return True

    def scan_directory(root_dir: str):
        """
        Traverses the specified directory, prints the structure, and displays
        the content of non-binary, non-excluded files.
        """
        root_path = Path(root_dir).resolve()
        
        if not root_path.is_dir():
            print(f"Error: The path '{root_dir}' is not a valid directory or does not exist.")
            sys.exit(1)
            
        print(f"--- Scanning Project Root: {root_path.name} ---")

        for dirpath_str, dirnames, filenames in os.walk(root_path, topdown=True):
            dirpath = Path(dirpath_str)
            
            # Calculate indentation level for tree structure formatting
            try:
                relative_path_parts = Path(os.path.relpath(dirpath, root_path)).parts
                # The root path itself will be ('.',), so we check and adjust level
                level = len(relative_path_parts) if relative_path_parts != ('.',) and relative_path_parts != ('',) else 0
                indent = '    ' * level
            except ValueError:
                level = 0
                indent = ''

            # --- Directory Filtering ---
            # Modify the 'dirnames' list in-place to exclude ignored directories
            dirnames[:] = [d for d in dirnames if d not in IGNORED_DIR_NAMES]

            # Print the directory name (skip the root directory as it's handled in the header)
            if level > 0:
                print(f"{indent}{C_DIR}[{dirpath.name}]/{C_END}")

            # --- File Processing ---
            for filename in filenames:
                filepath = dirpath / filename
                file_indent = '    ' * (level + 1)
                
                # Print file path in the structure
                print(f"{file_indent}{C_FILE}{filename}{C_END}")

                if is_text_file(filepath):
                    try:
                        # Print separator and content
                        print(f"{file_indent}  {C_SEPARATOR}|--- FILE CONTENT START ---|{C_END}")
                        
                        # Attempt to read with UTF-8 encoding
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Indent every line of the content for structure visibility
                            indented_content = '\n'.join([f'{file_indent}  {line}' for line in content.splitlines()])
                            print(indented_content)
                            
                        print(f"{file_indent}  {C_SEPARATOR}|--- FILE CONTENT END ---|{C_END}\n")

                    except UnicodeDecodeError:
                        print(f"{file_indent}  {C_SKIP}[CONTENT SKIPPED: Encoding Error - File is likely non-UTF-8 text]{C_END}\n")
                    except Exception as e:
                        print(f"{file_indent}  {C_SKIP}[CONTENT SKIPPED: Error reading file: {e}]{C_END}\n")
                else:
                    print(f"{file_indent}  {C_SKIP}[CONTENT SKIPPED: Binary or Excluded File Type]{C_END}\n")
                    

    if __name__ == "__main__":
        if len(sys.argv) != 2:
            print("Usage: python directory_scanner.py <path_to_directory>")
            sys.exit(1)

        input_dir = sys.argv[1]
        scan_directory(input_dir)
