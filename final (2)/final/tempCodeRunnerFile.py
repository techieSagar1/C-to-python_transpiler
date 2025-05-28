from flask import Flask, request, jsonify
from my_tokenisizer import tokenize, build_ast, generate_python_code  # Adjust import name

from anytree import RenderTree

app = Flask(__name__)

@app.route('/transpile', methods=['POST'])
def transpile():
    data = request.json
    c_code = data.get('code', '')
    
    try:
        tokens = tokenize(c_code)
        ast_root = build_ast(tokens)
        python_code = ""
        for child in ast_root.children:
            python_code += generate_python_code(child)

        return jsonify({'python_code': python_code.strip()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
