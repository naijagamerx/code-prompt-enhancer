import sys
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

from PyQt6.QtWidgets import QApplication
from qt_main_window import MainWindow

class PromptEnhancerBackend:
    """
    Backend logic for the Code Prompt Enhancer.
    This class handles configuration, API calls, history, and indexing,
    but contains no UI code.
    """
    
    DEFAULT_MODELS = [
        'moonshotai/kimi-k2-instruct', 'openai/gpt-oss-120b', 'qwen/qwen3-32b',
        'deepseek-r1-distill-llama-70b', 'gemma2-9b-it', 'llama-3.3-70b-versatile',
        'meta-llama/llama-4-maverick-17b-128e-instruct'
    ]
    
    THEME_MAP = {
        'Radiance (Polished)': 'radiance',
        'Plastik (3D)': 'plastik',
        'Breeze (Clean)': 'breeze',
        'Clearlooks (Classic)': 'clearlooks',
        'Windows Native': 'winnative',
    }
    
    THINK_TAG_PATTERN = re.compile(r'<think>.*?</think>', re.DOTALL | re.IGNORECASE)
    THINK_OPEN_CLOSE_PATTERN = re.compile(r'</?think[^>]*>', re.IGNORECASE)
    MULTIPLE_NEWLINES_PATTERN = re.compile(r'\n\s*\n')
    MULTIPLE_SPACES_PATTERN = re.compile(r'[ \t]+')
    
    def __init__(self):
        self._groq_client = None
        self._config_file = "enhancer_config.json"
        self._history_file = "enhancement_history.json"
        self.enhancement_history = []
        self.codebase_path = None
        self._is_enhancing = False
        self._thread_pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix="enhancer")
        
        # Default config values
        self.enhance_hotkey = 'ctrl+shift+e'
        self.alternative_hotkey = 'ctrl+shift+r'
        self.selected_model = self.DEFAULT_MODELS[0]
        self.theme_name = 'radiance'
        self.api_key = ''
        
        # Load initial state
        self.load_config()
        self.load_history()
        
    def set_ui(self, ui):
        """Reference to the UI to allow backend to update it."""
        self.ui = weakref.ref(ui)

    @property
    def groq_client(self):
        if self._groq_client is None and self.api_key:
            try:
                self._groq_client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"Error initializing Groq client: {e}")
        return self._groq_client
    
    def invalidate_client(self):
        self._groq_client = None
        
    def load_config(self):
        try:
            if not os.path.exists(self._config_file): return
            with open(self._config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.api_key = config.get('api_key', '')
            hotkey_config = config.get('hotkeys', {})
            self.enhance_hotkey = hotkey_config.get('enhance', 'ctrl+shift+e')
            self.alternative_hotkey = hotkey_config.get('alternative', 'ctrl+shift+r')
            self.theme_name = config.get('theme', 'radiance')
            self.selected_model = config.get('model', self.DEFAULT_MODELS[0])
        except Exception as e:
            print(f"Error loading config: {e}")
            
    def save_config(self):
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
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def load_history(self):
        try:
            if os.path.exists(self._history_file):
                with open(self._history_file, 'r', encoding='utf-8') as f:
                    self.enhancement_history = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading history: {e}")
            self.enhancement_history = []

    def save_history(self):
        try:
            with open(self._history_file, 'w', encoding='utf-8') as f:
                json.dump(self.enhancement_history, f, indent=4)
        except IOError as e:
            print(f"Error saving history: {e}")

    def add_to_history(self, text):
        if not text or not text.strip(): return
        self.enhancement_history.insert(0, text)
        self.enhancement_history = self.enhancement_history[:10]
        self.save_history()

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
        if self.codebase_path and os.path.isdir(self.codebase_path):
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
        """Search for relevant files using a pre-built index if available."""
        if not self.codebase_path or not keywords:
            return ""

        index_path = os.path.join(self.codebase_path, ".enhancer_cache", "index.json")

        ui = self.ui()
        if not ui: return ""

        if os.path.exists(index_path):
            # Use the pre-built index for instant results
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)

                relevant_files = set()
                for keyword in keywords:
                    if keyword in index:
                        relevant_files.update(index[keyword])

                if not relevant_files:
                    return ""
                return "Relevant files found (from index):\n- " + "\n- ".join(list(relevant_files)[:10])

            except (IOError, json.JSONDecodeError) as e:
                print(f"Error reading index file: {e}")
                return self._live_search_relevant_files(keywords)
        else:
            # Fallback to live search if no index exists
            ui.set_status("No index found. Performing live file search...")
            return self._live_search_relevant_files(keywords)

    def _live_search_relevant_files(self, keywords):
        """Perform a live search of the filesystem for relevant files."""
        relevant_files = set()
        for root, _, files in os.walk(self.codebase_path):
            if any(d in root for d in {'.git', '__pycache__', 'node_modules'}):
                continue

            for file in files:
                if len(relevant_files) >= 10:
                    break

                file_path = os.path.join(root, file)
                if any(k in file.lower() for k in keywords):
                    relevant_files.add(file_path)
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content_sample = f.read(512)
                        if any(k in content_sample.lower() for k in keywords):
                            relevant_files.add(file_path)
                except Exception:
                    continue

        if not relevant_files:
            return ""

        relative_paths = [os.path.relpath(p, self.codebase_path) for p in relevant_files]
        return "Relevant files found (live search):\n- " + "\n- ".join(relative_paths)

    def _enhance_with_groq(self, text):
        """Enhanced Groq API call with better error handling and optimization."""
        if not self.groq_client:
            raise ValueError("API Client not initialized.")
        
        try:
            completion = self.groq_client.chat.completions.create(
                model=self.selected_model,
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
        text = self.THINK_TAG_PATTERN.sub('', text)
        text = self.THINK_OPEN_CLOSE_PATTERN.sub('', text)
        text = self.MULTIPLE_NEWLINES_PATTERN.sub('\n\n', text)
        text = self.MULTIPLE_SPACES_PATTERN.sub(' ', text)
        return text.strip()

    def enhance_text_qt(self, input_text):
        ui = self.ui()
        if not ui or self._is_enhancing: return
        
        if not input_text:
            ui.show_message_box("Warning", "Please enter text to enhance")
            return
        
        self._is_enhancing = True
        ui.set_status("Enhancing...")
        
        self._thread_pool.submit(self._enhance_and_display_worker, input_text)

    def _enhance_and_display_worker(self, text):
        ui = self.ui()
        if not ui: return
        try:
            enhanced_text = self._enhance_with_groq(text)
            ui.update_output_text(enhanced_text)
            self.add_to_history(enhanced_text)
            ui.update_history_list()
            ui.set_status("Text enhanced successfully!")
        except Exception as e:
            ui.show_message_box("API Error", str(e))
            ui.set_status("API Error.")
        finally:
            self._is_enhancing = False

    def shutdown(self):
        self._thread_pool.shutdown(wait=False)
        try:
            keyboard.unhook_all()
        except Exception:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    backend = PromptEnhancerBackend()
    window = MainWindow(backend)
    backend.set_ui(window)
    window.show()
    sys.exit(app.exec())