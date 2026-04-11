from app import app
from extensions import db
from models import User, Event
from datetime import datetime, timedelta
import random

with app.app_context():
    # 创建一个管理员用户
    admin = User(username="admin", password="123456", role="admin")
    db.session.add(admin)

    # 活动类别
    categories = ["讲座", "比赛", "社团活动"]

    # 创建20个活动
    for i in range(1, 21):
        event = Event(
            title=f"校园活动 {i}",
            category=random.choice(categories),
            description=f"这是第{i}个活动",
            location=f"教学楼 {i}号教室",
            start_time=datetime.now() + timedelta(days=i),
            max_participants=random.randint(50, 200),
            status="报名中"
        )
        db.session.add(event)

    db.session.commit()
    print("测试数据插入成功！")