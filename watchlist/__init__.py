import sys
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):  # 创建用户回调函数
    from watchlist.models import User
    user = User.query.get(int(user_id))  # 用ID作为User查询
    return user

@app.context_processor
def inject_user():
    from watchlist.models import User
    user = User.query.first()
    return dict(user = user)


if __name__ == '__main__':
    app.run()

from watchlist import views, errors, commands
