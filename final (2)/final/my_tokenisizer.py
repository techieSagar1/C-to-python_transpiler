import re
from anytree import Node, RenderTree
import json

# Token patterns
TOKEN_PATTERNS = [
    (r'#include <[\w\.]+>', 'HEADER'),
    (r'\bint\b|\breturn\b|\bif\b|\belse\b|\bwhile\b', 'KEYWORD'),
    (r'\bprintf\b|\bscanf\b', 'FUNCTION'),
    (r'==|!=|<=|>=|=|<|>|%|\+|\-|\*|\/', 'OPERATOR'),
    (r'\d+', 'NUMBER'),
    (r'"[^"]*"', 'STRING'),
    (r'&\w+', 'ADDRESS'),
    (r'[a-zA-Z_]\w*', 'IDENTIFIER'),
    (r'[{}();,]', 'SYMBOL'),
]

# Tokenizer
def tokenize(code):
    tokens = []
    code = code.strip()
    while code:
        for pattern, token_type in TOKEN_PATTERNS:
            match = re.match(pattern, code)
            if match:
                tokens.append((match.group(), token_type))
                code = code[len(match.group()):].lstrip()
                break
        else:
            print(f"❌ Unknown token: {code[:20]}")
            code = code[1:].lstrip()
    return tokens

# AST Builder
def build_ast(tokens):
    root = Node("Program")
    i = 0
    current_function = None
    while i < len(tokens):
        token, tok_type = tokens[i]

        if tok_type == "HEADER":
            Node(f"Header: {token}", parent=root)
            i += 1

        elif token == "int" and tokens[i+1][1] == "IDENTIFIER" and tokens[i+2][0] == '(':
            func_name = tokens[i+1][0]
            current_function = Node(f"Function: {func_name}", parent=root)
            i += 4  # skip 'int main ( )'

        elif token == "while":
            condition, i = parse_condition(tokens, i + 1)
            while_node = Node("While", parent=current_function)
            Node(f"Condition: {condition}", parent=while_node)
            i = parse_block_or_statement(tokens, i, while_node)

        elif token == "if":
            condition, i = parse_condition(tokens, i + 1)
            if_node = Node("If", parent=current_function)
            Node(f"Condition: {condition}", parent=if_node)
            i = parse_block_or_statement(tokens, i, if_node)

        elif token == "else":
            if i + 1 < len(tokens) and tokens[i+1][0] == "if":
                condition, i = parse_condition(tokens, i + 2)
                elseif_node = Node("Elif", parent=current_function)
                Node(f"Condition: {condition}", parent=elseif_node)
                i = parse_block_or_statement(tokens, i, elseif_node)
            else:
                else_node = Node("Else", parent=current_function)
                i = parse_block_or_statement(tokens, i + 1, else_node)

        elif token == "printf":
            print_node = Node("Print", parent=current_function)
            string_value = tokens[i+2][0]
            if i+4 < len(tokens) and tokens[i+3][0] == ',' and tokens[i+4][1] == "IDENTIFIER":
                Node(f"FormattedString: {string_value},{tokens[i+4][0]}", parent=print_node)
                i += 6
            else:
                Node(f"String: {string_value}", parent=print_node)
                i += 5

        elif token == "scanf":
            scanf_node = Node("Scan", parent=current_function)
            Node(f"Format: {tokens[i+2][0]}", parent=scanf_node)
            Node(f"Variable: {tokens[i+4][0].lstrip('&')}", parent=scanf_node)
            i += 6

        elif token == "return":
            return_node = Node("Return", parent=current_function)
            Node(f"Number: {tokens[i+1][0]}", parent=return_node)
            i += 3

        elif tok_type == "IDENTIFIER" and i + 1 < len(tokens) and tokens[i+1][0] == "=":
            assign_node = Node("Assign", parent=current_function)
            Node(f"Var: {token}", parent=assign_node)
            expr_tokens = []
            i += 2
            while i < len(tokens) and tokens[i][0] != ";":
                expr_tokens.append(tokens[i][0])
                i += 1
            Node(f"Expr: {' '.join(expr_tokens)}", parent=assign_node)
            i += 1

        else:
            i += 1
    return root

def parse_condition(tokens, i):
    left = tokens[i+1][0]
    op = tokens[i+2][0]
    right = tokens[i+3][0]
    return f"{left} {op} {right}", i + 5

def parse_block_or_statement(tokens, i, parent):
    if tokens[i][0] == '{':
        i += 1
        while tokens[i][0] != '}':
            token = tokens[i][0]
            if token == 'printf':
                print_node = Node("Print", parent=parent)
                Node(f"String: {tokens[i+2][0]}", parent=print_node)
                i += 5
            elif token == 'return':
                return_node = Node("Return", parent=parent)
                Node(f"Number: {tokens[i+1][0]}", parent=return_node)
                i += 3
            elif tokens[i][1] == "IDENTIFIER" and tokens[i+1][0] == "=":
                assign_node = Node("Assign", parent=parent)
                Node(f"Var: {tokens[i][0]}", parent=assign_node)
                i += 2
                expr_tokens = []
                while tokens[i][0] != ";":
                    expr_tokens.append(tokens[i][0])
                    i += 1
                Node(f"Expr: {' '.join(expr_tokens)}", parent=assign_node)
                i += 1
            else:
                i += 1
        return i + 1
    else:
        token = tokens[i][0]
        if token == 'printf':
            print_node = Node("Print", parent=parent)
            Node(f"String: {tokens[i+2][0]}", parent=print_node)
            return i + 5
        elif token == 'return':
            return_node = Node("Return", parent=parent)
            Node(f"Number: {tokens[i+1][0]}", parent=return_node)
            return i + 3
    return i

# Code generator
def generate_python_code(node, indent=0):
    code = ""
    space = "    " * indent
    if node.name.startswith("Function:"):
        code += f"def {node.name.split(':')[1].strip()}():\n"
        for child in node.children:
            code += generate_python_code(child, indent + 1)
    elif node.name == "If":
        condition = [c.name.split(":")[1].strip() for c in node.children if c.name.startswith("Condition")][0]
        code += f"{space}if {condition}:\n"
        for child in node.children:
            if not child.name.startswith("Condition"):
                code += generate_python_code(child, indent + 1)
    elif node.name == "Elif":
        condition = [c.name.split(":")[1].strip() for c in node.children if c.name.startswith("Condition")][0]
        code += f"{space}elif {condition}:\n"
        for child in node.children:
            if not child.name.startswith("Condition"):
                code += generate_python_code(child, indent + 1)
    elif node.name == "Else":
        code += f"{space}else:\n"
        for child in node.children:
            code += generate_python_code(child, indent + 1)
    elif node.name == "While":
        condition = [c.name.split(":")[1].strip() for c in node.children if c.name.startswith("Condition")][0]
        code += f"{space}while {condition}:\n"
        for child in node.children:
            if not child.name.startswith("Condition"):
                code += generate_python_code(child, indent + 1)
    elif node.name == "Print":
        if node.children[0].name.startswith("FormattedString"):
            string_expr = node.children[0].name.split(":")[1].strip()
            if "," in string_expr:
                fmt, var = string_expr.split(",")
                fmt = fmt.strip()[1:-1]  # remove quotes
                code += f'{space}print(f"{fmt}{{{var.strip()}}}")\n'
            else:
                code += f'{space}print({string_expr})\n'
        else:
            string = node.children[0].name.split(":")[1].strip()
            code += f"{space}print({string})\n"
    elif node.name == "Scan":
        var = [c.name.split(":")[1].strip() for c in node.children if c.name.startswith("Variable")][0]
        code += f"{space}{var} = int(input())\n"
    elif node.name == "Assign":
        var = [c.name.split(":")[1].strip() for c in node.children if c.name.startswith("Var")][0]
        expr = [c.name.split(":")[1].strip() for c in node.children if c.name.startswith("Expr")][0]
        code += f"{space}{var} = {expr}\n"
    elif node.name == "Return":
        number = node.children[0].name.split(":")[1].strip()
        code += f"{space}return {number}\n"
    return code

# MAIN
if __name__ == "__main__":
    c_code = """
  #include <stdio.h>
int main() {
  int n, reversed = 0, remainder, original;
    printf("Enter an integer: ");
    scanf("%d", &n);
    original = n;

    // reversed integer is stored in reversed variable
    while (n != 0) {
        remainder = n % 10;
        reversed = reversed * 10 + remainder;
        n /= 10;
    }

    // palindrome if orignal and reversed are equal
    if (original == reversed)
        printf("%d is a palindrome.", original);
    else
        printf("%d is not a palindrome.", original);

    return 0;
}

Run Code

    """

    tokens = tokenize(c_code)
    print("\nFinal Token List:")
    print(tokens)

    ast_root = build_ast(tokens)

    print("\nGenerated AST (Tree Structure):")
    for pre, _, node in RenderTree(ast_root):
        print(f"{pre}{node.name}")

    print("\nGenerated AST (JSON Format):")
    print(json.dumps({"name": ast_root.name, "children": [child.name for child in ast_root.children]}, indent=4))

    # Python code generation
    generated_code = ""
    for child in ast_root.children:
        generated_code += generate_python_code(child)

    print("\nGenerated Python Code:\n")
    print(generated_code.strip())

    with open("output.py", "w") as f:
        f.write(generated_code.strip())
