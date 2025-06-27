import tkinter as tk
from tkinter import ttk, Menu
from tkinter import messagebox
from math import cos, sin, pi

# Базовий клас для побудови Квітки життя
class FlowerOfLife:
    def __init__(self, circle_count=7, radius=50):
        self.circle_count = circle_count  # Кількість кіл
        self.radius = radius              # Радіус кожного кола
        self.canvas_width = 600           # Ширина полотна
        self.canvas_height = 600          # Висота полотна
        self.center_x = self.canvas_width / 2  # Центр по осі X
        self.center_y = self.canvas_height / 2 # Центр по осі Y

    def get_points(self):
        # Обчислює координати центрів усіх кіл, розташованих по колу
        points = []
        for i in range(self.circle_count):
            angle = 2 * pi * i / self.circle_count
            x = self.radius * cos(angle)
            y = self.radius * sin(angle)
            points.append((x, y))
        return points

# Клас-нащадок, що додає колір і трансформації
class ColoredFlowerOfLife(FlowerOfLife):
    def __init__(self, circle_count=7, radius=50, color="black"):
        super().__init__(circle_count, radius)
        self.color = color                    # Колір обводки
        self.rotation_angle = 0               # Кут повороту (в радіанах)
        self.scale_factor = 1.0               # Масштаб
        self.translate_x = 0                  # Зсув по X
        self.translate_y = 0                  # Зсув по Y

    def __mul__(self, factor):
        # Масштабування: оператор *
        self.scale_factor *= factor
        return self

    def __add__(self, angle_degrees):
        # Поворот: оператор +
        self.rotation_angle += angle_degrees * pi / 180
        return self

    def __sub__(self, translation):
        # Зсув: оператор -
        if isinstance(translation, tuple) and len(translation) == 2:
            self.translate_x += translation[0]
            self.translate_y += translation[1]
        return self

    def mirror(self, axis='x'):
        # Дзеркальне відображення по осі X або Y
        if axis == 'x':
            self.translate_y = -self.translate_y
        elif axis == 'y':
            self.translate_x = -self.translate_x
        return self

    def __xor__(self, shear_factor):
        # Скошування (оператор ^)
        self.translate_x += shear_factor * self.translate_y
        return self

    def get_transformed_points(self):
        # Повертає точки після масштабування, повороту та зсуву
        points = super().get_points()
        transformed = []
        for x, y in points:
            x_scaled = x * self.scale_factor
            y_scaled = y * self.scale_factor

            x_rot = x_scaled * cos(self.rotation_angle) - y_scaled * sin(self.rotation_angle)
            y_rot = x_scaled * sin(self.rotation_angle) + y_scaled * cos(self.rotation_angle)

            x_final = x_rot + self.center_x + self.translate_x
            y_final = y_rot + self.center_y + self.translate_y
            transformed.append((x_final, y_final))
        return transformed

# Головний клас застосунку з графічним інтерфейсом
class FlowerOfLifeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Centered Flower of Life")
        self.geometry("800x700")

        # Змінні, які зв'язуються з полями введення
        self.circle_count_var = tk.IntVar(value=7)
        self.radius_var = tk.DoubleVar(value=50)
        self.color_var = tk.StringVar(value="black")

        # Створення початкової фігури
        self.flower = ColoredFlowerOfLife(
            circle_count=self.circle_count_var.get(),
            radius=self.radius_var.get(),
            color=self.color_var.get()
        )

        self.create_menu()
        self.create_widgets()
        self.create_canvas()

    def create_menu(self):
        # Створення меню з пунктами "Файл" і "Довідка"
        menu_bar = Menu(self)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Вихід", command=self.quit)
        menu_bar.add_cascade(label="Файл", menu=file_menu)

        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Про програму", command=lambda: messagebox.showinfo(
            "Інфо", "Програма для малювання центрованої Квітки життя з трансформаціями"))
        menu_bar.add_cascade(label="Довідка", menu=help_menu)

        self.config(menu=menu_bar)

    def create_widgets(self):
        # Створення панелі з полями введення параметрів
        controls = ttk.Frame(self)
        controls.pack(pady=5, fill=tk.X)

        ttk.Label(controls, text="Кількість кіл:").grid(row=0, column=0, padx=5, sticky="w")
        ttk.Entry(controls, textvariable=self.circle_count_var, width=10).grid(row=0, column=1, padx=5)

        ttk.Label(controls, text="Радіус:").grid(row=1, column=0, padx=5, sticky="w")
        ttk.Entry(controls, textvariable=self.radius_var, width=10).grid(row=1, column=1, padx=5)

        ttk.Label(controls, text="Колір:").grid(row=2, column=0, padx=5, sticky="w")
        ttk.Entry(controls, textvariable=self.color_var, width=10).grid(row=2, column=1, pady=5)

        # Кнопки для трансформацій
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=5, fill=tk.X)

        ttk.Button(button_frame, text="Масштабувати x1.5", command=lambda: self.transform(self.flower * 1.5)).grid(row=0, column=0, padx=2)
        ttk.Button(button_frame, text="Повернути 45°", command=lambda: self.transform(self.flower + 45)).grid(row=0, column=1, padx=2)
        ttk.Button(button_frame, text="Побудувати", command=self.update_and_draw).grid(row=0, column=2, padx=2)

    def create_canvas(self):
        # Створення області малювання
        self.canvas = tk.Canvas(self, width=600, height=600, bg="white")
        self.canvas.pack(pady=10)

    def draw_circle(self, x, y, r):
        # Малює одне коло з центром (x, y) та радіусом r
        self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=self.flower.color)

    def update_and_draw(self):
        # Оновлює фігуру за новими параметрами з полів введення і малює її
        try:
            self.flower = ColoredFlowerOfLife(
                circle_count=max(1, self.circle_count_var.get()),
                radius=max(10, self.radius_var.get()),
                color=self.color_var.get() or "black"
            )
            self.draw()
        except tk.TclError:
            messagebox.showerror("Помилка", "Введіть коректні числові значення!")

    def draw(self):
        # Малює всі кола на полотні відповідно до трансформованих координат
        self.canvas.delete("all")  # Очистити попереднє зображення
        points = self.flower.get_transformed_points()
        radius = self.flower.radius * self.flower.scale_factor

        for x, y in points:
            self.draw_circle(x, y, radius)
            for x2, y2 in points:
                if (x, y) != (x2, y2):
                    dist = ((x - x2) ** 2 + (y - y2) ** 2) ** 0.5
                    if dist <= 2 * radius:
                        self.draw_circle(x2, y2, radius)

    def transform(self, flower):
        # Застосовує трансформацію та перемальовує фігуру
        self.flower = flower
        self.draw()

# Запуск програми
if __name__ == "__main__":
    app = FlowerOfLifeApp()
    app.mainloop()
