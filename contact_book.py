import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QListWidget, QLabel, QComboBox, 
                             QTextEdit, QMessageBox, QInputDialog)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize

class ContactBook(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Contact Book")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('contact_icon.png'))  # Make sure to have an icon file

        self.init_db()
        self.init_ui()

    def init_db(self):
        self.conn = sqlite3.connect("advanced_contacts.db")
        self.cur = self.conn.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                category TEXT
            )
        """)
        self.conn.commit()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left side - Contact List and Search
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search contacts...")
        self.search_bar.textChanged.connect(self.search_contacts)
        left_layout.addWidget(self.search_bar)

        self.contact_list = QListWidget()
        self.contact_list.itemClicked.connect(self.display_contact)
        left_layout.addWidget(self.contact_list)

        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget)

        # Right side - Contact Details and Buttons
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Name")
        right_layout.addWidget(self.name_edit)

        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Phone")
        right_layout.addWidget(self.phone_edit)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email")
        right_layout.addWidget(self.email_edit)

        self.address_edit = QTextEdit()
        self.address_edit.setPlaceholderText("Address")
        self.address_edit.setMaximumHeight(100)
        right_layout.addWidget(self.address_edit)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Family", "Friend", "Work", "Other"])
        right_layout.addWidget(self.category_combo)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_contact)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update_contact)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_contact)
        button_layout.addWidget(self.delete_button)

        right_layout.addLayout(button_layout)

        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.load_contacts()

    def load_contacts(self):
        self.contact_list.clear()
        self.cur.execute("SELECT name FROM contacts ORDER BY name")
        contacts = self.cur.fetchall()
        for contact in contacts:
            self.contact_list.addItem(contact[0])

    def search_contacts(self):
        search_text = self.search_bar.text().lower()
        for i in range(self.contact_list.count()):
            item = self.contact_list.item(i)
            if search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def display_contact(self, item):
        name = item.text()
        self.cur.execute("SELECT * FROM contacts WHERE name=?", (name,))
        contact = self.cur.fetchone()
        if contact:
            self.name_edit.setText(contact[1])
            self.phone_edit.setText(contact[2])
            self.email_edit.setText(contact[3])
            self.address_edit.setText(contact[4])
            self.category_combo.setCurrentText(contact[5])

    def add_contact(self):
        name = self.name_edit.text()
        phone = self.phone_edit.text()
        email = self.email_edit.text()
        address = self.address_edit.toPlainText()
        category = self.category_combo.currentText()

        if not name:
            QMessageBox.warning(self, "Error", "Name is required.")
            return

        self.cur.execute("""
            INSERT INTO contacts (name, phone, email, address, category)
            VALUES (?, ?, ?, ?, ?)
        """, (name, phone, email, address, category))
        self.conn.commit()
        self.load_contacts()
        self.clear_fields()

    def update_contact(self):
        name = self.name_edit.text()
        phone = self.phone_edit.text()
        email = self.email_edit.text()
        address = self.address_edit.toPlainText()
        category = self.category_combo.currentText()

        if not name:
            QMessageBox.warning(self, "Error", "Name is required.")
            return

        self.cur.execute("""
            UPDATE contacts
            SET phone=?, email=?, address=?, category=?
            WHERE name=?
        """, (phone, email, address, category, name))
        self.conn.commit()
        self.load_contacts()

    def delete_contact(self):
        name = self.name_edit.text()
        if not name:
            QMessageBox.warning(self, "Error", "Select a contact to delete.")
            return

        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       f"Are you sure you want to delete {name}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.cur.execute("DELETE FROM contacts WHERE name=?", (name,))
            self.conn.commit()
            self.load_contacts()
            self.clear_fields()

    def clear_fields(self):
        self.name_edit.clear()
        self.phone_edit.clear()
        self.email_edit.clear()
        self.address_edit.clear()
        self.category_combo.setCurrentIndex(0)

    def closeEvent(self, event):
        self.conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ContactBook()
    window.show()
    sys.exit(app.exec())