import sys
import random
import time
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QPainter, QPen, QColor, QImage, QFont, QCursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QColorDialog, QVBoxLayout, QPushButton,
    QFileDialog, QHBoxLayout, QSpinBox, QLabel, QInputDialog, QMessageBox, QMenu
)


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1400, 600)
        self.image = QImage(self.size(), QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)

        # Рисование
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor("black")
        self.pen_width = 3
        self.eraser_mode = False

        # История для undo/redo
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = 60

    # --- История действий ---
    def push_history(self):
        if len(self.undo_stack) >= self.max_history:
            self.undo_stack.pop(0)
        self.undo_stack.append(self.image.copy())
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.update()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.update()

    # --- Получение пера ---
    def get_pen(self):
        color = Qt.GlobalColor.white if self.eraser_mode else self.pen_color
        return QPen(color, self.pen_width, Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

    # --- Изменение размера ---
    def ask_new_size(self):
        w, ok1 = QInputDialog.getInt(self, "Ширина", "Введите ширину:", self.width(), 100, 4000)
        if not ok1:
            return None, None
        h, ok2 = QInputDialog.getInt(self, "Высота", "Введите высоту:", self.height(), 100, 4000)
        if not ok2:
            return None, None
        return w, h

    def resize_canvas(self):
        w, h = self.ask_new_size()
        if w and h:
            self.push_history()
            new_img = QImage(QSize(w, h), QImage.Format.Format_RGB32)
            new_img.fill(Qt.GlobalColor.white)
            painter = QPainter(new_img)
            painter.drawImage(0, 0, self.image.scaled(w, h))
            painter.end()
            self.image = new_img
            self.setFixedSize(w, h)
            self.update()

    # --- Рисование ---
    def paintEvent(self, event):
        QPainter(self).drawImage(0, 0, self.image)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.push_history()
            self.drawing = True
            self.last_point = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.drawing:
            painter = QPainter(self.image)
            painter.setPen(self.get_pen())
            painter.drawLine(self.last_point, event.position().toPoint())
            painter.end()
            self.last_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    # --- Инструменты ---
    def clear(self):
        self.push_history()
        self.image.fill(Qt.GlobalColor.white)
        self.update()

    def save(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить", "", "PNG (*.png);;JPEG (*.jpg)")
        if path:
            self.image.save(path)

    def set_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.pen_color = color
            self.eraser_mode = False

    def toggle_eraser(self):
        self.eraser_mode = not self.eraser_mode

    def insert_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Вставить фото", "", "Изображения (*.png *.jpg *.jpeg *.bmp)")
        if path:
            img = QImage(path)
            if img.isNull():
                QMessageBox.warning(self, "Ошибка", "Не удалось открыть изображение")
                return
            self.push_history()
            painter = QPainter(self.image)
            x = (self.width() - img.width()) // 2
            y = (self.height() - img.height()) // 2
            painter.drawImage(x, y, img.scaled(self.image.size(), Qt.AspectRatioMode.KeepAspectRatio))
            painter.end()
            self.update()


class GoofyTools:
    def __init__(self, canvas):
        self.canvas = canvas
        self.messages = [
            "Попробуй использовать фиолетовый.",
            "Ты рисуешь как два курсора — и это талант.",
            "Иногда кот — это уже шедевр.",
        ]

    def random_mess(self):
        """Добавляет случайные фигуры на холст — точки, линии и круги."""
        import random
        painter = QPainter(self.canvas.image)

        for _ in range(40):
            # Случайный цвет
            color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            pen = QPen(color, random.randint(2, 8))
            painter.setPen(pen)

            # Случайный выбор фигуры
            shape = random.choice(["point", "line", "circle"])
            x1 = random.randint(0, self.canvas.width())
            y1 = random.randint(0, self.canvas.height())
            x2 = random.randint(0, self.canvas.width())
            y2 = random.randint(0, self.canvas.height())

            if shape == "point":
                painter.drawPoint(x1, y1)
            elif shape == "line":
                painter.drawLine(x1, y1, x2, y2)
            else:  # circle
                r = random.randint(10, 80)
                painter.drawEllipse(x1, y1, r, r)

        painter.end()
        self.canvas.update()

    def surprise(self):
        choice = random.choice(["rainbow", "green", "certificate"])
        if choice == "rainbow":
            self.canvas.image.fill(QColor(255, 192, 203))
        elif choice == "green":
            self.canvas.image.fill(QColor(0, 255, 0))
        else:
            QMessageBox.information(self.canvas, "Сюрприз!", "🎨 Сертификат художника!\nТы прошёл Paint-тест!")
        self.canvas.update()

    def meme_generator(self):
        painter = QPainter(self.canvas.image)
        painter.setPen(QColor("black"))
        painter.setFont(QFont("Comic Sans MS", 24))
        painter.drawText(50, 100, "Когда ты рисуешь в PyQt6, но забыл сохранить 😅")
        painter.end()
        self.canvas.update()

    def delayed_draw(self):
        painter = QPainter(self.canvas.image)
        painter.setPen(self.canvas.get_pen())
        for i in range(0, self.canvas.width(), 50):
            painter.drawLine(i, i//2, i+20, i//2+20)
            time.sleep(0.05)
        painter.end()
        self.canvas.update()

    def motivational_ai(self):
        tip = random.choice(self.messages)
        QMessageBox.information(self.canvas, "AI совет 🎭", tip)


class PaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Paint + Goofy Tools")
        self.canvas = Canvas()
        self.goofy = GoofyTools(self.canvas)

        # --- Панель инструментов ---
        btn_color = QPushButton("Цвет")
        btn_color.clicked.connect(self.canvas.set_color)

        btn_eraser = QPushButton("Ластик")
        btn_eraser.clicked.connect(self.canvas.toggle_eraser)

        btn_clear = QPushButton("Очистить")
        btn_clear.clicked.connect(self.canvas.clear)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.canvas.save)

        btn_open = QPushButton("Вставить фото")
        btn_open.clicked.connect(self.canvas.insert_image)

        btn_resize = QPushButton("Изменить размер")
        btn_resize.clicked.connect(self.canvas.resize_canvas)

        btn_goofy = QPushButton("Goofy Tools")
        btn_goofy.clicked.connect(self.show_goofy_menu)

        btn_undo = QPushButton("Отменить (Ctrl+Z)")
        btn_undo.clicked.connect(self.canvas.undo)

        btn_redo = QPushButton("Повторить (Ctrl+Y)")
        btn_redo.clicked.connect(self.canvas.redo)

        lbl_size = QLabel("Толщина:")
        spin_size = QSpinBox()
        spin_size.setRange(1, 50)
        spin_size.setValue(3)
        spin_size.valueChanged.connect(lambda v: setattr(self.canvas, "pen_width", v))

        # --- Разметка интерфейса ---
        controls = QHBoxLayout()
        for w in [btn_color, btn_eraser, btn_clear, btn_open, btn_resize,
                  btn_save, btn_undo, btn_redo, btn_goofy, lbl_size, spin_size]:
            controls.addWidget(w)
        controls.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(controls)
        layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_goofy_menu(self):
        menu = QMenu()
        menu.addAction("🎲 Случайная ерунда", self.goofy.random_mess)
        menu.addAction("🎁 Сюрприз", self.goofy.surprise)
        menu.addAction("😂 Мем-генератор", self.goofy.meme_generator)
        menu.addAction("🐢 Замедленное рисование", self.goofy.delayed_draw)
        menu.addAction("🧠 AI-подсказки", self.goofy.motivational_ai)
        menu.exec(QCursor.pos())

    def keyPressEvent(self, e):
        if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if e.key() == Qt.Key.Key_Z:
                self.canvas.undo()
            elif e.key() == Qt.Key.Key_Y:
                self.canvas.redo()
        else:
            super().keyPressEvent(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaintApp()
    window.show()
    sys.exit(app.exec())
