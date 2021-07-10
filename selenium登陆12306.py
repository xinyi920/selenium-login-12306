import pymysql
from selenium import webdriver
from selenium.webdriver import ActionChains
from chaojiying import Chaojiying_Client
import time
import os


class log_in:

    def __init__(self):
        self.wd = webdriver.Chrome()
        self.url = 'https://kyfw.12306.cn/otn/resources/login.html'

    @staticmethod
    def get_info():
        global CA, CP, SI, User, Password
        # CA:超级鹰account；CP：超级鹰password；SI：超级鹰softID；
        # User：12306用户名；Password：12306密码。
        # 1.建立连接        用户      密码      端口          数据库         编码
        conn = pymysql.connect(user='root', password='', port=3306,
                               database='12306_user_info', charset='utf8')
        # 在自己的mysql数据库中，创建一个数据库（12306_user_info）来存储信息，输入自己的数据库的密码
        # 2.创建游标对象
        cur = conn.cursor()
        # 3.使用游标对象execute方法
        name = input("请输入想要使用的名字的信息：")
        cur.execute('select * from user_info')
        result = cur.fetchall()
        # print(result)
        for i in result:
            # print(i)
            if i[1] == name:
                CA = i[2]
                CP = i[3]
                SI = i[4]
                User = i[5]
                Password = i[6]
        # noinspection PyUnboundLocalVariable
        # 5.关闭游标
        cur.close()
        # 6.关闭数据库
        conn.close()

    @staticmethod
    def input_username_password(driver):
        phone_tag = driver.find_element_by_id('J-userName')
        phone_tag.send_keys(User)
        time.sleep(1)
        phone_tag = driver.find_element_by_id('J-password')
        phone_tag.send_keys(Password)
        print('用户名和密码输入成功！')

    @staticmethod
    def get_captcha(driver):
        """
        保存验证码图片。
        :param driver: 浏览器引擎
        :return: 验证码图片的本地保存路径
        """
        img_path = './12306_login.png'
        # .screenshot(img_path):使用selenium中截图的方法保存验证码图片到指定路径img_path下。
        driver.find_element_by_id('J-loginImg').screenshot(img_path)

        return img_path

    @staticmethod
    def img_recognize(img_path):
        """
        超级鹰验证图片。
        :param img_path: 验证码图片的本地保存路径
        :return: 需要点击的验证码的相应位置的坐标的列表
        """
        chaojiying_obj = Chaojiying_Client(CA, CP, SI)
        with open(img_path, 'rb') as f:
            img = f.read()
        resp = chaojiying_obj.PostPic(img, 9004)
        '''
        print(resp, type(resp))    # 观察超级鹰返回的数据：
        {'err_no': 0, 'err_str': 'OK', 'pic_id': '1129514185497300001', 'pic_str': '37,79|65,97', 'md5': '6bddc1898298e90e8cd0eb18ac0450cb'} <class 'dict'>
        '''
        pic_str = resp['pic_str']
        pic_list = pic_str.split('|')  # ['37,79', '65,97']
        return pic_list

    @staticmethod
    def img_click(driver, pos_list):
        """
        通过超级鹰返回的数据点击验证码相应位置。
        :param driver: 浏览器引擎
        :param pos_list: 超级鹰返回的验证码需要点击的坐标列表
        :return:
        """
        img_element = driver.find_element_by_id('J-loginImg')
        for pos in pos_list:
            x, y = pos.split(',')
            ActionChains(driver).move_to_element_with_offset(img_element, int(x),
                                                             int(y)).click().perform()  # 一定要使用动作链完成！

    def login(self):
        # 1.获取想要使用的数据
        self.get_info()
        self.wd.get(self.url)
        # 窗口最大化
        self.wd.maximize_window()
        time.sleep(1)
        '''
            如果有一个按键点击不了，而且定位是正确的且人为操作是可以点击的，就尝试使用下述方法：
            wd.find_element_by_class_name('login-hd-account active').send_keys(Keys.ENTER)
            导入方法： from selenium.webdriver.common.keys import Keys
            '''
        # 2.找到登录界面
        self.wd.find_element_by_class_name('login-hd-account').click()
        time.sleep(1)
        # 3.输入用户名和密码
        self.input_username_password(self.wd)
        time.sleep(1)
        # 4.获取验证码图片
        path = self.get_captcha(self.wd)
        time.sleep(1)
        # 5.超级鹰识别验证码
        pic_list = self.img_recognize(path)
        time.sleep(5)
        # 6.点击图片验证
        self.img_click(self.wd, pic_list)
        # 7.点击登录
        time.sleep(1)
        self.wd.find_element_by_id('J-login').click()
        # 8.清除不必要文件，节省空间
        file = './12306_login.png'
        if not os.path.exists(file):
            print(f'no such file:{file}')
        else:
            os.remove(file)  # 如果文件存在则删除
        # 关闭模拟的浏览器
        # self.wd.close()


if __name__ == '__main__':
    a = log_in()
    a.login()
