"""Flask application."""

from flask import Flask, jsonify
from main import greet, farewell

app = Flask(__name__)

@app.route('/api/greet/<name>', methods=['GET'])
def api_greet(name):
    """Greet endpoint."""
    return jsonify({"message": greet(name)})

@app.route('/api/farewell', methods=['POST'])
def api_farewell():
    """Farewell endpoint."""
    return jsonify({"message": farewell("User")})

if __name__ == '__main__':
    app.run(debug=True)
