from flask import Blueprint, request, jsonify, send_file
from exts import db
from blueprint.chain_store import ChainStoreModel, ChainBandModel
import pandas as pd
import io
from datetime import datetime

chain_store_api_bp = Blueprint('chain_store_api', __name__, url_prefix='/api/chain_store')


@chain_store_api_bp.route('/list', methods=['GET'])
def list_chain_stores():
    """
    获取门店列表（分页）
    ---
    tags:
      - ChainStore
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
        description: 分页门店数据
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = ChainStoreModel.query.paginate(page=page, per_page=per_page, error_out=False)
    stores = pagination.items

    data = []
    for s in stores:
        data.append({
            "id": s.id,
            "chain_store_name": s.chain_store_name,
            "chain_band": s.chain_band,
            "actual_people_count": s.actual_people_count,
            "other_carrier": s.other_carrier,
            "key_person_name": s.key_person_name,
            "key_person_phone": s.key_person_phone,
            "competitor_services": s.competitor_services,
            "competitor_price": s.competitor_price,
            "competitor_expiry": s.competitor_expiry,
            "visitor_name": s.visitor_name,
            "remarks": s.remarks,
            "update_time": s.update_time
        })
    return jsonify({
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "data": data
    })


@chain_store_api_bp.route('/add', methods=['POST'])
def add_chain_store():
    """
    添加门店
    ---
    tags:
      - ChainStore
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - chain_store_name
          properties:
            chain_store_name:
              type: string
            chain_band:
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
    responses:
      200:
        description: 添加成功
    """
    data = request.get_json()
    store = ChainStoreModel(**data)
    db.session.add(store)
    db.session.commit()
    return jsonify({"message": "新增成功", "id": store.id})


@chain_store_api_bp.route('/<int:id>', methods=['PUT'])
def update_chain_store(id):
    """
    更新门店信息
    ---
    tags:
      - ChainStore
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
            chain_store_name:
              type: string
            chain_band:
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
    responses:
      200:
        description: 更新成功
    """
    data = request.get_json()
    store = ChainStoreModel.query.get(id)
    if not store:
        return jsonify({"error": "门店不存在"}), 404
    for key in data:
        if hasattr(store, key):
            setattr(store, key, data[key])
    db.session.commit()
    return jsonify({"message": "更新成功"})


@chain_store_api_bp.route('/<int:id>', methods=['DELETE'])
def delete_chain_store(id):
    """
    删除门店
    ---
    tags:
      - ChainStore
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: 删除成功
    """
    store = ChainStoreModel.query.get(id)
    if not store:
        return jsonify({"error": "门店不存在"}), 404
    db.session.delete(store)
    db.session.commit()
    return jsonify({"message": "删除成功"})


@chain_store_api_bp.route('/import', methods=['POST'])
def import_chain_stores():
    """
    批量导入门店信息（Excel）
    ---
    tags:
      - ChainStore
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: 包含门店数据的 Excel 文件（.xlsx）
    responses:
      200:
        description: 导入结果
    """
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "未上传文件"}), 400

    try:
        df = pd.read_excel(file, dtype=str)
    except Exception as e:
        return jsonify({"error": "无法读取Excel文件，请确认格式"}), 400

    expected_fields = [
        "chain_store_name", "chain_band", "visitor_name", "actual_people_count",
        "other_carrier", "key_person_name", "key_person_phone",
        "competitor_services", "competitor_price", "competitor_expiry",
        "remarks", "update_time"
    ]

    if list(df.columns[:len(expected_fields)]) != expected_fields:
        return jsonify({"error": "Excel表头不符合预期"}), 400

    for _, row in df.iterrows():
        row_data = row.to_dict()
        name = row_data.get("chain_store_name")
        if not name or pd.isna(name):
            continue
        if pd.isna(row_data.get("update_time")) or not str(row_data.get("update_time")).strip():
            row_data["update_time"] = datetime.now().strftime('%Y%m%d')
        store = ChainStoreModel.query.filter_by(chain_store_name=name).first()
        if store:
            for field, value in row_data.items():
                if field != 'chain_store_name' and pd.notna(value) and str(value).strip() != '':
                    setattr(store, field, value)
        else:
            filtered_data = {k: v for k, v in row_data.items() if pd.notna(v) and str(v).strip() != ''}
            store = ChainStoreModel(**filtered_data)
            db.session.add(store)

    db.session.commit()
    return jsonify({"message": "导入完成"})


@chain_store_api_bp.route('/export', methods=['GET'])
def export_chain_stores():
    """
    导出连锁品牌门店为 Excel 文件
    ---
    tags:
      - ChainStore
    responses:
      200:
        description: 下载 Excel 文件
        schema:
          type: file
    """
    bs_list = ChainBandModel.query.all()
    if not bs_list:
        return jsonify({"error": "没有设置连锁企业"}), 400

    output_data = []
    for bs in bs_list:
        store_detail = ChainStoreModel.query.filter_by(chain_store_name=bs.store).first()
        row_dict = {
            'band': bs.band,
            'store': bs.store
        }
        if store_detail:
            row_dict.update({
                'actual_people_count': store_detail.actual_people_count,
                'other_carrier': store_detail.other_carrier,
                'key_person_name': store_detail.key_person_name,
                'key_person_phone': store_detail.key_person_phone,
                'competitor_services': store_detail.competitor_services,
                'competitor_price': store_detail.competitor_price,
                'competitor_expiry': store_detail.competitor_expiry,
                'visitor_name': store_detail.visitor_name,
                'remarks': store_detail.remarks,
                'update_time': store_detail.update_time
            })
        else:
            row_dict.update({
                'actual_people_count': '', 'other_carrier': '', 'key_person_name': '',
                'key_person_phone': '', 'competitor_services': '', 'competitor_price': '',
                'competitor_expiry': '', 'visitor_name': '', 'remarks': '', 'update_time': ''
            })
        output_data.append(row_dict)

    df = pd.DataFrame(output_data)
    df.rename(columns={
        "band": "连锁品牌名称", "store": "连锁商铺名称",
        "actual_people_count": "单位实际人数", "other_carrier": "异网运营商",
        "key_person_name": "关键人姓名", "key_person_phone": "关键人电话",
        "competitor_services": "友商已有业务", "competitor_price": "友商合同价格",
        "competitor_expiry": "友商产品到期时间", "visitor_name": "拜访人",
        "remarks": "备注", "update_time": "更新时间"
    }, inplace=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='连锁品牌商铺导出')
    output.seek(0)

    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(
        output,
        as_attachment=True,
        download_name=f"连锁品牌商铺导出_{now_str}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )