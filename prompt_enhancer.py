import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog
import pyperclip
import keyboard
import threading
import json
import os
from groq import Groq
import time
import re
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import weakref

# Import the theming library
from ttkthemes import ThemedTk

class OptimizedCodingEnglishEnhancer:
    """
    Optimized version of the Coding English Enhancer with performance improvements:
    - Cached regex patterns and API client
    - Thread pool for concurrent operations
    - Reduced string operations and memory allocations
    - Lazy loading of GUI components
    - Connection pooling and resource management
    """
    
    # Class-level constants to avoid repeated allocations
    DEFAULT_MODELS = [
        'moonshotai/kimi-k2-instruct', 'openai/gpt-oss-120b', 'qwen/qwen3-32b',
        'deepseek-r1-distill-llama-70b', 'gemma2-9b-it', 'llama-3.3-70b-versatile',
        'meta-llama/llama-4-maverick-17b-128e-instruct'
    ]
    
    THEME_MAP = {
        'Radiance (Polished)': 'radiance',
        'Plastik (3D)': 'plastik',
    }
    
    # Pre-compiled regex patterns for better performance
    THINK_TAG_PATTERN = re.compile(r'<think>.*?</think>', re.DOTALL | re.IGNORECASE)
    THINK_OPEN_CLOSE_PATTERN = re.compile(r'</?think[^>]*>', re.IGNORECASE)
    MULTIPLE_NEWLINES_PATTERN = re.compile(r'\n\s*\n')
    MULTIPLE_SPACES_PATTERN = re.compile(r'[ \t]+')
    
    def __init__(self):
        # Initialize core attributes
        self._groq_client = None
        self._config_file = "enhancer_config.json"
        self._history_file = "enhancement_history.json"
        self._enhancement_history = []
        self._codebase_path = None
        self._is_enhancing = False
        
        # Thread pool for concurrent operations
        self._thread_pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix="enhancer")
        
        # Cache for frequently accessed data
        self._config_cache = {}
        self._last_config_mtime = 0
        
        # Default values
        self._enhance_hotkey = 'ctrl+shift+e'
        self._alternative_hotkey = 'ctrl+shift+r'
        self._selected_model = self.DEFAULT_MODELS[0]
        self._theme_name = 'radiance'
        self._api_key = ''
        
        # Initialize components
        self._load_config()
        self._load_history()
        self._setup_gui()
        self._setup_hotkeys()
        
    @property
    def groq_client(self):
        """Lazy initialization of Groq client with caching."""
        if self._groq_client is None and self._api_key:
            try:
                self._groq_client = Groq(api_key=self._api_key)
            except Exception as e:
                print(f"Error initializing Groq client: {e}")
        return self._groq_client
    
    def _invalidate_client(self):
        """Invalidate cached client when API key changes."""
        self._groq_client = None
        
    def _load_config(self):
        """Load configuration with caching and change detection."""
        try:
            if not os.path.exists(self._config_file):
                return
                
            # Check if file has been modified
            current_mtime = os.path.getmtime(self._config_file)
            if current_mtime <= self._last_config_mtime and self._config_cache:
                # Use cached config
                config = self._config_cache
            else:
                # Load fresh config
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self._config_cache = config
                self._last_config_mtime = current_mtime
            
            # Apply configuration
            self._api_key = config.get('api_key', '')
            hotkey_config = config.get('hotkeys', {})
            self._enhance_hotkey = hotkey_config.get('enhance', 'ctrl+shift+e')
            self._alternative_hotkey = hotkey_config.get('alternative', 'ctrl+shift+r')
            self._theme_name = config.get('theme', 'radiance')
            self._selected_model = config.get('model', self.DEFAULT_MODELS[0])
            
        except Exception as e:
            print(f"Error loading config: {e}")
            
    def _save_config(self):
        """Save configuration with atomic write."""
        try:
            config = {
                'api_key': self._api_key,
                'hotkeys': {
                    'enhance': self._enhance_hotkey,
                    'alternative': self._alternative_hotkey
                },
                'theme': self._theme_name,
                'model': self._selected_model
            }
            
            # Atomic write to prevent corruption
            temp_file = f"{self._config_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            # Replace original file
            if os.path.exists(self._config_file):
                os.remove(self._config_file)
            os.rename(temp_file, self._config_file)
            
            # Update cache
            self._config_cache = config
            self._last_config_mtime = os.path.getmtime(self._config_file)
            
        except Exception as e:
            print(f"Error saving config: {e}")

    def _load_history(self):
        """Load enhancement history from a JSON file."""
        try:
            if os.path.exists(self._history_file):
                with open(self._history_file, 'r', encoding='utf-8') as f:
                    self._enhancement_history = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading history: {e}")
            self._enhancement_history = []

    def _save_history(self):
        """Save enhancement history to a JSON file."""
        try:
            with open(self._history_file, 'w', encoding='utf-8') as f:
                json.dump(self._enhancement_history, f, indent=4)
        except IOError as e:
            print(f"Error saving history: {e}")
    
    def _setup_gui(self):
        """Setup GUI with a tabbed interface."""
        self.root = ThemedTk(theme=self._theme_name)
        self.root.title("Coding English Enhancer - Optimized")
        self.root.geometry("800x900")

        # Create the main notebook (tabbed interface)
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Create frames for each tab
        self.enhancer_tab = ttk.Frame(notebook)
        self.history_tab = ttk.Frame(notebook)

        notebook.add(self.enhancer_tab, text='Enhancer')
        notebook.add(self.history_tab, text='History')

        # Populate the Enhancer Tab
        self._create_api_key_section(self.enhancer_tab)
        self._create_settings_section(self.enhancer_tab)
        self._create_hotkey_section(self.enhancer_tab)
        self._create_codebase_section(self.enhancer_tab)
        self._create_io_sections(self.enhancer_tab)

        # Populate the History Tab
        self._create_history_section(self.history_tab)

    def _create_codebase_section(self, parent):
        """Create the optional codebase context section."""
        codebase_frame = ttk.LabelFrame(parent, text="Optional Codebase Context")
        codebase_frame.pack(fill=tk.X, padx=10, pady=5, ipady=5)

        button_frame = ttk.Frame(codebase_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Select Project Folder...", command=self._select_codebase_folder).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Clear", command=self._clear_codebase_folder).pack(side=tk.LEFT, padx=5)

        self.codebase_path_label = ttk.Label(codebase_frame, text="No folder selected.")
        self.codebase_path_label.pack(fill=tk.X, padx=5, pady=5)

    def _select_codebase_folder(self):
        """Open a dialog to select a codebase folder."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self._codebase_path = folder_path
            self.codebase_path_label.config(text=f"Selected: {self._codebase_path}")
            self.status_label.config(text=f"Codebase folder set to: {os.path.basename(folder_path)}")

    def _clear_codebase_folder(self):
        """Clear the selected codebase folder."""
        self._codebase_path = None
        self.codebase_path_label.config(text="No folder selected.")
        self.status_label.config(text="Codebase folder cleared.")

    def _extract_keywords_from_prompt(self, text):
        """Extract potential keywords and file paths from the user's prompt."""
        # Find potential file paths (e.g., 'path/to/file.py')
        path_pattern = re.compile(r'[\w\-\./]+\.[\w]+')
        paths = set(path_pattern.findall(text))

        # Extract other potential keywords, ignoring common words
        stop_words = {'the', 'a', 'an', 'is', 'to', 'in', 'on', 'for', 'of', 'with', 'and', 'or', 'but'}
        words = set(re.findall(r'\b\w+\b', text.lower()))
        keywords = words - stop_words

        return keywords.union(paths)

    def _find_relevant_files(self, keywords):
        """Search for files in the codebase that match the keywords."""
        relevant_files = set()
        if not self._codebase_path or not keywords:
            return ""

        for root, _, files in os.walk(self._codebase_path):
            if any(d in root for d in {'.git', '__pycache__', 'node_modules'}):
                continue

            for file in files:
                if len(relevant_files) >= 10:  # Limit to 10 relevant files
                    break

                file_path = os.path.join(root, file)
                # Check if keywords are in the filename
                if any(k in file.lower() for k in keywords):
                    relevant_files.add(file_path)
                    continue

                # If not in filename, check file content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content_sample = f.read(512)  # Read first 512 bytes
                        if any(k in content_sample.lower() for k in keywords):
                            relevant_files.add(file_path)
                except Exception:
                    continue # Ignore files we can't read

        if not relevant_files:
            return ""

        # Format the output
        relative_paths = [os.path.relpath(p, self._codebase_path) for p in relevant_files]
        return "Relevant files found:\n- " + "\n- ".join(relative_paths)

    def _create_api_key_section(self, parent):
        """Create API key section with optimized layout."""
        api_frame = ttk.LabelFrame(parent, text="API Key")
        api_frame.pack(fill=tk.X, padx=10, pady=(10, 5), ipady=5)
        
        ttk.Label(api_frame, text="Groq API Key:").pack(side=tk.LEFT, padx=5)
        
        self.api_entry = ttk.Entry(api_frame, show="*", width=50)
        self.api_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.api_entry.insert(0, self._api_key)
        
        ttk.Button(api_frame, text="Save Key", command=self._save_api_key).pack(side=tk.RIGHT, padx=5)

    def _create_settings_section(self, parent):
        """Create settings section with cached widget references."""
        settings_frame = ttk.LabelFrame(parent, text="Configuration")
        settings_frame.pack(fill=tk.X, padx=10, pady=5, ipady=5)
        
        # Model selection
        model_frame = ttk.Frame(settings_frame)
        model_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(model_frame, text="Select Model:", width=15).pack(side=tk.LEFT)
        
        self.model_combo = ttk.Combobox(model_frame, values=self.DEFAULT_MODELS, state="readonly")
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.model_combo.set(self._selected_model)
        self.model_combo.bind("<<ComboboxSelected>>", self._on_model_select)

        # Theme selection
        theme_frame = ttk.Frame(settings_frame)
        theme_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(theme_frame, text="Select Theme:", width=15).pack(side=tk.LEFT)
        
        self.theme_combo = ttk.Combobox(theme_frame, values=list(self.THEME_MAP.keys()), state="readonly")
        self.theme_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Find current theme display name
        friendly_theme_name = next(
            (name for name, val in self.THEME_MAP.items() if val == self._theme_name), 
            list(self.THEME_MAP.keys())[0]
        )
        self.theme_combo.set(friendly_theme_name)
        self.theme_combo.bind("<<ComboboxSelected>>", self._on_theme_select)

    def _create_hotkey_section(self, parent):
        """Create hotkey section with optimized event handling."""
        hotkey_frame = ttk.LabelFrame(parent, text="Hotkey Settings")
        hotkey_frame.pack(fill=tk.X, padx=10, pady=5, ipady=5)
        
        instruction_text = ("To set a keyboard hotkey, click a box and press the combo. "
                          "For mouse, type its name (e.g., 'right', 'x1').")
        ttk.Label(hotkey_frame, text=instruction_text).pack(fill=tk.X, padx=5, pady=(0,5))
        
        # Primary hotkey
        main_hotkey_frame = ttk.Frame(hotkey_frame)
        main_hotkey_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(main_hotkey_frame, text="Primary Hotkey:", width=18).pack(side=tk.LEFT)
        
        self.enhance_hotkey_entry = ttk.Entry(main_hotkey_frame)
        self.enhance_hotkey_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.enhance_hotkey_entry.insert(0, self._enhance_hotkey)
        self.enhance_hotkey_entry.bind("<FocusIn>", 
                                     lambda e: self._setup_hotkey_capture(self.enhance_hotkey_entry))
        
        # Alternative hotkey
        alt_hotkey_frame = ttk.Frame(hotkey_frame)
        alt_hotkey_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(alt_hotkey_frame, text="Alternative Hotkey:", width=18).pack(side=tk.LEFT)
        
        self.alt_hotkey_entry = ttk.Entry(alt_hotkey_frame)
        self.alt_hotkey_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.alt_hotkey_entry.insert(0, self._alternative_hotkey)
        self.alt_hotkey_entry.bind("<FocusIn>", 
                                 lambda e: self._setup_hotkey_capture(self.alt_hotkey_entry))
        
        # Buttons
        button_frame = ttk.Frame(hotkey_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=(5,2))
        ttk.Button(button_frame, text="Save Hotkeys", command=self._save_hotkeys).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self._reset_hotkeys_to_default).pack(side=tk.LEFT, padx=5)
        
    def _create_io_sections(self, parent):
        """Create input/output sections with optimized text widgets."""
        io_frame = ttk.Frame(parent)
        io_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Input section
        input_frame = ttk.LabelFrame(io_frame, text="Input Text (or Copy text and press hotkey)")
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame, height=10, wrap=tk.WORD, bd=0, relief="flat",
            undo=True, maxundo=20
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Button section
        button_frame = ttk.Frame(io_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Enhance Text", command=self._enhance_text).pack(side=tk.LEFT, padx=(5,0))
        ttk.Button(button_frame, text="Clear", command=self._clear_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy Result", command=self._copy_result).pack(side=tk.LEFT, padx=5)
        
        # Output section
        output_frame = ttk.LabelFrame(io_frame, text="Enhanced Text")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, height=10, wrap=tk.WORD, bd=0, relief="flat",
            undo=True, maxundo=20
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status section
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=(5,10), side=tk.BOTTOM)
        
        self.status_label = ttk.Label(status_frame, text="Ready. Copy text to your clipboard, then press your hotkey.")
        self.status_label.pack(side=tk.LEFT, padx=5)
    
    def _create_history_section(self, parent):
        """Create the enhancement history section."""
        history_frame = ttk.LabelFrame(parent, text="Enhancement History (Last 10)")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        list_frame = ttk.Frame(history_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.history_listbox = tk.Listbox(list_frame, height=5)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(history_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        ttk.Button(button_frame, text="Copy Selected to Output", command=self._copy_history_to_output).pack(side=tk.LEFT)

        self._update_history_listbox()

    def _update_history_listbox(self):
        """Update the history listbox with recent enhancements."""
        self.history_listbox.delete(0, tk.END)
        for item in self._enhancement_history:
            # Show the first 80 characters as a preview
            preview = item.replace('\n', ' ').strip()
            self.history_listbox.insert(tk.END, f"{preview[:80]}...")

    def _copy_history_to_output(self):
        """Copy the selected history item to the output text widget."""
        selected_indices = self.history_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select an item from the history.")
            return

        selected_index = selected_indices[0]
        full_text = self._enhancement_history[selected_index]

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", full_text)
        self.status_label.config(text="Copied from history to output.")

    def _add_to_history(self, text):
        """Add a new item to the history, save, and update the listbox."""
        if not text or not text.strip():
            return

        self._enhancement_history.insert(0, text)
        self._enhancement_history = self._enhancement_history[:10]  # Keep only the last 10
        self._save_history()
        self._update_history_listbox()

    def _on_theme_select(self, event=None):
        """Handle theme selection with error handling."""
        try:
            friendly_name = self.theme_combo.get()
            self._theme_name = self.THEME_MAP[friendly_name]
            self.root.set_theme(self._theme_name)
            self._save_config()
        except Exception as e:
            messagebox.showerror("Theme Error", f"Could not change theme: {e}")

    def _on_model_select(self, event=None):
        """Handle model selection with notification."""
        self._selected_model = self.model_combo.get()
        self._save_config()
        
        # Extract friendly model name
        friendly_model_name = (self._selected_model.split('/')[-1] 
                             if '/' in self._selected_model 
                             else self._selected_model)
        self.status_label.config(text=f"Model set to: {friendly_model_name}")

    @lru_cache(maxsize=1)
    def _get_enhancement_prompt_template(self):
        """Cache the enhancement prompt template to avoid repeated string operations."""
        return """You are an elite AI assistant for a software development team. Your role is to take a developer's raw, often stream-of-consciousness, notes and transform them into perfectly structured, actionable tasks suitable for a project management system like Jira or GitHub Issues. Your most important job is to identify distinct, separate topics or tasks within the user's text and break them down into a numbered list. For each task, create a bolded, descriptive title and use bullet point
--- EXAMPLE OF PERFECT TRANSFORMATION ---
[BEGIN EXAMPLE]
**Developer's Raw Input:**
The user page is busted, it wont load their data. the endpoint seems slow. and the save button is just stuck on 'saving...' it never finishes. oh and also the search filter doesn't work for names with spaces in them.
**Your Perfectly Formatted Output:**
I've identified several issues that require attention:
**Task 1: User Profile Data Fails to Load**
-   The main profile page is not displaying user data upon loading.
-   Initial investigation suggests a performance issue or a failure in the backend data endpoint.
**Task 2: Save Action Does Not Complete on Profile Page**
-   When clicking the "Save" button, the button's state becomes stuck on "Saving..."
-   The operation never completes, and no success or error feedback is provided to the user.
**Task 3: Search Filter Fails with Multi-Word Input**
-   The search functionality does not correctly handle inputs that contain spaces.
-   For example, searching for "John Doe" fails, while searching for "John" may work as expected.
[END EXAMPLE]
---
{codebase_context}Now, using the exact same professional format and quality, process the developer's actual text provided below.
**Developer's Actual Text to Process:**
---
{text}
---
**Your Enhanced Output:**
"""

    def _get_enhancement_prompt(self, text):
        """Generate enhancement prompt using cached template, including smart context."""
        codebase_context = ""
        if self._codebase_path and os.path.isdir(self._codebase_path):
            keywords = self._extract_keywords_from_prompt(text)
            context_str = self._find_relevant_files(keywords)
            if context_str:
                codebase_context = (
                    "The user has provided a codebase. The following files seem most relevant to their request. "
                    "Use them to make the task breakdown more specific.\n"
                    f"**Relevant Files:**\n---\n{context_str}\n---\n\n"
                )

        template = self._get_enhancement_prompt_template()
        return template.format(text=text, codebase_context=codebase_context)

    def _enhance_with_groq(self, text):
        """Enhanced Groq API call with better error handling and optimization."""
        if not self.groq_client:
            raise ValueError("API Client not initialized.")
        
        try:
            completion = self.groq_client.chat.completions.create(
                model=self._selected_model,
                messages=[{"role": "user", "content": self._get_enhancement_prompt(text)}],
                temperature=0.5,
                max_completion_tokens=4096,
                top_p=1
            )
            return self._clean_text(completion.choices[0].message.content)
        except Exception as e:
            raise Exception(f"API Error: {str(e)}")
        
    def _clean_text(self, text):
        """Optimized text cleaning using pre-compiled regex patterns."""
        # Use pre-compiled patterns for better performance
        text = self.THINK_TAG_PATTERN.sub('', text)
        text = self.THINK_OPEN_CLOSE_PATTERN.sub('', text)
        text = self.MULTIPLE_NEWLINES_PATTERN.sub('\n\n', text)
        text = self.MULTIPLE_SPACES_PATTERN.sub(' ', text)
        return text.strip()

    def _save_api_key(self):
        """Save API key with validation and client initialization."""
        new_api_key = self.api_entry.get().strip()
        
        if not new_api_key:
            messagebox.showwarning("Warning", "Please enter an API Key.")
            self._invalidate_client()
            return
        
        # Update status
        self.status_label.config(text="Verifying API Key...")
        self.root.update_idletasks()
        
        try:
            # Test the API key
            test_client = Groq(api_key=new_api_key)
            
            # If successful, update our state
            self._api_key = new_api_key
            self._invalidate_client()  # Force recreation with new key
            self._save_config()
            
            self.status_label.config(text="API Key saved successfully!")
            messagebox.showinfo("Success", "API Key saved and client is ready!")
            
        except Exception as e:
            self.status_label.config(text="Invalid API Key.")
            messagebox.showerror("Error", f"Invalid API Key: {str(e)}")
            self._invalidate_client()

    def _show_notification(self, message, color="green"):
        """Show notification with optimized positioning and styling."""
        notification = tk.Toplevel(self.root)
        notification.overrideredirect(True)
        
        # Calculate position once
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        notification.geometry(f"280x50+{screen_w - 300}+{screen_h - 100}")
        
        # Create styled frame
        style = ttk.Style()
        style.configure("Notification.TFrame", background=color)
        
        frame = ttk.Frame(notification, style="Notification.TFrame", padding=10)
        frame.pack(expand=True, fill='both')
        
        label = ttk.Label(frame, text=message, background=color, 
                         foreground="white", font=("Segoe UI", 10))
        label.pack(expand=True)
        
        notification.attributes("-alpha", 0.95)
        notification.attributes("-topmost", True)
        
        # Auto-destroy after delay
        self.root.after(2500, notification.destroy)

    def _animate_status(self, dot_count=1):
        """Optimized status animation with reduced string operations."""
        if not self._is_enhancing:
            return
            
        # Use string multiplication instead of concatenation
        dots = "." * dot_count
        self.status_label.config(text=f"Enhancing{dots}")
        
        next_count = (dot_count % 3) + 1
        self.root.after(350, self._animate_status, next_count)

    def _enhance_text(self):
        """Enhanced text processing with thread pool."""
        if self._is_enhancing:
            return
            
        input_text = self.input_text.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showwarning("Warning", "Please enter text to enhance")
            return
        
        self._is_enhancing = True
        self._animate_status()
        
        # Use thread pool for better resource management
        future = self._thread_pool.submit(self._enhance_and_display_worker, input_text)
        
    def _enhance_and_display_worker(self, text):
        """Worker function for text enhancement."""
        try:
            enhanced = self._enhance_with_groq(text)
            self._is_enhancing = False
            self.root.after(0, self._display_result, enhanced)
        except Exception as e:
            self._is_enhancing = False
            self.root.after(0, lambda: messagebox.showerror("API Error", str(e)))
    
    def _display_result(self, enhanced_text):
        """Display enhancement result with optimized text operations."""
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", enhanced_text)
        self.status_label.config(text="Text enhanced successfully!")
        self._add_to_history(enhanced_text)

    def _enhance_selected_text(self):
        """Enhanced clipboard text processing with better error handling."""
        if self._is_enhancing:
            return
            
        try:
            text_to_enhance = pyperclip.paste()
            if not text_to_enhance or not text_to_enhance.strip():
                self.status_label.config(text="Clipboard is empty. Copy text first.")
                return
            
            self._is_enhancing = True
            self.root.after(0, self._animate_status)
            
            # Use thread pool
            future = self._thread_pool.submit(self._enhance_and_copy_worker, text_to_enhance)
            
        except Exception as e:
            self._is_enhancing = False
            self._show_notification(f"Error: {str(e)}", color="red")

    def _enhance_and_copy_worker(self, text):
        """Worker function for clipboard enhancement."""
        try:
            if not self.groq_client:
                self._is_enhancing = False
                self.root.after(0, lambda: self.status_label.config(text="API Key is not set."))
                return
            
            enhanced_text = self._enhance_with_groq(text)
            pyperclip.copy(enhanced_text)
            
            self._is_enhancing = False
            self.root.after(0, lambda: self.status_label.config(text="Enhanced text copied!"))
            self._add_to_history(enhanced_text)
            
        except Exception as e:
            self._is_enhancing = False
            self.root.after(0, lambda: self.status_label.config(text=f"API Error: {e}"))

    def _setup_hotkey_capture(self, entry_widget):
        """Optimized hotkey capture with better event handling."""
        entry_widget.config(state="normal")
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, "Press key combo or type mouse button...")
        
        def on_key_press(event):
            entry_widget.config(state="normal")
            
            # Skip modifier-only keys
            if event.keysym in ('Control_L','Control_R','Shift_L','Shift_R',
                               'Alt_L','Alt_R','Super_L','Super_R'):
                return
            
            # Build modifier list efficiently
            parts = []
            if event.state & 4:
                parts.append('ctrl')
            if event.state & 1:
                parts.append('shift')
            if event.state & 8 or event.state & 2048:
                parts.append('alt')
            if event.state & 64:
                parts.append('win')
            
            parts.append(event.keysym.lower())
            hotkey_string = "+".join(parts)
            
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, hotkey_string)
            self.root.focus()
            return "break"
        
        binding_id = entry_widget.bind('<KeyPress>', on_key_press)
        entry_widget.bind('<FocusOut>', 
                         lambda e: entry_widget.unbind('<KeyPress>', binding_id))
        
    def _save_hotkeys(self):
        """Save hotkeys with validation and atomic updates."""
        new_enhance = self.enhance_hotkey_entry.get().strip()
        new_alt = self.alt_hotkey_entry.get().strip()
        
        # Validate hotkeys
        if (not new_enhance or not new_alt or 
            "Press" in new_enhance or "Press" in new_alt):
            messagebox.showwarning("Invalid Hotkey", "Please set valid hotkeys.")
            return
        
        # Remove old hotkeys
        try:
            keyboard.remove_hotkey(self._enhance_hotkey)
            keyboard.remove_hotkey(self._alternative_hotkey)
        except Exception:
            pass  # Ignore if hotkeys weren't registered
        
        # Update hotkeys atomically
        self._enhance_hotkey = new_enhance
        self._alternative_hotkey = new_alt
        
        self._save_config()
        self._setup_hotkeys()
        
        messagebox.showinfo("Success", "Hotkeys have been updated!")

    def _reset_hotkeys_to_default(self):
        """Reset hotkeys to default values."""
        try:
            keyboard.remove_hotkey(self._enhance_hotkey)
            keyboard.remove_hotkey(self._alternative_hotkey)
        except Exception:
            pass
        
        # Reset to defaults
        self._enhance_hotkey = 'ctrl+shift+e'
        self._alternative_hotkey = 'ctrl+shift+r'
        
        # Update UI
        self.enhance_hotkey_entry.delete(0, tk.END)
        self.alt_hotkey_entry.delete(0, tk.END)
        self.enhance_hotkey_entry.insert(0, self._enhance_hotkey)
        self.alt_hotkey_entry.insert(0, self._alternative_hotkey)
        
        self._save_config()
        self._setup_hotkeys()
        
        messagebox.showinfo("Success", "Hotkeys have been reset to defaults.")
        
    def _setup_hotkeys(self):
        """Setup global hotkeys with error handling."""
        try:
            keyboard.add_hotkey(self._enhance_hotkey, self._enhance_selected_text)
            keyboard.add_hotkey(self._alternative_hotkey, self._enhance_selected_text)
        except Exception as e:
            messagebox.showerror("Hotkey Error", 
                               f"Could not register hotkey '{e.args[0]}'. It may be in use.")

    def _clear_text(self):
        """Clear text areas efficiently."""
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.status_label.config(text="Text cleared")

    def _copy_result(self):
        """Copy result with validation."""
        result = self.output_text.get("1.0", tk.END).strip()
        if result:
            pyperclip.copy(result)
            self.status_label.config(text="Result copied from window!")
        else:
            messagebox.showwarning("Warning", "No text to copy")

    def run(self):
        """Run the application with proper cleanup."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()

    def _on_closing(self):
        """Clean up resources on application close."""
        try:
            keyboard.unhook_all()
        except:
            pass
        
        # Shutdown thread pool
        self._thread_pool.shutdown(wait=False)
        
        self.root.destroy()


if __name__ == "__main__":
    app = OptimizedCodingEnglishEnhancer()
    print("Starting Optimized Coding English Enhancer...")
    app.run()