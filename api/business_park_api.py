from flask import Blueprint, request, jsonify
from exts import db
from blueprint.business_park import BusinessParkModel  # 复用 model

business_park_api_bp = Blueprint('business_park_api', __name__, url_prefix='/api/park')


@business_park_api_bp.route('/list', methods=['GET'])
def list_business_parks():
    """
    获取所有园区列表
    ---
    tags:
      - BusinessPark
    responses:
      200:
        description: 成功返回园区列表
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              area:
                type: string
              company_name:
                type: string
              remark:
                type: string
    """
    parks = BusinessParkModel.query.all()
    data = [
        {
            "id": p.id,
            "name": p.name,
            "area": p.area,
            "company_name": p.company_name,
            "remark": p.remark
        } for p in parks
    ]
    return jsonify(data)


@business_park_api_bp.route('/add', methods=['POST'])
def add_business_park():
    """
    添加园区
    ---
    tags:
      - BusinessPark
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
            area:
              type: string
            company_name:
              type: string
            remark:
              type: string
    responses:
      200:
        description: 添加成功
        schema:
          type: object
          properties:
            message:
              type: string
            id:
              type: integer
    """
    data = request.get_json()
    park = BusinessParkModel(**data)
    db.session.add(park)
    db.session.commit()
    return jsonify({"message": "新增成功", "id": park.id})


@business_park_api_bp.route('/<int:id>', methods=['PUT'])
def update_business_park(id):
    """
    更新园区信息
    ---
    tags:
      - BusinessPark
    parameters:
      - in: path
        name: id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            area:
              type: string
            company_name:
              type: string
            remark:
              type: string
    responses:
      200:
        description: 更新成功
        schema:
          type: object
          properties:
            message:
              type: string
    """
    data = request.get_json()
    park = BusinessParkModel.query.get(id)
    if not park:
        return jsonify({"error": "园区不存在"}), 404

    for key in ["name", "area", "company_name", "remark"]:
        if key in data:
            setattr(park, key, data[key])

    db.session.commit()
    return jsonify({"message": "更新成功"})


@business_park_api_bp.route('/<int:id>', methods=['DELETE'])
def delete_business_park(id):
    """
    删除园区信息
    ---
    tags:
      - BusinessPark
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: 删除成功
        schema:
          type: object
          properties:
            message:
              type: string
    """
    park = BusinessParkModel.query.get(id)
    if not park:
        return jsonify({"error": "园区不存在"}), 404
    db.session.delete(park)
    db.session.commit()
    return jsonify({"message": "删除成功"})
