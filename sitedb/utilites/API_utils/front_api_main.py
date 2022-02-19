import sys
import sqlite3
import requests
import os

from PyQt5 import QtGui, QtWidgets

from front_API.arrising_windows import Connect_win, Choose_tables
import back_API


class MainWind(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.session = None
        self.table_names = ['Структури', 'Кейс', 'Статті', 'Права людини', 'Статус в переслідуванні',
                            'Актори акту', 'Місце роботи', 'Людина', 'Організаціія',
                            'Переслідування', 'Акт', 'Місце позбавлення волі',]
        self.path = os.getcwd()
        self.check_base()
        self.__initUI()
        self.check_site()

    def __initUI(self):
        self.connLabel = QtWidgets.QLabel(self)
        self.connLabel.setMinimumHeight(100)
        self.connLabel.setToolTip('Статус подкючения к сайту')
        self.connLabel.setText(' - ')

        self.conn_btn = QtWidgets.QPushButton('Подключится к сайту', self)
        self.conn_btn.setToolTip('Подключение к сайту, ввод новых логина пароля')
        self.conn_btn.setMaximumHeight(30)
        self.conn_btn.clicked.connect(lambda: self.connect_to_site())

        self.take_btn = QtWidgets.QPushButton('Выбрать таблицы', self)
        self.take_btn.setToolTip('Очистить таблицы базы перед внесением данных из Access')
        self.take_btn.setMaximumHeight(30)
        self.take_btn.clicked.connect(lambda: self.ch_table())

        self.cl_btn = QtWidgets.QPushButton('Удалить выбранные', self)
        self.cl_btn.setToolTip('Очистить таблицы базы перед внесением данных из Access')
        self.cl_btn.setMaximumHeight(30)
        self.cl_btn.clicked.connect(lambda: self.drop_table())
        self.cl_btn.setDisabled((True))

        self.synch_btn = QtWidgets.QPushButton('Синхронизировать', self)
        self.synch_btn.setToolTip('Внесение данных из Access')
        self.synch_btn.setMaximumHeight(30)
        self.synch_btn.clicked.connect(lambda: self.synchronisation())


        self.setGeometry(600, 300, 300, 300)
        self.setWindowTitle('Синхронизация')
        self.setWindowIcon(QtGui.QIcon('C:\\Python\\CHRG_logo.gif'))

        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.connLabel, 0, 0)
        grid.addWidget(self.conn_btn, 1, 0)
        grid.addWidget(self.take_btn, 2, 0)
        grid.addWidget(self.cl_btn, 3, 0)
        grid.addWidget(self.synch_btn, 4, 0)
        self.setLayout(grid)


        self.show()

    def closeEvent(self, event):
        self.conn.commit()
        self.conn.close()

    def get_site(self):
        """

        Создате путь к базе  и ссылку на сайт.
        временное решение до создания интерфейса с настройкой
        """

    def check_base(self):
        """

        подключается к базе, если ее нет, то создает
        проверяет наличие и при отсутвии создает:
            таблицу с технической информацией, (
                - адрес сайта,
                    если нет записи "site" создает адрес по умолчанию "http://127.0.0.1:8000/")
                - логин и  пароль админа, (создается или проверяется при подключении к базе )


            таблица имен таблиц на сайте
            таблица дат обновлений таблиц на сайте
        считывает имена таблиц в базе

        """
        base = 'synch_API.sqlite3'
        print(base)
        self.conn = sqlite3.connect(base)
        self.curs = self.conn.cursor()
        # self.curs.execute("DROP TABLE 'tech_tbl'")
        list_existed_tables = (title[0] for title in self.curs.execute('SELECT name from sqlite_master where type= "table"').fetchall())
        print('name_of_tables begin', list(list_existed_tables))
        tech_tbl = 'CREATE TABLE tech_tbl (tech_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, ' \
                   'name VARCHAR(50) NOT NULL, info VARCHAR(50) NOT NULL );'
        try:
            self.curs.execute(tech_tbl)
        except:
            pass
        print_table_head(self.curs,'tech_tbl')
        url = self.curs.execute("SELECT info FROM tech_tbl WHERE name = 'site'").fetchone()
        if not url:
            self.url = 'http://127.0.0.1:8000/'
            self.curs.execute("INSERT INTO tech_tbl (name,info) VALUES ('%s','%s')" % ('site', self.url))
            self.conn.commit()
        else: self.url = url[0]
        print(self.url)


    def check_site(self):
        """
            проверяет наличие логина и пароля админа,
                если нет предлагате внести, открывает окно для внесения.
            проверяет  их корректность
            при неудачном сообщает о проблемме подключения и ее типе
            при удачном создает токен и сессию подключения self.session
            token

        """
        self.login = self.curs.execute("SELECT info FROM tech_tbl WHERE name = 'login'").fetchone()
        if self.login:
            self.login = self.login[0]
        self.password = self.curs.execute("SELECT info FROM tech_tbl WHERE name = 'password'").fetchone()
        if self.password:
            self.password = self.password[0]
        if not self.login or not self.password:
            self.connLabel.setText('НЕТ пароля или логина')
            return
        auth = {"username": [self.login], "password": [self.password]}
        self.check(auth)

    def check(self, auth):
        t_url = self.url + "api-token-auth/"
        try:
            token = requests.post(t_url, data=auth)
        except:
            self.connLabel.setText(
                'Подключение не установлено')
            return
        if not 'token' in token.json():
            print(token.json())
            self.connLabel.setText("Логин/пароль не верен")
            return False
        self.token = token.json()['token']
        session = requests.Session()
        session.headers.update({'Authorization': 'token %s' % self.token})
        test_url = self.url + 'persons_api/'
        cont = session.get(test_url).json()
        if 'detail' in cont:
            self.connLabel.setText('У вас недостаточно прав')
            return False
        self.connLabel.setText('Подключение установлено')
        self.session = session
        return True

    def connect_to_site(self):
        Connect_win(self)

    def ch_table(self):
        self.tables = Choose_tables(self)

    def drop_table(self):
        print(self.tables.choosen_list)
        for table_name in self.tables.choosen_list:
            self.curs.execute("DROP TABLE '%s'" % table_name)
        self.cl_btn.setDisabled(True)

    def synchronisation(self):
        back_API.api_synch(self.url, self.curs, self.session)


def print_table_head(cur,table_name):
	cur.execute('SELECT * FROM %s' % table_name)
	h_head = list(i[0] for i in cur.description)
	print(h_head)

def main():
    app = QtWidgets.QApplication(sys.argv)
    mn = MainWind()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
