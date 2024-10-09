from flask import Blueprint, jsonify

# Blueprint is used to organize routes
api = Blueprint('api', __name__)

# Example route
@api.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello from Flask API!'})
