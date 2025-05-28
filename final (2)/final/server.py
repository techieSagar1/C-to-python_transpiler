from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from my_tokenisizer import tokenize, build_ast, generate_python_code

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    c_code = data.get('c_code', '')

    try:
        tokens = tokenize(c_code)
        ast_root = build_ast(tokens)

        python_code = ""
        for child in ast_root.children:
            python_code += generate_python_code(child)

        return jsonify({'python_code': python_code.strip()})
    except Exception as e:
        return jsonify({'python_code': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
