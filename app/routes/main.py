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

@main_bp.route('/endpoints')
def list_endpoints():
    """List all available endpoints."""
    from flask import current_app
    endpoints = []
    for rule in current_app.url_map.iter_rules():
        endpoints.append({
            'endpoint': rule.rule,
            'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
            'blueprint': rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'main'
        })
    return jsonify({'endpoints': endpoints})
