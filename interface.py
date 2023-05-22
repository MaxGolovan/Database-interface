import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import psycopg2
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QColor

app = QApplication(sys.argv)

class DatabaseConnection:
    def __init__(self, host, port, database, user, password):
        self.host = "localhost"
        self.port = "5432"
        self.database = "timetable"
        self.user = "postgres"
        self.password = "1435"
        self.connection = None

    def connect(self):
        try:
            # Устанавливаем соединение с базой данных PostgreSQL
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")

    def disconnect(self):
        if self.connection:
            self.connection.close()  # Закрываем соединение с базой данных


class ScheduleEditor(QMainWindow):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection

        self.setWindowTitle("Schedule Editor")
        self.setGeometry(100, 100, 1000, 800)

        self.setStyleSheet(
            "background-color: #333333; color: #ffffff; font-size: 16px; font-family: Arial;"
        )

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setGeometry(0, 0, 1000, 800)
        self.tab_widget.setStyleSheet(
            "QTabWidget::pane { background-color: #222222; }"
            "QTabBar::tab { background-color: #222222; color: #ffffff; }"
            "QTabBar::tab:selected { background-color: #444444; }"
        )

        self.init_odd_week_tab()  # Инициализация вкладки "Odd Week"
        self.init_even_week_tab()  # Инициализация вкладки "Even Week"
        self.init_important_dates_tab()  # Инициализация вкладки "Important Events"

        self.show()

    def init_odd_week_tab(self):
        tab_layout = QVBoxLayout()

        day_tabs = QTabWidget()
        day_tabs.setStyleSheet(
            "QTabWidget::pane { background-color: #222222; }"
            "QTabBar::tab { background-color: #222222; color: #ffffff; }"
            "QTabBar::tab:selected { background-color: #444444; }"
        )

        day_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        for day in day_of_week:
            layout = QVBoxLayout()

            day_table = QTableWidget()
            day_table.setColumnCount(8)
            day_table.setStyleSheet("font-size: 18px;")
            day_table.setHorizontalHeaderLabels(
                ["Day of Week", "Date", "Pair", "Time Slot", "Subject", "Lecturer", "Activity Type", "Classroom"])
            self.update_day_table(day_table, "odd_week", day)  # Обновление таблицы дня недели

            update_button = QPushButton("Update", self)
            update_button.setStyleSheet("font-size: 18px;")
            update_button.clicked.connect(
                lambda _, table=day_table, w="odd_week", d=day: self.update_database(table, w, d))  # Обработчик кнопки обновления

            layout.addWidget(day_table)
            layout.addWidget(update_button)

            day_tab = QWidget()
            day_tab.setLayout(layout)
            day_tabs.addTab(day_tab, day)  # Добавление вкладки дня недели

        tab_layout.addWidget(day_tabs)

        odd_week_tab = QWidget()
        odd_week_tab.setLayout(tab_layout)
        self.tab_widget.addTab(odd_week_tab, "Odd Week")  # Добавление вкладки "Odd Week"

    def update_day_table(self, table, week, day):
        self.db_connection.connect()  # Установка соединения с базой данных
        cursor = self.db_connection.connection.cursor()
        cursor.execute(f"SELECT * FROM {week} WHERE \"day_of_week\" = '{day}'")  # Выполнение SQL-запроса для получения данных
        data = cursor.fetchall()  # Получение всех строк результата
        table.setRowCount(len(data))  # Установка количества строк в таблице
        for row_index, row_data in enumerate(data):
            for column_index, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                table.setItem(row_index, column_index, item)  # Установка значения ячейки в таблице
        self.db_connection.disconnect()  # Закрытие соединения с базой данных

    def update_database(self, table, week, day):
        self.db_connection.connect()  # Установка соединения с базой данных
        cursor = self.db_connection.connection.cursor()

        # Очищаем данные для указанного дня недели
        cursor.execute(f"DELETE FROM {week} WHERE \"day_of_week\" = '{day}'")

        # Обновляем данные в базе данных на основе значений в таблице
        for row in range(table.rowCount()):
            data = []
            for column in range(table.columnCount()):
                item = table.item(row, column)
                if item is not None:
                    data.append(item.text())
                else:
                    data.append("")
            cursor.execute(
                f"INSERT INTO {week} (\"day_of_week\", \"date\", \"pair\", \"time_slot\", \"subject\", \"lecturer\", \"activity_type\", \"classroom\") "
                f"VALUES ('{day}', %s, %s, %s, %s, %s, %s, %s)",
                (data[1], data[2], data[3], data[4], data[5], data[6], data[7])
            )
        self.db_connection.connection.commit()  # Применение изменений в базе данных
        self.db_connection.disconnect()  # Закрытие соединения с базой данных

    def init_even_week_tab(self):
        tab_layout = QVBoxLayout()

        day_tabs = QTabWidget()
        day_tabs.setStyleSheet(
            "QTabWidget::pane { background-color: #222222; }"
            "QTabBar::tab { background-color: #222222; color: #ffffff; }"
            "QTabBar::tab:selected { background-color: #444444; }"
        )

        day_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        for day in day_of_week:
            layout = QVBoxLayout()

            day_table = QTableWidget()
            day_table.setColumnCount(8)
            day_table.setStyleSheet("font-size: 18px;")
            day_table.setHorizontalHeaderLabels(
                ["Day of Week", "Date", "Pair", "Time Slot", "Subject", "Lecturer", "Activity Type", "Classroom"])
            self.update_day_table(day_table, "even_week", day)  # Обновление таблицы дня недели

            update_button = QPushButton("Update", self)
            update_button.setStyleSheet("font-size: 18px;")
            update_button.clicked.connect(
                lambda _, table=day_table, w="even_week", d=day: self.update_database(table, w, d))  # Обработчик кнопки обновления

            layout.addWidget(day_table)
            layout.addWidget(update_button)

            day_tab = QWidget()
            day_tab.setLayout(layout)
            day_tabs.addTab(day_tab, day)  # Добавление вкладки дня недели

        tab_layout.addWidget(day_tabs)

        even_week_tab = QWidget()
        even_week_tab.setLayout(tab_layout)
        self.tab_widget.addTab(even_week_tab, "Even Week")  # Добавление вкладки "Even Week"

    def init_important_dates_tab(self):
        layout = QVBoxLayout()

        dates_table = QTableWidget()
        dates_table.setColumnCount(2)
        dates_table.setStyleSheet("font-size: 18px;")
        dates_table.setHorizontalHeaderLabels(["Date", "Event"])
        self.update_dates_table(dates_table)  # Обновление таблицы важных событий

        update_button = QPushButton("Update", self)
        update_button.setStyleSheet("font-size: 18px;")
        update_button.clicked.connect(lambda _, table=dates_table: self.update_important_dates(table))  # Обработчик кнопки обновления

        layout.addWidget(dates_table)
        layout.addWidget(update_button)

        important_dates_tab = QWidget()
        important_dates_tab.setLayout(layout)
        self.tab_widget.addTab(important_dates_tab, "Important events")  # Добавление вкладки "Important Dates"

    def update_dates_table(self, table):
        self.db_connection.connect()  # Установка соединения с базой данных
        cursor = self.db_connection.connection.cursor()
        cursor.execute("SELECT * FROM important_events")  # Выполнение SQL-запроса для получения данных
        data = cursor.fetchall()  # Получение всех строк результата
        table.setRowCount(len(data))  # Установка количества строк в таблице
        for row_index, row_data in enumerate(data):
            for column_index, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                table.setItem(row_index, column_index, item)  # Установка значения ячейки в таблице
        self.db_connection.disconnect()  # Закрытие соединения с базой данных

    def update_important_dates(self, table):
        self.db_connection.connect()  # Установка соединения с базой данных
        cursor = self.db_connection.connection.cursor()

        # Очищаем данные в таблице важных событий
        cursor.execute("DELETE FROM important_events")

        # Обновляем данные в базе данных на основе значений в таблице
        for row in range(table.rowCount()):
            data = []
            for column in range(table.columnCount()):
                item = table.item(row, column)
                if item is not None:
                    data.append(item.text())
                else:
                    data.append("")
            cursor.execute(
                "INSERT INTO important_events (\"date\", \"event\") "
                "VALUES (%s, %s)",
                (data[0], data[1])
            )
        self.db_connection.connection.commit()  # Применение изменений в базе данных
        self.db_connection.disconnect()  # Закрытие соединения с базой данных


# Создаем экземпляр класса DatabaseConnection
db_connection = DatabaseConnection("localhost", "5432", "timetable", "postgres", "1435")

# Создаем экземпляр класса ScheduleEditor и передаем ему экземпляр db_connection
editor = ScheduleEditor(db_connection)
sys.exit(app.exec_())

