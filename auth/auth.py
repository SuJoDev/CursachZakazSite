from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QApplication, QMessageBox
import sys
import requests

# Импорт главного окна
from main_window import MainWindow  # Предположим, что это основной интерфейс приложения

class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        login_lbl = QLabel("Логин", self)
        layout.addWidget(login_lbl)
        
        self.login_edit = QLineEdit(self)
        layout.addWidget(self.login_edit)
        
        password_lbl = QLabel("Пароль", self)
        layout.addWidget(password_lbl)
        
        self.password_edit = QLineEdit(self)
        layout.addWidget(self.password_edit)
        
        commit_btn = QPushButton("Войти", self)
        commit_btn.clicked.connect(self.auth)
        layout.addWidget(commit_btn)
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
    def auth(self):
        login = self.login_edit.text()
        if login == "":
            QMessageBox.critical(self, "Ошибка", "Вы не можете оставить поле логина пустым")
            return
        password = self.password_edit.text()
        if password == "":
            QMessageBox.critical(self, "Ошибка", "Вы не можете оставить поле пароля пустым")
            return
        
        response = requests.post(f"http://127.0.0.1:8000/api/v1/SignIn?login={login}&password={password}")
        if response.status_code == 200:
            self.role = response.json()
            print(self.role)  # Логирование информации о роли пользователя
            
            # Открыть главное окно после успешной авторизации
            self.open_main_window()
        else:
            QMessageBox.critical(self, "Ошибка", "Вы не прошли авторизацию")
        
    def open_main_window(self):
        self.main_window = MainWindow()
        if self.role == 2:
            self.main_window.tools_reader.setVisible(False)
            self.main_window.reader_table.itemClicked.disconnect(self.main_window.on_reader_selected)
            self.main_window.tools_inssue.setVisible(False)
            self.main_window.inssue_table.itemClicked.disconnect(self.main_window.on_inssue_selected)
            self.main_window.showMaximized() 
        elif self.role == 3:
            self.main_window.tools_books.setVisible(False)
            self.main_window.books_table.itemClicked.disconnect(self.main_window.on_book_selected)
            self.main_window.tools_reader.setVisible(False)
            self.main_window.reader_table.itemClicked.disconnect(self.main_window.on_reader_selected)
            self.main_window.tools_inssue.setVisible(False)
            self.main_window.inssue_table.itemClicked.disconnect(self.main_window.on_inssue_selected)
            self.main_window.showMaximized()
        elif self.role == 1:
            self.main_window.showMaximized()
        self.close()