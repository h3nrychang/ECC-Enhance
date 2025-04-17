from flask import Blueprint, request, jsonify, send_file
from exts import db
from blueprint.company import CompanyModel, BusinessParkModel
from datetime import datetime
import pandas as pd
import io

company_api_bp = Blueprint('company_api', __name__, url_prefix='/api/company')

@company_api_bp.route('/list', methods=['GET'])
def list_companies():
    """
    获取企业分页列表
    ---
    tags:
      - Company
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
        description: 企业列表数据
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = CompanyModel.query.paginate(page=page, per_page=per_page, error_out=False)
    companies = pagination.items

    data = []
    for c in companies:
        data.append({
            "id": c.id,
            "company_name": c.company_name,
            "actual_people_count": c.actual_people_count,
            "other_carrier": c.other_carrier,
            "key_person_name": c.key_person_name,
            "key_person_phone": c.key_person_phone,
            "competitor_services": c.competitor_services,
            "competitor_price": c.competitor_price,
            "competitor_expiry": c.competitor_expiry,
            "visitor_name": c.visitor_name,
            "remarks": c.remarks,
            "update_time": c.update_time,
            "business_park": c.business_park
        })

    return jsonify({
        "data": data,
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    })


@company_api_bp.route('/add', methods=['POST'])
def add_company():
    """
    添加企业信息
    ---
    tags:
      - Company
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - company_name
          properties:
            company_name:
              type: string
              description: 企业名称
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
        description: 成功添加企业
        schema:
          type: object
          properties:
            message:
              type: string
            id:
              type: integer
    """
    data = request.get_json()
    company = CompanyModel(**data)
    db.session.add(company)
    db.session.commit()
    return jsonify({"message": "新增成功", "id": company.id})


@company_api_bp.route('/<int:id>', methods=['PUT'])
def update_company(id):
    """
    更新企业信息
    ---
    tags:
      - Company
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
            company_name:
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
        description: 成功更新企业信息
    """
    data = request.get_json()
    company = CompanyModel.query.get(id)
    if not company:
        return jsonify({"error": "公司不存在"}), 404

    for key in data:
        if hasattr(company, key):
            setattr(company, key, data[key])
    db.session.commit()
    return jsonify({"message": "更新成功"})


@company_api_bp.route('/<int:id>', methods=['DELETE'])
def delete_company(id):
    """
    删除企业信息
    ---
    tags:
      - Company
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: 成功删除企业
    """
    company = CompanyModel.query.get(id)
    if not company:
        return jsonify({"error": "公司不存在"}), 404
    db.session.delete(company)
    db.session.commit()
    return jsonify({"message": "删除成功"})


@company_api_bp.route('/import', methods=['POST'])
def import_companies():
    """
    批量导入企业信息（Excel）
    ---
    tags:
      - Company
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: 包含企业数据的 Excel 文件（.xlsx）
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

    expected_fields = [
        "company_name", "visitor_name", "actual_people_count",
        "other_carrier", "key_person_name", "key_person_phone",
        "competitor_services", "competitor_price", "competitor_expiry",
        "remarks", "update_time"
    ]

    if list(df.columns[:len(expected_fields)]) != expected_fields:
        return jsonify({"error": "Excel表头不符合预期"}), 400

    for _, row in df.iterrows():
        row_data = row.to_dict()
        company_name = row_data.get("company_name")
        if not company_name or pd.isna(company_name):
            continue

        if pd.isna(row_data.get("update_time")) or not str(row_data.get("update_time")).strip():
            row_data["update_time"] = datetime.now().strftime('%Y%m%d')

        company = CompanyModel.query.filter_by(company_name=company_name).first()
        if company:
            for field, value in row_data.items():
                if field != 'company_name' and pd.notna(value) and str(value).strip() != '':
                    setattr(company, field, value)
        else:
            filtered_data = {
                k: v for k, v in row_data.items() if pd.notna(v) and str(v).strip() != ''
            }
            company = CompanyModel(**filtered_data)
            db.session.add(company)

    db.session.commit()
    return jsonify({"message": "导入完成"})


@company_api_bp.route('/export', methods=['GET'])
def export_park_company():
    """
    导出楼园-企业详细信息为 Excel
    ---
    tags:
      - Company
    responses:
      200:
        description: 返回 Excel 文件
        schema:
          type: file
    """
    pc_list = BusinessParkModel.query.all()
    if not pc_list:
        return jsonify({"error": "没有楼园数据"}), 400

    output_data = []
    for pc in pc_list:
        company_detail = CompanyModel.query.filter_by(company_name=pc.company_name).first()
        row_dict = {
            'name': pc.name,
            'company_name': pc.company_name
        }
        if company_detail:
            row_dict.update({
                'actual_people_count': company_detail.actual_people_count,
                'other_carrier': company_detail.other_carrier,
                'key_person_name': company_detail.key_person_name,
                'key_person_phone': company_detail.key_person_phone,
                'competitor_services': company_detail.competitor_services,
                'competitor_price': company_detail.competitor_price,
                'competitor_expiry': company_detail.competitor_expiry,
                'visitor_name': company_detail.visitor_name,
                'remarks': company_detail.remarks,
                'update_time': company_detail.update_time
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
        "name": "楼园名称", "company_name": "企业名称", "actual_people_count": "单位实际人数",
        "other_carrier": "异网运营商", "key_person_name": "关键人姓名", "key_person_phone": "关键人电话",
        "competitor_services": "友商已有业务", "competitor_price": "友商合同价格",
        "competitor_expiry": "友商产品到期时间", "visitor_name": "拜访人", "remarks": "备注",
        "update_time": "更新时间"
    }, inplace=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='楼园企业导出')
    output.seek(0)

    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(
        output,
        as_attachment=True,
        download_name=f"楼园企业导出_{now_str}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
