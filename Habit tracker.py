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
            """Aplciar tema recursivamente a widgets"""
            widget_class = widget.info_class()

            if widget_class == "Frame":
                if hasattr(widget, '_theme_type'):
                    if widget._theme_tyoe == 'card':
                        widget.configure(bg=self.get_theme("card_bg"))
                    elif widget._theme_type == 'stats':
                        widget.configure(bg=self.get_theme("stats_bg"))
                    elif widget._theme_type =='header':
                        widget.configure(bg=self.get_theme("bg_accent"))
                    else:
                        widget.configure(bg=self.get_theme("bg_primary"))
                else:
                    widget.configure(bg=self.get_theme("bg_primary"))
            
            elif widget_class == "Label":
                if hasattr(widget, '_theme_type'):
                    if widget._theme_type == 'header':
                        widget.configure(bg=self.get_theme("bg_accent"), fg=self.get_theme("text_accent"))
                    elif widget._theme_tyoe == 'accent':
                        widget.configure(bg=self.get_theme("bg_accent"), fg=self.get_theme("text_accent"))
                    elif widget._theme_type == 'card':
                        widget.configure(bg=self.get_theme("card_bg"),fg=self.get_theme("text_primary"))
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
            styles = ttk.Style()
            style.theme_use('clam')

            # Estilo para botones principales
            style.configure("Primary.TButton",
                            background=self.get_theme("bg_accent"),
                            foreground=self.get_theme("text_accent"),
                            padding=(10, 8),
                            font=("Arial", 10, "bold"))
            
            # Estilos apra notebook (pestañas)
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
                                          commando=self.toggle_theme,
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
            self.notebook.add(main_frame, text=" Habtitos")

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
                     font=("Arial", 18, "bold").pack(side="left"))
            
            # Selector de habito
            selector_frame = tk.Frame(top_frame)
            selector_frame.configure(bg=self.get_theme("bg_priamry"))
            selector_frame.pack(side="right")

            tk.label(selector_frame, text="Habito",
                     font=("Arial", 12)).pack(side="left", padx=(0,5))
            
            self.habit_selector= ttk.Combobox(selector_frame, width=20,
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
                                         commando=self.prev_month,
                                         bg=self.get_theme("bg_accent"),
                                         fg=self.get_theme("text_accent"),
                                         font=("Arial", 10, "bold"))
            self.prev_button.pack(side="left")

            self.month_label = tk.Label(nav_frame, text="",
                                        font=("Arial", 16, "bold"))
            self.month_label.pack(side="left", expand=True)

            self.next_button = tk.Button(nav_frame, text="> Siguiente",
                                         command=self.nex_month,
                                         bg=self.get_theme("bg_accent"),
                                         fg=self.get_theme("text_accent"),
                                         font=("Arial", 10, "bold"))
            self.next_button.pack(side="right")

            # Variables para el calendario
            self.current_cal_date = datetime.now()

            # Grid del calendario
            self.calendar_grid_frame = tk.Frame(self.calednar_frame)
            self.calendar_grid_frame.configure(bg=self.get_theme("bg_primary"))
            self.calendar_grid_frame.pack(fill="both", expand=True)

            self.notebook.add(calendar_frame, text=" Calendario")

            # Actualizar calendario inicial
            self.update.calendar()


        def on_habit_selected(self, event=None):
            """Cuando se selecciona un habigto en el calendario"""
            selected = self.habit_selector.get()
            if selected and selected in self.habits:
                self.selected_habit_for_calendar = selected
                self.update_calendar()

        def prev_month(self):
            """Ir al mes anterior"""
            if self.current_cal_date.month == 1:
                self.current_cal_date = self.current_cal_date.replace(uear=self.current_cal_date.year-1, month=12)
            else: 
                self.current_cal_date = self.current_cal_date.replace(month=self.current_cal_date.month-1)
            self.update_calendar()
