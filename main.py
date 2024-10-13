import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, font
from regulation_manager import RegulationManager
from requirement_checker import RequirementChecker
from docx import Document
import pdfplumber

class ReportCheckerApp:
    def __init__(self, master):
        self.master = master
        master.title("Проверка отчетов на соответствие регламентам")
        master.geometry("1000x600")
        master.configure(bg="#f0f0f0")

        # Шрифт для заголовков
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.text_font = font.Font(family="Helvetica", size=12)

        # Заголовок приложения
        self.title_label = tk.Label(master, text="Проверка отчетов", font=self.title_font, bg="#f0f0f0")
        self.title_label.grid(row=0, column=1, pady=10)

        # Менеджер регламентов
        self.regulation_manager = RegulationManager()
        self.requirement_checker = RequirementChecker(self.regulation_manager)

        # Загрузка регламентов
        self.load_regulations()

        # Левая панель с прошлыми файлами
        self.recent_files_label = tk.Label(master, text="Последние файлы:", font=self.text_font, bg="#f0f0f0")
        self.recent_files_label.grid(row=1, column=0, padx=10, sticky="nw")

        self.recent_files_listbox = tk.Listbox(master, font=self.text_font, width=30, height=20)
        self.recent_files_listbox.grid(row=2, column=0, padx=10, pady=10, sticky="nw")
        self.recent_files_listbox.bind("<<ListboxSelect>>", self.open_recent_file)

        # Кнопка "ОБЗОР" для выбора файла
        self.browse_button = tk.Button(master, text="ОБЗОР", command=self.load_report, font=self.text_font, bg="#4CAF50", fg="white")
        self.browse_button.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        # Поле для вывода результатов с настройкой шрифта, отключаем перенос слов
        self.text_area = scrolledtext.ScrolledText(master, width=70, height=25, font=self.text_font, wrap="none")
        self.text_area.grid(row=2, column=1, padx=10, pady=10)

        # Хранение последних файлов (полный путь)
        self.recent_files_paths = []
        # Хранение последних имен файлов (для отображения)
        self.recent_files = []

    def load_regulations(self):
        """Загружает регламенты из указанных папок."""
        self.regulation_manager.load_regulations(r"C:\Users\user\Documents\hack\hack\data\regulations")

    def load_report(self):
        """Открывает диалоговое окно для выбора файла и проверяет его."""
        file_path = filedialog.askopenfilename(
            title="Выберите файл отчета", 
            filetypes=(("Word and PDF files", "*.docx *.pdf"), ("All files", "*.*"))
        )
        if file_path:
            self.process_report(file_path)

    def process_report(self, file_path):
        """Обрабатывает файл отчета и проверяет его."""
        requirements = self.load_requirements(file_path)
        if requirements:
            # Извлекаем имя файла без пути и расширения
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            # Передаем имя файла в функцию проверки
            results = self.requirement_checker.check_requirements(requirements, file_name)
            self.display_results(results)
            self.save_recent_file(file_path)

    def load_requirements(self, file_path):
        """Загружает требования из файла DOCX или PDF."""
        try:
            if file_path.endswith(".docx"):
                return self.load_from_docx(file_path)
            elif file_path.endswith(".pdf"):
                return self.load_from_pdf(file_path)
            else:
                messagebox.showerror("Ошибка", "Неверный формат файла. Используйте DOCX или PDF.")
                return None
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {e}")
            return None

    def load_from_docx(self, file_path):
        """Загружает требования из DOCX файла."""
        doc = Document(file_path)
        return [para.text.strip() for para in doc.paragraphs if para.text.strip()]

    def load_from_pdf(self, file_path):
        """Загружает требования из PDF файла."""
        requirements = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    requirements.extend([line.strip() for line in text.split("\n") if line.strip()])
        return requirements

    def display_results(self, results):
        """Отображает результаты проверки в текстовом поле."""
        self.text_area.delete(1.0, tk.END)  # Очистка текстового поля
        self.text_area.insert(tk.END, results)

    def save_recent_file(self, file_path):
        """Сохраняет файл в список недавних."""
        file_name = os.path.basename(file_path)
        if file_name not in self.recent_files:
            self.recent_files.append(file_name)
            self.recent_files_paths.append(file_path)
            self.recent_files_listbox.insert(tk.END, file_name)

        # Ограничение на 5 последних файлов
        if len(self.recent_files) > 5:
            self.recent_files.pop(0)
            self.recent_files_paths.pop(0)
            self.recent_files_listbox.delete(0)

    def open_recent_file(self, event):
        """Открывает выбранный файл из списка последних."""
        selection = self.recent_files_listbox.curselection()
        if selection:
            index = selection[0]
            file_path = self.recent_files_paths[index]
            self.process_report(file_path)  # Перезагружаем файл

if __name__ == "__main__":
    root = tk.Tk()
    app = ReportCheckerApp(root)
    root.mainloop()
