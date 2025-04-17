from flask import Blueprint, request, jsonify, send_file
from exts import db
from blueprint.hotel import HotelModel
from datetime import datetime
import pandas as pd
import io

hotel_api_bp = Blueprint('hotel_api', __name__, url_prefix='/api/hotel')


@hotel_api_bp.route('/list', methods=['GET'])
def list_hotels():
    """
    获取酒店分页列表
    ---
    tags:
      - Hotel
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 20
    responses:
      200:
        description: 酒店列表数据
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = HotelModel.query.paginate(page=page, per_page=per_page, error_out=False)
    hotels = pagination.items

    data = []
    for h in hotels:
        data.append({
            "id": h.id,
            "hotel_name": h.hotel_name,
            "actual_people_count": h.actual_people_count,
            "other_carrier": h.other_carrier,
            "key_person_name": h.key_person_name,
            "key_person_phone": h.key_person_phone,
            "competitor_services": h.competitor_services,
            "competitor_price": h.competitor_price,
            "competitor_expiry": h.competitor_expiry,
            "visitor_name": h.visitor_name,
            "remarks": h.remarks,
            "update_time": h.update_time,
            "business_park": h.business_park
        })
    return jsonify({
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "data": data
    })


@hotel_api_bp.route('/add', methods=['POST'])
def add_hotel():
    """
    添加酒店信息
    ---
    tags:
      - Hotel
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - hotel_name
          properties:
            hotel_name:
              type: string
            actual_people_count:
              type: string
            other_carrier:
              type: string
            key_person_name:
              type: string
            key_person_phone:
              type: string
            competitor_services:
              type: string
            competitor_price:
              type: string
            competitor_expiry:
              type: string
            visitor_name:
              type: string
            remarks:
              type: string
            update_time:
              type: string
            business_park:
              type: string
    responses:
      200:
        description: 添加成功
    """
    data = request.get_json()
    hotel = HotelModel(**data)
    db.session.add(hotel)
    db.session.commit()
    return jsonify({"message": "新增成功", "id": hotel.id})


@hotel_api_bp.route('/<int:id>', methods=['PUT'])
def update_hotel(id):
    """
    更新酒店信息
    ---
    tags:
      - Hotel
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
            hotel_name:
              type: string
            actual_people_count:
              type: string
            other_carrier:
              type: string
            key_person_name:
              type: string
            key_person_phone:
              type: string
            competitor_services:
              type: string
            competitor_price:
              type: string
            competitor_expiry:
              type: string
            visitor_name:
              type: string
            remarks:
              type: string
            update_time:
              type: string
            business_park:
              type: string
    responses:
      200:
        description: 更新成功
    """
    data = request.get_json()
    hotel = HotelModel.query.get(id)
    if not hotel:
        return jsonify({"error": "酒店不存在"}), 404

    for key in data:
        if hasattr(hotel, key):
            setattr(hotel, key, data[key])
    db.session.commit()
    return jsonify({"message": "更新成功"})


@hotel_api_bp.route('/<int:id>', methods=['DELETE'])
def delete_hotel(id):
    """
    删除酒店
    ---
    tags:
      - Hotel
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: 删除成功
    """
    hotel = HotelModel.query.get(id)
    if not hotel:
        return jsonify({"error": "酒店不存在"}), 404
    db.session.delete(hotel)
    db.session.commit()
    return jsonify({"message": "删除成功"})


@hotel_api_bp.route('/import', methods=['POST'])
def import_hotels():
    """
    导入酒店信息（Excel）
    ---
    tags:
      - Hotel
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: 包含酒店数据的 Excel 文件（.xlsx）
    responses:
      200:
        description: 导入成功
    """
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "未上传文件"}), 400

    try:
        df = pd.read_excel(file, dtype=str)
    except Exception as e:
        return jsonify({"error": "无法读取Excel文件，请确认格式"}), 400

    expected_fields = [
        "hotel_name", "visitor_name", "actual_people_count", "other_carrier",
        "key_person_name", "key_person_phone", "competitor_services",
        "competitor_price", "competitor_expiry", "remarks", "update_time"
    ]

    if list(df.columns[:len(expected_fields)]) != expected_fields:
        return jsonify({"error": "Excel表头不符合预期"}), 400

    for _, row in df.iterrows():
        row_data = row.to_dict()
        hotel_name = row_data.get("hotel_name")
        if not hotel_name or pd.isna(hotel_name):
            continue

        if pd.isna(row_data.get("update_time")) or not str(row_data.get("update_time")).strip():
            row_data["update_time"] = datetime.now().strftime('%Y%m%d')

        hotel = HotelModel.query.filter_by(hotel_name=hotel_name).first()
        if hotel:
            for field, value in row_data.items():
                if field != 'hotel_name' and pd.notna(value) and str(value).strip() != '':
                    setattr(hotel, field, value)
        else:
            filtered_data = {
                k: v for k, v in row_data.items() if pd.notna(v) and str(v).strip() != ''
            }
            hotel = HotelModel(**filtered_data)
            db.session.add(hotel)

    db.session.commit()
    return jsonify({"message": "导入完成"})


@hotel_api_bp.route('/export', methods=['GET'])
def export_hotels():
    """
    导出酒店信息为 Excel 文件
    ---
    tags:
      - Hotel
    responses:
      200:
        description: 返回 Excel 文件
        schema:
          type: file
    """
    hotels = HotelModel.query.all()
    if not hotels:
        return jsonify({"error": "无可导出数据"}), 400

    data = []
    for h in hotels:
        data.append({
            "hotel_name": h.hotel_name,
            "business_park": h.business_park,
            "visitor_name": h.visitor_name,
            "actual_people_count": h.actual_people_count,
            "other_carrier": h.other_carrier,
            "key_person_name": h.key_person_name,
            "key_person_phone": h.key_person_phone,
            "competitor_services": h.competitor_services,
            "competitor_price": h.competitor_price,
            "competitor_expiry": h.competitor_expiry,
            "remarks": h.remarks,
            "update_time": h.update_time
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='HotelData')
    output.seek(0)

    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(
        output,
        as_attachment=True,
        download_name=f"hotel_data_{now_str}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )