import unittest

from app import app, db, User, Movie,forge, initdb

class WatchListTestCase(unittest.TestCase):
    def setUp(self):
        print('setUp')

        # 更新配置
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'  # 使用内存中的 SQLite 数据库
        )

        # 创建应用上下文
        self.app_context = app.app_context()
        self.app_context.push()

        # 创建数据库和表
        db.create_all()
        user = User(name='Test', username='test')
        user.set_password('123')
        movie = Movie(title='Test Movie Title', year='2019')

        db.session.add_all([user, movie])
        db.session.commit()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

    def tearDown(self):
        print('tearDown')
        db.session.remove()
        db.drop_all()

        # 移除应用上下文
        self.app_context.pop()

    def test_app_exist(self):
        self.assertIsNotNone(app)

    #测试404页面
    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404',data)
        self.assertIn('Go Back',data)
        self.assertEqual(response.status_code,404)

    #测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist',data)
        self.assertIn('Test Movie Title',data)
        self.assertEqual(response.status_code,200)

    #测试登录
    def login(self):
        self.client.post('/login',data=dict(
            username='test',
            password='123'
        ),follow_redirects=True)

    #测试创建条目
    def test_create_item(self):
        self.login()

        #创建条目
        response = self.client.post('/',data=dict(
            title='New Movie',
            year='2019'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.',data)
        self.assertIn('New Movie',data)

        #创建条目但是 标题为空
        response = self.client.post('/', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

        #创建条目 但是年份为空
        response = self.client.post('/', data=dict(
            title='New',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

    def test_update_item(self):
        self.login()

        #测试更新页面
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item',data)
        self.assertIn('Test Movie Title', data)
        self.assertIn('2019', data)

        #更新条目操作
        response=self.client.post('/movie/edit/1',data=dict(
            title='New Movie Edited',
            year='2018'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.',data)
        self.assertIn('New Movie Edited',data)

        #更新条目 但是标题为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2018'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertIn('Invalid input.', data)

        # 更新条目 但是年份为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited Again',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertNotIn('New Movie Edited Again', data)
        self.assertIn('Invalid input.', data)

    #测试删除条目
    def test_delete_item(self):
        self.login()

        response = self.client.post('/movie/delete/1',follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.',data)
        self.assertNotIn('Test Movie Title', data)

    #测试登录保护
    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout',data)
        self.assertNotIn('Settings',data)
        self.assertNotIn('<form method="post">',data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)
        self.assertIn('Login',data)

    #测试登录
    def test_login(self):
        response=self.client.post('/login',data=dict(
            username='test',
            password='123'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success',data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('Delete', data)
        self.assertIn('Edit', data)
        self.assertIn('<form method="post">', data)

        #使用错误的用户名登陆
        response = self.client.post('/login', data=dict(
            username='test1',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success', data)
        self.assertIn('Invalid username or password.',data)

        # 使用错误的密码登陆
        response = self.client.post('/login', data=dict(
            username='test',
            password='1234'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success', data)
        self.assertIn('Invalid username or password.', data)

        # 使用空用户名登陆
        response = self.client.post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success', data)
        self.assertIn('Invalid username or password.', data)

        # 使用空密码登陆
        response = self.client.post('/login', data=dict(
            username='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success', data)
        self.assertIn('Invalid username or password.', data)


    #测试登出
    def test_logout(self):
        self.login()
        response = self.client.get('/logout', follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertIn('Goodbye.',data)
        self.assertNotIn('Logout',data)
        self.assertNotIn('Settings',data)
        self.assertNotIn('Delete',data)
        self.assertNotIn('Edit',data)
        self.assertNotIn('<form method="post">',data)
        self.assertNotIn('Logout',data)

    #测试设置
    def test_settings(self):
        self.login()

        #测试设置页面
        response=self.client.get('/settings')
        data=response.get_data(as_text=True)
        self.assertIn('Settings',data)
        self.assertIn('Your Name',data)

        # 测试更新设置
        response=self.client.post('/settings',data=dict(
            name='Grey Li',
        ),follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertIn('Settings updated.',data)
        self.assertIn('Grey Li',data)

        # 测试名称为空
        response=self.client.post('/settings',data=dict(
            name='',
        ),follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertNotIn('Settings updated.',data)
        self.assertIn('Invalid input.',data)

    #测试虚拟数据
    def test_forge_command(self):
        result= self.runner.invoke(forge)
        self.assertEqual('Done.',result.output.strip())
        self.assertNotEqual(Movie.query.count(),0)
    #测试初始化数据库
    def test_initdb_command(self):
        result=self.runner.invoke(initdb)
        self.assertEqual('Initialized database.',result.output.strip())

    #测试生成管理员账户
    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        res = self.runner.invoke(args=['admin', '--username', 'grey', '--password', '123'])
        self.assertIn('Creating user...', res.output)
        self.assertIn('Done.', res.output.strip())
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'grey')
        self.assertTrue(User.query.first().validate_password('123'))

    #更新管理员账户
    def test_admin_command_update(self):
        #使用args参数给出完整的命令参数列表
        result=self.runner.invoke(args=['admin','--username','peter','--password','456'])
        self.assertIn('Updating user...',result.output)
        self.assertIn('Done.',result.output.strip())
        self.assertEqual(User.query.count(),1)
        self.assertEqual(User.query.first().username,'peter')
        self.assertTrue(User.query.first().validate_password('456'))

if __name__ == '__main__':
    unittest.main()