import os
import sys
import faulthandler

faulthandler.enable()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer

app = QApplication(sys.argv)
from app.theme import apply_theme

apply_theme(app)
from app import i18n
from app.components import update_manager
from app.components.settings_panel import SettingsPanel

shown = []


def fake_info(parent, title, text):
    shown.append(("INFO", str(title), str(text)))
    return QMessageBox.StandardButton.Ok


def fake_warn(parent, title, text):
    shown.append(("WARN", str(title), str(text)))
    return QMessageBox.StandardButton.Ok


QMessageBox.information = fake_info
QMessageBox.warning = fake_warn
QMessageBox.exec = lambda self: 0

print("Nhan nut:", i18n.tr("check_updates"))
print("VI:", i18n.VI["check_updates"], "|", i18n.VI["engine_up_to_date"])

s = SettingsPanel({"language": "en"})
assert s.update_btn.text() == "Check for updates...", s.update_btn.text()

# NHANH 1: da la ban moi nhat -> thong bao, KHONG tai
update_manager.is_newer_real = update_manager.is_newer
s._start_engine_update()


def after_check_1():
    info = [x for x in shown if x[0] == "INFO"]
    print("Ket qua nhanh 1 (da moi nhat):", info[-1] if info else "CHUA CO")
    runner = getattr(s, "_update_runner", None)
    print("  Khong tai (dung luong):", runner is None)
    assert runner is None, "Khong duoc tai khi da moi nhat!"

    # NHANH 2: gia lap co ban moi -> tai that + progress
    shown.clear()
    update_manager.is_newer = lambda current, latest: bool(latest)
    done = []
    orig_run = update_manager.run_update

    def traced(parent, on_done=None, force=True):
        return orig_run(
            parent,
            on_done=lambda ok, msg: (done.append((ok, msg)), on_done and on_done(ok, msg)),
            force=force,
        )

    update_manager.run_update = traced
    s._start_engine_update()

    def poll():
        if done:
            print("Ket qua nhanh 2 (co ban moi):", done, shown)
            ok = done[0][0] and any(x[0] == "INFO" for x in shown)
            print("PASS" if ok else "FAIL")
            app.quit()
        else:
            QTimer.singleShot(500, poll)

    QTimer.singleShot(500, poll)


QTimer.singleShot(8000, after_check_1)
QTimer.singleShot(180000, app.quit)
app.exec()
