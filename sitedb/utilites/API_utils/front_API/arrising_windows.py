import os
import sqlite3
import requests

from PyQt5 import QtCore, QtGui, QtWidgets, QtTest



class Connect_win(QtWidgets.QDialog):
	def __init__(self, root):
		super().__init__()
		self.root = root
		self.conn = self.root.conn
		self.curs = self.conn.cursor()
		self.__initUI()
		self.draw()


	def __initUI(self):
		self.login = QtWidgets.QLineEdit(self)
		self.login.setGeometry(QtCore.QRect(10, 20, 240, 30))
		self.login.setObjectName("Login")
		self.login.setText(self.root.login)

		self.password = QtWidgets.QLineEdit(self)
		self.password.setGeometry(QtCore.QRect(10, 60, 240, 30))
		self.password.setObjectName("Password")
		self.password.setText(self.root.password)

		self.add_btn = QtWidgets.QPushButton('Проверить', self)
		self.add_btn.setToolTip('Проверить логин и пароль')
		self.add_btn.setGeometry(QtCore.QRect(20, 100, 220, 30))
		self.add_btn.clicked.connect(lambda: self.check())

	def closeEvent(self, event):
		print("UPDATE tech_tbl  SET info = '%s' WHERE name = '%s'" % ('login', self.login.text()))
		current_log = self.curs.execute("SELECT * FROM tech_tbl WHERE info = 'login'").fetchall()
		if current_log:

			self.curs.execute("UPDATE tech_tbl  SET info = '%s' WHERE name = '%s'" % ('login', self.login.text()))
			self.curs.execute("UPDATE tech_tbl  SET info = '%s' WHERE name = '%s'" % ('password', self.password.text()))
		else:
			print("INSERT INTO tech_tbl VALUES ({},{})".format('login', self.login.text()))
			self.curs.execute("INSERT INTO tech_tbl (name,info) VALUES ('%s','%s')" % ('login', self.login.text()))
			self.curs.execute("INSERT INTO tech_tbl (name,info) VALUES ('%s','%s')" % ('password', self.password.text()))
		self.conn.commit()
		test = self.curs.execute("SELECT * from tech_tbl").fetchall()
		print(test)

		print(' Новій логин:{}, новій пароль: {}'.format(self.login.text(),self.password.text()))
		self.conn.commit()
		password = self.curs.execute("SELECT info FROM tech_tbl WHERE name = 'password'").fetchone()
		print (password)

	def draw(self):
		self.setWindowTitle('Подключение')
		self.setGeometry(600, 200, 260, 140)
		self.show()

	def check(self):
		auth = {"username": [self.login.text()], "password": [self.password.text()]}
		if not self.root.check(auth):
			self.close()
			return





class ListWidget(QtWidgets.QListWidget):
	def __init__(self, Wind, **kwargs):
		super().__init__(Wind, **kwargs)
		self.Wind = Wind
		self.setSelectionMode(QtWidgets.QListWidget.MultiSelection)
		self.__initUI()

	def __initUI(self):
		self.show()


class Choose_tables(QtWidgets.QDialog):
	def __init__(self, *args,**kwarg):
		super().__init__(*args, **kwarg)
		self.root = args[0]
		self.choosen_list = []
		self.conn = self.root.conn
		self.curs = self.conn.cursor()
		self.__initUI()
		self.draw()

	def __initUI(self):
		self.list = QtWidgets.QListWidget(self)
		self.list.setSelectionMode(QtWidgets.QListWidget.MultiSelection)
		self.list.setMinimumHeight(300)

		list_existed_tables = list(
			title[0] for title in self.curs.execute('SELECT name from sqlite_master where type= "table"').fetchall()
			if title[0] in self.root.table_names)
		self.mainlist = list_existed_tables
		for i in self.mainlist:
			self.list.addItem(i)

		self.clear_button = QtWidgets.QPushButton('Выбрать', self)
		self.clear_button.setToolTip('Удалить выбранные таблицы базы перед внесением данных из Access')
		self.clear_button.setMaximumHeight(30)
		self.clear_button.clicked.connect(lambda: self.clear_base())

		grid = QtWidgets.QGridLayout()
		grid.addWidget(self.list, 0, 0)
		grid.addWidget(self.clear_button, 1, 0)
		self.setLayout(grid)
		print('name_of_tables begin', self.mainlist)

		self.show()

	def clear_base(self):
		self.choosen_list = list(item.text() for item in self.list.selectedItems())
		print('name of choosen', self.choosen_list)
		self.close()

	def closeEvent(self, event):
		if len(self.choosen_list) > 0:
			self.root.cl_btn.setDisabled(False)

	def draw(self):
		self.setWindowTitle('Выбор таблиц')
		self.setGeometry(600, 200, 460, 140)
		self.show()

