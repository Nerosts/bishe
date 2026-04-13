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
# 工具函数
# =====================
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
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


def calc_event_status(event):
    if event.start_time and event.start_time < datetime.now():
        return "已结束"
    return event.status if event.status else "报名中"


def get_request_user_id():
    user_id = request.args.get("user_id")

    if not user_id:
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")

    if not user_id:
        user_id = request.headers.get("X-User-Id")

    return user_id


def check_role(required_role):
    user_id = get_request_user_id()

    if not user_id:
        return False, None, (jsonify({"message": "缺少 user_id"}), 403)

    user = User.query.get(user_id)
    if not user:
        return False, None, (jsonify({"message": "用户不存在"}), 404)

    if user.role != required_role:
        return False, None, (jsonify({"message": f"权限不足，需要 {required_role} 角色"}), 403)

    return True, user, None


def check_student():
    user_id = get_request_user_id()

    if not user_id:
        return False, None, (jsonify({"message": "缺少 user_id"}), 403)

    user = User.query.get(user_id)
    if not user:
        return False, None, (jsonify({"message": "用户不存在"}), 404)

    if user.role != "student":
        return False, None, (jsonify({"message": "只有 student 可以执行该操作"}), 403)

    return True, user, None


def check_organizer_access(route_organizer_id):
    user_id = get_request_user_id()

    if not user_id:
        return False, None, (jsonify({"message": "缺少 user_id"}), 403)

    current_user = User.query.get(user_id)
    if not current_user:
        return False, None, (jsonify({"message": "用户不存在"}), 404)

    if current_user.role != "organizer":
        return False, None, (jsonify({"message": "只有 organizer 可以访问该接口"}), 403)

    if int(current_user.id) != int(route_organizer_id):
        return False, None, (jsonify({"message": "你无权访问其他组织者的数据"}), 403)

    return True, current_user, None


def approve_registration_logic(registration_id):
    registration = Registration.query.get(registration_id)
    if not registration:
        return jsonify({"message": "报名记录不存在"}), 404

    event = Event.query.get(registration.event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    real_status = calc_event_status(event)
    if real_status == "已结束":
        return jsonify({"message": "活动已结束，不能再审核通过"}), 400

    approved_count = Registration.query.filter_by(
        event_id=registration.event_id,
        status="已通过"
    ).count()

    if registration.status != "已通过" and approved_count >= event.max_participants:
        return jsonify({"message": "活动人数已满，无法审核通过"}), 400

    registration.status = "已通过"
    db.session.commit()

    return jsonify({"message": "审核通过"})


def reject_registration_logic(registration_id):
    registration = Registration.query.get(registration_id)
    if not registration:
        return jsonify({"message": "报名记录不存在"}), 404

    registration.status = "已拒绝"
    db.session.commit()

    return jsonify({"message": "审核拒绝"})


# =====================
# 基础接口
# =====================
@app.route("/")
def hello():
    return "Flask + MySQL 已连接成功！"


@app.route("/network-info", methods=["GET"])
def network_info():
    return jsonify({
        "local_ip": get_local_ip(),
        "frontend_base_url": get_frontend_base_url(),
        "backend_base_url": get_backend_base_url()
    })


# =====================
# 用户模块
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


@app.route("/admin/create_user", methods=["POST"])
def admin_create_user():
    ok, user, error_response = check_role("admin")
    if not ok:
        return error_response

    data = request.get_json()

    if not data:
        return jsonify({"message": "请求体不能为空"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "").strip()

    if not username or not password or not role:
        return jsonify({"message": "用户名、密码、角色不能为空"}), 400

    if role not in ["student", "organizer", "admin"]:
        return jsonify({"message": "角色不合法"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "用户名已存在"}), 400

    new_user = User(
        username=username,
        password=password,
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "创建用户成功",
        "user_id": new_user.id,
        "username": new_user.username,
        "role": new_user.role
    })


@app.route("/admin/batch_create_users", methods=["POST"])
def admin_batch_create_users():
    ok, user, error_response = check_role("admin")
    if not ok:
        return error_response

    data = request.get_json()

    if not data:
        return jsonify({"message": "请求体不能为空"}), 400

    usernames_text = data.get("usernames_text", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "").strip()

    if not usernames_text:
        return jsonify({"message": "请输入批量用户名"}), 400

    if not password:
        return jsonify({"message": "请输入统一密码"}), 400

    if role not in ["student", "organizer", "admin"]:
        return jsonify({"message": "角色不合法"}), 400

    raw_lines = usernames_text.splitlines()
    username_list = []

    for line in raw_lines:
        item = line.strip()
        if item:
            username_list.append(item)

    if len(username_list) == 0:
        return jsonify({"message": "没有有效用户名"}), 400

    success_users = []
    duplicate_users = []
    invalid_users = []

    for username in username_list:
        if " " in username:
            invalid_users.append(username)
            continue

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            duplicate_users.append(username)
            continue

        new_user = User(
            username=username,
            password=password,
            role=role
        )
        db.session.add(new_user)
        success_users.append(username)

    db.session.commit()

    return jsonify({
        "message": "批量创建完成",
        "success_count": len(success_users),
        "duplicate_count": len(duplicate_users),
        "invalid_count": len(invalid_users),
        "success_users": success_users,
        "duplicate_users": duplicate_users,
        "invalid_users": invalid_users
    })


@app.route("/admin/users", methods=["GET"])
def get_admin_users():
    ok, user, error_response = check_role("admin")
    if not ok:
        return error_response

    username = request.args.get("username", "").strip()
    role = request.args.get("role", "").strip()

    query = User.query

    if username:
        query = query.filter(User.username.like(f"%{username}%"))

    if role:
        query = query.filter(User.role == role)

    users = query.order_by(User.id.asc()).all()

    result = []
    for user_item in users:
        result.append({
            "id": user_item.id,
            "username": user_item.username,
            "role": user_item.role,
            "created_at": user_item.created_at.strftime("%Y-%m-%d %H:%M:%S") if user_item.created_at else ""
        })

    return jsonify(result)


@app.route("/admin/users/<int:user_id>", methods=["DELETE"])
def delete_admin_user(user_id):
    ok, current_user, error_response = check_role("admin")
    if not ok:
        return error_response

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "用户不存在"}), 404

    if user.role == "admin":
        return jsonify({"message": "不能删除管理员账号"}), 400

    if str(user.id) == str(current_user.id):
        return jsonify({"message": "不能删除当前登录账号"}), 400

    related_registrations = Registration.query.filter_by(user_id=user.id).all()
    for item in related_registrations:
        db.session.delete(item)

    related_checkins = Checkin.query.filter_by(user_id=user.id).all()
    for item in related_checkins:
        db.session.delete(item)

    if user.role == "organizer":
        organizer_events = Event.query.filter_by(organizer_id=user.id).all()
        for event in organizer_events:
            event_regs = Registration.query.filter_by(event_id=event.id).all()
            for item in event_regs:
                db.session.delete(item)

            event_checks = Checkin.query.filter_by(event_id=event.id).all()
            for item in event_checks:
                db.session.delete(item)

            qrcode_file = os.path.join("static", "qrcodes", f"event_{event.id}_qrcode.png")
            if os.path.exists(qrcode_file):
                os.remove(qrcode_file)

            db.session.delete(event)

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "用户删除成功"})


# =====================
# 活动模块
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
            "status": calc_event_status(event),
            "created_at": event.created_at.strftime("%Y-%m-%d %H:%M:%S") if event.created_at else "",
            "organizer_id": event.organizer_id
        })

    return jsonify(result)


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
        "status": calc_event_status(event),
        "created_at": event.created_at.strftime("%Y-%m-%d %H:%M:%S") if event.created_at else "",
        "organizer_id": event.organizer_id
    }

    return jsonify(result)


@app.route("/events", methods=["POST"])
def create_event():
    ok, current_user, error_response = check_role("organizer")
    if not ok:
        return error_response

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

    if int(organizer_id) != int(current_user.id):
        return jsonify({"message": "你不能冒用其他组织者身份发布活动"}), 403

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
# 报名模块
# =====================
@app.route("/registrations", methods=["POST"])
def create_registration():
    ok, current_user, error_response = check_student()
    if not ok:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({"message": "请求体不能为空"}), 400

    event_id = data.get("event_id")
    user_id = current_user.id

    if not event_id:
        return jsonify({"message": "缺少活动ID"}), 400

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    real_status = calc_event_status(event)
    if real_status == "已结束":
        return jsonify({"message": "活动已结束，无法报名"}), 400

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


@app.route("/users/<int:user_id>/registrations", methods=["GET"])
def get_user_registrations(user_id):
    ok, current_user, error_response = check_student()
    if not ok:
        return error_response

    if int(user_id) != int(current_user.id):
        return jsonify({"message": "不能查看其他用户的报名"}), 403

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


@app.route("/registrations/<int:registration_id>", methods=["DELETE"])
def cancel_registration(registration_id):
    ok, current_user, error_response = check_student()
    if not ok:
        return error_response

    registration = Registration.query.get(registration_id)
    if not registration:
        return jsonify({"message": "报名记录不存在"}), 404

    if int(registration.user_id) != int(current_user.id):
        return jsonify({"message": "你只能取消自己的报名"}), 403

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
# 管理员审核模块（第56关优化）
# =====================
@app.route("/admin/review", methods=["GET"])
def admin_review_list():
    ok, user, error_response = check_role("admin")
    if not ok:
        return error_response

    view_type = request.args.get("view", "pending").strip()
    status_filter = request.args.get("status", "").strip()

    query = Registration.query

    if view_type == "pending":
        query = query.filter_by(status="待审核")
    elif view_type == "history":
        query = query.filter(Registration.status.in_(["已通过", "已拒绝"]))
        if status_filter in ["已通过", "已拒绝"]:
            query = query.filter_by(status=status_filter)

    registrations = query.order_by(Registration.id.desc()).all()

    result = []
    for item in registrations:
        student = User.query.get(item.user_id)
        event = Event.query.get(item.event_id)

        result.append({
            "registration_id": item.id,
            "user_id": item.user_id,
            "username": student.username if student else "未知用户",
            "event_id": item.event_id,
            "event_title": event.title if event else "未知活动",
            "status": item.status,
            "register_time": item.signup_time.strftime("%Y-%m-%d %H:%M:%S") if item.signup_time else ""
        })

    return jsonify(result)


@app.route("/admin/review/<int:registration_id>/approve", methods=["POST"])
def admin_review_approve(registration_id):
    ok, user, error_response = check_role("admin")
    if not ok:
        return error_response
    return approve_registration_logic(registration_id)


@app.route("/admin/review/<int:registration_id>/reject", methods=["POST"])
def admin_review_reject(registration_id):
    ok, user, error_response = check_role("admin")
    if not ok:
        return error_response
    return reject_registration_logic(registration_id)


# 兼容旧接口，防止你前端还有旧调用
@app.route("/registrations/<int:registration_id>/approve", methods=["PUT"])
def approve_registration(registration_id):
    ok, user, error_response = check_role("admin")
    if not ok:
        return error_response
    return approve_registration_logic(registration_id)


@app.route("/registrations/<int:registration_id>/reject", methods=["PUT"])
def reject_registration(registration_id):
    ok, user, error_response = check_role("admin")
    if not ok:
        return error_response
    return reject_registration_logic(registration_id)


# =====================
# 二维码签到模块
# =====================
@app.route("/events/<int:event_id>/qrcode", methods=["GET"])
def generate_event_qrcode(event_id):
    ok, current_user, error_response = check_role("organizer")
    if not ok:
        return error_response

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    if int(event.organizer_id) != int(current_user.id):
        return jsonify({"message": "你无权查看其他组织者活动的二维码"}), 403

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


@app.route("/static/qrcodes/<path:filename>")
def serve_qrcode(filename):
    return send_from_directory("static/qrcodes", filename)


@app.route("/checkin_page", methods=["GET"])
def checkin_page():
    event_id = request.args.get("event_id")
    return f"签到页面兼容地址：event_id={event_id}，请使用前端 /checkin 页面"


@app.route("/checkin", methods=["POST"])
def do_checkin():
    ok, current_user, error_response = check_student()
    if not ok:
        return error_response

    data = request.get_json()

    if not data:
        return jsonify({"message": "请求体不能为空"}), 400

    event_id = data.get("event_id")
    user_id = current_user.id

    if not event_id:
        return jsonify({"message": "缺少 event_id"}), 400

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
# 管理员签到记录
# =====================
@app.route("/admin/checkins", methods=["GET"])
def get_admin_checkins():
    ok, user, error_response = check_role("admin")
    if not ok:
        return error_response

    username = request.args.get("username", "").strip()
    event_id = request.args.get("event_id", "").strip()

    query = db.session.query(Checkin, User, Event).join(
        User, Checkin.user_id == User.id
    ).join(
        Event, Checkin.event_id == Event.id
    )

    if username:
        query = query.filter(User.username.like(f"%{username}%"))

    if event_id:
        try:
            query = query.filter(Checkin.event_id == int(event_id))
        except ValueError:
            return jsonify({"message": "活动ID格式错误"}), 400

    rows = query.order_by(Checkin.id.desc()).all()

    result = []
    for checkin, user_item, event in rows:
        result.append({
            "checkin_id": checkin.id,
            "user_id": user_item.id,
            "username": user_item.username,
            "event_id": event.id,
            "event_title": event.title,
            "checkin_time": checkin.checkin_time.strftime("%Y-%m-%d %H:%M:%S") if checkin.checkin_time else ""
        })

    all_events = Event.query.order_by(Event.id.asc()).all()
    event_options = []
    for e in all_events:
        event_options.append({
            "id": e.id,
            "title": e.title
        })

    return jsonify({
        "checkins": result,
        "events": event_options
    })


@app.route("/admin/checkins/export", methods=["GET"])
def export_admin_checkins():
    ok, user, error_response = check_role("admin")
    if not ok:
        return error_response

    username = request.args.get("username", "").strip()
    event_id = request.args.get("event_id", "").strip()

    query = db.session.query(Checkin, User, Event).join(
        User, Checkin.user_id == User.id
    ).join(
        Event, Checkin.event_id == Event.id
    )

    if username:
        query = query.filter(User.username.like(f"%{username}%"))

    if event_id:
        try:
            query = query.filter(Checkin.event_id == int(event_id))
        except ValueError:
            return jsonify({"message": "活动ID格式错误"}), 400

    rows = query.order_by(Checkin.id.desc()).all()

    data = []
    for checkin, user_item, event in rows:
        data.append({
            "签到ID": checkin.id,
            "用户ID": user_item.id,
            "用户名": user_item.username,
            "活动ID": event.id,
            "活动标题": event.title,
            "签到时间": checkin.checkin_time.strftime("%Y-%m-%d %H:%M:%S") if checkin.checkin_time else ""
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="admin_checkins.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =====================
# 热度分析与导出
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
# 组织者模块
# =====================
@app.route("/organizer/<int:organizer_id>/events", methods=["GET"])
def get_organizer_events(organizer_id):
    ok, current_user, error_response = check_organizer_access(organizer_id)
    if not ok:
        return error_response

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
            "status": calc_event_status(event),
            "created_at": event.created_at.strftime("%Y-%m-%d %H:%M:%S") if event.created_at else "",
            "organizer_id": event.organizer_id
        })

    return jsonify(result)


@app.route("/organizer/<int:organizer_id>/events/<int:event_id>/registrations", methods=["GET"])
def get_organizer_event_registrations(organizer_id, event_id):
    ok, current_user, error_response = check_organizer_access(organizer_id)
    if not ok:
        return error_response

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    if int(event.organizer_id) != int(current_user.id):
        return jsonify({"message": "你无权查看这个活动的报名名单"}), 403

    registrations = Registration.query.filter_by(event_id=event_id).order_by(Registration.id.desc()).all()

    result = []
    for item in registrations:
        user_item = User.query.get(item.user_id)

        result.append({
            "registration_id": item.id,
            "user_id": item.user_id,
            "username": user_item.username if user_item else "",
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


@app.route("/organizer/<int:organizer_id>/events/<int:event_id>/checkin-stats", methods=["GET"])
def get_organizer_event_checkin_stats(organizer_id, event_id):
    ok, current_user, error_response = check_organizer_access(organizer_id)
    if not ok:
        return error_response

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    if int(event.organizer_id) != int(current_user.id):
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
        user_item = User.query.get(reg.user_id)

        user_info = {
            "user_id": reg.user_id,
            "username": user_item.username if user_item else "",
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


@app.route("/organizer/<int:organizer_id>/events/<int:event_id>", methods=["DELETE"])
def delete_organizer_event(organizer_id, event_id):
    ok, current_user, error_response = check_organizer_access(organizer_id)
    if not ok:
        return error_response

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    if int(event.organizer_id) != int(current_user.id):
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


@app.route("/organizer/<int:organizer_id>/events/<int:event_id>", methods=["PUT"])
def update_organizer_event(organizer_id, event_id):
    ok, current_user, error_response = check_organizer_access(organizer_id)
    if not ok:
        return error_response

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "活动不存在"}), 404

    if int(event.organizer_id) != int(current_user.id):
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)