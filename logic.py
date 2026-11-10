
import sqlite3
from config import DATABASE
class DB_Manager():
    def __init__(self, database):
        self.database = database

    def create_database(self):
        """Создаёт файл базы данных, если его ещё нет"""
        try:
            conn = sqlite3.connect(self.database)
            conn.close()
            print(f"База данных '{self.database}' успешно создана или уже существует")
        except Exception as e:
            print(f"Ошибка при создании базы данных: {e}")

    def create_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS answers(
                    question_id INTEGER,
                    answer_id   INTEGER,
                    question     TEXT,
                    answer      TEXT,
                    user_id TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS problems(
                    problem_id INTEGER,
                    user_id    INTEGER,
                    problem    TEXT,
                    date       INTEGER
                )
            ''')

    def save_answers(self):
        """Заполняет таблицу answers парами вопрос-ответ"""
        data = [
            ("Как оформить заказ?",
             'Для оформления заказа, пожалуйста, выберите интересующий вас товар '
             'и нажмите кнопку "Добавить в корзину", затем перейдите в корзину '
             'и следуйте инструкциям для завершения покупки.'),
            ("Как узнать статус моего заказа?",
             'Вы можете узнать статус вашего заказа, войдя в свой аккаунт на нашем сайте '
             'и перейдя в раздел "Мои заказы". Там будет указан текущий статус вашего заказа.'),
            ("Как отменить заказ?",
             'Если вы хотите отменить заказ, пожалуйста, свяжитесь с нашей службой поддержки '
             'как можно скорее. Мы постараемся помочь вам с отменой заказа до его отправки.'),
            ("Что делать, если товар пришел поврежденным?",
             'При получении поврежденного товара, пожалуйста, сразу свяжитесь с нашей службой '
             'поддержки и предоставьте фотографии повреждений. Мы поможем вам с обменом '
             'или возвратом товара.'),
            ("Как связаться с вашей технической поддержкой?",
             'Вы можете связаться с нашей технической поддержкой через телефон на нашем сайте '
             'или написать нам в чат-бота.'),
            ("Как узнать информацию о доставке?",
             'Информацию о доставке вы можете найти на странице оформления заказа на нашем сайте. '
             'Там указаны доступные способы доставки и сроки.'),
        ]

        conn = sqlite3.connect(self.database)
        try:
            with conn:
                cursor = conn.cursor()
                for i, (question, answer) in enumerate(data, 1):
                    cursor.execute(
                        '''INSERT INTO answers (question_id, answer_id, question, answer)
                           VALUES (?, ?, ?, ?)''',
                        (i, i, question, answer)
                    )
            print(f"Сохранено записей: {len(data)}")
        except sqlite3.Error as e:
            print(f"Ошибка при сохранении в БД: {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    manager = DB_Manager(DATABASE)
    manager.create_database()
    manager.create_table()
    manager.save_answers()
