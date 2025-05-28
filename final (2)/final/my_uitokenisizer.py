import streamlit as st
from my_tokenisizer import tokenize, build_ast, generate_python_code
from anytree import RenderTree
import json

st.set_page_config(page_title="C to Python Converter", layout="wide")

st.title("🔄 C to Python Code Translator")
st.markdown("Paste your C code below, and see its **tokens**, **AST**, and **generated Python code** visualized!")

# Input
c_code = st.text_area("🧾 Enter your C code", height=300, value="""
#include <stdio.h>
int main() {
    int n, reversed = 0, remainder, original;
    printf("Enter an integer: ");
    scanf("%d", &n);
    original = n;

    while (n != 0) {
        remainder = n % 10;
        reversed = reversed * 10 + remainder;
        n /= 10;
    }

    if (original == reversed)
        printf("%d is a palindrome.", original);
    else
        printf("%d is not a palindrome.", original);

    return 0;
}
""")

if st.button("🚀 Run Tokenizer and Translator"):
    with st.spinner("Tokenizing..."):
        tokens = tokenize(c_code)
        st.success("✅ Tokenization complete")

        # Token Table
        st.subheader("🔎 Tokens")
        st.dataframe(tokens, use_container_width=True)

    with st.spinner("Building AST..."):
        ast_root = build_ast(tokens)
        st.success("✅ AST built")

        # AST Display
        st.subheader("🌳 AST Structure")

        def render_ast_tree(node):
            tree_str = ""
            for pre, _, n in RenderTree(node):
                tree_str += f"{pre}{n.name}\n"
            return tree_str

        st.code(render_ast_tree(ast_root), language="text")

    with st.spinner("Generating Python code..."):
        generated_code = ""
        for child in ast_root.children:
            generated_code += generate_python_code(child)
        st.success("✅ Python code generated")

        st.subheader("🐍 Generated Python Code")
        st.code(generated_code.strip(), language="python")

        with open("output.py", "w") as f:
            f.write(generated_code.strip())
