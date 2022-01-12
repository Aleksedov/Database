import sqlite3

class Tables():
	"""класс таблица данных"""
	def __init__(self, table_name,curs):
		self.table_name = table_name 	# название таблицы
		self.curs = curs
		self.items = {}					# словарь записей таблицы с ключем ID
		self.curs.execute("SELECT * FROM %s" % self.table_name).fetchall()
		self.title = list(i[0] for i in curs.description)

	def add_item(self,item):
		""" добавление записи в словарь с ключем  item.id """
		self.items[item[0]] = Table_items(item)
		for attr,val in zip(self.title,item):
			self.items[item[0]].__dict__[attr] = val

	def add_all_items(self):
		for item in self.curs.execute("SELECT * FROM %s" % self.table_name).fetchall():
			self.add_item(item)


	def __str__(self):
		return self.table_name+" Список полей = "+ str(self.title)


class Table_items(Tables):
	def __init__(self, *args):
		pass


def main():
	conn = sqlite3.connect('db.sqlite3')
	curs=conn.cursor()
	name_of_tables = 	list(curs.execute('SELECT name from sqlite_master where type= "table"'))
	print ('name_of_tables begin',name_of_tables)
	# curs.execute("DROP TABLE 'Людина'")
	# conn.commit()

	site_pers = Tables('sitedb_person',curs)
	print (site_pers)
	site_pers.add_all_items()
	print (len(site_pers.items))


	conn2 = sqlite3.connect('source_db.db')
	curs2=conn2.cursor()
	name_of_tables2 = 	list(curs2.execute('SELECT name from sqlite_master where type= "table"'))
	print ('name_of_tables begin',name_of_tables2)

	db_pers = Tables('Людина',curs2)
	print (db_pers)
	db_pers.add_all_items()
	print (len(db_pers.items))

	# for i in site_pers.items.keys():
	# 	print (site_pers.items[i].__dict__['name'], 'site_pers_date  =>' ,site_pers.items[i].__dict__['date_of_birth'])
	# 	curs.execute('UPDATE sitedb_person SET  date_of_birth=Null WHERE id= %s' % i) 
	# 	conn.commit()

	def transit_date(date1):
		raw_date = date1.split('.')
		new_date = '%s-%s-%s' %(raw_date[2],raw_date[1],raw_date[0])
		return new_date

	site_pers_date = site_pers.items[1].__dict__['date_of_birth']
	print ('site_pers_date  =>',type(site_pers_date) , site_pers_date)

	db_pers_date = db_pers.items[1].__dict__['Дата народження']
	print ('db_pers_date  =>' ,type(db_pers_date) , db_pers_date)
	transit_date(db_pers_date)



	for i in site_pers.items.keys():

		"""экспорт даты рождения"""
		# 	# print (site_pers.items[i].__dict__['name'], 'site_pers_date  =>' ,site_pers.items[i].__dict__['date_of_birth']@)
		# 	db_pers_date = db_pers.items[i].__dict__['Дата народження']
		# 	if db_pers_date:
		# 		new_date = transit_date(db_pers_date)
		# 		# print (new_date)
		# 		curs.execute('UPDATE sitedb_person SET  date_of_birth="%s" WHERE id= %s' % (new_date,i)) 

		"""замена изображения по умолчанию"""
		site_pers_image = site_pers.items[i].__dict__['photo']

		if site_pers_image and not 'images' in site_pers_image:
			new_way  = 'sitedb/images/person/' + site_pers_image


		# 	noimage = "images/Noface.JPG"
			curs.execute('UPDATE sitedb_person SET  photo="%s" WHERE id= %s' % (new_way,i)) 
			conn.commit()		


	# conn.commit()


if __name__ == '__main__':
	main()