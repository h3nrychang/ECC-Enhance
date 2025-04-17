from flask import Blueprint, request, jsonify

version_bp = Blueprint('version', __name__, url_prefix='/api')

@version_bp.route('/version', methods=['GET'])
def list_version():
    """
    获取版本信息
    ---

    """
    # parks = BusinessParkModel.query.all()
    data = {
        "version": "1.6.0"
    }

    return jsonify(data)