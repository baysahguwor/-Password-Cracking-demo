"""
Main dashboard widget containing all panels.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QProgressBar, QTextEdit, QFrame, QGridLayout,
    QSizePolicy, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QFont, QColor, QPalette

from ui.charts import AttemptsChart
from password_analyzer import analyze_password
from brute_force_engine import BruteForceEngine
from dictionary_attack import DictionaryAttackEngine
from hybrid_attack import HybridAttackEngine
from attack_logger import AttackLogger

# ── Palette ─────────────────────────────────────────────────────────────────
BG_DARK      = "#0D1117"
BG_PANEL     = "#111820"
BG_CARD      = "#161D27"
BORDER_COLOR = "#1E2A38"
NEON_BLUE    = "#00BFFF"
NEON_GREEN   = "#39FF14"
NEON_RED     = "#FF4444"
NEON_ORANGE  = "#FF8C00"
NEON_YELLOW  = "#FFD700"
TEXT_PRIMARY = "#E0EAF4"
TEXT_MUTED   = "#5A7A94"
ACCENT       = "#0A84FF"

FONT_MONO = QFont("Consolas", 9)
FONT_MONO_SM = QFont("Consolas", 8)
FONT_HEADER = QFont("Segoe UI", 10, QFont.Weight.Bold)
FONT_TITLE  = QFont("Segoe UI", 12, QFont.Weight.Bold)


def _card(title: str = "") -> QFrame:
    frame = QFrame()
    frame.setStyleSheet(f"""
        QFrame {{
            background: {BG_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
        }}
    """)
    return frame


def _label(text: str, font=None, color=TEXT_PRIMARY) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color: {color}; background: transparent; border: none;")
    if font:
        lbl.setFont(font)
    return lbl


def _section_title(text: str) -> QLabel:
    lbl = QLabel(f"  {text}")
    lbl.setFont(FONT_HEADER)
    lbl.setStyleSheet(f"""
        color: {NEON_BLUE};
        background: {BG_PANEL};
        border-bottom: 1px solid {BORDER_COLOR};
        padding: 6px 0 6px 4px;
        border-radius: 0px;
    """)
    lbl.setFixedHeight(32)
    return lbl


# ── Signal bridge for cross-thread UI updates ─────────────────────────────
class _Bridge(QObject):
    progress = Signal(dict)
    done     = Signal(dict)


# ── Dashboard ─────────────────────────────────────────────────────────────
class Dashboard(QWidget):
    DEMO_PASSWORDS = ["password123", "admin", "Welcome@123", "MyStrongPass!2026"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = AttackLogger()
        self._engine = None
        self._active_attack = None
        self._current_run_id = 0
        self._last_terminal_attempts = 0
        self._bridge = _Bridge()
        self._bridge.progress.connect(self._on_progress)
        self._bridge.done.connect(self._on_done)

        self._build_ui()
        self._load_log_table()

    # ── UI construction ────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # Header bar
        root.addWidget(self._build_header())

        # Main body splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #1E2A38; width: 2px; }")
        splitter.addWidget(self._build_left_column())
        splitter.addWidget(self._build_center_column())
        splitter.addWidget(self._build_right_column())
        splitter.setSizes([340, 480, 360])
        root.addWidget(splitter, 1)

        # Status bar
        self._status_bar = _label("Ready.", FONT_MONO_SM, TEXT_MUTED)
        self._status_bar.setStyleSheet(f"color:{TEXT_MUTED}; padding:2px 6px; background:{BG_PANEL}; border-top:1px solid {BORDER_COLOR};")
        root.addWidget(self._status_bar)

    def _build_header(self) -> QWidget:
        frame = QFrame()
        frame.setFixedHeight(52)
        frame.setStyleSheet(f"background:{BG_PANEL}; border-bottom: 1px solid {BORDER_COLOR};")
        hl = QHBoxLayout(frame)
        hl.setContentsMargins(12, 0, 12, 0)

        icon_lbl = _label("🔐", QFont("Segoe UI Emoji", 20))
        title_lbl = _label("  PASSWORD CRACKING VISUALIZER", QFont("Segoe UI", 14, QFont.Weight.Bold), NEON_BLUE)
        subtitle = _label("  Cybersecurity Educational Demo  |  Local Simulation Only", FONT_MONO_SM, TEXT_MUTED)

        hl.addWidget(icon_lbl)
        hl.addWidget(title_lbl)
        hl.addStretch()
        hl.addWidget(subtitle)
        return frame

    # ── Left column: password input + strength + education ─────────────────
    def _build_left_column(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{BG_DARK};")
        vl = QVBoxLayout(w)
        vl.setSpacing(8)
        vl.setContentsMargins(4, 4, 4, 4)

        vl.addWidget(_section_title("[ PASSWORD INPUT ]"))
        vl.addWidget(self._build_input_panel())
        vl.addWidget(_section_title("[ STRENGTH ANALYSIS ]"))
        vl.addWidget(self._build_strength_panel())
        vl.addWidget(_section_title("[ SECURITY TIPS ]"))
        vl.addWidget(self._build_education_panel())
        vl.addStretch()
        return w

    def _build_input_panel(self) -> QFrame:
        card = _card()
        vl = QVBoxLayout(card)
        vl.setSpacing(6)
        vl.setContentsMargins(10, 10, 10, 10)

        vl.addWidget(_label("Enter Password to Test:", FONT_HEADER, NEON_BLUE))

        self._pw_input = QLineEdit()
        self._pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._pw_input.setFont(FONT_MONO)
        self._pw_input.setPlaceholderText("Type a password...")
        self._pw_input.setStyleSheet(f"""
            QLineEdit {{
                background: #0A0F16;
                color: {NEON_GREEN};
                border: 1px solid {NEON_BLUE};
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 14px;
            }}
            QLineEdit:focus {{ border: 1.5px solid {NEON_GREEN}; }}
        """)
        self._pw_input.textChanged.connect(self._on_pw_changed)
        vl.addWidget(self._pw_input)

        # Show/hide toggle
        self._show_btn = QPushButton("Show")
        self._show_btn.setCheckable(True)
        self._show_btn.clicked.connect(self._toggle_echo)
        self._show_btn.setFixedWidth(60)
        self._show_btn.setStyleSheet(self._btn_style(NEON_BLUE))
        vl.addWidget(self._show_btn, alignment=Qt.AlignmentFlag.AlignRight)

        analyze_btn = QPushButton("⚡  Analyze Password")
        analyze_btn.setFont(FONT_HEADER)
        analyze_btn.setStyleSheet(self._btn_style(NEON_BLUE, large=True))
        analyze_btn.clicked.connect(self._do_analyze)
        vl.addWidget(analyze_btn)

        # Quick demo buttons
        vl.addWidget(_label("Quick Demo Passwords:", FONT_MONO_SM, TEXT_MUTED))
        grid = QGridLayout()
        grid.setSpacing(4)
        for i, pw in enumerate(self.DEMO_PASSWORDS):
            btn = QPushButton(pw)
            btn.setFont(FONT_MONO_SM)
            btn.setStyleSheet(self._btn_style(NEON_ORANGE))
            btn.clicked.connect(lambda _, p=pw: self._set_demo(p))
            grid.addWidget(btn, i // 2, i % 2)
        vl.addLayout(grid)
        return card

    def _build_strength_panel(self) -> QFrame:
        card = _card()
        vl = QVBoxLayout(card)
        vl.setContentsMargins(10, 10, 10, 10)
        vl.setSpacing(6)

        self._strength_label = _label("—", QFont("Segoe UI", 20, QFont.Weight.Bold), TEXT_MUTED)
        self._strength_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(self._strength_label)

        self._strength_bar = QProgressBar()
        self._strength_bar.setRange(0, 100)
        self._strength_bar.setValue(0)
        self._strength_bar.setTextVisible(False)
        self._strength_bar.setFixedHeight(16)
        self._strength_bar.setStyleSheet(self._progress_style(NEON_BLUE))
        vl.addWidget(self._strength_bar)

        self._crack_time_label = _label("Estimated Crack Time: —", FONT_MONO, NEON_YELLOW)
        self._crack_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(self._crack_time_label)

        # Factor indicators
        self._factors_grid = QGridLayout()
        self._factors_grid.setSpacing(4)
        self._factor_labels = {}
        factors = [
            ("length", "Length ≥ 8"),
            ("has_upper", "Uppercase"),
            ("has_lower", "Lowercase"),
            ("has_digit", "Numbers"),
            ("has_symbol", "Symbols"),
            ("no_common", "No Common Words"),
        ]
        for i, (key, text) in enumerate(factors):
            dot = _label("●", FONT_MONO_SM, TEXT_MUTED)
            lbl = _label(text, FONT_MONO_SM, TEXT_MUTED)
            self._factor_labels[key] = (dot, lbl)
            self._factors_grid.addWidget(dot, i, 0)
            self._factors_grid.addWidget(lbl, i, 1)
        vl.addLayout(self._factors_grid)
        return card

    def _build_education_panel(self) -> QFrame:
        card = _card()
        vl = QVBoxLayout(card)
        vl.setContentsMargins(10, 10, 10, 10)
        tips = [
            "✔ Use passwords longer than 12 characters",
            "✔ Avoid dictionary words",
            "✔ Mix uppercase, lowercase, digits & symbols",
            "✔ Do not reuse passwords across sites",
            "✔ Enable multi-factor authentication (MFA)",
            "✔ Use a password manager",
            "✔ Change passwords after a breach",
        ]
        for tip in tips:
            l = _label(tip, FONT_MONO_SM, NEON_GREEN)
            l.setWordWrap(True)
            vl.addWidget(l)
        return card

    # ── Center column: attack simulation ──────────────────────────────────
    def _build_center_column(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{BG_DARK};")
        vl = QVBoxLayout(w)
        vl.setSpacing(8)
        vl.setContentsMargins(4, 4, 4, 4)

        vl.addWidget(_section_title("[ ATTACK SIMULATION ]"))
        vl.addWidget(self._build_attack_buttons())
        vl.addWidget(_section_title("[ LIVE STATISTICS ]"))
        vl.addWidget(self._build_stats_panel())
        vl.addWidget(_section_title("[ ATTACK TERMINAL ]"))
        vl.addWidget(self._build_terminal_panel(), 1)
        return w

    def _build_attack_buttons(self) -> QFrame:
        card = _card()
        hl = QHBoxLayout(card)
        hl.setContentsMargins(10, 8, 10, 8)
        hl.setSpacing(8)

        self._bf_btn = QPushButton("💻  Brute Force")
        self._dict_btn = QPushButton("📖  Dictionary")
        self._hybrid_btn = QPushButton("🔀  Hybrid")
        self._stop_btn = QPushButton("⛔  Stop Attack")

        for btn, color in [
            (self._bf_btn, NEON_RED),
            (self._dict_btn, NEON_ORANGE),
            (self._hybrid_btn, NEON_YELLOW),
        ]:
            btn.setFont(FONT_HEADER)
            btn.setStyleSheet(self._btn_style(color, large=True))
            hl.addWidget(btn)

        self._stop_btn.setFont(FONT_HEADER)
        self._stop_btn.setStyleSheet(self._btn_style("#555555", large=True))
        self._stop_btn.setEnabled(False)
        hl.addWidget(self._stop_btn)

        self._bf_btn.clicked.connect(lambda: self._start_attack("brute_force"))
        self._dict_btn.clicked.connect(lambda: self._start_attack("dictionary"))
        self._hybrid_btn.clicked.connect(lambda: self._start_attack("hybrid"))
        self._stop_btn.clicked.connect(self._stop_attack)
        return card

    def _build_stats_panel(self) -> QFrame:
        card = _card()
        grid = QGridLayout(card)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setSpacing(10)

        def _stat(label_text, value_text, color):
            vl = QVBoxLayout()
            lbl = _label(label_text, FONT_MONO_SM, TEXT_MUTED)
            val = _label(value_text, QFont("Consolas", 15, QFont.Weight.Bold), color)
            val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vl.addWidget(val)
            vl.addWidget(lbl)
            return vl, val

        self._stat_attempts_vl, self._stat_attempts   = _stat("ATTEMPTS",     "0",      NEON_BLUE)
        self._stat_speed_vl,    self._stat_speed      = _stat("SPEED /sec",   "0",      NEON_GREEN)
        self._stat_elapsed_vl,  self._stat_elapsed    = _stat("ELAPSED (s)",  "0.00",   NEON_YELLOW)
        self._stat_progress_vl, self._stat_progress_n = _stat("PROGRESS",     "0%",     NEON_ORANGE)

        grid.addLayout(self._stat_attempts_vl,  0, 0)
        grid.addLayout(self._stat_speed_vl,     0, 1)
        grid.addLayout(self._stat_elapsed_vl,   0, 2)
        grid.addLayout(self._stat_progress_vl,  0, 3)

        self._attack_progress_bar = QProgressBar()
        self._attack_progress_bar.setRange(0, 100)
        self._attack_progress_bar.setValue(0)
        self._attack_progress_bar.setFixedHeight(18)
        self._attack_progress_bar.setTextVisible(False)
        self._attack_progress_bar.setStyleSheet(self._progress_style(NEON_RED))
        grid.addWidget(self._attack_progress_bar, 1, 0, 1, 4)

        return card

    def _build_terminal_panel(self) -> QFrame:
        card = _card()
        vl = QVBoxLayout(card)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        self._terminal = QTextEdit()
        self._terminal.setReadOnly(True)
        self._terminal.setFont(FONT_MONO)
        self._terminal.setStyleSheet(f"""
            QTextEdit {{
                background: #060C12;
                color: {NEON_GREEN};
                border: none;
                padding: 8px;
            }}
        """)
        vl.addWidget(self._terminal)
        return card

    # ── Right column: chart + result + log table ───────────────────────────
    def _build_right_column(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{BG_DARK};")
        vl = QVBoxLayout(w)
        vl.setSpacing(8)
        vl.setContentsMargins(4, 4, 4, 4)

        vl.addWidget(_section_title("[ CRACKING TIMELINE ]"))
        self._chart = AttemptsChart()
        vl.addWidget(self._chart)

        vl.addWidget(_section_title("[ ATTACK RESULT ]"))
        vl.addWidget(self._build_result_panel())
        vl.addWidget(_section_title("[ ATTACK LOG DATABASE ]"))
        vl.addWidget(self._build_log_panel(), 1)
        return w

    def _build_result_panel(self) -> QFrame:
        card = _card()
        grid = QGridLayout(card)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setSpacing(4)

        labels = ["Attack Type:", "Password:", "Attempts:", "Time to Crack:", "Strength:"]
        self._result_vals = []
        for i, lbl_text in enumerate(labels):
            lbl = _label(lbl_text, FONT_MONO_SM, TEXT_MUTED)
            val = _label("—", FONT_MONO_SM, NEON_BLUE)
            grid.addWidget(lbl, i, 0)
            grid.addWidget(val, i, 1)
            self._result_vals.append(val)

        self._result_verdict = _label("", QFont("Segoe UI", 11, QFont.Weight.Bold), NEON_GREEN)
        self._result_verdict.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self._result_verdict, len(labels), 0, 1, 2)
        return card

    def _build_log_panel(self) -> QFrame:
        card = _card()
        vl = QVBoxLayout(card)
        vl.setContentsMargins(0, 4, 0, 0)
        vl.setSpacing(4)

        self._log_table = QTableWidget()
        self._log_table.setColumnCount(6)
        self._log_table.setHorizontalHeaderLabels(
            ["Timestamp", "Len", "Attack", "Attempts", "Time(s)", "Result"])
        self._log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._log_table.verticalHeader().setVisible(False)
        self._log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._log_table.setAlternatingRowColors(True)
        self._log_table.setFont(FONT_MONO_SM)
        self._log_table.setStyleSheet(f"""
            QTableWidget {{
                background: #060C12;
                color: {TEXT_PRIMARY};
                border: none;
                gridline-color: {BORDER_COLOR};
            }}
            QHeaderView::section {{
                background: {BG_PANEL};
                color: {NEON_BLUE};
                border: 1px solid {BORDER_COLOR};
                padding: 3px;
                font-size: 8pt;
            }}
            QTableWidget::item:alternate {{ background: #0D1520; }}
            QTableWidget::item:selected {{ background: #1A3050; }}
        """)
        vl.addWidget(self._log_table)

        clear_btn = QPushButton("Clear Log")
        clear_btn.setFont(FONT_MONO_SM)
        clear_btn.setStyleSheet(self._btn_style(NEON_RED))
        clear_btn.setFixedHeight(24)
        clear_btn.clicked.connect(self._clear_log)
        vl.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        return card

    # ── Style helpers ─────────────────────────────────────────────────────
    def _btn_style(self, color: str, large=False) -> str:
        pad = "8px 14px" if large else "4px 10px"
        return f"""
            QPushButton {{
                background: transparent;
                color: {color};
                border: 1px solid {color};
                border-radius: 4px;
                padding: {pad};
            }}
            QPushButton:hover {{ background: {color}22; }}
            QPushButton:pressed {{ background: {color}44; }}
            QPushButton:disabled {{ color: #334455; border-color: #223344; }}
        """

    def _progress_style(self, color: str) -> str:
        return f"""
            QProgressBar {{
                background: #0A0F16;
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}88, stop:1 {color});
                border-radius: 3px;
            }}
        """

    # ── Logic ─────────────────────────────────────────────────────────────
    def _on_pw_changed(self, text):
        if not text:
            self._strength_label.setText("—")
            self._strength_label.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent; border:none;")
            self._strength_bar.setValue(0)
            self._crack_time_label.setText("Estimated Crack Time: —")
            return
        self._do_analyze()

    def _toggle_echo(self, checked):
        if checked:
            self._pw_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self._show_btn.setText("Hide")
        else:
            self._pw_input.setEchoMode(QLineEdit.EchoMode.Password)
            self._show_btn.setText("Show")

    def _set_demo(self, pw: str):
        self._pw_input.setText(pw)
        self._pw_input.setEchoMode(QLineEdit.EchoMode.Normal)
        self._show_btn.setChecked(True)
        self._show_btn.setText("Hide")
        self._do_analyze()

    def _do_analyze(self):
        pw = self._pw_input.text()
        if not pw:
            return
        result = analyze_password(pw)
        self._strength_label.setText(result["strength"])
        self._strength_label.setStyleSheet(
            f"color:{result['color']}; font-size:20px; font-weight:bold; background:transparent; border:none;")
        self._strength_bar.setStyleSheet(self._progress_style(result["color"]))
        self._strength_bar.setValue(result["strength_percent"])
        self._crack_time_label.setText(f"Est. Crack Time: {result['crack_time_str']}")

        # Update factor dots
        checks = {
            "length":    result["length"] >= 8,
            "has_upper": result["has_upper"],
            "has_lower": result["has_lower"],
            "has_digit": result["has_digit"],
            "has_symbol": result["has_symbol"],
            "no_common": not result["has_common"],
        }
        for key, (dot, lbl) in self._factor_labels.items():
            ok = checks[key]
            color = NEON_GREEN if ok else NEON_RED
            dot.setStyleSheet(f"color:{color}; background:transparent; border:none;")
            lbl.setStyleSheet(f"color:{color}; background:transparent; border:none;")

    def _set_attack_buttons_enabled(self, enabled: bool):
        for btn in [self._bf_btn, self._dict_btn, self._hybrid_btn]:
            btn.setEnabled(enabled)
        self._stop_btn.setEnabled(not enabled)

    def _start_attack(self, attack_type: str):
        pw = self._pw_input.text()
        if not pw:
            self._terminal_write("[ERROR] Please enter a password first.", NEON_RED)
            return

        # Stop any running attack
        self._stop_attack()
        self._current_run_id += 1
        run_id = self._current_run_id

        self._active_attack = attack_type
        self._last_terminal_attempts = 0
        self._set_attack_buttons_enabled(False)
        self._attack_progress_bar.setValue(0)
        self._chart.reset()
        self._reset_stats()

        names = {"brute_force": "BRUTE FORCE", "dictionary": "DICTIONARY", "hybrid": "HYBRID"}
        name = names[attack_type]

        self._terminal.clear()
        self._terminal_write(f"[ATTACK ENGINE INITIALIZED]", NEON_BLUE)
        self._terminal_write(f"[TARGET PASSWORD LENGTH: {len(pw)}]", NEON_BLUE)

        if attack_type == "brute_force":
            self._terminal_write("Starting brute force engine...", NEON_GREEN)
            self._terminal_write(f"Charset: a-z + 0-9 | Max length: {min(len(pw), 6)}", TEXT_MUTED)
            engine = BruteForceEngine(
                target=pw,
                progress_callback=lambda **kw: self._bridge.progress.emit({**kw, "type": "brute_force", "run_id": run_id}),
                done_callback=lambda **kw: self._bridge.done.emit({**kw, "type": "brute_force", "run_id": run_id}),
                max_length=min(len(pw), 6),
            )
        elif attack_type == "dictionary":
            self._terminal_write("Loading dictionary wordlist...", NEON_GREEN)
            self._terminal_write("Starting dictionary attack engine...", NEON_GREEN)
            engine = DictionaryAttackEngine(
                target=pw,
                progress_callback=lambda **kw: self._bridge.progress.emit({**kw, "type": "dictionary", "run_id": run_id}),
                done_callback=lambda **kw: self._bridge.done.emit({**kw, "type": "dictionary", "run_id": run_id}),
            )
        else:
            self._terminal_write("Loading dictionary + hybrid mutations...", NEON_GREEN)
            self._terminal_write("Starting hybrid attack engine...", NEON_GREEN)
            engine = HybridAttackEngine(
                target=pw,
                progress_callback=lambda **kw: self._bridge.progress.emit({**kw, "type": "hybrid", "run_id": run_id}),
                done_callback=lambda **kw: self._bridge.done.emit({**kw, "type": "hybrid", "run_id": run_id}),
            )

        self._engine = engine
        engine.start()
        self._status_bar.setText(f"⚡ {name} attack running...")

    def _stop_attack(self):
        if self._engine:
            # Invalidate queued cross-thread updates from the previous run immediately.
            self._current_run_id += 1
            self._engine.stop()
            self._engine = None
        self._set_attack_buttons_enabled(True)
        self._active_attack = None
        self._status_bar.setText("Attack stopped.")

    def _terminal_write(self, text: str, color: str = NEON_GREEN):
        self._terminal.append(f'<span style="color:{color}; font-family:Consolas;">{text}</span>')
        sb = self._terminal.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _reset_stats(self):
        self._stat_attempts.setText("0")
        self._stat_speed.setText("0")
        self._stat_elapsed.setText("0.00")
        self._stat_progress_n.setText("0%")
        for val in self._result_vals:
            val.setText("—")
        self._result_verdict.setText("")

    def _on_progress(self, data: dict):
        if data.get("run_id") != self._current_run_id:
            return

        attempts = data.get("attempts", 0)
        elapsed  = data.get("elapsed", 0)
        speed    = data.get("speed", 0)
        progress = data.get("progress", 0)
        current  = data.get("current", "")

        self._stat_attempts.setText(f"{attempts:,}")
        self._stat_speed.setText(f"{speed:,.0f}")
        self._stat_elapsed.setText(f"{elapsed:.2f}")
        self._stat_progress_n.setText(f"{progress}%")
        self._attack_progress_bar.setValue(progress)

        attack_type = data.get("type", "")
        if attack_type == "brute_force":
            if attempts - self._last_terminal_attempts >= 5000:
                self._terminal_write(f"Trying: {current}", NEON_GREEN)
                self._last_terminal_attempts = attempts
        elif attack_type == "dictionary":
            self._terminal_write(f"Testing: {current}", NEON_ORANGE)
        else:
            self._terminal_write(f"Hybrid testing: {current}", NEON_YELLOW)

        self._chart.update_data(elapsed, attempts)

    def _on_done(self, data: dict):
        if data.get("run_id") != self._current_run_id:
            return

        found     = data.get("found", False)
        stopped   = data.get("stopped", False)
        attempts  = data.get("attempts", 0)
        elapsed   = data.get("elapsed", 0.0)
        speed     = data.get("speed", 0)
        attack_type = data.get("type", "brute_force")

        self._set_attack_buttons_enabled(True)
        if found:
            self._attack_progress_bar.setValue(100)
        self._engine = None

        pw = self._pw_input.text()
        analysis = analyze_password(pw)

        names = {"brute_force": "Brute Force", "dictionary": "Dictionary", "hybrid": "Hybrid"}
        if stopped:
            result_str = "STOPPED"
        else:
            result_str = "CRACKED" if found else "NOT FOUND"

        # Update result panel
        self._result_vals[0].setText(names.get(attack_type, attack_type))
        display_pw = pw if len(pw) <= 20 else pw[:17] + "..."
        self._result_vals[1].setText(display_pw)
        self._result_vals[2].setText(f"{attempts:,}")
        self._result_vals[3].setText(f"{elapsed:.4f}s")
        self._result_vals[4].setText(analysis["strength"])

        if found:
            verdict_color = NEON_RED
            verdict_text  = f"🔓  PASSWORD CRACKED via {names.get(attack_type).upper()}"
            self._terminal_write(f"\n[!] PASSWORD CRACKED: {pw}", NEON_RED)
            self._terminal_write(f"    Attempts: {attempts:,}", NEON_RED)
            self._terminal_write(f"    Time: {elapsed:.4f}s", NEON_RED)
        elif stopped:
            verdict_color = NEON_ORANGE
            verdict_text  = "⏹  Attack stopped by user"
            self._terminal_write("\n[~] Attack manually stopped.", NEON_ORANGE)
            self._terminal_write(f"    Attempts before stop: {attempts:,}", NEON_ORANGE)
            self._terminal_write(f"    Time elapsed: {elapsed:.4f}s", NEON_ORANGE)
        else:
            verdict_color = NEON_GREEN
            verdict_text  = f"🔒  Password not found in this simulation"
            self._terminal_write(f"\n[✓] Password not found in simulation range.", NEON_GREEN)
            self._terminal_write(f"    This indicates a stronger password.", NEON_GREEN)

        self._result_verdict.setText(verdict_text)
        self._result_verdict.setStyleSheet(
            f"color:{verdict_color}; font-size:11px; font-weight:bold; background:transparent; border:none;")

        self.logger.log(
            password_length=len(pw),
            attack_type=attack_type,
            attempts=attempts,
            time_taken=elapsed,
            result=result_str,
        )
        self._load_log_table()
        self._status_bar.setText(
            f"Attack complete. Result: {result_str} | {attempts:,} attempts in {elapsed:.2f}s")

    def _load_log_table(self):
        rows = self.logger.get_recent(100)
        self._log_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            # id, timestamp, length, type, attempts, time, result
            vals = [row[1], str(row[2]), row[3], f"{row[4]:,}", f"{row[5]:.3f}", row[6]]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if val == "CRACKED":
                    item.setForeground(QColor(NEON_RED))
                elif val == "NOT FOUND":
                    item.setForeground(QColor(NEON_GREEN))
                elif val == "STOPPED":
                    item.setForeground(QColor(NEON_ORANGE))
                self._log_table.setItem(r, c, item)

    def _clear_log(self):
        self.logger.clear()
        self._load_log_table()
        self._terminal_write("[LOG] Attack log database cleared.", TEXT_MUTED)
