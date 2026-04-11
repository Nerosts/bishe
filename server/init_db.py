from app import app
from extensions import db
import models

with app.app_context():
    db.create_all()
    print("数据库表创建成功！")