class Tables():
    """класс таблица обхектов - строк в таблце базы данных """

    def __init__(self, table_name, curs):
        self.table_name = table_name  # название таблицы
        self.curs = curs
        self.items = {}  # словарь записей таблицы с ключем ID
        self.curs.execute("SELECT * FROM '%s'" % self.table_name).fetchall()
        self.title = list(i[0] for i in curs.description)

    def add_item(self, item):
        """ добавление записи в словарь с ключем  item.id """
        self.items[item[0]] = Table_items(item)
        for attr, val in zip(self.title, item):
            self.items[item[0]].__dict__[attr] = val

    def add_all_items(self):
        for item in self.curs.execute("SELECT * FROM '%s'" % self.table_name).fetchall():
            self.add_item(item)

    def __str__(self):
        return self.table_name + " Список полей = " + str(self.title)


class JSON_Tables():
    """класс таблица объектов преобразованная из JSON """

    def __init__(self, table_name, json_table):
        self.table_name = table_name            # название таблицы
        self.items = {}                         # словарь записей таблицы с ключем ID
        self.json_table = json_table            # файл JSON
        self.title = self.json_table[0].keys()


    def add_item(self, item):
        """ добавление записи в словарь с ключем  item.id """
        self.items[item['id']] = Table_js_items(item)
        for attr, val in item.items():
            self.items[item['id']].__dict__[attr] = val

    def add_all_items(self):
        for item in self.json_table:
            self.add_item(item)

    def __str__(self):
        return self.table_name + " Список полей = " + str(self.title)


class Table_items():
    def __init__(self, *args):
        pass


class Table_js_items():
    def __init__(self, *args):
        pass
