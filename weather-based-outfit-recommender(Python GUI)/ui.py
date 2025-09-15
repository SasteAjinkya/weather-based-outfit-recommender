import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import threading
from datetime import datetime
from outfit_recommender import OutfitRecommender
from db_handler import DatabaseHandler
from config import APP_TITLE, WINDOW_SIZE
from PIL import Image, ImageTk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
from bson.objectid import ObjectId

class WeatherOutfitUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(800, 650)
        self.root.resizable(True, True)

        self.recommender = OutfitRecommender()
        self.db = DatabaseHandler()

        self.spinner_frames = []
        self.load_spinner_frames()

        self.setup_styles()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_recommendation_tab()
        self.create_collection_viewer_tab()
        self.create_visualization_tab()

        self.status_label = ttk.Label(self.root, text="Ready", style='Info.TLabel')
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.weather_icon = None
        self.spinner_anim_id = None

        self.check_database_connection()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_spinner_frames(self):
        try:
            spinner_path = 'spinner.gif'
            if os.path.exists(spinner_path):
                self.spinner_frames = [tk.PhotoImage(file=spinner_path, format=f'gif -index {i}') for i in range(10)]
            else:
                self.spinner_frames = []
        except Exception:
            self.spinner_frames = []

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
    
        # Base colors
        bg_light = "#fdfdfd"         # soft off-white background
        panel_bg = "#f5f5f5"         # slightly darker panels
        text_primary = "#333333"     # dark gray text
        text_secondary = "#555555"   # medium gray text
        accent_primary = "#007acc"   # vibrant blue accent
        accent_secondary = "#ff7f50" # coral accent for highlights
        success_color = "#28a745"    # green
        error_color = "#dc3545"      # red
    
        # Frames and general labels
        style.configure('TFrame', background=bg_light)
        style.configure('TLabel', background=bg_light, foreground=text_primary)
    
        # Title label
        style.configure(
            'Title.TLabel',
            font=('Segoe UI', 18, 'bold'),
            foreground=accent_primary,
            background=panel_bg
        )
    
        # Section headers
        style.configure(
            'Header.TLabel',
            font=('Segoe UI', 13, 'bold'),
            foreground=accent_secondary,
            background=bg_light
        )
    
        # Info text
        style.configure(
            'Info.TLabel',
            font=('Segoe UI', 10),
            foreground=text_secondary,
            background=bg_light
        )
    
        # Status labels
        style.configure(
            'Success.TLabel',
            font=('Segoe UI', 10, 'bold'),
            foreground=success_color,
            background=bg_light
        )
        style.configure(
            'Error.TLabel',
            font=('Segoe UI', 10, 'bold'),
            foreground=error_color,
            background=bg_light
        )
    
        # Buttons
        style.configure(
            'TButton',
            font=('Segoe UI', 11, 'bold'),
            foreground='white',
            background=accent_primary,
            padding=8,
            relief='flat'
        )
        style.map(
            'TButton',
            foreground=[('active', 'white')],
            background=[('active', accent_secondary)]
        )
    

    ############# Tab 1: Outfit Recommendation #############

    def create_recommendation_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Outfit Recommendation")

        ttk.Label(tab, text="Weather-Based Outfit Recommendation System", style='Title.TLabel').pack(pady=(10, 15))

        input_frame = ttk.LabelFrame(tab, text="Get Outfit Recommendation", padding="10")
        input_frame.pack(fill=tk.X, padx=10)

        ttk.Label(input_frame, text="City:", style='Header.TLabel').grid(row=0, column=0, padx=5, sticky=tk.W)
        self.city_var = tk.StringVar(value="Mumbai")
        self.city_entry = ttk.Entry(input_frame, textvariable=self.city_var, font=('Arial', 11))
        self.city_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        input_frame.columnconfigure(1, weight=1)

        self.recommend_button = ttk.Button(input_frame, text="\u2601 Get Recommendation", command=self.get_recommendation_threaded)
        self.recommend_button.grid(row=0, column=2, padx=5)

        progress_frame = ttk.Frame(input_frame)
        progress_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.spinner_label = ttk.Label(progress_frame, background='#e6f2ff')
        self.spinner_label.pack(side=tk.LEFT, padx=5)

        results_frame = ttk.LabelFrame(tab, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        weather_frame = ttk.Frame(results_frame)
        weather_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(weather_frame, text="Weather:", style='Header.TLabel').pack(side=tk.LEFT)
        self.weather_label = ttk.Label(weather_frame, text="Enter city and click 'Get Recommendation'", style='Info.TLabel', compound='left')
        self.weather_label.pack(side=tk.LEFT, padx=10)

        ttk.Label(results_frame, text="Outfit Recommendations:", style='Header.TLabel').pack(anchor=tk.W)
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, wrap=tk.WORD, font=('Arial', 10), background="white")
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        buttons_frame = ttk.Frame(tab)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(5,10))
        ttk.Button(buttons_frame, text="\u23F3 View History", command=self.view_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="\u274C Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="\u2139 Database Stats", command=self.show_db_stats).pack(side=tk.LEFT, padx=5)

        self.city_entry.bind('<Return>', lambda e: self.get_recommendation_threaded())

    def get_recommendation_threaded(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return
        self.progress.start()
        self.animate_spinner()
        self.recommend_button.config(state='disabled')
        self.update_status("Fetching weather data and generating recommendations...", "info")
        threading.Thread(target=self.get_recommendation).start()

    def get_recommendation(self):
        try:
            city = self.city_var.get().strip()
            result = self.recommender.get_weather_and_recommend(city)
            self.root.after(0, self.display_results, result)
        except Exception as e:
            self.root.after(0, self.display_error, f"Error getting recommendation: {e}")

    def display_results(self, result):
        self.progress.stop()
        self.stop_spinner()
        self.recommend_button.config(state='normal')
        if result['success']:
            weather = result['weather']
            outfits = result['outfits']
            icon_map = {
                'clear': 'sun.png', 'rain': 'rain.png', 'clouds': 'cloud.png',
                'snow': 'snow.png', 'thunderstorm': 'storm.png'
            }
            condition = weather['weather_main'].lower()
            icon_file = icon_map.get(condition, 'default.png')
            if os.path.exists(icon_file):
                img = Image.open(icon_file).resize((50,50), Image.ANTIALIAS)
                self.weather_icon = ImageTk.PhotoImage(img)
                self.weather_label.config(image=self.weather_icon, compound='left',
                                          text=f"{weather['city']}, {weather['country']} | "
                                               f"{weather['temperature']}°C (feels like {weather['feels_like']}°C) | "
                                               f"{weather['weather_description']} | Humidity: {weather['humidity']}%")
            else:
                self.weather_label.config(image='', compound='none',
                                          text=f"{weather['city']}, {weather['country']} | "
                                               f"{weather['temperature']}°C (feels like {weather['feels_like']}°C) | "
                                               f"{weather['weather_description']} | Humidity: {weather['humidity']}%")

            self.results_text.delete(1.0, tk.END)
            if outfits:
                advice = self.recommender.get_weather_advice(weather)
                self.results_text.insert(tk.END, f"Weather Advice:\n{advice}\n\n")
                for group in outfits:
                    self.results_text.insert(tk.END, f"{group['outfit_type']}:\n")
                    for item in group['items']:
                        s = (f"• {item['clothing_type']} ({item['category']})\n"
                             f" Material: {item.get('material','N/A')} | Comfort: {item.get('comfort_rating',0)}/10\n"
                             f" Temp range: {item['temp_min']}°C to {item['temp_max']}°C\n\n")
                        self.results_text.insert(tk.END, s)
                self.update_status(f"Generated {len(outfits)} outfit recommendations", "success")
            else:
                self.results_text.insert(tk.END, "No suitable outfits found.\nTry adding more items to the database.\n")
                self.update_status("No outfit recommendations found", "error")
        else:
            self.display_error(result.get('error','Unknown error occurred'))

    def display_error(self, msg):
        self.progress.stop()
        self.stop_spinner()
        self.recommend_button.config(state='normal')
        self.weather_label.config(image='', compound='none', text="Error fetching weather data")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Error: {msg}\n\nPlease check:\n1. Internet connection\n2. City name spelling\n3. API key in config.py\n4. Database connection\n")
        self.update_status(f"Error: {msg}", "error")

    def animate_spinner(self, ind=0):
        if self.spinner_frames:
            self.spinner_label.config(image=self.spinner_frames[ind])
            ind = (ind+1) % len(self.spinner_frames)
            self.spinner_anim_id = self.root.after(100, self.animate_spinner, ind)
        else:
            self.spinner_label.config(image='')

    def stop_spinner(self):
        if self.spinner_anim_id:
            self.root.after_cancel(self.spinner_anim_id)
            self.spinner_label.config(image='')
            self.spinner_anim_id = None

    def view_history(self):
        try:
            history = self.db.get_recommendations_history(10)
            win = tk.Toplevel(self.root)
            win.title("Recommendation History")
            win.geometry("600x400")
            frame = ttk.Frame(win, padding=10)
            frame.pack(fill=tk.BOTH, expand=True)
            text = scrolledtext.ScrolledText(frame, font=('Arial',10))
            text.pack(fill=tk.BOTH, expand=True)
            if history:
                for i, rec in enumerate(history,1):
                    t_str = rec.get('timestamp','Unknown time')
                    city = rec.get('city','Unknown city')
                    weather = rec.get('weather',{})
                    temp = weather.get('temperature','N/A')
                    cond = weather.get('weather_description','N/A')
                    count = rec.get('recommendation_count',0)
                    text.insert(tk.END, f"{i}. {t_str}\n  City: {city}\n  Weather: {temp}°C, {cond}\n  Recommendations: {count} outfit groups\n\n")
            else:
                text.insert(tk.END, "No recommendation history found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history: {e}")

    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
        self.weather_label.config(image='', compound='none', text="Enter city and click 'Get Recommendation'")
        self.update_status("Results cleared", "info")

    def show_db_stats(self):
        try:
            stats = self.db.get_collection_stats()
            msg = (f"Database Statistics:\n\n"
                   f"Weather records: {stats.get('weather_count',0)}\n"
                   f"Outfit items: {stats.get('outfit_count',0)}\n"
                   f"Recommendations: {stats.get('recommendations_count',0)}")
            messagebox.showinfo("Database Statistics", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get database stats: {e}")

    ############# Tab 2: Collection Data Viewer with CRUD #############

    def create_collection_viewer_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Collection Data Viewer")

        selector_frame = ttk.Frame(tab, padding=10)
        selector_frame.pack(fill=tk.X)

        ttk.Label(selector_frame, text="Select Collection:", style='Header.TLabel').pack(side=tk.LEFT, padx=5)

        self.collection_var = tk.StringVar()
        self.collection_combo = ttk.Combobox(selector_frame, textvariable=self.collection_var,
                                             values=['weather', 'outfit', 'recommendations'], state='readonly')
        self.collection_combo.pack(side=tk.LEFT, padx=5)
        self.collection_combo.current(0)

        self.load_collection_btn = ttk.Button(selector_frame, text="Load Data", command=self.load_collection_data_threaded)
        self.load_collection_btn.pack(side=tk.LEFT, padx=10)

        self.tree_frame = ttk.Frame(tab)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.collection_tree = ttk.Treeview(self.tree_frame, show='headings', selectmode="extended")
        self.collection_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.collection_tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = ttk.Scrollbar(tab, orient=tk.HORIZONTAL, command=self.collection_tree.xview)
        scroll_x.pack(fill=tk.X, padx=10)
        self.collection_tree.config(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Add Record", command=self.add_record_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Selected", command=self.edit_selected_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected_records).pack(side=tk.LEFT, padx=5)

        self.collection_status_label = ttk.Label(tab, text="", style='Info.TLabel')
        self.collection_status_label.pack(fill=tk.X, padx=10, pady=(0,5))

    def load_collection_data_threaded(self):
        self.load_collection_btn.config(state='disabled')
        self.collection_status_label.config(text="Loading data...")
        threading.Thread(target=self.load_collection_data).start()

    def load_collection_data(self):
        try:
            cname = self.collection_var.get()
            if cname not in ['weather','outfit','recommendations']:
                raise ValueError("Unknown collection selected")

            self.collection_tree.delete(*self.collection_tree.get_children())
            self.collection_tree["columns"] = ()

            if cname == 'weather':
                data = self.db.get_weather_data(limit=50)
            elif cname == 'outfit':
                data = list(self.db.outfit_collection.find().limit(50))
            else:
                data = list(self.db.recommendations_collection.find().limit(50))

            if not data:
                self.root.after(0, lambda: self.collection_status_label.config(text="No data found."))
                self.root.after(0, lambda: self.load_collection_btn.config(state='normal'))
                return

            cols = sorted(data[0].keys())
            if '_id' in cols:
                cols.remove('_id')
                cols.insert(0, '_id')

            self.root.after(0, lambda: self.setup_treeview_columns(cols))
            for doc in data:
                row = []
                for col in cols:
                    v = doc.get(col, '')
                    if col == '_id':  # display as string
                        v = str(v)
                    elif isinstance(v, datetime):
                        v = v.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(v, list):
                        v = ', '.join(str(i) for i in v)
                    row.append(str(v))
                self.root.after(0, lambda r=row: self.collection_tree.insert('', tk.END, values=r))

            self.root.after(0, lambda: self.collection_status_label.config(text=f"Loaded {len(data)} records from '{cname}' collection."))
        except Exception as e:
            self.root.after(0, lambda: self.collection_status_label.config(text=f"Error loading data: {e}"))
            messagebox.showerror("Error", f"Failed to load collection data: {e}")
        finally:
            self.root.after(0, lambda: self.load_collection_btn.config(state='normal'))

    def setup_treeview_columns(self, cols):
        self.collection_tree["columns"] = cols
        for c in cols:
            self.collection_tree.heading(c, text=c)
            self.collection_tree.column(c, width=130, anchor=tk.CENTER)

    # Add Record dialog
    def add_record_dialog(self):
        cname = self.collection_var.get()
        dlg = RecordDialog(self.root, f"Add Record to '{cname}'", {}, self.insert_record, cname)

    def insert_record(self, cname, record):
        try:
            col = self.get_collection(cname)
            result = col.insert_one(record)
            messagebox.showinfo("Success", f"Record inserted with ID: {result.inserted_id}")
            self.load_collection_data_threaded()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to insert record: {e}")

    # Edit Record dialog
    def edit_selected_record(self):
        selected = self.collection_tree.selection()
        if not selected:
            messagebox.showwarning("Select record", "Please select a record to edit.")
            return
        if len(selected) > 1:
            messagebox.showwarning("Multiple records", "Please select only one record to edit.")
            return
        item = self.collection_tree.item(selected[0])
        values = item['values']
        cols = self.collection_tree['columns']
        record = {cols[i]: values[i] for i in range(len(cols))}
        datasource = self.collection_var.get()
        dlg = RecordDialog(self.root, f"Edit Record in '{datasource}'", record, self.update_record, datasource)

    def update_record(self, cname, record):
        try:
            col = self.get_collection(cname)
            _id_str = record.get('_id','')
            if _id_str == '':
                messagebox.showerror("Error","Record id (_id) missing")
                return
            _id = ObjectId(_id_str)
            new_record = record.copy()
            del new_record['_id']  # _id cannot be updated
            # Convert any datetimes or lists if needed here
            col.update_one({'_id': _id}, {'$set': new_record})
            messagebox.showinfo("Success", "Record updated successfully")
            self.load_collection_data_threaded()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update record: {e}")

    # Delete selected records
    def delete_selected_records(self):
        selected = self.collection_tree.selection()
        if not selected:
            messagebox.showwarning("Select records", "Please select records to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(selected)} selected record(s)?"):
            return
        try:
            col = self.get_collection(self.collection_var.get())
            for sel in selected:
                item = self.collection_tree.item(sel)
                values = item['values']
                cols = self.collection_tree['columns']
                record = {cols[i]: values[i] for i in range(len(cols))}
                _id = ObjectId(record.get('_id'))
                col.delete_one({'_id': _id})
            messagebox.showinfo("Deleted", f"Deleted {len(selected)} record(s)")
            self.load_collection_data_threaded()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete records: {e}")

    def get_collection(self, cname):
        if cname == 'weather':
            return self.db.weather_collection
        elif cname == 'outfit':
            return self.db.outfit_collection
        else:
            return self.db.recommendations_collection

    ############# Tab 3: Visual Analytics (Line Chart) #############

    def create_visualization_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Visual Analytics")

        controls_frame = ttk.Frame(tab, padding=10)
        controls_frame.pack(fill=tk.X)

        ttk.Label(controls_frame, text="Visualize Recommendations by City and Date", style='Header.TLabel').pack(side=tk.LEFT)
        self.refresh_viz_btn = ttk.Button(controls_frame, text="Refresh Visualization", command=self.load_visualization_threaded)
        self.refresh_viz_btn.pack(side=tk.LEFT, padx=10)

        self.fig, self.ax = plt.subplots(figsize=(8,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=tab)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.visualization_status_label = ttk.Label(tab, text="", style='Info.TLabel')
        self.visualization_status_label.pack(fill=tk.X, padx=10, pady=(0, 5))

    def load_visualization_threaded(self):
        self.refresh_viz_btn.config(state='disabled')
        self.visualization_status_label.config(text="Loading visualization...")
        threading.Thread(target=self.load_visualization).start()

    def load_visualization(self):
        try:
            data = list(self.db.recommendations_collection.find().sort('timestamp', -1).limit(100))
            if not data:
                self.root.after(0, lambda: self.visualization_status_label.config(text="No recommendation data found."))
                return

            counts = defaultdict(lambda: defaultdict(int))
            for rec in data:
                city = rec.get('city', 'Unknown')
                ts = rec.get('timestamp')
                if not ts:
                    continue
                #date_str = ts.strftime('%Y-%m-%d')

                ts = rec.get('timestamp')
                if not ts:
                    continue
                if isinstance(ts, str):  # already a string
                    try:
                        # Try parsing into datetime
                        ts = datetime.fromisoformat(ts)
                    except Exception:
                        # If not ISO format, just use as string
                        date_str = ts.split(" ")[0]
                    else:
                        date_str = ts.strftime('%Y-%m-%d')
                elif isinstance(ts, datetime):
                    date_str = ts.strftime('%Y-%m-%d')
                else:
                    continue
                counts[city][date_str] += 1

            cities = sorted(counts.keys())
            all_dates = sorted({d for city in counts for d in counts[city]})

            self.ax.clear()
            for city in cities:
                city_counts = [counts[city].get(d, 0) for d in all_dates]
                self.ax.plot(all_dates, city_counts, marker='o', label=city)

            self.ax.set_title("Outfit Recommendations per City Over Dates (Line Chart)")
            self.ax.set_xlabel("Date")
            self.ax.set_ylabel("Recommendation Count")
            self.ax.legend(loc='upper left')
            self.ax.grid(True)
            self.ax.tick_params(axis='x', rotation=45)
            self.fig.tight_layout()

            self.root.after(0, self.canvas.draw)
            self.root.after(0, lambda: self.visualization_status_label.config(text=f"Loaded visualization for {len(data)} records."))

        except Exception as e:
            self.root.after(0, lambda: self.visualization_status_label.config(text=f"Error loading visualization: {e}"))
            messagebox.showerror("Error", f"Failed to load visualization: {e}")
        finally:
            self.root.after(0, lambda: self.refresh_viz_btn.config(state='normal'))

    ############# Common Utilities #############

    def check_database_connection(self):
        try:
            if self.db.test_connection():
                self.update_status("Database connected successfully", "success")
            else:
                self.update_status("Database connection failed", "error")
        except Exception as e:
            self.update_status(f"Database error: {e}", "error")

    def update_status(self, msg, status_type="info"):
        self.status_label.config(text=f"{datetime.now().strftime('%H:%M:%S')} - {msg}")
        if status_type == "success":
            self.status_label.config(style='Success.TLabel')
        elif status_type == "error":
            self.status_label.config(style='Error.TLabel')
        else:
            self.status_label.config(style='Info.TLabel')

    def on_closing(self):
        try:
            self.recommender.close()
            self.db.close_connection()
        except Exception as e:
            print(f"Cleanup error: {e}")
        self.root.destroy()

    def run(self):
        self.root.mainloop()

# Dialog window for Add/Edit Record
class RecordDialog(tk.Toplevel):
    def __init__(self, parent, title, record, callback, collection_name):
        super().__init__(parent)
        self.title(title)
        self.callback = callback
        self.collection_name = collection_name
        self.record = record.copy()
        self.result = None
        self.geometry("600x600")
        self.grab_set()
        self.transient(parent)

        self.vars = {}
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Show each key except _id as editable field
        row = 0
        for k, v in self.record.items():
            ttk.Label(frame, text=k).grid(row=row, column=0, sticky=tk.W, pady=3)
            val = str(v)
            e = ttk.Entry(frame)
            e.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=3)
            e.insert(0, val)
            if k == '_id':
                e.config(state='readonly')
            self.vars[k] = e
            row += 1

        # If record empty (add new), provide field to add keys and values
        if not self.record:
            # Allow user to add keys dynamically (for simplicity just fixed fields)
            fields = ['field1', 'field2']
            for f in fields:
                ttk.Label(frame, text=f).grid(row=row, column=0, sticky=tk.W, pady=3)
                e = ttk.Entry(frame)
                e.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=3)
                self.vars[f] = e
                row += 1

        ttk.Button(self, text="Save", command=self.on_save).pack(pady=10)
        ttk.Button(self, text="Cancel", command=self.destroy).pack()

    def on_save(self):
        new_rec = {}
        for k, e in self.vars.items():
            # Skip empty keys or _id modification
            v = e.get()
            if k == '_id':
                new_rec[k] = v
            elif v != '':
                # Try to interpret numbers and lists? For simplicity, keep string
                new_rec[k] = v
        self.callback(self.collection_name, new_rec)
        self.destroy()


if __name__ == "__main__":
    try:
        app = WeatherOutfitUI()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
