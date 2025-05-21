import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk
import subprocess
import threading
import os
import json
from datetime import datetime

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Command Runner")
        self.root.geometry("800x800")  # Increased initial size
        
        # Set color scheme (Unreal Engine inspired)
        self.colors = {
            'bg_dark': '#1B1B1B',
            'bg_medium': '#2A2A2A',
            'bg_light': '#303030',
            'text': '#CCCCCC',
            'accent': '#2196F3',
            'accent_hover': '#1E88E5',
            'error': '#FF4444',
            'success': '#4CAF50'
        }
        
        # Configure root window colors
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('Custom.TCombobox',
                           fieldbackground=self.colors['bg_light'],
                           background=self.colors['bg_medium'],
                           foreground=self.colors['text'],
                           selectbackground=self.colors['accent'],
                           selectforeground=self.colors['text'])
        self.style.map('Custom.TCombobox',
                      fieldbackground=[('readonly', self.colors['bg_light'])],
                      selectbackground=[('readonly', self.colors['accent'])],
                      foreground=[('readonly', self.colors['text'])])
        self.style.configure('Custom.TNotebook',
                           background=self.colors['bg_dark'])
        self.style.configure('Custom.TNotebook.Tab',
                           background=self.colors['bg_medium'],
                           foreground=self.colors['text'],
                           padding=[10, 2])
        self.style.map('Custom.TNotebook.Tab',
                      background=[('selected', self.colors['accent'])],
                      foreground=[('selected', self.colors['text'])])
        
        # Initialize state variables
        self.profiles_file = "command_profiles.json"
        self.working_dir = ""
        self.output_visible = False
        
        # Load profiles before creating UI
        self.load_profiles()
        
        # Create top frame for directory selection
        self.top_frame = tk.Frame(self.root, bg=self.colors['bg_dark'], padx=5, pady=5)
        self.top_frame.pack(fill='x')
        
        # Create directory selection in top
        self.dir_frame = tk.Frame(self.top_frame, bg=self.colors['bg_dark'])
        self.dir_frame.pack(fill='x')
        
        # Create directory dropdown frame
        self.dir_dropdown_frame = tk.Frame(self.dir_frame, bg=self.colors['bg_dark'])
        self.dir_dropdown_frame.pack(side='left', fill='x', expand=True)
        
        self.dir_label = tk.Label(
            self.dir_dropdown_frame,
            text="Directory:",
            font=("Arial", 9),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        self.dir_label.pack(side='left')
        
        # Create directory dropdown
        self.dir_var = tk.StringVar()
        self.dir_dropdown = ttk.Combobox(
            self.dir_dropdown_frame,
            textvariable=self.dir_var,
            font=("Consolas", 10),
            style='Custom.TCombobox'
        )
        self.dir_dropdown.pack(side='left', fill='x', expand=True, padx=(5, 5))
        self.dir_dropdown.bind('<<ComboboxSelected>>', self.on_dir_selected)
        
        # Create browse button
        self.browse_button = tk.Button(
            self.dir_frame,
            text="Browse...",
            command=self.browse_directory,
            font=("Arial", 9),
            bg=self.colors['accent'],
            fg=self.colors['text'],
            activebackground=self.colors['accent_hover'],
            activeforeground=self.colors['text'],
            relief='flat',
            padx=10
        )
        self.browse_button.pack(side='right')
        
        # Create notebook (tabs container)
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create Command tab
        self.cmd_tab = tk.Frame(self.notebook, bg=self.colors['bg_dark'])
        self.notebook.add(self.cmd_tab, text='Cmd')
        
        # Create Package tab
        self.package_tab = tk.Frame(self.notebook, bg=self.colors['bg_dark'])
        self.notebook.add(self.package_tab, text='Package')
        
        # Setup Command tab
        self.setup_cmd_tab()
        
        # Setup Package tab
        self.setup_package_tab()
        
        # Initialize UI state
        self.update_dir_display()
        self.command_dropdown['values'] = []
        self.command_var.set("")
        
        # Configure hover effects for buttons
        for button in [self.browse_button, self.button]:
            button.bind('<Enter>', lambda e, b=button: b.configure(
                bg=self.colors['accent_hover']))
            button.bind('<Leave>', lambda e, b=button: b.configure(
                bg=self.colors['accent']))
    
    def load_profiles(self):
        """Load profiles from JSON file"""
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, 'r') as f:
                    self.profiles = json.load(f)
            else:
                self.profiles = {}
        except:
            self.profiles = {}
    
    def save_profiles(self):
        """Save profiles to JSON file"""
        with open(self.profiles_file, 'w') as f:
            json.dump(self.profiles, f, indent=2)
    
    def update_dir_dropdown(self):
        """Update directory dropdown with saved directories"""
        dirs = [''] + list(self.profiles.keys())
        self.dir_dropdown['values'] = dirs
        
        # Set current directory in dropdown if it exists
        if self.working_dir in dirs:
            self.dir_var.set(self.working_dir)
        else:
            self.dir_var.set('')
    
    def on_dir_selected(self, event=None):
        """Handle directory selection from dropdown"""
        selected_dir = self.dir_var.get()
        if selected_dir:
            self.working_dir = selected_dir
            self.update_dir_display()
            
            # Load package settings if they exist
            if 'package_settings' in self.profiles.get(selected_dir, {}):
                settings = self.profiles[selected_dir]['package_settings']
                for param, value in settings.items():
                    if param in self.package_params:
                        self.package_params[param].set(value)
                self.update_package_command()
    
    def update_dir_display(self):
        """Update directory display and command history"""
        # Update directory dropdown
        self.update_dir_dropdown()
        
        # Update command history based on working directory
        if self.working_dir:
            self.command_dropdown['values'] = self.profiles.get(self.working_dir, {}).get('commands', [])
        else:
            self.command_dropdown['values'] = []
    
    def browse_directory(self):
        """Open directory browser dialog"""
        new_dir = filedialog.askdirectory(
            initialdir=self.working_dir if self.working_dir else None,
            title="Select Working Directory"
        )
        if new_dir:  # Only update if a directory was selected
            self.working_dir = new_dir
            
            # Initialize profile for this directory if it doesn't exist
            if new_dir not in self.profiles:
                self.profiles[new_dir] = {
                    'commands': []
                }
            
            self.update_dir_display()
            self.save_profiles()
    
    def save_current_profile(self):
        """Save command to current directory's profile"""
        if self.working_dir:
            # Save command history
            command = self.command_var.get().strip()
            if command and command not in self.profiles[self.working_dir]['commands']:
                self.profiles[self.working_dir]['commands'].insert(0, command)
            
            # Save package settings
            if 'package_settings' not in self.profiles[self.working_dir]:
                self.profiles[self.working_dir]['package_settings'] = {}
            
            # Save all package parameters
            for param, var in self.package_params.items():
                if isinstance(var, tk.BooleanVar):
                    self.profiles[self.working_dir]['package_settings'][param] = var.get()
                else:  # StringVar
                    self.profiles[self.working_dir]['package_settings'][param] = var.get()
            
            self.save_profiles()
            self.command_dropdown['values'] = self.profiles[self.working_dir]['commands']
    
    def toggle_output(self):
        """Toggle output area visibility"""
        self.output_visible = not self.output_visible
        if self.output_visible:
            self.toggle_button.config(text="▼ Hide Output")
            self.output_container.pack(fill='both', expand=True)
            self.root.geometry("600x400")
        else:
            self.toggle_button.config(text="▶ Show Output")
            self.output_container.pack_forget()
            self.root.geometry("600x200")
    
    def run_command(self):
        """Execute the current command"""
        if not self.working_dir:
            messagebox.showwarning("Warning", "Please select a working directory first")
            return
            
        command = self.command_var.get().strip()
        if not command:
            messagebox.showwarning("Warning", "Please enter a command")
            return
        
        # Save command to profile
        self.save_current_profile()
            
        # Disable button while command is running
        self.button.config(state='disabled')
        self.browse_button.config(state='disabled')
        self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, f"Running command: {command}\n")
        self.output_area.insert(tk.END, f"Working directory: {self.working_dir}\n\n")
        
        # Run command in a separate thread to prevent GUI freezing
        def execute_command():
            try:
                # Run the command and capture output
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=self.working_dir
                )
                
                # Get output and errors
                output, errors = process.communicate()
                
                # Update GUI in the main thread
                self.root.after(0, self.update_output, output, errors)
            except Exception as e:
                self.root.after(0, self.update_output, "", str(e))
            finally:
                self.root.after(0, lambda: self.button.config(state='normal'))
                self.root.after(0, lambda: self.browse_button.config(state='normal'))
        
        threading.Thread(target=execute_command, daemon=True).start()
    
    def update_output(self, output, errors):
        """Update output area with command results"""
        if output:
            self.output_area.insert(tk.END, "Output:\n" + output + "\n")
        if errors:
            self.output_area.insert(tk.END, "Errors:\n" + errors + "\n")
        self.output_area.see(tk.END)

    def setup_cmd_tab(self):
        """Setup the Command tab UI"""
        # Create main frame in Command tab
        self.main_frame = tk.Frame(self.cmd_tab, bg=self.colors['bg_dark'], padx=20, pady=20)
        self.main_frame.pack(expand=True, fill='both')
        
        # Create command frame
        self.cmd_frame = tk.Frame(self.main_frame, bg=self.colors['bg_dark'])
        self.cmd_frame.pack(fill='x', pady=(0, 10))
        
        self.label = tk.Label(
            self.cmd_frame,
            text="Enter command:",
            font=("Arial", 10),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        self.label.pack(side='left')
        
        # Create command input container
        self.cmd_input_frame = tk.Frame(self.cmd_frame, bg=self.colors['bg_dark'])
        self.cmd_input_frame.pack(side='left', fill='x', expand=True, padx=(5, 5))
        
        self.command_var = tk.StringVar()
        self.command_dropdown = ttk.Combobox(
            self.cmd_input_frame,
            textvariable=self.command_var,
            font=("Consolas", 12),
            style='Custom.TCombobox'
        )
        self.command_dropdown.pack(side='left', fill='x', expand=True)
        
        # Bind Enter key to run command
        self.command_dropdown.bind('<Return>', lambda e: self.run_command())
        
        # Create button next to command input
        self.button = tk.Button(
            self.cmd_frame,
            text="Run",
            command=self.run_command,
            font=("Arial", 12),
            padx=15,
            pady=0,
            bg=self.colors['accent'],
            fg=self.colors['text'],
            activebackground=self.colors['accent_hover'],
            activeforeground=self.colors['text'],
            relief='flat'
        )
        self.button.pack(side='right')
        
        # Create output section frame
        self.output_frame = tk.Frame(self.main_frame, bg=self.colors['bg_dark'])
        self.output_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        self.toggle_frame = tk.Frame(self.output_frame, bg=self.colors['bg_dark'])
        self.toggle_frame.pack(fill='x')
        
        self.toggle_button = tk.Button(
            self.toggle_frame,
            text="▼ Show Output",
            command=self.toggle_output,
            font=("Arial", 10),
            relief="flat",
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            activebackground=self.colors['bg_light'],
            activeforeground=self.colors['text'],
            anchor="w"
        )
        self.toggle_button.pack(fill='x')
        
        self.output_container = tk.Frame(self.output_frame, bg=self.colors['bg_dark'])
        self.output_container.pack(fill='both', expand=True)
        self.output_container.pack_forget()  # Initially hidden
        
        self.output_area = scrolledtext.ScrolledText(
            self.output_container,
            height=12,
            font=("Consolas", 10),
            wrap=tk.WORD,
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        self.output_area.pack(fill='both', expand=True)

    def setup_package_tab(self):
        """Setup the Package tab UI"""
        # Create main frame in Package tab with scrollbar
        self.package_outer_frame = tk.Frame(self.package_tab, bg=self.colors['bg_dark'])
        self.package_outer_frame.pack(fill='both', expand=True)
        
        # Add canvas and scrollbar
        self.package_canvas = tk.Canvas(
            self.package_outer_frame,
            bg=self.colors['bg_dark'],
            highlightthickness=0
        )
        self.package_scrollbar = ttk.Scrollbar(
            self.package_outer_frame,
            orient='vertical',
            command=self.package_canvas.yview
        )
        
        # Configure canvas
        self.package_frame = tk.Frame(self.package_canvas, bg=self.colors['bg_dark'], padx=20, pady=20)
        self.package_canvas.configure(yscrollcommand=self.package_scrollbar.set)
        
        # Pack scrollbar and canvas
        self.package_scrollbar.pack(side='right', fill='y')
        self.package_canvas.pack(side='left', fill='both', expand=True)
        
        # Add the frame to the canvas
        self.canvas_frame = self.package_canvas.create_window(
            (0, 0),
            window=self.package_frame,
            anchor='nw',
            width=self.package_canvas.winfo_width()
        )
        
        # Configure canvas scrolling
        self.package_frame.bind('<Configure>', self.on_frame_configure)
        self.package_canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Create parameters
        self.package_params = {
            'Project': tk.StringVar(value=''),
            'Platform': tk.StringVar(value='Win64'),
            'Configuration': tk.StringVar(value='Development'),
            'Cook': tk.StringVar(value='cook'),
            'NoXGE': tk.BooleanVar(value=True),
            'NoCompileEditor': tk.BooleanVar(value=True),
            'SkipBuildEditor': tk.BooleanVar(value=True),
            'Prereqs': tk.BooleanVar(value=True),
            'Build': tk.BooleanVar(value=True),
            'Stage': tk.BooleanVar(value=True),
            'Package': tk.BooleanVar(value=True),
            'Archive': tk.BooleanVar(value=True),
            'NoSndbsShaderCompile': tk.BooleanVar(value=True),
            'NoRemoteShaderCompile': tk.BooleanVar(value=True),
            'ArchiveDirectory': tk.StringVar(value=''),
            'CookerOptions': tk.StringVar(value='-cookprocesscount=4'),
            'Compressed': tk.BooleanVar(value=True)
        }
        
        # Add trace to all parameters for auto-save
        for param_name, var in self.package_params.items():
            var.trace_add('write', lambda *args, param=param_name: self.on_package_param_change(param))
        
        # Rest of the package tab setup code remains the same, but use self.package_frame instead of self.package_frame
        self.params_frame = tk.Frame(self.package_frame, bg=self.colors['bg_dark'])
        self.params_frame.pack(fill='x', pady=(0, 10))
        
        # Create parameter inputs
        row = 0
        
        # Create left and right frames for two-column layout
        left_frame = tk.Frame(self.params_frame, bg=self.colors['bg_dark'])
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        right_frame = tk.Frame(self.params_frame, bg=self.colors['bg_dark'])
        right_frame.grid(row=0, column=1, sticky='nsew')
        
        self.params_frame.grid_columnconfigure(0, weight=1)
        self.params_frame.grid_columnconfigure(1, weight=1)
        
        # Left column - Main settings
        current_frame = left_frame
        row = 0
        
        # Project selection
        tk.Label(
            current_frame,
            text="Project:",
            font=("Arial", 10),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).grid(row=row, column=0, sticky='w', pady=2)
        
        project_frame = tk.Frame(current_frame, bg=self.colors['bg_dark'])
        project_frame.grid(row=row, column=1, sticky='ew', pady=2)
        
        self.project_entry = tk.Entry(
            project_frame,
            textvariable=self.package_params['Project'],
            font=("Consolas", 10),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        self.project_entry.pack(side='left', fill='x', expand=True)
        
        project_browse = tk.Button(
            project_frame,
            text="Browse",
            command=self.browse_project,
            font=("Arial", 9),
            bg=self.colors['accent'],
            fg=self.colors['text'],
            activebackground=self.colors['accent_hover'],
            activeforeground=self.colors['text'],
            relief='flat',
            padx=10
        )
        project_browse.pack(side='right', padx=(5, 0))
        
        row += 1
        
        # Platform dropdown
        tk.Label(
            current_frame,
            text="Platform:",
            font=("Arial", 10),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).grid(row=row, column=0, sticky='w', pady=2)
        
        platform_dropdown = ttk.Combobox(
            current_frame,
            textvariable=self.package_params['Platform'],
            values=['Win64', 'PS5', 'XSX', 'Linux', 'Mac'],
            state='readonly',
            style='Custom.TCombobox'
        )
        platform_dropdown.grid(row=row, column=1, sticky='ew', pady=2)
        
        row += 1
        
        # Configuration dropdown
        tk.Label(
            current_frame,
            text="Configuration:",
            font=("Arial", 10),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).grid(row=row, column=0, sticky='w', pady=2)
        
        config_dropdown = ttk.Combobox(
            current_frame,
            textvariable=self.package_params['Configuration'],
            values=['Development', 'Shipping', 'DebugGame'],
            state='readonly',
            style='Custom.TCombobox'
        )
        config_dropdown.grid(row=row, column=1, sticky='ew', pady=2)
        
        row += 1
        
        # Cook dropdown
        tk.Label(
            current_frame,
            text="Cook:",
            font=("Arial", 10),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).grid(row=row, column=0, sticky='w', pady=2)
        
        cook_dropdown = ttk.Combobox(
            current_frame,
            textvariable=self.package_params['Cook'],
            values=['cook', 'skipcook'],
            state='readonly',
            style='Custom.TCombobox'
        )
        cook_dropdown.grid(row=row, column=1, sticky='ew', pady=2)
        
        row += 1

        # Archive Directory
        tk.Label(
            current_frame,
            text="Archive Dir:",
            font=("Arial", 10),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).grid(row=row, column=0, sticky='w', pady=2)
        
        archive_dir_frame = tk.Frame(current_frame, bg=self.colors['bg_dark'])
        archive_dir_frame.grid(row=row, column=1, sticky='ew', pady=2)
        
        archive_dir_entry = tk.Entry(
            archive_dir_frame,
            textvariable=self.package_params['ArchiveDirectory'],
            font=("Consolas", 10),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        archive_dir_entry.pack(side='left', fill='x', expand=True)
        
        archive_dir_browse = tk.Button(
            archive_dir_frame,
            text="Browse",
            command=self.browse_archive_directory,
            font=("Arial", 9),
            bg=self.colors['accent'],
            fg=self.colors['text'],
            activebackground=self.colors['accent_hover'],
            activeforeground=self.colors['text'],
            relief='flat',
            padx=10
        )
        archive_dir_browse.pack(side='right', padx=(5, 0))
        
        row += 1
        
        # Cooker Options
        tk.Label(
            current_frame,
            text="Cooker Opts:",
            font=("Arial", 10),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).grid(row=row, column=0, sticky='w', pady=2)
        
        cooker_options_entry = tk.Entry(
            current_frame,
            textvariable=self.package_params['CookerOptions'],
            font=("Consolas", 10),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        cooker_options_entry.grid(row=row, column=1, sticky='ew', pady=2)
        
        # Right column - Checkboxes
        current_frame = right_frame
        
        # Create a frame specifically for checkboxes with a grid layout
        checkbox_frame = tk.Frame(current_frame, bg=self.colors['bg_dark'])
        checkbox_frame.pack(fill='both', expand=True)
        
        # Organize checkboxes in a grid (3 columns)
        checkbox_params = [
            ('Build', 0, 0), ('Stage', 0, 1), ('Package', 0, 2),
            ('Archive', 1, 0), ('Prereqs', 1, 1), ('NoXGE', 1, 2),
            ('NoCompileEditor', 2, 0), ('SkipBuildEditor', 2, 1), ('Compressed', 2, 2),
            ('NoSndbsShaderCompile', 3, 0), ('NoRemoteShaderCompile', 3, 1)
        ]
        
        # Configure grid columns to be equal width
        for i in range(3):
            checkbox_frame.grid_columnconfigure(i, weight=1)
        
        # Create checkboxes in the grid
        for param, row, col in checkbox_params:
            checkbox = tk.Checkbutton(
                checkbox_frame,
                text=param,
                variable=self.package_params[param],
                bg=self.colors['bg_dark'],
                fg=self.colors['text'],
                selectcolor=self.colors['bg_medium'],
                activebackground=self.colors['bg_dark'],
                activeforeground=self.colors['text']
            )
            checkbox.grid(row=row, column=col, sticky='w', pady=1, padx=2)
        
        # Create command display
        tk.Label(
            self.package_frame,
            text="Generated Command:",
            font=("Arial", 10),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).pack(anchor='w', pady=(10, 5))
        
        self.package_command_display = tk.Text(
            self.package_frame,
            height=3,
            font=("Consolas", 10),
            wrap=tk.WORD,
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            state='disabled'
        )
        self.package_command_display.pack(fill='x')
        
        # Create run button
        self.package_button = tk.Button(
            self.package_frame,
            text="Run Package",
            command=self.run_package,
            font=("Arial", 12),
            padx=20,
            pady=5,
            bg=self.colors['accent'],
            fg=self.colors['text'],
            activebackground=self.colors['accent_hover'],
            activeforeground=self.colors['text'],
            relief='flat'
        )
        self.package_button.pack(pady=10)
        
        # Create output section
        self.package_output_frame = tk.Frame(self.package_frame, bg=self.colors['bg_dark'])
        self.package_output_frame.pack(fill='both', expand=True)
        
        self.package_toggle_frame = tk.Frame(self.package_output_frame, bg=self.colors['bg_dark'])
        self.package_toggle_frame.pack(fill='x')
        
        self.package_toggle_button = tk.Button(
            self.package_toggle_frame,
            text="▼ Show Output",
            command=self.toggle_package_output,
            font=("Arial", 10),
            relief="flat",
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            activebackground=self.colors['bg_light'],
            activeforeground=self.colors['text'],
            anchor="w"
        )
        self.package_toggle_button.pack(fill='x')
        
        self.package_output_container = tk.Frame(self.package_output_frame, bg=self.colors['bg_dark'])
        self.package_output_container.pack(fill='both', expand=True)
        self.package_output_container.pack_forget()
        
        self.package_output_area = scrolledtext.ScrolledText(
            self.package_output_container,
            height=12,
            font=("Consolas", 10),
            wrap=tk.WORD,
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        self.package_output_area.pack(fill='both', expand=True)
        
        # Initialize command display
        self.package_output_visible = False
        self.update_package_command()

    def browse_project(self):
        """Browse for .uproject file"""
        project_file = filedialog.askopenfilename(
            initialdir=self.working_dir if self.working_dir else None,
            title="Select .uproject file",
            filetypes=[("Unreal Project", "*.uproject")]
        )
        if project_file:
            self.package_params['Project'].set(project_file)
            self.update_package_command()

    def update_package_command(self):
        """Update the package command display based on parameters"""
        if not self.working_dir:
            command = "Please select a working directory first"
        else:
            base_cmd = os.path.join(self.working_dir, "Engine/Build/BatchFiles/RunUAT.bat BuildCookRun")
            project = self.package_params['Project'].get()
            if not project:
                command = "Please select a project file"
            else:
                params = [
                    f'-project="{project}"',
                    f'-platform={self.package_params["Platform"].get()}',
                    f'-configuration={self.package_params["Configuration"].get()}'
                ]
                
                # Add boolean parameters
                if self.package_params['Build'].get():
                    params.append('-build')
                
                # Handle cook/skipcook
                cook_value = self.package_params['Cook'].get()
                if cook_value == 'cook':
                    params.append('-cook')
                elif cook_value == 'skipcook':
                    params.append('-skipcook')
                
                if self.package_params['Stage'].get():
                    params.append('-stage')
                if self.package_params['Package'].get():
                    params.append('-package')
                if self.package_params['Archive'].get():
                    params.append('-archive')
                if self.package_params['Prereqs'].get():
                    params.append('-prereqs')
                if self.package_params['NoXGE'].get():
                    params.append('-NoXGE')
                if self.package_params['NoCompileEditor'].get():
                    params.append('-nocompileeditor')
                if self.package_params['SkipBuildEditor'].get():
                    params.append('-skipbuildeditor')
                if self.package_params['NoSndbsShaderCompile'].get():
                    params.append('-NoSndbsShaderCompile')
                if self.package_params['NoRemoteShaderCompile'].get():
                    params.append('-NoRemoteShaderCompile')
                if self.package_params['Compressed'].get():
                    params.append('-compressed')
                
                # Add string parameters if they have values
                archive_dir = self.package_params['ArchiveDirectory'].get().strip()
                if archive_dir:
                    params.append(f'-archivedirectory="{archive_dir}"')
                
                cooker_options = self.package_params['CookerOptions'].get().strip()
                if cooker_options:
                    params.append(f'-AdditionalCookerOptions={cooker_options}')
                
                command = f'{base_cmd} {" ".join(params)}'
        
        # Update display
        self.package_command_display.config(state='normal')
        self.package_command_display.delete(1.0, tk.END)
        self.package_command_display.insert(1.0, command)
        self.package_command_display.config(state='disabled')

    def toggle_package_output(self):
        """Toggle package output visibility"""
        self.package_output_visible = not self.package_output_visible
        if self.package_output_visible:
            self.package_toggle_button.config(text="▼ Hide Output")
            self.package_output_container.pack(fill='both', expand=True)
        else:
            self.package_toggle_button.config(text="▶ Show Output")
            self.package_output_container.pack_forget()

    def run_package(self):
        """Run the package command"""
        if not self.working_dir:
            messagebox.showwarning("Warning", "Please select a working directory first")
            return
            
        if not self.package_params['Project'].get():
            messagebox.showwarning("Warning", "Please select a project file")
            return
        
        # Get command from display
        command = self.package_command_display.get(1.0, tk.END).strip()
        
        # Disable button while command is running
        self.package_button.config(state='disabled')
        self.package_output_area.delete(1.0, tk.END)
        self.package_output_area.insert(tk.END, f"Running packaging command...\n\n")
        
        # Run command in a separate thread
        def execute_package():
            try:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=self.working_dir
                )
                
                output, errors = process.communicate()
                
                self.root.after(0, self.update_package_output, output, errors)
            except Exception as e:
                self.root.after(0, self.update_package_output, "", str(e))
            finally:
                self.root.after(0, lambda: self.package_button.config(state='normal'))
        
        threading.Thread(target=execute_package, daemon=True).start()

    def update_package_output(self, output, errors):
        """Update package output area with command results"""
        if output:
            self.package_output_area.insert(tk.END, "Output:\n" + output + "\n")
        if errors:
            self.package_output_area.insert(tk.END, "Errors:\n" + errors + "\n")
        self.package_output_area.see(tk.END)

    def browse_archive_directory(self):
        """Browse for archive directory"""
        archive_dir = filedialog.askdirectory(
            initialdir=self.working_dir if self.working_dir else None,
            title="Select Archive Directory"
        )
        if archive_dir:
            self.package_params['ArchiveDirectory'].set(archive_dir)
            self.update_package_command()

    def on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.package_canvas.configure(scrollregion=self.package_canvas.bbox('all'))

    def on_canvas_configure(self, event=None):
        """When the canvas is resized, resize the inner frame to match"""
        if event is not None:
            self.package_canvas.itemconfig(self.canvas_frame, width=event.width)

    def on_package_param_change(self, param_name):
        """Handle package parameter changes"""
        if self.working_dir:  # Only save if we have a working directory
            # Update the command display
            self.update_package_command()
            
            # Save to profile
            if 'package_settings' not in self.profiles[self.working_dir]:
                self.profiles[self.working_dir]['package_settings'] = {}
            
            # Save the changed parameter
            var = self.package_params[param_name]
            if isinstance(var, tk.BooleanVar):
                self.profiles[self.working_dir]['package_settings'][param_name] = var.get()
            else:  # StringVar
                self.profiles[self.working_dir]['package_settings'][param_name] = var.get()
            
            # Save profiles to disk
            self.save_profiles()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop() 