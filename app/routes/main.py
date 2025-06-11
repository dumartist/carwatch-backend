from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def hello_world():
    return jsonify({
        'message': 'CarWatch Backend API is running',
        'version': '1.0.0',
        'status': 'healthy'
    })

@main_bp.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'carwatch-backend',
        'endpoints': {
            'auth': '/auth/*',
            'api': '/api/*'
        }
    })