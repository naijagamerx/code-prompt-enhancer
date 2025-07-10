import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import pyperclip
import keyboard
import threading
import json
import os
from cryptography.fernet import Fernet
from groq import Groq
import time

# Import the theming library
from ttkthemes import ThemedTk

class CodingEnglishEnhancer:
    def __init__(self):
        self.groq_client = None
        self.config_file = "encrypted_config.json"
        self.encryption_key_file = "encryption.key"
        
        self.enhance_hotkey = 'ctrl+shift+e'
        self.alternative_hotkey = 'ctrl+shift+r'
        
        self.models = [
            'qwen/qwen3-32b', 'deepseek-r1-distill-llama-70b', 'gemma2-9b-it',
            'llama-3.3-70b-versatile', 'meta-llama/llama-4-maverick-17b-128e-instruct'
        ]
        self.selected_model = self.models[0]

        # --- MODIFIED: The theme list is now simplified to only your two preferred themes ---
        self.theme_map = {
            'Radiance (Polished)': 'radiance',
            'Plastik (3D)': 'plastik',
        }
        self.theme_name = 'radiance' # Default theme

        self.is_enhancing = False
        self.load_config()
        self.setup_gui()
        self.setup_hotkeys()
        
    def load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.encryption_key_file):
                with open(self.encryption_key_file, "rb") as key_file:
                    key = key_file.read()
                f = Fernet(key)

                if os.path.exists(self.config_file):
                    with open(self.config_file, 'rb') as f:
                        encrypted_data = f.read()
                    decrypted_data = f.decrypt(encrypted_data).decode()
                    config = json.loads(decrypted_data)

                    self.api_key = config.get('api_key', '')
                    hotkey_config = config.get('hotkeys', {})
                    self.enhance_hotkey = hotkey_config.get('enhance', 'ctrl+shift+e')
                    self.alternative_hotkey = hotkey_config.get('alternative', 'ctrl+shift+r')
                    self.theme_name = config.get('theme', 'radiance')
                    self.selected_model = config.get('model', self.models[0])
                else:
                    self.api_key = ''
            else:
                print("Encryption key not found. Please ensure 'encryption.key' exists.")
                self.api_key = ''

        except Exception as e:
            print(f"Error loading config: {e}"); self.api_key = ''
            
    def save_config(self):
        """Save configuration to file."""
        try:
            config = {
                'api_key': self.api_key,
                'hotkeys': {
                    'enhance': self.enhance_hotkey,
                    'alternative': self.alternative_hotkey
                },
                'theme': self.theme_name,
                'model': self.selected_model
            }
            # Saving the config is disabled, since the config is encrypted
            # with open(self.config_file, 'w') as f: json.dump(config, f, indent=4)
        except Exception as e: print(f"Error saving config: {e}")
    
    def setup_gui(self):
        """Setup the main GUI with theme and model selection."""
        self.root = ThemedTk(theme=self.theme_name)
        self.root.title("Coding English Enhancer")
        self.root.geometry("800x750")
        
        self._create_api_key_section()
        self._create_settings_section()
        self._create_hotkey_section()
        self._create_io_sections()

    def _create_api_key_section(self):
        api_frame = ttk.LabelFrame(self.root, text="API Key")
        api_frame.pack(fill=tk.X, padx=10, pady=(10, 5), ipady=5)
        ttk.Label(api_frame, text="Groq API Key:").pack(side=tk.LEFT, padx=5)
        self.api_entry = ttk.Entry(api_frame, show="*", width=50)
        self.api_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.api_entry.insert(0, self.api_key)
        ttk.Button(api_frame, text="Save Key", command=self.save_api_key).pack(side=tk.RIGHT, padx=5)

    def _create_settings_section(self):
        settings_frame = ttk.LabelFrame(self.root, text="Configuration")
        settings_frame.pack(fill=tk.X, padx=10, pady=5, ipady=5)
        
        model_frame = ttk.Frame(settings_frame)
        model_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(model_frame, text="Select Model:", width=15).pack(side=tk.LEFT)
        self.model_combo = ttk.Combobox(model_frame, values=self.models, state="readonly")
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.model_combo.set(self.selected_model)
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_select)

        theme_frame = ttk.Frame(settings_frame)
        theme_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(theme_frame, text="Select Theme:", width=15).pack(side=tk.LEFT)
        self.theme_combo = ttk.Combobox(theme_frame, values=list(self.theme_map.keys()), state="readonly")
        self.theme_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        friendly_theme_name = next((name for name, val in self.theme_map.items() if val == self.theme_name), list(self.theme_map.keys())[0])
        self.theme_combo.set(friendly_theme_name)
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_select)

    def _create_hotkey_section(self):
        hotkey_frame = ttk.LabelFrame(self.root, text="Hotkey Settings")
        hotkey_frame.pack(fill=tk.X, padx=10, pady=5, ipady=5)
        ttk.Label(hotkey_frame, text="To set a keyboard hotkey, click a box and press the combo. For mouse, type its name (e.g., 'right', 'x1').").pack(fill=tk.X, padx=5, pady=(0,5))
        main_hotkey_subframe = ttk.Frame(hotkey_frame)
        main_hotkey_subframe.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(main_hotkey_subframe, text="Primary Hotkey:", width=18).pack(side=tk.LEFT)
        self.enhance_hotkey_entry = ttk.Entry(main_hotkey_subframe)
        self.enhance_hotkey_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.enhance_hotkey_entry.insert(0, self.enhance_hotkey)
        self.enhance_hotkey_entry.bind("<FocusIn>", lambda e: self.setup_hotkey_capture(self.enhance_hotkey_entry))
        alt_hotkey_subframe = ttk.Frame(hotkey_frame)
        alt_hotkey_subframe.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(alt_hotkey_subframe, text="Alternative Hotkey:", width=18).pack(side=tk.LEFT)
        self.alt_hotkey_entry = ttk.Entry(alt_hotkey_subframe)
        self.alt_hotkey_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.alt_hotkey_entry.insert(0, self.alternative_hotkey)
        self.alt_hotkey_entry.bind("<FocusIn>", lambda e: self.setup_hotkey_capture(self.alt_hotkey_entry))
        hotkey_button_frame = ttk.Frame(hotkey_frame)
        hotkey_button_frame.pack(fill=tk.X, padx=5, pady=(5,2))
        ttk.Button(hotkey_button_frame, text="Save Hotkeys", command=self.save_hotkeys).pack(side=tk.LEFT)
        ttk.Button(hotkey_button_frame, text="Reset to Defaults", command=self.reset_hotkeys_to_default).pack(side=tk.LEFT, padx=5)
        
    def _create_io_sections(self):
        input_frame = ttk.LabelFrame(self.root, text="Input Text (or Copy text and press hotkey)")
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.input_text = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD, bd=0, relief="flat")
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(button_frame, text="Enhance Text", command=self.enhance_text).pack(side=tk.LEFT, padx=(5,0))
        ttk.Button(button_frame, text="Clear", command=self.clear_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy Result", command=self.copy_result).pack(side=tk.LEFT, padx=5)
        output_frame = ttk.LabelFrame(self.root, text="Enhanced Text")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, height=10, wrap=tk.WORD, bd=0, relief="flat")
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=(5,10))
        self.status_label = ttk.Label(status_frame, text="Ready. Copy text to your clipboard, then press your hotkey.")
        self.status_label.pack(side=tk.LEFT, padx=5)
    
    def on_theme_select(self, event=None):
        friendly_name = self.theme_combo.get()
        self.theme_name = self.theme_map[friendly_name]
        try:
            self.root.set_theme(self.theme_name)
            self.save_config()
        except Exception as e: messagebox.showerror("Theme Error", f"Could not change theme: {e}")

    def on_model_select(self, event=None):
        self.selected_model = self.model_combo.get()
        self.save_config()
        friendly_model_name = self.selected_model.split('/')[-1] if '/' in self.selected_model else self.selected_model
        self.show_notification(f"Model set to: {friendly_model_name}")

    def enhance_with_groq(self, text):
        if not self.groq_client: raise ValueError("API Client not initialized.")
        completion = self.groq_client.chat.completions.create(model=self.selected_model, messages=[{"role": "user", "content": self.get_enhancement_prompt(text)}], temperature=0.5, max_completion_tokens=4096, top_p=1)
        return self.clean_text(completion.choices[0].message.content)
        
    def get_enhancement_prompt(self, text):
        return f"""You are an elite AI assistant for a software development team. Your role is to take a developer's raw, often stream-of-consciousness, notes and transform them into perfectly structured, actionable tasks suitable for a project management system like Jira or GitHub Issues. Your most important job is to identify distinct, separate topics or tasks within the user's text and break them down into a numbered list. For each task, create a bolded, descriptive title and use bullet points for the details. **Do not suggest code or implementation details.** Focus only on describing the problem and the context.
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
Now, using the exact same professional format and quality, process the developer's actual text provided below.
**Developer's Actual Text to Process:**
---
{text}
---
**Your Enhanced Output:**
"""

    def save_api_key(self):
        self.api_key = self.api_entry.get().strip()
        if not self.api_key: messagebox.showwarning("Warning", "Please enter an API Key."); self.groq_client = None; return
        try:
            self.status_label.config(text="Verifying API Key...")
            self.groq_client = Groq(api_key=self.api_key); self.save_config()
            self.status_label.config(text="API Key saved successfully!")
            messagebox.showinfo("Success", "API Key saved and client is ready!")
        except Exception as e: self.status_label.config(text="Invalid API Key."); messagebox.showerror("Error", f"Invalid API Key: {str(e)}"); self.groq_client = None

    def show_notification(self, message, color="green"):
        notification = tk.Toplevel(self.root)
        notification.overrideredirect(True)
        screen_w, screen_h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        notification.geometry(f"280x50+{screen_w - 300}+{screen_h - 100}")
        style = ttk.Style(); style.configure("Notification.TFrame", background=color)
        frame = ttk.Frame(notification, style="Notification.TFrame", padding=10)
        frame.pack(expand=True, fill='both')
        label = ttk.Label(frame, text=message, background=color, foreground="white", font=("Segoe UI", 10))
        label.pack(expand=True)
        notification.attributes("-alpha", 0.95); notification.attributes("-topmost", True)
        self.root.after(2500, notification.destroy)

    def animate_status(self, dot_count=1):
        if not self.is_enhancing: return
        dots = "." * dot_count; self.status_label.config(text=f"Enhancing{dots}")
        next_count = (dot_count % 3) + 1; self.root.after(350, self.animate_status, next_count)

    def enhance_text(self):
        if self.is_enhancing: return
        input_text = self.input_text.get("1.0", tk.END).strip()
        if not input_text: messagebox.showwarning("Warning", "Please enter text to enhance"); return
        self.is_enhancing = True; self.animate_status(); threading.Thread(target=self._enhance_and_display_worker, args=(input_text,), daemon=True).start()

    def _enhance_and_display_worker(self, text):
        try:
            enhanced = self.enhance_with_groq(text)
            self.is_enhancing = False; self.root.after(0, self._display_result, enhanced)
        except Exception as e: self.is_enhancing = False; self.root.after(0, lambda: messagebox.showerror("API Error", str(e)))
    
    def _display_result(self, enhanced_text):
        self.output_text.delete("1.0", tk.END); self.output_text.insert("1.0", enhanced_text); self.status_label.config(text="Text enhanced successfully!")

    def enhance_selected_text(self):
        if self.is_enhancing: return
        try:
            text_to_enhance = pyperclip.paste()
            if not text_to_enhance or not text_to_enhance.strip(): self.show_notification("Clipboard is empty. Copy text first.", color="#DAA520"); return
            self.is_enhancing = True; self.root.after(0, self.animate_status)
            threading.Thread(target=self._enhance_and_copy_worker, args=(text_to_enhance,), daemon=True).start()
        except Exception as e: self.is_enhancing = False; self.show_notification(f"Error: {str(e)}", color="red")

    def _enhance_and_copy_worker(self, text):
        try:
            if not self.groq_client: self.is_enhancing = False; self.root.after(0, lambda: self.show_notification("API Key is not set.", color="red")); return
            enhanced_text = self.enhance_with_groq(text); pyperclip.copy(enhanced_text)
            self.is_enhancing = False; self.root.after(0, lambda: self.show_notification("Enhanced text copied!"))
        except Exception as e: self.is_enhancing = False; self.root.after(0, lambda: self.show_notification(f"API Error: {e}", color="red"))

    def setup_hotkey_capture(self, entry_widget):
        entry_widget.config(state="normal"); entry_widget.delete(0, tk.END); entry_widget.insert(0, "Press key combo or type mouse button...")
        def on_key_press(event):
            entry_widget.config(state="normal")
            if event.keysym in ('Control_L','Control_R','Shift_L','Shift_R','Alt_L','Alt_R','Super_L','Super_R'): return
            parts = ['ctrl'] if event.state & 4 else []
            if event.state & 1: parts.append('shift')
            if event.state & 8 or event.state & 2048: parts.append('alt')
            if event.state & 64: parts.append('win')
            parts.append(event.keysym.lower())
            hotkey_string = "+".join(parts); entry_widget.delete(0, tk.END); entry_widget.insert(0, hotkey_string); self.root.focus(); return "break"
        binding_id = entry_widget.bind('<KeyPress>', on_key_press); entry_widget.bind('<FocusOut>', lambda e: entry_widget.unbind('<KeyPress>', binding_id))
        
    def save_hotkeys(self):
        new_enhance, new_alt = self.enhance_hotkey_entry.get().strip(), self.alt_hotkey_entry.get().strip()
        if not new_enhance or not new_alt or "Press" in new_enhance or "Press" in new_alt: messagebox.showwarning("Invalid Hotkey", "Please set valid hotkeys."); return
        try: keyboard.remove_hotkey(self.enhance_hotkey); keyboard.remove_hotkey(self.alternative_hotkey)
        except Exception: pass
        self.enhance_hotkey, self.alternative_hotkey = new_enhance, new_alt
        self.save_config(); self.setup_hotkeys()
        messagebox.showinfo("Success", "Hotkeys have been updated!")

    def reset_hotkeys_to_default(self):
        try: keyboard.remove_hotkey(self.enhance_hotkey); keyboard.remove_hotkey(self.alternative_hotkey)
        except Exception: pass
        self.enhance_hotkey, self.alternative_hotkey = 'ctrl+shift+e', 'ctrl+shift+r'
        self.enhance_hotkey_entry.delete(0, tk.END); self.alt_hotkey_entry.delete(0, tk.END)
        self.enhance_hotkey_entry.insert(0, self.enhance_hotkey); self.alt_hotkey_entry.insert(0, self.alternative_hotkey)
        self.save_config(); self.setup_hotkeys(); messagebox.showinfo("Success", "Hotkeys have been reset to defaults.")
        
    def setup_hotkeys(self):
        try:
            keyboard.add_hotkey(self.enhance_hotkey, self.enhance_selected_text)
            keyboard.add_hotkey(self.alternative_hotkey, self.enhance_selected_text)
        except Exception as e: messagebox.showerror("Hotkey Error", f"Could not register hotkey '{e.args[0]}'. It may be in use.")

    def clean_text(self, text):
        import re
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'</?think[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    def run(self): self.root.protocol("WM_DELETE_WINDOW", self.on_closing); self.root.mainloop()
    def on_closing(self):
        try: keyboard.unhook_all()
        except: pass
        self.root.destroy()
    def clear_text(self): self.input_text.delete("1.0", tk.END); self.output_text.delete("1.0", tk.END); self.status_label.config(text="Text cleared")
    def copy_result(self): result = self.output_text.get("1.0", tk.END).strip(); pyperclip.copy(result); self.show_notification("Result copied from window!")

def disable_context_menu(event):
    pass  # Do nothing on right-click

if __name__ == "__main__":
    app = CodingEnglishEnhancer()
    app.root.bind("<Button-3>", disable_context_menu)
    print("Starting Coding English Enhancer...")
    app.run()