
import sys
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QPainter, QPen, QColor, QImage
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QColorDialog, QVBoxLayout, QPushButton, QFileDialog,
    QHBoxLayout, QSpinBox, QLabel, QInputDialog, QMessageBox
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
        self.max_history = 30

    # --- Служебные методы истории ---
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

    # --- Основное рисование ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.push_history()
            self.drawing = True
            self.last_point = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.drawing:
            painter = QPainter(self.image)
            color = Qt.GlobalColor.white if self.eraser_mode else self.pen_color
            pen = QPen(color, self.pen_width, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.position().toPoint())
            painter.end()
            self.last_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    # --- Кнопочные действия ---
    def clear(self):
        self.push_history()
        self.image.fill(Qt.GlobalColor.white)
        self.update()

    def save(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить изображение", "", "PNG (*.png);;JPEG (*.jpg)")
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
        """Открыть картинку и вставить её на холст"""
        path, _ = QFileDialog.getOpenFileName(self, "Открыть изображение", "", "Изображения (*.png *.jpg *.jpeg *.bmp)")
        if path:
            img = QImage(path)
            if img.isNull():
                QMessageBox.warning(self, "Ошибка", "Не удалось открыть изображение")
                return
            self.push_history()
            painter = QPainter(self.image)
            # Вписать в холст по центру
            x = (self.width() - img.width()) // 2
            y = (self.height() - img.height()) // 2
            painter.drawImage(x, y, img.scaled(self.image.size(), Qt.AspectRatioMode.KeepAspectRatio))
            painter.end()
            self.update()

    def resize_canvas(self):
        """Изменить размер холста"""
        w, ok1 = QInputDialog.getInt(self, "Ширина", "Введите новую ширину (пиксели):", self.width(), 100, 4000)
        if not ok1:
            return
        h, ok2 = QInputDialog.getInt(self, "Высота", "Введите новую высоту (пиксели):", self.height(), 100, 4000)
        if not ok2:
            return

        self.push_history()
        new_img = QImage(QSize(w, h), QImage.Format.Format_RGB32)
        new_img.fill(Qt.GlobalColor.white)
        painter = QPainter(new_img)
        painter.drawImage(0, 0, self.image.scaled(w, h))
        painter.end()

        self.image = new_img
        self.setFixedSize(w, h)
        self.update()


class PaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Paint (PyQt6 — Undo/Redo, Фото, Размер)")
        self.canvas = Canvas()

        # Кнопки инструментов
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

        btn_undo = QPushButton("Отменить (Ctrl+Z)")
        btn_undo.clicked.connect(self.canvas.undo)

        btn_redo = QPushButton("Повторить (Ctrl+Y)")
        btn_redo.clicked.connect(self.canvas.redo)

        # Толщина кисти
        lbl_size = QLabel("Толщина:")
        spin_size = QSpinBox()
        spin_size.setRange(1, 50)
        spin_size.setValue(3)
        spin_size.valueChanged.connect(lambda v: setattr(self.canvas, "pen_width", v))

        # Панель управления
        controls = QHBoxLayout()
        for widget in [btn_color, btn_eraser, btn_clear, btn_open, btn_resize,
                       btn_save, btn_undo, btn_redo, lbl_size, spin_size]:
            controls.addWidget(widget)
        controls.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(controls)
        layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # --- Горячие клавиши ---
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
