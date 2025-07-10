import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import pyperclip
import keyboard
import threading
import json
import os
from groq import Groq
import time

class CodingEnglishEnhancer:
    # ... (all other functions like __init__, load_config, setup_gui, etc., are exactly the same) ...
    # ... (I am omitting them here for brevity, but they should remain in your file) ...

    def __init__(self):
        self.groq_client = None
        self.config_file = "enhancer_config.json"
        
        self.enhance_hotkey = 'ctrl+shift+e'
        self.alternative_hotkey = 'ctrl+shift+r'

        self.load_config()
        self.setup_gui()
        self.setup_hotkeys()
        
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key', '')
                    hotkey_config = config.get('hotkeys', {})
                    self.enhance_hotkey = hotkey_config.get('enhance', 'ctrl+shift+e')
                    self.alternative_hotkey = hotkey_config.get('alternative', 'ctrl+shift+r')
            else:
                self.api_key = ''
        except Exception as e:
            print(f"Error loading config: {e}")
            self.api_key = ''
            
    def save_config(self):
        try:
            config = {
                'api_key': self.api_key,
                'hotkeys': {
                    'enhance': self.enhance_hotkey,
                    'alternative': self.alternative_hotkey
                }
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Coding English Enhancer")
        self.root.geometry("800x700")
        
        api_frame = ttk.Frame(self.root)
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(api_frame, text="Groq API Key:").pack(side=tk.LEFT)
        self.api_entry = ttk.Entry(api_frame, show="*", width=50)
        self.api_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.api_entry.insert(0, self.api_key)
        ttk.Button(api_frame, text="Save Key", command=self.save_api_key).pack(side=tk.RIGHT, padx=5)
        
        hotkey_frame = ttk.LabelFrame(self.root, text="Hotkey Settings")
        hotkey_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(hotkey_frame, text="Click a box and press your desired key combination.").pack(fill=tk.X, padx=5, pady=(0, 5))
        main_hotkey_subframe = ttk.Frame(hotkey_frame)
        main_hotkey_subframe.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(main_hotkey_subframe, text="Primary Enhance Hotkey:", width=22).pack(side=tk.LEFT)
        self.enhance_hotkey_entry = ttk.Entry(main_hotkey_subframe)
        self.enhance_hotkey_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.enhance_hotkey_entry.insert(0, self.enhance_hotkey)
        self.enhance_hotkey_entry.config(state="readonly")
        self.enhance_hotkey_entry.bind("<FocusIn>", lambda e: self.setup_hotkey_capture(self.enhance_hotkey_entry))
        alt_hotkey_subframe = ttk.Frame(hotkey_frame)
        alt_hotkey_subframe.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(alt_hotkey_subframe, text="Alternative Enhance Hotkey:", width=22).pack(side=tk.LEFT)
        self.alt_hotkey_entry = ttk.Entry(alt_hotkey_subframe)
        self.alt_hotkey_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.alt_hotkey_entry.insert(0, self.alternative_hotkey)
        self.alt_hotkey_entry.config(state="readonly")
        self.alt_hotkey_entry.bind("<FocusIn>", lambda e: self.setup_hotkey_capture(self.alt_hotkey_entry))
        hotkey_button_frame = ttk.Frame(hotkey_frame)
        hotkey_button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(hotkey_button_frame, text="Save Hotkeys", command=self.save_hotkeys).pack(side=tk.LEFT)
        ttk.Button(hotkey_button_frame, text="Reset to Defaults", command=self.reset_hotkeys_to_default).pack(side=tk.LEFT, padx=5)

        input_frame = ttk.LabelFrame(self.root, text="Input Text (or Copy text and press hotkey)")
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.input_text = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(button_frame, text="Enhance Text", command=self.enhance_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy Result", command=self.copy_result).pack(side=tk.LEFT, padx=5)
        
        output_frame = ttk.LabelFrame(self.root, text="Enhanced Text")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, height=10, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        self.status_label = ttk.Label(status_frame, text="Ready. Copy text to your clipboard, then press your hotkey.")
        self.status_label.pack(side=tk.LEFT)
        
        self.setup_context_menu()
    
    def setup_hotkeys(self):
        try:
            keyboard.add_hotkey(self.enhance_hotkey, self.enhance_selected_text)
            print(f"Hotkey '{self.enhance_hotkey}' registered successfully")
            keyboard.add_hotkey(self.alternative_hotkey, self.enhance_selected_text)
            print(f"Hotkey '{self.alternative_hotkey}' registered successfully")
        except Exception as e:
            messagebox.showerror("Hotkey Error", f"Could not register hotkey: {e}\n\nIt might be in use by another application.")
            print(f"Error registering hotkeys: {e}")

    def setup_hotkey_capture(self, entry_widget):
        entry_widget.config(state="normal")
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, "Press a key combination...")
        
        def on_key_press(event):
            entry_widget.config(state="normal")
            if event.keysym in ('Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'Super_L', 'Super_R'): return
            parts = []
            if event.state & 4: parts.append('ctrl')
            if event.state & 1: parts.append('shift')
            if event.state & 8 or event.state & 2048: parts.append('alt')
            if event.state & 64: parts.append('win')
            parts.append(event.keysym.lower())
            hotkey_string = "+".join(parts)
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, hotkey_string)
            entry_widget.config(state="readonly")
            self.root.focus()
            return "break"

        binding_id = entry_widget.bind('<KeyPress>', on_key_press)
        def on_focus_out(event):
            entry_widget.unbind('<KeyPress>', binding_id)
        entry_widget.bind('<FocusOut>', on_focus_out)

    def save_hotkeys(self):
        new_enhance = self.enhance_hotkey_entry.get()
        new_alt = self.alt_hotkey_entry.get()
        if not new_enhance or not new_alt or "Press a key" in new_enhance or "Press a key" in new_alt:
            messagebox.showwarning("Invalid Hotkey", "Please set a valid hotkey for both fields.")
            return
        try:
            keyboard.remove_hotkey(self.enhance_hotkey)
            keyboard.remove_hotkey(self.alternative_hotkey)
        except (KeyError, ValueError) as e:
            print(f"Could not unregister old hotkey (this is often okay): {e}")
        self.enhance_hotkey = new_enhance
        self.alternative_hotkey = new_alt
        self.save_config()
        self.setup_hotkeys()
        messagebox.showinfo("Success", "Hotkeys have been updated successfully!")

    def reset_hotkeys_to_default(self):
        try:
            keyboard.remove_hotkey(self.enhance_hotkey)
            keyboard.remove_hotkey(self.alternative_hotkey)
        except (KeyError, ValueError) as e:
            print(f"Could not unregister old hotkey (this is often okay): {e}")
        self.enhance_hotkey = 'ctrl+shift+e'
        self.alternative_hotkey = 'ctrl+shift+r'
        self.enhance_hotkey_entry.config(state="normal")
        self.alt_hotkey_entry.config(state="normal")
        self.enhance_hotkey_entry.delete(0, tk.END)
        self.alt_hotkey_entry.delete(0, tk.END)
        self.enhance_hotkey_entry.insert(0, self.enhance_hotkey)
        self.alt_hotkey_entry.insert(0, self.alternative_hotkey)
        self.enhance_hotkey_entry.config(state="readonly")
        self.alt_hotkey_entry.config(state="readonly")
        self.save_config()
        self.setup_hotkeys()
        messagebox.showinfo("Success", "Hotkeys have been reset to defaults.")
        
    def setup_context_menu(self):
        try:
            import winreg, sys
            script_path = os.path.abspath(sys.argv[0])
            key_path = r"Software\Classes\*\shell\EnhanceText"
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValue(key, "", winreg.REG_SZ, "Enhance Text with AI")
                winreg.CloseKey(key)
                cmd_key_path = key_path + r"\command"
                cmd_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_key_path)
                command = f'pythonw "{script_path}" --enhance-file "%1"'
                winreg.SetValue(cmd_key, "", winreg.REG_SZ, command)
                winreg.CloseKey(cmd_key)
                print("Right-click context menu installed successfully")
            except Exception as e:
                print(f"Could not install context menu: {e}")
        except ImportError:
            print("Context menu only available on Windows")
    
    def save_api_key(self):
        self.api_key = self.api_entry.get().strip()
        if self.api_key:
            try:
                self.groq_client = Groq(api_key=self.api_key)
                self.save_config()
                self.status_label.config(text="API Key saved successfully!")
                messagebox.showinfo("Success", "API Key saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Invalid API Key: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Please enter a valid API Key")
    
    def clean_text(self, text):
        import re
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'</?think[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = text.strip()
        return text

    # --- THIS IS THE ONLY FUNCTION THAT HAS CHANGED ---
    def get_enhancement_prompt(self, text):
        """Generate the enhancement prompt for coding context using a few-shot example."""
        return f"""You are an elite AI assistant for a software development team. Your role is to take a developer's raw, often stream-of-consciousness, notes and transform them into perfectly structured, actionable tasks suitable for a project management system like Jira or GitHub Issues.

Your most important job is to identify distinct, separate topics or tasks within the user's text and break them down into a numbered list. For each task, create a bolded title and use bullet points for the details.

--- EXAMPLE ---
[BEGIN EXAMPLE]
Developer's Rough Input:
hey so i found a bug the login page is broken on mobile, the inputs are too wide. also the profile pic upload is not working, it gives a 500 error when i try to upload a png. and one more thing the dashboard loading spinner never goes away its just stuck.

Your Perfect Output:
I've identified a few issues that need attention:

**Task 1: Fix Login Page on Mobile**
-   The input fields on the login page are too wide on mobile viewports, causing horizontal scrolling.
-   Please ensure the login form is fully responsive and usable on small screens.

**Task 2: Resolve Profile Picture Upload Error**
-   Attempting to upload a PNG file as a profile picture results in a 500 Internal Server Error.
-   This feature needs to be debugged to allow for successful image uploads.

**Task 3: Correct Dashboard Loading Spinner**
-   The loading spinner on the main dashboard remains on-screen indefinitely after the content has loaded.
-   The spinner should hide automatically once the dashboard data is fully rendered.
[END EXAMPLE]
---

Now, process the following developer notes using the exact same format and level of quality.

--- DEVELOPER'S ACTUAL TEXT TO PROCESS ---
{text}
--- YOUR ENHANCED OUTPUT ---
"""

    def enhance_with_groq(self, text):
        if not self.groq_client:
            if not self.api_key: return "Error: Please set your Groq API key first"
            try: self.groq_client = Groq(api_key=self.api_key)
            except Exception as e: return f"Error: Invalid API key - {str(e)}"
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="qwen/qwen3-32b",
                messages=[{"role": "user", "content": self.get_enhancement_prompt(text)}],
                temperature=0.6, max_completion_tokens=4096, top_p=0.95, stream=False, stop=None
            )
            raw_output = completion.choices[0].message.content
            cleaned_output = self.clean_text(raw_output)
            return cleaned_output
        except Exception as e:
            return f"Error enhancing text: {str(e)}"
    
    def enhance_text(self):
        input_text = self.input_text.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showwarning("Warning", "Please enter some text to enhance")
            return
        self.status_label.config(text="Enhancing text...")
        self.root.update()
        threading.Thread(target=self._enhance_and_display, args=(input_text,), daemon=True).start()
    
    def _enhance_and_display(self, text):
        enhanced = self.enhance_with_groq(text)
        self.root.after(0, self._display_result, enhanced)
    
    def _display_result(self, enhanced_text):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", enhanced_text)
        self.status_label.config(text="Text enhanced successfully!")
    
    def enhance_selected_text(self):
        try:
            text_to_enhance = pyperclip.paste()
            if text_to_enhance and text_to_enhance.strip():
                self.root.after(0, lambda: self.status_label.config(text="Enhancing clipboard text..."))
                enhanced_text = self.enhance_with_groq(text_to_enhance)
                pyperclip.copy(enhanced_text)
                self.root.after(0, lambda: self.status_label.config(text="Enhanced text copied to clipboard!"))
            else:
                self.root.after(0, lambda: self.status_label.config(text="Clipboard is empty. Copy some text first."))
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}"))
    
    def clear_text(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.status_label.config(text="Text cleared")
    
    def copy_result(self):
        result = self.output_text.get("1.0", tk.END).strip()
        if result:
            pyperclip.copy(result)
            self.status_label.config(text="Enhanced text copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No enhanced text to copy")
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        try: keyboard.unhook_all()
        except: pass
        self.root.destroy()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "--enhance-file":
        file_path = sys.argv[2]
        try:
            with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
            enhancer = CodingEnglishEnhancer()
            if enhancer.api_key:
                enhanced = enhancer.enhance_with_groq(content)
                pyperclip.copy(enhanced)
                print("Enhanced text copied to clipboard!")
            else: print("Please set up API key first by running the application normally")
        except Exception as e: print(f"Error: {e}")
        exit()
    
    try: import pyperclip, keyboard
    except ImportError as e:
        print(f"Missing required package: {e}\npip install pyperclip keyboard groq")
        exit(1)
    
    app = CodingEnglishEnhancer()
    print("Starting Coding English Enhancer...")
    app.run()