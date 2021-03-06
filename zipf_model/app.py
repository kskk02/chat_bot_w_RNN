#!flask/bin/python
from flask import Flask, jsonify
from suggestion_model import Suggestion_Generator
'''
USAGE in Bash shell:

1) python app.py
2) curl http://localhost:5000/find_suggestions/'what+is+y'
'''

app = Flask(__name__)

@app.route('/find_suggestions/<path:search_term>', methods=['GET'])
def get_tasks(search_term):
    input_term = search_term.replace('+',' ')
    model = Suggestion_Generator()
    model.load_from_pickle()
    return jsonify({'suggestions': model.find_suggestions(input_term)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
