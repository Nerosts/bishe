import os
import io
import qrcode
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from config import Config
from extensions import db
from models import User, Event, Registration, Checkin

app = Flask(__name__)
app.config.from_object(Config)
app.config["JSON_AS_ASCII"] = False
app.json.ensure_ascii = False

CORS(app)

db.init_app(app)


# =====================
# 首页测试
# =====================
@app.route("/")
def hello():
    return "Flask + MySQL 已连接成功！"


# =====================
# 第21关：用户注册
# =====================
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"message": "请求体不能为空"}), 400

    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "student")

    if not username or not password:
        return jsonify({"message": "缺少用户名或密码"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "用户名已存在"}), 400

    user = User(
        username=username,
        password=password,
        role=role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "注册成功",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    })


# =====================
# 第21关：用户登录
# =====================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "请求体不能为空"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "缺少用户名或密码"}), 400

    user = User.query.filter_by(username=username, password=password).first()

    if not user:
        return jsonify({"message": "用户名或密码错误"}), 401

    return jsonify({
        "message": "登录成功",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    })


# =====================
# 获取所有活动
# =====================
@app.route("/events", methods=["GET"])
def get_events():
    events = Event.query.all()

    result = []
    for event in events:
        approved_count = Registration.query.filter_by(
            event_id=event.id,
            status="已通过"
        ).count()

        result.append({
            "id": event.id,
            "title": event.title,
            "category": event.category,
            "description": event.description,
            "location": event.location,
            "start_time": event.start_time.strftime("%Y-%m-%d %H:%M:%S") if event.start_time else "",
            "max_participants": event.max_participants,
            "approved_count": approved_count,
            "status": event.status,
            "created_at": event.created_at.strftime("%Y-%m-%d %H:%M:%S") if event.created_at else ""
        })

    return jsonify(result)


# =====================
# 获取单个活动
# =====================
@app.route("/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    event = Event.query.get(event_id)

    if not event:
        return jsonify({"message": "活动不存在"}), 404

    approved_count = Registration.query.filter_by(
        event_id=event.id,
        status="已通过"
    ).count()

    result = {
        "id": event.id,
        "title": event.title,
        "category": event.category,
        "description": event.description,
        "location": event.location,
        "start_time": event.start_time.strftime("%Y-%m-%d %H:%M:%S") if event.start_time else "",
        "max_participants": event.max_participants,
        "approved_count": approved_count,
        "status": event.status,
        "created_at": event.created_at.strftime("%Y-%m-%d %H:%M:%S") if event.created_at else ""
    }

    return jsonify(result)


# =====================
# 报名活动
# =====================
@app.route("/registrations", methods=["POST"])
def create_registration():
    data = request.get_json()

    if not data:
        return jsonify({"message": "请求体不能为空"}), 400

    user_id = data.get("user_id", 1)
    event_id = data.get("event_id")

    if not event_id:
        return jsonify({"message": "缺少活动ID"}), 400

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    existing_registration = Registration.query.filter_by(
        user_id=user_id,
        event_id=event_id
    ).first()

    if existing_registration:
        return jsonify({"message": "你已经报名过该活动"}), 400

    approved_count = Registration.query.filter_by(
        event_id=event_id,
        status="已通过"
    ).count()

    if approved_count >= event.max_participants:
        return jsonify({"message": "活动已满，无法报名"}), 400

    registration = Registration(
        user_id=user_id,
        event_id=event_id,
        status="待审核"
    )

    db.session.add(registration)
    db.session.commit()

    return jsonify({
        "message": "报名成功",
        "registration_id": registration.id
    })


# =====================
# 获取所有报名记录
# =====================
@app.route("/registrations", methods=["GET"])
def get_registrations():
    registrations = Registration.query.all()

    result = []
    for r in registrations:
        result.append({
            "id": r.id,
            "user_id": r.user_id,
            "event_id": r.event_id,
            "status": r.status,
            "signup_time": r.signup_time.strftime("%Y-%m-%d %H:%M:%S") if r.signup_time else ""
        })

    return jsonify(result)


# =====================
# 获取某个用户的报名记录
# =====================
@app.route("/users/<int:user_id>/registrations", methods=["GET"])
def get_user_registrations(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "用户不存在"}), 404

    registrations = Registration.query.filter_by(user_id=user_id).all()

    result = []
    for r in registrations:
        event = Event.query.get(r.event_id)

        result.append({
            "registration_id": r.id,
            "user_id": r.user_id,
            "event_id": r.event_id,
            "event_title": event.title if event else "",
            "event_category": event.category if event else "",
            "event_location": event.location if event else "",
            "event_start_time": event.start_time.strftime("%Y-%m-%d %H:%M:%S") if event and event.start_time else "",
            "status": r.status,
            "signup_time": r.signup_time.strftime("%Y-%m-%d %H:%M:%S") if r.signup_time else ""
        })

    return jsonify(result)


# =====================
# 审核通过
# =====================
@app.route("/registrations/<int:registration_id>/approve", methods=["PUT"])
def approve_registration(registration_id):
    registration = Registration.query.get(registration_id)

    if not registration:
        return jsonify({"message": "报名记录不存在"}), 404

    event = Event.query.get(registration.event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    approved_count = Registration.query.filter_by(
        event_id=registration.event_id,
        status="已通过"
    ).count()

    if registration.status != "已通过" and approved_count >= event.max_participants:
        return jsonify({"message": "活动人数已满，无法审核通过"}), 400

    registration.status = "已通过"
    db.session.commit()

    return jsonify({"message": "审核通过"})


# =====================
# 审核拒绝
# =====================
@app.route("/registrations/<int:registration_id>/reject", methods=["PUT"])
def reject_registration(registration_id):
    registration = Registration.query.get(registration_id)

    if not registration:
        return jsonify({"message": "报名记录不存在"}), 404

    registration.status = "已拒绝"
    db.session.commit()

    return jsonify({"message": "已拒绝"})


# =====================
# 生成活动签到二维码
# =====================
@app.route("/events/<int:event_id>/qrcode", methods=["GET"])
def generate_event_qrcode(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    os.makedirs("static/qrcodes", exist_ok=True)

    checkin_url = f"http://127.0.0.1:5000/checkin_page?event_id={event_id}&user_id=1"

    qr = qrcode.make(checkin_url)
    filename = f"event_{event_id}_qrcode.png"
    file_path = os.path.join("static", "qrcodes", filename)
    qr.save(file_path)

    return jsonify({
        "message": "二维码生成成功",
        "event_id": event_id,
        "qrcode_image_url": f"http://127.0.0.1:5000/static/qrcodes/{filename}",
        "checkin_url": checkin_url
    })


# =====================
# 访问二维码图片
# =====================
@app.route("/static/qrcodes/<path:filename>")
def serve_qrcode(filename):
    return send_from_directory("static/qrcodes", filename)


# =====================
# 模拟扫码后打开的签到页面
# =====================
@app.route("/checkin_page", methods=["GET"])
def checkin_page():
    event_id = request.args.get("event_id")
    user_id = request.args.get("user_id")

    return f"签到页面：event_id={event_id}, user_id={user_id}，后续可接前端页面"


# =====================
# 执行签到
# =====================
@app.route("/checkin", methods=["POST"])
def do_checkin():
    data = request.get_json()

    if not data:
        return jsonify({"message": "请求体不能为空"}), 400

    user_id = data.get("user_id")
    event_id = data.get("event_id")

    if not user_id or not event_id:
        return jsonify({"message": "缺少 user_id 或 event_id"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "用户不存在"}), 404

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    registration = Registration.query.filter_by(
        user_id=user_id,
        event_id=event_id,
        status="已通过"
    ).first()

    if not registration:
        return jsonify({"message": "你未通过审核，不能签到"}), 400

    existing_checkin = Checkin.query.filter_by(
        user_id=user_id,
        event_id=event_id
    ).first()

    if existing_checkin:
        return jsonify({"message": "你已经签到过了"}), 400

    checkin = Checkin(
        user_id=user_id,
        event_id=event_id
    )

    db.session.add(checkin)
    db.session.commit()

    return jsonify({
        "message": "签到成功",
        "checkin_id": checkin.id
    })


# =====================
# 查询所有签到记录
# =====================
@app.route("/checkins", methods=["GET"])
def get_checkins():
    checkins = Checkin.query.all()

    result = []
    for c in checkins:
        result.append({
            "id": c.id,
            "user_id": c.user_id,
            "event_id": c.event_id,
            "checkin_time": c.checkin_time.strftime("%Y-%m-%d %H:%M:%S") if c.checkin_time else ""
        })

    return jsonify(result)


# =====================
# 单个活动统计
# =====================
@app.route("/events/<int:event_id>/stats", methods=["GET"])
def get_event_stats(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    approved_count = Registration.query.filter_by(
        event_id=event_id,
        status="已通过"
    ).count()

    checkin_count = Checkin.query.filter_by(
        event_id=event_id
    ).count()

    if approved_count == 0:
        attendance_rate = "0%"
    else:
        attendance_rate = f"{round(checkin_count / approved_count * 100, 2)}%"

    return jsonify({
        "event_id": event.id,
        "title": event.title,
        "approved_count": approved_count,
        "checkin_count": checkin_count,
        "attendance_rate": attendance_rate
    })


# =====================
# 活动热度排行
# =====================
@app.route("/events/hot", methods=["GET"])
def get_hot_events():
    events = Event.query.all()

    result = []
    for event in events:
        registration_count = Registration.query.filter_by(event_id=event.id).count()
        checkin_count = Checkin.query.filter_by(event_id=event.id).count()
        heat = registration_count + checkin_count

        result.append({
            "event_id": event.id,
            "title": event.title,
            "registration_count": registration_count,
            "checkin_count": checkin_count,
            "heat": heat
        })

    result.sort(key=lambda x: x["heat"], reverse=True)

    return jsonify(result)


# =====================
# 导出活动报名名单 Excel
# =====================
@app.route("/events/<int:event_id>/export", methods=["GET"])
def export_event_registrations(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    registrations = Registration.query.filter_by(event_id=event_id).all()

    data = []
    for r in registrations:
        data.append({
            "用户ID": r.user_id,
            "活动ID": r.event_id,
            "状态": r.status,
            "报名时间": r.signup_time.strftime("%Y-%m-%d %H:%M:%S") if r.signup_time else ""
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=f"event_{event_id}_registrations.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =====================
# 图表数据：报名人数
# =====================
@app.route("/charts/registrations", methods=["GET"])
def chart_registrations():
    events = Event.query.all()

    titles = []
    registration_counts = []

    for event in events:
        count = Registration.query.filter_by(event_id=event.id).count()
        titles.append(event.title)
        registration_counts.append(count)

    return jsonify({
        "titles": titles,
        "registration_counts": registration_counts
    })


# =====================
# 图表数据：签到率
# =====================
@app.route("/charts/attendance", methods=["GET"])
def chart_attendance():
    events = Event.query.all()

    titles = []
    attendance_rates = []

    for event in events:
        approved_count = Registration.query.filter_by(
            event_id=event.id,
            status="已通过"
        ).count()

        checkin_count = Checkin.query.filter_by(
            event_id=event.id
        ).count()

        if approved_count == 0:
            rate = 0
        else:
            rate = round(checkin_count / approved_count * 100, 2)

        titles.append(event.title)
        attendance_rates.append(rate)

    return jsonify({
        "titles": titles,
        "attendance_rates": attendance_rates
    })


# =====================
# 图表数据：热度
# =====================
@app.route("/charts/hot", methods=["GET"])
def chart_hot():
    events = Event.query.all()

    titles = []
    heats = []

    sorted_events = []
    for event in events:
        registration_count = Registration.query.filter_by(event_id=event.id).count()
        checkin_count = Checkin.query.filter_by(event_id=event.id).count()
        heat = registration_count + checkin_count

        sorted_events.append({
            "title": event.title,
            "heat": heat
        })

    sorted_events.sort(key=lambda x: x["heat"], reverse=True)

    for item in sorted_events:
        titles.append(item["title"])
        heats.append(item["heat"])

    return jsonify({
        "titles": titles,
        "heats": heats
    })


# =====================
# 启动
# =====================
if __name__ == "__main__":
    app.run(debug=True)