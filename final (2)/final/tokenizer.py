import re

# Define regex patterns for different token types
TOKEN_PATTERNS = [
    (r'#include\s*<[^>\n]+>', 'HEADER'),  # #include <stdio.h>
    (r'\b(int|return|if|for|while|void|float|char|double)\b', 'KEYWORD'),  # C keywords
    (r'printf', 'PRINT'),  # printf function
    (r'\b[a-zA-Z_]\w*\b', 'IDENTIFIER'),  # Identifiers
    (r'\b\d+(\.\d+)?\b', 'NUMBER'),  # Numbers
    (r'"[^"]*"', 'STRING'),  # Strings
    (r'[=+\-*/<>]', 'OPERATOR'),  # Operators
    (r'[{}();,]', 'SYMBOL')  # Punctuation
]

# Function to tokenize C code
def tokenize_c_code(code):
    tokens = []
    while code:
        code = code.lstrip()  # Remove leading spaces/newlines
        if not code:  # If nothing left, stop
            break  

        print(f"Processing: {repr(code[:20])}")  # Debug: Show first 20 chars

        match_found = False
        for pattern, token_type in TOKEN_PATTERNS:
            match = re.match(pattern, code)
            if match:
                tokens.append((match.group(), token_type))  # Store token
                code = code[len(match.group()):]  # Remove matched part
                match_found = True
                break

        if not match_found:
            print(f"❌ Unknown token: {repr(code[:20])}")  # Debug unknown token
            code = code[1:]  # Skip unknown character

    return tokens

# Example C Code
c_code = """
#include <stdio.h>

int main() {
    int x = 10;
    printf("Hello, World!");
    return 0;
}
"""

# Tokenize and print results
tokens = tokenize_c_code(c_code)
print("\nFinal Token List:")
for token in tokens:
    print(token)
    
