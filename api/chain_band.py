from flask import Blueprint, request, jsonify, send_file
from exts import db
from blueprint.chain_band import ChainBandModel
import pandas as pd
import io
from datetime import datetime

chain_band_api_bp = Blueprint('chain_band_api', __name__, url_prefix='/api/chain_band')


@chain_band_api_bp.route('/list', methods=['GET'])
def list_chain_bands():
    """
    获取连锁品牌列表
    ---
    tags:
      - ChainBand
    responses:
      200:
        description: 返回品牌数据列表
    """
    bands = ChainBandModel.query.all()
    data = [
        {
            "id": b.id,
            "band": b.band,
            "area": b.area,
            "store": b.store,
            "remark": b.remark
        } for b in bands
    ]
    return jsonify(data)


@chain_band_api_bp.route('/add', methods=['POST'])
def add_chain_band():
    """
    添加连锁品牌记录
    ---
    tags:
      - ChainBand
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            band:
              type: string
            area:
              type: string
            store:
              type: string
            remark:
              type: string
    responses:
      200:
        description: 添加成功
    """
    data = request.get_json()
    band = ChainBandModel(**data)
    db.session.add(band)
    db.session.commit()
    return jsonify({"message": "新增成功", "id": band.id})


@chain_band_api_bp.route('/<int:id>', methods=['PUT'])
def update_chain_band(id):
    """
    更新品牌信息
    ---
    tags:
      - ChainBand
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
            band:
              type: string
            area:
              type: string
            store:
              type: string
            remark:
              type: string
    responses:
      200:
        description: 更新成功
    """
    data = request.get_json()
    band = ChainBandModel.query.get(id)
    if not band:
        return jsonify({"error": "记录不存在"}), 404

    for key in data:
        if hasattr(band, key):
            setattr(band, key, data[key])
    db.session.commit()
    return jsonify({"message": "更新成功"})


@chain_band_api_bp.route('/<int:id>', methods=['DELETE'])
def delete_chain_band(id):
    """
    删除品牌记录
    ---
    tags:
      - ChainBand
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: 删除成功
    """
    band = ChainBandModel.query.get(id)
    if not band:
        return jsonify({"error": "记录不存在"}), 404
    db.session.delete(band)
    db.session.commit()
    return jsonify({"message": "删除成功"})


@chain_band_api_bp.route('/import', methods=['POST'])
def import_chain_band():
    """
    导入品牌信息（Excel）
    ---
    tags:
      - ChainBand
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: 包含品牌数据的 Excel 文件（.xlsx）
    responses:
      200:
        description: 导入结果
        schema:
          type: object
          properties:
            message:
              type: string
    """
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "未上传文件"}), 400

    try:
        df = pd.read_excel(file, dtype=str)
    except Exception as e:
        return jsonify({"error": "无法读取Excel文件，请确认格式"}), 400

    expected_fields = ["band", "area", "store", "remark"]
    if list(df.columns[:len(expected_fields)]) != expected_fields:
        return jsonify({"error": "Excel表头不符合预期"}), 400

    for _, row in df.iterrows():
        row_data = row.to_dict()
        band_name = row_data.get("band")
        if not band_name or pd.isna(band_name):
            continue
        filtered_data = {
            k: v for k, v in row_data.items() if pd.notna(v) and str(v).strip() != ''
        }
        band = ChainBandModel(**filtered_data)
        db.session.add(band)

    db.session.commit()
    return jsonify({"message": "导入完成"})


@chain_band_api_bp.route('/export', methods=['GET'])
def export_chain_band():
    """
    导出品牌信息为 Excel 文件
    ---
    tags:
      - ChainBand
    responses:
      200:
        description: 下载 Excel 文件
        schema:
          type: file
    """
    bands = ChainBandModel.query.all()
    if not bands:
        return jsonify({"error": "无可导出数据"}), 400

    data = [
        {
            "band": b.band,
            "area": b.area,
            "store": b.store,
            "remark": b.remark
        } for b in bands
    ]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='ChainBands')
    output.seek(0)

    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(
        output,
        as_attachment=True,
        download_name=f"chain_band_data_{now_str}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )