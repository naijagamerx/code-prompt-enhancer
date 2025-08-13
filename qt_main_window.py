import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QGroupBox, QLabel, QLineEdit, QPushButton, QComboBox,
    QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, backend=None):
        super().__init__()
        self.backend = backend
        self.setWindowTitle("Code Prompt Enhancer - PyQt Edition")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()
        if self.backend:
            self.load_initial_state()
            self._connect_signals()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("Ready.")
        main_layout.addWidget(self.status_label, 0, Qt.AlignmentFlag.AlignBottom)

        self.tabs = QTabWidget()
        main_layout.insertWidget(0, self.tabs)

        self.enhancer_tab = QWidget()
        self.history_tab = QWidget()
        self.about_tab = QWidget()
        self.tabs.addTab(self.enhancer_tab, "Enhancer")
        self.tabs.addTab(self.history_tab, "History")
        self.tabs.addTab(self.about_tab, "About")

        self.setup_enhancer_tab()
        self.setup_history_tab()
        self.setup_about_tab()

    def setup_enhancer_tab(self):
        enhancer_layout = QHBoxLayout(self.enhancer_tab)
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        enhancer_layout.addWidget(left_column, 1)
        enhancer_layout.addWidget(right_column, 1)

        self._create_api_key_section(left_layout)
        self._create_settings_section(left_layout)
        self._create_hotkey_section(left_layout)
        self._create_codebase_section(left_layout)
        self._create_input_section(left_layout)
        self._create_output_section(right_layout)

    def _create_api_key_section(self, layout):
        group = QGroupBox("API Key")
        layout.addWidget(group)
        group_layout = QHBoxLayout(group)
        label = QLabel("Groq API Key:")
        self.api_entry = QLineEdit()
        self.api_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.save_api_key_button = QPushButton("Save Key")
        group_layout.addWidget(label)
        group_layout.addWidget(self.api_entry, 1)
        group_layout.addWidget(self.save_api_key_button)

    def _create_settings_section(self, layout):
        group = QGroupBox("Configuration")
        layout.addWidget(group)
        group_layout = QVBoxLayout(group)
        model_layout = QHBoxLayout()
        model_label = QLabel("Select Model:")
        self.model_combo = QComboBox()
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo, 1)
        group_layout.addLayout(model_layout)
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Select Theme:")
        self.theme_combo = QComboBox()
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo, 1)
        group_layout.addLayout(theme_layout)

    def _create_hotkey_section(self, layout):
        group = QGroupBox("Hotkey Settings")
        layout.addWidget(group)
        group_layout = QVBoxLayout(group)
        instruction_label = QLabel("Note: Hotkeys are global and managed by the 'keyboard' library.")
        group_layout.addWidget(instruction_label)
        primary_layout = QHBoxLayout()
        primary_label = QLabel("Primary Hotkey:")
        self.enhance_hotkey_entry = QLineEdit()
        primary_layout.addWidget(primary_label)
        primary_layout.addWidget(self.enhance_hotkey_entry)
        group_layout.addLayout(primary_layout)
        alt_layout = QHBoxLayout()
        alt_label = QLabel("Alternative Hotkey:")
        self.alt_hotkey_entry = QLineEdit()
        alt_layout.addWidget(alt_label)
        alt_layout.addWidget(self.alt_hotkey_entry)
        group_layout.addLayout(alt_layout)
        button_layout = QHBoxLayout()
        self.save_hotkeys_button = QPushButton("Save Hotkeys")
        self.reset_hotkeys_button = QPushButton("Reset to Defaults")
        button_layout.addWidget(self.save_hotkeys_button)
        button_layout.addWidget(self.reset_hotkeys_button)
        button_layout.addStretch()
        group_layout.addLayout(button_layout)

    def _create_codebase_section(self, layout):
        group = QGroupBox("Context and Actions")
        layout.addWidget(group)
        group_layout = QVBoxLayout(group)
        context_button_layout = QHBoxLayout()
        self.select_folder_button = QPushButton("Select Project Folder...")
        self.clear_folder_button = QPushButton("Clear Folder")
        self.index_button = QPushButton("Index Project")
        context_button_layout.addWidget(self.select_folder_button)
        context_button_layout.addWidget(self.clear_folder_button)
        context_button_layout.addWidget(self.index_button)
        context_button_layout.addStretch()
        group_layout.addLayout(context_button_layout)
        self.codebase_path_label = QLabel("No folder selected.")
        group_layout.addWidget(self.codebase_path_label)
        group_layout.addWidget(QLabel("--- Main Actions ---"))
        action_button_layout = QHBoxLayout()
        self.enhance_button = QPushButton("Enhance Text")
        self.clear_button = QPushButton("Clear Text")
        self.copy_button = QPushButton("Copy Result")
        action_button_layout.addWidget(self.enhance_button)
        action_button_layout.addWidget(self.clear_button)
        action_button_layout.addWidget(self.copy_button)
        action_button_layout.addStretch()
        group_layout.addLayout(action_button_layout)

    def _create_input_section(self, layout):
        group = QGroupBox("Input Text")
        layout.addWidget(group)
        group_layout = QVBoxLayout(group)
        self.input_text = QTextEdit()
        group_layout.addWidget(self.input_text)

    def _create_output_section(self, layout):
        group = QGroupBox("Enhanced Text")
        layout.addWidget(group)
        group_layout = QVBoxLayout(group)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        group_layout.addWidget(self.output_text)

    def setup_history_tab(self):
        history_layout = QVBoxLayout(self.history_tab)
        group = QGroupBox("Enhancement History (Last 10)")
        history_layout.addWidget(group)
        group_layout = QVBoxLayout(group)
        self.history_list = QTextEdit()
        self.history_list.setReadOnly(True)
        group_layout.addWidget(self.history_list)
        button_layout = QHBoxLayout()
        self.copy_history_button = QPushButton("Copy Selected to Output")
        button_layout.addWidget(self.copy_history_button)
        button_layout.addStretch()
        group_layout.addLayout(button_layout)

    def setup_about_tab(self):
        layout = QVBoxLayout(self.about_tab)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        title_label = QLabel("Code Prompt Enhancer")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        version_label = QLabel("Version: 2.0 (PyQt Edition)")
        version_label.setStyleSheet("font-size: 14px; color: grey;")
        layout.addWidget(version_label)
        layout.addSpacing(20)
        description = (
            "The Code Prompt Enhancer is a Python application designed to streamline the workflow "
            "of software developers by transforming raw, unstructured notes into well-defined, "
            "actionable tasks suitable for AI code agents."
        )
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        layout.addSpacing(20)
        github_label = QLabel('<a href="https://github.com/naijagamerx/code-prompt-enhancer">View Project on GitHub</a>')
        github_label.setOpenExternalLinks(True)
        layout.addWidget(github_label)

    # --- UI Update Methods ---
    def load_initial_state(self):
        self.api_entry.setText(self.backend.api_key)
        self.model_combo.addItems(self.backend.DEFAULT_MODELS)
        self.model_combo.setCurrentText(self.backend.selected_model)
        self.theme_combo.addItems(self.backend.THEME_MAP.keys())
        theme_name_key = next((k for k, v in self.backend.THEME_MAP.items() if v == self.backend.theme_name), "Windows Native")
        self.theme_combo.setCurrentText(theme_name_key)
        self.enhance_hotkey_entry.setText(self.backend.enhance_hotkey)
        self.alt_hotkey_entry.setText(self.backend.alternative_hotkey)
        self.update_history_list()
        self.apply_theme(self.backend.theme_name)

    def update_output_text(self, text):
        self.output_text.setPlainText(text)

    def update_history_list(self):
        self.history_list.setPlainText("\n\n---\\n\n".join(self.backend.enhancement_history))

    def set_status(self, text):
        self.status_label.setText(text)

    def show_message_box(self, title, message):
        QMessageBox.information(self, title, message)

    def _connect_signals(self):
        self.enhance_button.clicked.connect(self.on_enhance_click)
        self.save_api_key_button.clicked.connect(self.on_save_api_key_click)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)

    def on_enhance_click(self):
        input_text = self.input_text.toPlainText()
        self.backend.enhance_text_qt(input_text)

    def on_save_api_key_click(self):
        api_key = self.api_entry.text()
        if not api_key:
            self.show_message_box("Warning", "Please enter an API key.")
            return

        self.backend.api_key = api_key
        self.backend._groq_client = None # Force re-initialization
        self.backend.save_config()

        self.show_message_box("Success", "API Key saved successfully.")

    def apply_theme(self, theme_name):
        if theme_name == 'winnative':
            self.setStyleSheet("")
            return

        qss_file = f"themes/{theme_name}.qss"
        if os.path.exists(qss_file):
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Theme file not found: {qss_file}")

    def on_theme_changed(self, theme_display_name):
        theme_name = self.backend.THEME_MAP.get(theme_display_name)
        if theme_name:
            self.backend.theme_name = theme_name
            self.backend.save_config()
            self.apply_theme(theme_name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
