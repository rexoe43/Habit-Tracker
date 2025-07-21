import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import calendar
from collections import defaultdict

class HabitTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Habit Tracker - Seguimiento de Habitos")
        self.root.geometry("1100x800")

        # Configuracion de temas
        self.current_theme = "light"
        self.themes = {
            "light": {
                "bg_primary": "#f0f4f8",
                "bg_secondary": "white",
                "bg_accent": "#4338ca",
                "text_primary": "#1e293b",
                "text_secondary": "#64748b",
                "text_accent": "white",
                "border": "#e2e8f0",
                "success": "#059669",
                "danger": "#dc2626",
                "card_bg": "white",
                "stats_bg": "#f8fafc"
            },
            "dark": {
                "bg_primary": "#0f172a",
                "bg_secondary": "#1e293b",
                "bg_accent": "#6366f1",
                "text_primary": "#f1f5f9",
                "text_secondary": "#94a3b8",
                "text_accent": "white",
                "border": "#334155",
                "success": "#10b981",
                "danger": "#ef4444",
                "card_bg": "#1e293b",
                "stats_bg": "#0f172a"
            }
        }

        # Datos 
        self.data_file = "habits_data.json"
        self.habits = {}
        self.completions = defaultdict(set) # {habit_name: set(dates)}
        self.selected_habit_for_calendar = None

        # Cargar datos exsistentes
        self.load_data()

        # Configurar estilos
        self.setup_styles()

        # Crear interfaz
        self.create_widgets()

        # Actualizar vista
        self.refresh_display()
        self.apply_theme()

    def get_theme(self, key):
        """Obtener color del tema actual"""
        return self.themes[self.current_theme][key]
    
    def toggle_theme(self):
        """Cambiar entre tema claro y oscuro"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()

    def apply_theme(self):
        """Aplicar tema actual a todos los widgets"""
        # Configurar root
        self.root.configure(bg=self.get_theme("bg_primary"))

        # Aplicar tema recursivamente
        self._apply_theme_recursive(self.root)

        # Actualizar estilos de ttk
        self.setup_styles()

    def _apply_theme_recursive(self, widget):
        """Aplicar tema recursivamente a widgets"""
        widget_class = widget.winfo_class()

        if widget_class == "Frame":
            if hasattr(widget, '_theme_type'):
                if widget._theme_type == 'card':
                    widget.configure(bg=self.get_theme("card_bg"))
                elif widget._theme_type == 'stats':
                    widget.configure(bg=self.get_theme("stats_bg"))
                elif widget._theme_type == 'header':
                    widget.configure(bg=self.get_theme("bg_accent"))
                else:
                    widget.configure(bg=self.get_theme("bg_primary"))
            else:
                widget.configure(bg=self.get_theme("bg_primary"))
        
        elif widget_class == "Label":
            if hasattr(widget, '_theme_type'):
                if widget._theme_type == 'header':
                    widget.configure(bg=self.get_theme("bg_accent"), fg=self.get_theme("text_accent"))
                elif widget._theme_type == 'accent':
                    widget.configure(bg=self.get_theme("bg_accent"), fg=self.get_theme("text_accent"))
                elif widget._theme_type == 'card':
                    widget.configure(bg=self.get_theme("card_bg"), fg=self.get_theme("text_primary"))
                elif widget._theme_type == 'stats':
                    widget.configure(bg=self.get_theme("stats_bg"), fg=self.get_theme("text_primary"))
                elif widget._theme_type == 'secondary':
                    widget.configure(bg=self.get_theme("card_bg"), fg=self.get_theme("text_secondary"))
                else:
                    widget.configure(bg=self.get_theme("bg_primary"), fg=self.get_theme("text_primary"))
            else:
                # Detectar por color de fondo actual
                current_bg = str(widget.cget("bg"))
                if current_bg in ["white", "#ffffff"]:
                    widget.configure(bg=self.get_theme("card_bg"), fg=self.get_theme("text_primary"))
                else:
                    widget.configure(bg=self.get_theme("bg_primary"), fg=self.get_theme("text_primary"))

        elif widget_class == "Button":
            # Los botones mantienen sus colores especificos
            pass
        elif widget_class == "Canvas":
            widget.configure(bg=self.get_theme("bg_primary"))

        # Aplicar recursivamente a hijos
        for child in widget.winfo_children():
            self._apply_theme_recursive(child)

    def setup_styles(self):
        """Configurar estilos personalizados"""
        style = ttk.Style()
        style.theme_use('clam')

        # Estilo para botones principales
        style.configure("Primary.TButton",
                        background=self.get_theme("bg_accent"),
                        foreground=self.get_theme("text_accent"),
                        padding=(10, 8),
                        font=("Arial", 10, "bold"))
        
        # Estilos para notebook (pestañas)
        style.configure("Custom.TNotebook",
                        background=self.get_theme("bg_primary"))
        style.configure("Custom.TNotebook.Tab",
                        background=self.get_theme("bg_secondary"),
                        foreground=self.get_theme("text_primary"),
                        padding=[20, 10])
        
        # Estilo para combobox
        style.configure("Custom.TCombobox",
                        fieldbackground=self.get_theme("card_bg"),
                        background=self.get_theme("card_bg"),
                        foreground=self.get_theme("text_primary"))
        
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Header con boton de tema
        self.create_header()

        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.root, style="Custom.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Pestaña principal (habitos)
        self.create_main_tab()

        # Pestaña calendario
        self.create_calendar_tab()
    
    def create_header(self):
        """Crear el header de la aplicacion"""
        header_frame = tk.Frame(self.root, height=100)
        header_frame._theme_type = 'header'
        header_frame.pack(fill="x", padx=20, pady=(20, 20))
        header_frame.pack_propagate(False)

        # Titulo
        title_label = tk.Label(header_frame,
                               text=" Habit Tracker",
                               font=("Arial", 24, "bold"))
        title_label._theme_type = 'header'
        title_label.pack(side="left", padx=20, pady=20)

        # Botones del header
        header_buttons = tk.Frame(header_frame)
        header_buttons._theme_type = 'header'
        header_buttons.pack(side="right", padx=20, pady=20)

        # Boton cambiar tema
        theme_text = " Oscuro" if self.current_theme == "light" else "Claro"
        self.theme_button = tk.Button(header_buttons, text=theme_text,
                                      command=self.toggle_theme,
                                      bg=self.get_theme("card_bg"),
                                      fg=self.get_theme("text_primary"),
                                      font=("Arial", 10, "bold"),
                                      relief="solid", bd=1)
        self.theme_button.pack()
    
    def create_main_tab(self):
        """Crear pestaña principal con habitos"""
        # Frame principal con scrollbar
        main_frame = tk.Frame(self.notebook)
        main_frame.configure(bg=self.get_theme("bg_primary"))

        main_canvas = tk.Canvas(main_frame, bg=self.get_theme("bg_primary"))
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = tk.Frame(main_canvas)
        self.scrollable_frame.configure(bg=self.get_theme("bg_primary"))

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        # Estadisticas
        self.create_stats_section()

        # Formulario para agregar habito
        self.create_add_habit_form()

        # Lista de habitos
        self.create_habits_section()

        # Configurar scroll con mouse
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        main_canvas.bind("<MouseWheel>", _on_mousewheel)

        # Packs canvas y scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Agregar al notebook
        self.notebook.add(main_frame, text=" Habitos")

    def create_calendar_tab(self):
        """Crear pestaña de calendario"""
        calendar_frame = tk.Frame(self.notebook)
        calendar_frame.configure(bg=self.get_theme("bg_primary"))

        # Frame principal del calendario
        main_cal_frame = tk.Frame(calendar_frame)
        main_cal_frame.configure(bg=self.get_theme("bg_primary"))
        main_cal_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Titulo y selector de habito
        top_frame = tk.Frame(main_cal_frame)
        top_frame.configure(bg=self.get_theme("bg_primary"))
        top_frame.pack(fill="x", pady=(0, 20))

        tk.Label(top_frame, text="Calendario de habitos",
                 font=("Arial", 18, "bold")).pack(side="left")
        
        # Selector de habito
        selector_frame = tk.Frame(top_frame)
        selector_frame.configure(bg=self.get_theme("bg_primary"))
        selector_frame.pack(side="right")

        tk.Label(selector_frame, text="Habito",
                 font=("Arial", 12)).pack(side="left", padx=(0,5))
        
        self.habit_selector = ttk.Combobox(selector_frame, width=20,
                                          style="Custom.TCombobox")
        
        self.habit_selector.pack(side="left")
        self.habit_selector.bind('<<ComboboxSelected>>', self.on_habit_selected)

        # Frame del calendario
        self.calendar_frame = tk.Frame(main_cal_frame)
        self.calendar_frame.configure(bg=self.get_theme("bg_primary"))
        self.calendar_frame.pack(fill="both", expand=True)

        # Controles de navegacion del calendario
        nav_frame = tk.Frame(self.calendar_frame)
        nav_frame.configure(bg=self.get_theme("bg_primary"))
        nav_frame.pack(fill="x", pady=(0, 20))

        self.prev_button = tk.Button(nav_frame, text="< Anterior",
                                     command=self.prev_month,
                                     bg=self.get_theme("bg_accent"),
                                     fg=self.get_theme("text_accent"),
                                     font=("Arial", 10, "bold"))
        self.prev_button.pack(side="left")

        self.month_label = tk.Label(nav_frame, text="",
                                    font=("Arial", 16, "bold"))
        self.month_label.pack(side="left", expand=True)

        self.next_button = tk.Button(nav_frame, text="> Siguiente",
                                     command=self.next_month,
                                     bg=self.get_theme("bg_accent"),
                                     fg=self.get_theme("text_accent"),
                                     font=("Arial", 10, "bold"))
        self.next_button.pack(side="right")

        # Variables para el calendario
        self.current_cal_date = datetime.now()

        # Grid del calendario
        self.calendar_grid_frame = tk.Frame(self.calendar_frame)
        self.calendar_grid_frame.configure(bg=self.get_theme("bg_primary"))
        self.calendar_grid_frame.pack(fill="both", expand=True)

        self.notebook.add(calendar_frame, text=" Calendario")

        # Actualizar calendario inicial
        self.update_calendar()

    def on_habit_selected(self, event=None):
        """Cuando se selecciona un habito en el calendario"""
        selected = self.habit_selector.get()
        if selected and selected in self.habits:
            self.selected_habit_for_calendar = selected
            self.update_calendar()

    def prev_month(self):
        """Ir al mes anterior"""
        if self.current_cal_date.month == 1:
            self.current_cal_date = self.current_cal_date.replace(year=self.current_cal_date.year-1, month=12)
        else: 
            self.current_cal_date = self.current_cal_date.replace(month=self.current_cal_date.month-1)
        self.update_calendar()

    def next_month(self):
        """Ir al mes siguiente"""
        if self.current_cal_date.month == 12:
            self.current_cal_date = self.current_cal_date.replace(year=self.current_cal_date.year+1, month=1)
        else:
            self.current_cal_date = self.current_cal_date.replace(month=self.current_cal_date.month+1)
        self.update_calendar()

    def update_calendar(self):
        """Actualizar el calendario"""
        # Limpiar grid anterior
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()

        # Actualizar selector de habitos
        habit_names = list(self.habits.keys()) if self.habits else []
        self.habit_selector['values'] = habit_names

        if not self.selected_habit_for_calendar and habit_names:
            self.selected_habit_for_calendar = habit_names[0]
            self.habit_selector.set(self.selected_habit_for_calendar)

        # Actualizar etiqueta del mes
        month_year = self.current_cal_date.strftime("%B %Y").title()
        self.month_label.configure(text=month_year)

        if not self.selected_habit_for_calendar:
            no_habit_label = tk.Label(self.calendar_grid_frame,
                                      text="No hay habitos para mostrar",
                                      font=("Arial", 14),
                                      fg=self.get_theme("text_secondary"))
            no_habit_label.pack(expand=True)
            return
        
        # Crear calendario
        cal = calendar.monthcalendar(self.current_cal_date.year, self.current_cal_date.month)

        # Headers de dias de la semana
        days = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']
        for i, day in enumerate(days):
            header = tk.Label(self.calendar_grid_frame, text=day,
                              font=("Arial", 12, "bold"),
                              fg=self.get_theme("text_secondary"))
            header._theme_type = 'secondary'
            header.grid(row=0, column=i, pady=1, padx=1, sticky="nsew")

        # Dias del calendario
        completions = self.completions.get(self.selected_habit_for_calendar, set())

        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Dia vacio
                    empty_frame = tk.Frame(self.calendar_grid_frame,
                                           width=60, height=60,
                                           bg=self.get_theme("bg_primary"))
                    empty_frame.grid(row=week_num+1, column=day_num, padx=1, pady=1, sticky="nsew")
                else:
                    # Dia del mes
                    date_str = f"{self.current_cal_date.year}-{self.current_cal_date.month:02d}-{day:02d}"
                    is_completed = date_str in completions
                    is_today = (datetime.now().date() ==
                                datetime(self.current_cal_date.year, self.current_cal_date.month, day).date())
                    
                    # Color del dia
                    if is_completed:
                        bg_color = self.get_theme("success")
                        text_color = "white"
                    elif is_today:
                        bg_color = self.get_theme("bg_accent")
                        text_color = "white"
                    else:
                        bg_color = self.get_theme("card_bg")
                        text_color = self.get_theme("text_primary")

                    day_frame = tk.Frame(self.calendar_grid_frame,
                                         width=60, height=60,
                                         bg=bg_color,
                                         relief="solid", bd=1)
                    day_frame.grid(row=week_num+1, column=day_num, padx=1, pady=1, sticky="nsew")
                    day_frame.pack_propagate(False)

                    day_label = tk.Label(day_frame, text=str(day),
                                         bg=bg_color, fg=text_color,
                                         font=("Arial", 12, "bold"))
                    day_label.pack(expand=True)

                    # Indicador visual para dias completados
                    if is_completed:
                        check_label = tk.Label(day_frame, text="✓",
                                               bg=bg_color, fg=text_color,
                                               font=("Arial", 8, "bold"))
                        check_label.place(relx=0.8, rely=0.2)

            # Configurar peso de filas y columnas
            for i in range(7):
                self.calendar_grid_frame.columnconfigure(i, weight=1)
            for i in range(len(cal)+1):
                self.calendar_grid_frame.rowconfigure(i, weight=1)

            # Actualizar tema del calendario
            self._apply_theme_recursive(self.calendar_grid_frame)
        
    def create_stats_section(self):
        """Crear seccion de estadisticas"""
        stats_frame = tk.Frame(self.scrollable_frame)
        stats_frame.pack(fill="x", padx=0, pady=20)

        tk.Label(stats_frame,
                 text="Estadisticas",
                 font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Frame para las estadisticas
        self.stats_container = tk.Frame(stats_frame)
        self.stats_container.pack(fill="x")
    
    def create_add_habit_form(self):
        """Crear formulario para agregar habitos"""
        form_frame = tk.Frame(self.scrollable_frame, relief="solid", bd=1)
        form_frame._theme_type = 'card'
        form_frame.pack(fill="x", pady=(0, 20))

        title_label = tk.Label(form_frame,
                               text="Agregar Nuevo Habito",
                               font=("Arial", 16, "bold"))
        title_label._theme_type = 'card'
        title_label.pack(anchor="w", padx=20, pady=(20, 10))

        input_frame = tk.Frame(form_frame)
        input_frame._theme_type = 'card'
        input_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Nombre del habito
        name_label = tk.Label(input_frame, text="Nombre del habito:")
        name_label._theme_type = 'card'
        name_label.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.habit_name_entry = tk.Entry(input_frame, width=30, font=("Arial", 11),
                                         bg=self.get_theme("card_bg"),
                                         fg=self.get_theme("text_primary"),
                                         relief="solid", bd=1)
        self.habit_name_entry.grid(row=0, column=1, padx=(0,20))

        # Categoria
        cat_label = tk.Label(input_frame, text="Categoria:")
        cat_label._theme_type = 'card'
        cat_label.grid(row=0, column=2, sticky="w", padx=(0, 10))

        self.category_var = tk.StringVar(value="Salud")
        category_combo = ttk.Combobox(input_frame, textvariable=self.category_var,
                                      values=["Salud", "Ejercicio", "Estudio", "Trabajo", "Personal", "Otro"],
                                      style="Custom.TCombobox")
        category_combo.grid(row=0, column=3, padx=(0, 20))

        # Descripcion
        desc_label = tk.Label(input_frame, text="Descripcion:")
        desc_label._theme_type = 'card'
        desc_label.grid(row=1, column=0, sticky="w", pady=(10, 0), padx=(0, 10))

        self.description_entry = tk.Entry(input_frame, width=50, font=("Arial", 11),
                                          bg=self.get_theme("card_bg"),
                                          fg=self.get_theme("text_primary"),
                                          relief="solid", bd=1)
        self.description_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(10,0), padx=(0, 20))

        # Boton agregar
        add_button = ttk.Button(input_frame, text="Agregar Habito",
                                 command=self.add_habit, style="Primary.TButton")
        add_button.grid(row=1, column=3, pady=(10, 0))

        # Configurar peso de columnas
        input_frame.columnconfigure(1, weight=1)

    def create_habits_section(self):
        """Crear seccion de habitos existentes"""
        self.habits_frame = tk.Frame(self.scrollable_frame)
        self.habits_frame.pack(fill="both", expand=True, pady=(0, 20))

        habits_title = tk.Label(self.habits_frame,
                                text="Mis habitos",
                                font=("Arial", 16, "bold"))
        habits_title.pack(anchor="w", pady=(0, 15))

    def add_habit(self):
        """Agregar un nuevo habito"""
        name = self.habit_name_entry.get().strip()
        category = self.category_var.get()
        description = self.description_entry.get().strip()

        if not name:
            messagebox.showwarning("Error", "Por favor ingresa el nombre del habito")
            return
        
        if name in self.habits:
            messagebox.showwarning("Error", "Este habito ya existe")
            return
        
        # Agregar habito
        self.habits[name] = {
            "category": category,
            "description": description,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "target_frequency": "daily"
        }

        # Limpiar formulario
        self.habit_name_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

        # Guardar y actualizar 
        self.save_data()
        self.refresh_display()

        messagebox.showinfo("Exito", f"Habito '{name}' agregado correctamente")

    def toggle_habit_completion(self, habit_name):
        """Marcar/desmarcar habito como completado para hoy"""
        today = datetime.now().strftime("%Y-%m-%d")

        if today in self.completions[habit_name]:
            self.completions[habit_name].discard(today)
            status = "desmarcado"
        else:
            self.completions[habit_name].add(today)
            status = "completado"

        self.save_data()
        self.refresh_display()

        messagebox.showinfo("Actualizado", f"Habito '{habit_name}' {status} para hoy")

    def delete_habit(self, habit_name):
        """Eliminar un habito"""
        if messagebox.askyesno("Confirmar", f"¿Estas seguro de eliminar '{habit_name}'?"):
            del self.habits[habit_name]
            if habit_name in self.completions:
                del self.completions[habit_name]

            # Actualizar selector del calendario
            if self.selected_habit_for_calendar == habit_name:
                self.selected_habit_for_calendar = None

            self.save_data()
            self.refresh_display()
            messagebox.showinfo("Eliminado", f"Habito '{habit_name}' eliminado")

    def calculate_streak(self, habit_name):
        """Calcular racha actual de un habito """
        if habit_name not in self.completions:
            return 0
        
        completed_dates = sorted(self.completions[habit_name])
        if not completed_dates:
            return 0
        
        # Verificar racha desde hoy hacia atras 
        current_date = datetime.now().date()
        streak = 0

        while True:
            date_str = current_date.strftime("%Y-%m-%d")
            if date_str in completed_dates:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        return streak
    
    def calculate_completion_rate(self, habit_name, days=30):
        """Calcular porcentaje de completitud en los ultimos N dias"""
        if habit_name not in self.habits:
            return 0
        
        created_date = datetime.strptime(self.habits[habit_name]["created_date"], "%Y-%m-%d").date()
        end_date = datetime.now().date()
        start_date = max(created_date, end_date - timedelta(days=days-1))

        total_days = (end_date - start_date).days + 1
        completed_days = 0

        current_date = start_date
        while current_date <= end_date:
            if current_date.strftime("%Y-%m-%d") in self.completions[habit_name]:
                completed_days += 1
            current_date += timedelta(days=1)

        return (completed_days / total_days) * 100 if total_days > 0 else 0
    
    def refresh_display(self):
        """Actualizar toda la interfaz"""
        self.update_stats()
        self.update_habits_display()
        self.update_calendar()

        # Actualizar boton de tema
        theme_text = "Oscuro" if self.current_theme == "light" else "Claro"
        self.theme_button.configure(text=theme_text,
                                    bg=self.get_theme("card_bg"),
                                    fg=self.get_theme("text_primary"))
        
    def update_stats(self):
        """Actualizar seccion de estadisticas"""
        # limpiar estadisticas anteriores
        for widget in self.stats_container.winfo_children():
            widget.destroy()

        # Calcular estadistica
        total_habits = len(self.habits)
        today = datetime.now().strftime("%Y-%m-%d")
        completed_today = sum(1 for habit in self.habits if today in self.completions[habit])

        # Calcular racha promedio
        avg_streak = 0
        if self.habits:
            total_streak = sum(self.calculate_streak(habit) for habit in self.habits)
            avg_streak = total_streak / len(self.habits)

        # Crear cards de estadistica
        stats_data = [
            ("Habitos Totales", total_habits, self.get_theme("bg_accent")),
            ("Completados Hoy", completed_today, self.get_theme("success")),
            ("Racha Promedio", f"{avg_streak:.1f}", self.get_theme("danger")),
        ]

        for i, (label, value, color) in enumerate(stats_data):
            stat_frame = tk.Frame(self.stats_container, relief="solid", bd=1)
            stat_frame._theme_type = 'stats'
            stat_frame.configure(bg=self.get_theme("stats_bg"))
            stat_frame.pack(side="left", expand=True, fill="both", padx=10)

            stat_label = tk.Label(stat_frame, text=label,
                                  font=("Arial", 12), fg=self.get_theme("text_secondary"))
            stat_label._theme_type = 'stats'
            stat_label.pack(pady=(10, 0))

            value_label = tk.Label(stat_frame, text=str(value),
                                    font=("Arial", 20, "bold"), bg=color,
                                    fg="white", width=12, height=2)
            value_label._theme_type = 'accent'
            value_label.pack(pady=10)

    def update_habits_display(self):
        """Actualizar la lista de habitos mostrados"""
        # Limpiar habitos anteriores
        for widget in self.habits_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()

        for habit_name, habit_data in self.habits.items():
            habit_frame = tk.Frame(self.habits_frame, relief="solid", bd=1)
            habit_frame._theme_type = 'card'
            habit_frame.pack(fill="x", padx=0, pady=5)

            title_label = tk.Label(habit_frame, text=habit_name,
                                   font=("Arial", 14, "bold"))
            title_label._theme_type = 'card'
            title_label.pack(anchor="w", padx=10, pady=5)

            info_label = tk.Label(habit_frame, text=f"{habit_data['category']} - {habit_data['description']}",
                                  font=("Arial", 10))
            info_label._theme_type = 'secondary'
            info_label.pack(anchor="w", padx=10, pady=(0, 10))

            # Botones
            btn_frame = tk.Frame(habit_frame)
            btn_frame._theme_type = 'card'
            btn_frame.pack(anchor="e", padx=10, pady=(0, 10))

            complete_btn = ttk.Button(btn_frame, text="Completar Hoy",
                                      command=lambda name=habit_name: self.toggle_habit_completion(name),
                                      style="Primary.TButton")
            complete_btn.pack(side="left", padx=(0, 10))

            delete_btn = tk.Button(btn_frame, text="Eliminar",
                                   command=lambda name=habit_name: self.delete_habit(name),
                                   bg=self.get_theme("danger"),
                                   fg="white", relief="flat", font=("Arial", 10, "bold"))
            delete_btn.pack(side="left")

    def save_data(self):
        """Guardar datos a archivos JSON"""
        data = {
            "habits": self.habits,
            "completions": {k: list(v) for k, v in self.completions.items()}
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        """Cargar datos desde archivo JSON"""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.habits = data.get("habits", {})
                self.completions = defaultdict(set,
                                               {k: set(v) for k, v in data.get("completions", {})}
                                               )
    
    def run(self):
        """Ejecutar la app"""
        self.root.mainloop()

if __name__ == "__main__":
    HabitTracker().run()
