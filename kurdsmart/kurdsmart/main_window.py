from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .database import initialize_database
from .services.dictionary_service import DictionaryService
from .services.practice_service import PracticeService
from .services.sentence_service import SentenceService
from .services.tts_service import TTSService
from .workers import WorkerTask, run_in_thread


class KurdSmartWindow(QMainWindow):
    def __init__(self, db_path: Path) -> None:
        super().__init__()
        self.setWindowTitle("KurdSmart - Kurdish Language Tutor")
        self.resize(1120, 760)

        self.dictionary_service = DictionaryService(db_path)
        self.sentence_service = SentenceService()
        self.practice_service = PracticeService(db_path)
        self.tts_service = TTSService()

        self._threads = []

        self.dark_mode = False
        self._setup_menu()
        self._setup_ui()
        self.apply_theme()

    def _setup_menu(self) -> None:
        view_menu = self.menuBar().addMenu("View")
        self.toggle_theme_action = QAction("Toggle Dark/Light", self)
        self.toggle_theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.toggle_theme_action)

    def _setup_ui(self) -> None:
        base_font = QFont("Segoe UI", 10)
        app = QApplication.instance()
        if app:
            app.setFont(base_font)

        tabs = QTabWidget()
        tabs.addTab(self._dictionary_tab(), "Dictionary")
        tabs.addTab(self._sentences_tab(), "Sentences")
        tabs.addTab(self._practice_tab(), "Practice")
        tabs.addTab(self._review_tab(), "Saved Vocabulary")
        self.setCentralWidget(tabs)

    def _dialect_selector(self) -> QComboBox:
        combo = QComboBox()
        combo.addItems(["Sorani", "Kurmanji"])
        return combo

    def _dictionary_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        top_bar = QHBoxLayout()
        self.dict_dialect = self._dialect_selector()
        self.domain_filter = QComboBox()
        self.domain_filter.addItems(["all", "general", "medical", "technical"])
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Kurdish, Persian, or English...")
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_dictionary)

        top_bar.addWidget(QLabel("Dialect"))
        top_bar.addWidget(self.dict_dialect)
        top_bar.addWidget(QLabel("Domain"))
        top_bar.addWidget(self.domain_filter)
        top_bar.addWidget(self.search_input, stretch=1)
        top_bar.addWidget(search_btn)

        self.dict_table = QTableWidget(0, 5)
        self.dict_table.setHorizontalHeaderLabels(["Kurdish", "Persian", "English", "Domain", "Dialect"])
        self.dict_table.horizontalHeader().setStretchLastSection(True)
        self.dict_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        action_bar = QHBoxLayout()
        save_btn = QPushButton("Save Selected Word")
        save_btn.clicked.connect(self.save_selected_word)
        pronounce_btn = QPushButton("Pronounce Selected Kurdish")
        pronounce_btn.clicked.connect(self.pronounce_selected_word)
        action_bar.addWidget(save_btn)
        action_bar.addWidget(pronounce_btn)

        layout.addLayout(top_bar)
        layout.addWidget(self.dict_table)
        layout.addLayout(action_bar)
        return page

    def _sentences_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        self.sentence_dialect = self._dialect_selector()
        form = QFormLayout()
        self.subject_input = QLineEdit("Ez / من")
        self.verb_input = QLineEdit("dixwazim / دەمەوێت")
        self.object_input = QLineEdit("fêr bibim kurdî / فێربم کوردی")
        form.addRow("Dialect", self.sentence_dialect)
        form.addRow("Subject", self.subject_input)
        form.addRow("Verb", self.verb_input)
        form.addRow("Object", self.object_input)

        generate_btn = QPushButton("Generate Sentences")
        generate_btn.clicked.connect(self.generate_sentences)
        self.generated_output = QTextEdit()
        self.generated_output.setReadOnly(True)

        analysis_btn = QPushButton("Analyze Current Text")
        analysis_btn.clicked.connect(self.analyze_sentence)
        self.analysis_output = QLabel("Analysis appears here.")
        self.analysis_output.setWordWrap(True)

        pronunciation_box = QHBoxLayout()
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setRange(120, 220)
        self.rate_slider.setValue(170)
        speak_btn = QPushButton("Pronounce Text")
        speak_btn.clicked.connect(self.pronounce_generated_text)
        pronunciation_box.addWidget(QLabel("Speed"))
        pronunciation_box.addWidget(self.rate_slider)
        pronunciation_box.addWidget(speak_btn)

        layout.addLayout(form)
        layout.addWidget(generate_btn)
        layout.addWidget(self.generated_output)
        layout.addWidget(analysis_btn)
        layout.addWidget(self.analysis_output)
        layout.addLayout(pronunciation_box)
        return page

    def _practice_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        top = QHBoxLayout()
        self.practice_dialect = self._dialect_selector()
        load_btn = QPushButton("Load Exercises")
        load_btn.clicked.connect(self.load_exercises)
        top.addWidget(QLabel("Dialect"))
        top.addWidget(self.practice_dialect)
        top.addWidget(load_btn)
        top.addStretch()

        self.exercise_prompt = QLabel("Click 'Load Exercises' to start.")
        self.exercise_prompt.setWordWrap(True)
        self.exercise_answer = QLineEdit()
        self.exercise_answer.setPlaceholderText("Type your answer...")
        check_btn = QPushButton("Check Answer")
        check_btn.clicked.connect(self.check_exercise_answer)
        self.practice_feedback = QLabel("")

        layout.addLayout(top)
        layout.addWidget(self.exercise_prompt)
        layout.addWidget(self.exercise_answer)
        layout.addWidget(check_btn)
        layout.addWidget(self.practice_feedback)

        self._exercise_cache: list[dict] = []
        self._exercise_index = 0
        return page

    def _review_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        refresh_btn = QPushButton("Refresh Saved Words")
        refresh_btn.clicked.connect(self.refresh_saved_words)

        self.saved_table = QTableWidget(0, 6)
        self.saved_table.setHorizontalHeaderLabels(
            ["Kurdish", "Persian", "English", "Domain", "Dialect", "Saved At"]
        )
        self.saved_table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(refresh_btn)
        layout.addWidget(self.saved_table)
        return page

    def apply_theme(self) -> None:
        if self.dark_mode:
            self.setStyleSheet(
                """
                QWidget { background-color: #1f1f1f; color: #f2f2f2; }
                QLineEdit, QTextEdit, QComboBox, QTableWidget {
                    background-color: #2a2a2a;
                    color: #f2f2f2;
                    border: 1px solid #3a3a3a;
                }
                QPushButton { background-color: #324f7b; border-radius: 4px; padding: 6px; }
                QPushButton:hover { background-color: #3f669d; }
                """
            )
        else:
            self.setStyleSheet("")

    def toggle_theme(self) -> None:
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def search_dictionary(self) -> None:
        rows = self.dictionary_service.search(
            self.search_input.text(),
            self.dict_dialect.currentText(),
            self.domain_filter.currentText(),
        )
        self.dict_table.setRowCount(len(rows))
        self.dict_table.setProperty("row_data", rows)

        for r, row in enumerate(rows):
            self.dict_table.setItem(r, 0, QTableWidgetItem(row["kurdish"]))
            self.dict_table.setItem(r, 1, QTableWidgetItem(row["persian"]))
            self.dict_table.setItem(r, 2, QTableWidgetItem(row["english"]))
            self.dict_table.setItem(r, 3, QTableWidgetItem(row["domain"]))
            self.dict_table.setItem(r, 4, QTableWidgetItem(row["dialect"]))

    def save_selected_word(self) -> None:
        current_row = self.dict_table.currentRow()
        rows = self.dict_table.property("row_data") or []
        if current_row < 0 or current_row >= len(rows):
            self._info("Please select a dictionary row first.")
            return
        self.dictionary_service.save_word(rows[current_row]["id"])
        self._info("Word saved for review.")

    def pronounce_selected_word(self) -> None:
        current_row = self.dict_table.currentRow()
        if current_row < 0:
            self._info("Select a row to pronounce.")
            return
        text = self.dict_table.item(current_row, 0).text()
        self._run_tts(text)

    def generate_sentences(self) -> None:
        sentences = self.sentence_service.generate(
            self.subject_input.text(),
            self.verb_input.text(),
            self.object_input.text(),
            self.sentence_dialect.currentText(),
        )
        self.generated_output.setText("\n".join(f"• {sentence}" for sentence in sentences))

    def analyze_sentence(self) -> None:
        analysis = self.sentence_service.analyze(self.generated_output.toPlainText())
        self.analysis_output.setText(
            f"Words: {analysis['word_count']} | Characters: {analysis['characters']}\n"
            f"Tokens: {', '.join(analysis['tokens'])}\nHint: {analysis['hint']}"
        )

    def pronounce_generated_text(self) -> None:
        text = self.generated_output.toPlainText()
        self._run_tts(text)

    def _run_tts(self, text: str) -> None:
        task = WorkerTask(
            fn=self.tts_service.speak,
            args=(text, self.rate_slider.value()),
            kwargs={},
        )
        thread, worker = run_in_thread(task)
        worker.signals.finished.connect(lambda result: self.statusBar().showMessage(str(result), 5000))
        worker.signals.failed.connect(lambda msg: self.statusBar().showMessage(f"TTS error: {msg}", 5000))
        self._threads.append(thread)
        thread.start()

    def load_exercises(self) -> None:
        self._exercise_cache = self.practice_service.list_exercises(self.practice_dialect.currentText())
        self._exercise_index = 0
        self._show_current_exercise()

    def _show_current_exercise(self) -> None:
        if not self._exercise_cache:
            self.exercise_prompt.setText("No exercises available for selected dialect.")
            return
        prompt = self._exercise_cache[self._exercise_index]["prompt"]
        self.exercise_prompt.setText(prompt)
        self.exercise_answer.clear()

    def check_exercise_answer(self) -> None:
        if not self._exercise_cache:
            self.practice_feedback.setText("Load exercises first.")
            return
        current = self._exercise_cache[self._exercise_index]
        correct = self.practice_service.check_answer(self.exercise_answer.text(), current["answer"])

        if correct:
            self.practice_feedback.setText("✅ Correct. Great progress!")
            self._exercise_index = (self._exercise_index + 1) % len(self._exercise_cache)
            self._show_current_exercise()
        else:
            self.practice_feedback.setText(f"❌ Try again. Hint answer starts with: {current['answer'][:1]}")

    def refresh_saved_words(self) -> None:
        rows = self.dictionary_service.get_saved_words()
        self.saved_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.saved_table.setItem(r, 0, QTableWidgetItem(row["kurdish"]))
            self.saved_table.setItem(r, 1, QTableWidgetItem(row["persian"]))
            self.saved_table.setItem(r, 2, QTableWidgetItem(row["english"]))
            self.saved_table.setItem(r, 3, QTableWidgetItem(row["domain"]))
            self.saved_table.setItem(r, 4, QTableWidgetItem(row["dialect"]))
            self.saved_table.setItem(r, 5, QTableWidgetItem(row["created_at"]))

    def _info(self, text: str) -> None:
        QMessageBox.information(self, "KurdSmart", text)


def run() -> None:
    app = QApplication(sys.argv)
    data_dir = Path.home() / "AppData" / "Local" / "KurdSmart"
    db_path = initialize_database(data_dir)
    window = KurdSmartWindow(db_path)
    window.show()
    sys.exit(app.exec())
