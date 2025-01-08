from html import escape

from flask import Flask, request, url_for

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/home')
@app.route('/index')
def hello():
    return '<h1>Home</h1> <img src = "http://helloflask.com/totoro.gif">'



@app.route('/user/<name>')
def user_page(name):
    return f'User: {escape(name)}'



@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page',name = 'peter'))
    print(url_for('test_url_for'))
    return 'Test'


@app.route('/signin', methods=['GET'])
def signin_form():
    return '''<form action="/signin" method="post">
              <p><input name="username"></p>
              <p><input name="password" type="password"></p>
              <p><button type="submit">Sign In</button></p>
              </form>'''

@app.route('/signin', methods=['POST'])
def signin():
    # 需要从request对象读取表单内容：
    if request.form['username']=='admin' and request.form['password']=='password':
        return '<h3>Hello, admin!</h3>'
    return '<h3>Bad username or password.</h3>'

if __name__ == '__main__':
    app.run()