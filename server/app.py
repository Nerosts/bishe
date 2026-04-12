import os
import io
import socket
import qrcode
import pandas as pd
from datetime import datetime
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
# 自动获取当前电脑局域网 IP
# =====================
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 不需要真的连通，只是借系统路由拿本机出口IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_frontend_base_url():
    return f"http://{get_local_ip()}:5173"


def get_backend_base_url():
    return f"http://{get_local_ip()}:5000"


# =====================
# 首页测试
# =====================
@app.route("/")
def hello():
    return "Flask + MySQL 已连接成功！"


# =====================
# 查看当前自动识别的访问地址
# 方便你调试手机扫码
# =====================
@app.route("/network-info", methods=["GET"])
def network_info():
    return jsonify({
        "local_ip": get_local_ip(),
        "frontend_base_url": get_frontend_base_url(),
        "backend_base_url": get_backend_base_url()
    })


# =====================
# 用户注册
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
# 用户登录
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
            "created_at": event.created_at.strftime("%Y-%m-%d %H:%M:%S") if event.created_at else "",
            "organizer_id": event.organizer_id
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
        "created_at": event.created_at.strftime("%Y-%m-%d %H:%M:%S") if event.created_at else "",
        "organizer_id": event.organizer_id
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

    user_id = data.get("user_id")
    event_id = data.get("event_id")

    if not user_id or not event_id:
        return jsonify({"message": "缺少用户ID或活动ID"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "用户不存在"}), 404

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
# 学生取消报名
# =====================
@app.route("/registrations/<int:registration_id>", methods=["DELETE"])
def cancel_registration(registration_id):
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    registration = Registration.query.get(registration_id)
    if not registration:
        return jsonify({"message": "报名记录不存在"}), 404

    if not user_id:
        return jsonify({"message": "缺少用户ID"}), 400

    if int(registration.user_id) != int(user_id):
        return jsonify({"message": "你无权取消这条报名记录"}), 403

    checkin = Checkin.query.filter_by(
        user_id=registration.user_id,
        event_id=registration.event_id
    ).first()

    if checkin:
        return jsonify({"message": "你已经签到，不能取消报名"}), 400

    db.session.delete(registration)
    db.session.commit()

    return jsonify({"message": "取消报名成功"})


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
# 自动使用当前局域网IP
# =====================
@app.route("/events/<int:event_id>/qrcode", methods=["GET"])
def generate_event_qrcode(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    os.makedirs("static/qrcodes", exist_ok=True)

    checkin_url = f"{get_frontend_base_url()}/checkin?event_id={event_id}"

    qr = qrcode.make(checkin_url)
    filename = f"event_{event_id}_qrcode.png"
    file_path = os.path.join("static", "qrcodes", filename)
    qr.save(file_path)

    return jsonify({
        "message": "二维码生成成功",
        "event_id": event_id,
        "event_title": event.title,
        "qrcode_image_url": f"{get_backend_base_url()}/static/qrcodes/{filename}",
        "checkin_url": checkin_url,
        "current_ip": get_local_ip()
    })


# =====================
# 访问二维码图片
# =====================
@app.route("/static/qrcodes/<path:filename>")
def serve_qrcode(filename):
    return send_from_directory("static/qrcodes", filename)


# =====================
# 兼容旧地址
# =====================
@app.route("/checkin_page", methods=["GET"])
def checkin_page():
    event_id = request.args.get("event_id")
    return f"签到页面兼容地址：event_id={event_id}，请使用前端 /checkin 页面"


# =====================
# 学生签到
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

    if user.role != "student":
        return jsonify({"message": "只有学生账号可以签到"}), 400

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
        "checkin_id": checkin.id,
        "checkin_time": checkin.checkin_time.strftime("%Y-%m-%d %H:%M:%S") if checkin.checkin_time else ""
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
# 图表数据：时段分析
# =====================
@app.route("/charts/time-slots", methods=["GET"])
def chart_time_slots():
    events = Event.query.all()

    hour_counts = [0] * 24
    labels = []

    for i in range(24):
        labels.append(f"{i}:00")

    for event in events:
        if event.start_time:
            hour = event.start_time.hour
            hour_counts[hour] += 1

    return jsonify({
        "labels": labels,
        "counts": hour_counts
    })


# =====================
# 组织者发布活动
# =====================
@app.route("/events", methods=["POST"])
def create_event():
    data = request.get_json()

    if not data:
        return jsonify({"message": "请求体不能为空"}), 400

    title = data.get("title")
    category = data.get("category")
    location = data.get("location")
    start_time = data.get("start_time")
    max_participants = data.get("max_participants")
    description = data.get("description", "")
    organizer_id = data.get("organizer_id")
    status = data.get("status", "报名中")

    if not title or not category or not location or not start_time or not max_participants:
        return jsonify({"message": "缺少必要字段"}), 400

    if not organizer_id:
        return jsonify({"message": "缺少组织者ID"}), 400

    organizer = User.query.get(organizer_id)
    if not organizer or organizer.role != "organizer":
        return jsonify({"message": "组织者不存在或角色错误"}), 400

    try:
        start_time_obj = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"message": "时间格式错误，应为 YYYY-MM-DD HH:MM:SS"}), 400

    new_event = Event(
        title=title,
        category=category,
        location=location,
        start_time=start_time_obj,
        max_participants=int(max_participants),
        description=description,
        status=status,
        organizer_id=int(organizer_id)
    )

    db.session.add(new_event)
    db.session.commit()

    return jsonify({
        "message": "活动发布成功",
        "event_id": new_event.id
    })


# =====================
# 组织者查看自己发布的活动
# =====================
@app.route("/organizer/<int:organizer_id>/events", methods=["GET"])
def get_organizer_events(organizer_id):
    organizer = User.query.get(organizer_id)
    if not organizer:
        return jsonify({"message": "组织者不存在"}), 404

    if organizer.role != "organizer":
        return jsonify({"message": "当前用户不是组织者"}), 400

    events = Event.query.filter_by(organizer_id=organizer_id).order_by(Event.id.desc()).all()

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
            "created_at": event.created_at.strftime("%Y-%m-%d %H:%M:%S") if event.created_at else "",
            "organizer_id": event.organizer_id
        })

    return jsonify(result)


# =====================
# 组织者查看某个自己发布活动的报名名单
# =====================
@app.route("/organizer/<int:organizer_id>/events/<int:event_id>/registrations", methods=["GET"])
def get_organizer_event_registrations(organizer_id, event_id):
    organizer = User.query.get(organizer_id)
    if not organizer:
        return jsonify({"message": "组织者不存在"}), 404

    if organizer.role != "organizer":
        return jsonify({"message": "当前用户不是组织者"}), 400

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    if event.organizer_id != organizer_id:
        return jsonify({"message": "你无权查看这个活动的报名名单"}), 403

    registrations = Registration.query.filter_by(event_id=event_id).order_by(Registration.id.desc()).all()

    result = []
    for item in registrations:
        user = User.query.get(item.user_id)

        result.append({
            "registration_id": item.id,
            "user_id": item.user_id,
            "username": user.username if user else "",
            "event_id": item.event_id,
            "status": item.status,
            "signup_time": item.signup_time.strftime("%Y-%m-%d %H:%M:%S") if item.signup_time else ""
        })

    return jsonify({
        "event_id": event.id,
        "event_title": event.title,
        "event_category": event.category,
        "event_location": event.location,
        "event_start_time": event.start_time.strftime("%Y-%m-%d %H:%M:%S") if event.start_time else "",
        "registrations": result
    })


# =====================
# 组织者删除自己发布的活动
# =====================
@app.route("/organizer/<int:organizer_id>/events/<int:event_id>", methods=["DELETE"])
def delete_organizer_event(organizer_id, event_id):
    organizer = User.query.get(organizer_id)
    if not organizer:
        return jsonify({"message": "组织者不存在"}), 404

    if organizer.role != "organizer":
        return jsonify({"message": "当前用户不是组织者"}), 400

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    if event.organizer_id != organizer_id:
        return jsonify({"message": "你无权删除这个活动"}), 403

    related_registrations = Registration.query.filter_by(event_id=event_id).all()
    for item in related_registrations:
        db.session.delete(item)

    related_checkins = Checkin.query.filter_by(event_id=event_id).all()
    for item in related_checkins:
        db.session.delete(item)

    qrcode_file = os.path.join("static", "qrcodes", f"event_{event_id}_qrcode.png")
    if os.path.exists(qrcode_file):
        os.remove(qrcode_file)

    db.session.delete(event)
    db.session.commit()

    return jsonify({"message": "活动删除成功"})


# =====================
# 组织者编辑自己发布的活动
# =====================
@app.route("/organizer/<int:organizer_id>/events/<int:event_id>", methods=["PUT"])
def update_organizer_event(organizer_id, event_id):
    organizer = User.query.get(organizer_id)
    if not organizer:
        return jsonify({"message": "组织者不存在"}), 404

    if organizer.role != "organizer":
        return jsonify({"message": "当前用户不是组织者"}), 400

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    if event.organizer_id != organizer_id:
        return jsonify({"message": "你无权编辑这个活动"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"message": "请求体不能为空"}), 400

    title = data.get("title")
    category = data.get("category")
    location = data.get("location")
    start_time = data.get("start_time")
    max_participants = data.get("max_participants")
    description = data.get("description", "")
    status = data.get("status", "报名中")

    if not title or not category or not location or not start_time or not max_participants:
        return jsonify({"message": "缺少必要字段"}), 400

    try:
        start_time_obj = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"message": "时间格式错误，应为 YYYY-MM-DD HH:MM:SS"}), 400

    approved_count = Registration.query.filter_by(
        event_id=event.id,
        status="已通过"
    ).count()

    if int(max_participants) < approved_count:
        return jsonify({"message": "人数上限不能小于当前已通过人数"}), 400

    event.title = title
    event.category = category
    event.location = location
    event.start_time = start_time_obj
    event.max_participants = int(max_participants)
    event.description = description
    event.status = status

    db.session.commit()

    return jsonify({"message": "活动修改成功"})


# =====================
# 组织者查看某个自己发布活动的签到情况
# =====================
@app.route("/organizer/<int:organizer_id>/events/<int:event_id>/checkin-stats", methods=["GET"])
def get_organizer_event_checkin_stats(organizer_id, event_id):
    organizer = User.query.get(organizer_id)
    if not organizer:
        return jsonify({"message": "组织者不存在"}), 404

    if organizer.role != "organizer":
        return jsonify({"message": "当前用户不是组织者"}), 400

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    if event.organizer_id != organizer_id:
        return jsonify({"message": "你无权查看这个活动的签到情况"}), 403

    approved_regs = Registration.query.filter_by(
        event_id=event_id,
        status="已通过"
    ).all()

    checked_user_ids = {
        item.user_id for item in Checkin.query.filter_by(event_id=event_id).all()
    }

    checked_list = []
    unchecked_list = []

    for reg in approved_regs:
        user = User.query.get(reg.user_id)

        user_info = {
            "user_id": reg.user_id,
            "username": user.username if user else "",
            "signup_time": reg.signup_time.strftime("%Y-%m-%d %H:%M:%S") if reg.signup_time else ""
        }

        if reg.user_id in checked_user_ids:
            checkin = Checkin.query.filter_by(
                user_id=reg.user_id,
                event_id=event_id
            ).first()

            user_info["checkin_time"] = (
                checkin.checkin_time.strftime("%Y-%m-%d %H:%M:%S")
                if checkin and checkin.checkin_time else ""
            )
            checked_list.append(user_info)
        else:
            unchecked_list.append(user_info)

    return jsonify({
        "event_id": event.id,
        "event_title": event.title,
        "event_category": event.category,
        "event_location": event.location,
        "event_start_time": event.start_time.strftime("%Y-%m-%d %H:%M:%S") if event.start_time else "",
        "approved_count": len(approved_regs),
        "checked_count": len(checked_list),
        "unchecked_count": len(unchecked_list),
        "checked_list": checked_list,
        "unchecked_list": unchecked_list
    })

# =====================
# 启动
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)