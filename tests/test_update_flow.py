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
from app.components import update_manager

# Gia lap: co ban moi -> hien prompt -> auto Yes -> tai that 17MB
update_manager.is_newer = lambda current, latest: bool(latest)
shown = []
yes_holder = {}
orig_add = QMessageBox.addButton
orig_clicked = QMessageBox.clickedButton


def fake_add(self, btn):
    btn_obj = orig_add(self, btn)
    if btn == QMessageBox.Yes:
        yes_holder["yes"] = btn_obj
    return btn_obj


QMessageBox.addButton = fake_add
QMessageBox.clickedButton = lambda self: yes_holder.get("yes")
QMessageBox.exec = lambda self: 0


def fake_info(parent, title, text):
    shown.append(("INFO", title, str(text)))


def fake_warn(parent, title, text):
    shown.append(("WARN", title, str(text)))


QMessageBox.information = fake_info
QMessageBox.warning = fake_warn

from app.main_window import MainWindow

print("MW imported")
w = MainWindow()
w.show()
print("MW shown")

done = []
orig_run = update_manager.run_update


def traced_run(parent, on_done=None, force=True):
    print(">>> run_update duoc goi, bat dau tai...")
    return orig_run(
        parent,
        on_done=lambda ok, msg: (done.append((ok, msg)), on_done and on_done(ok, msg)),
        force=force,
    )


update_manager.run_update = traced_run


def poll():
    if done:
        print("Runner finished:", done)
        for s in shown:
            print("Dialog:", s)
        app.quit()
    else:
        QTimer.singleShot(500, poll)


QTimer.singleShot(300, w._check_engine_update)
QTimer.singleShot(2000, poll)
QTimer.singleShot(120000, app.quit)

app.exec()

from engine import yt_dlp_binary

print("Final version:", yt_dlp_binary.get_version())
ok = bool(done) and done[0][0] and shown and shown[0][0] == "INFO"
print("PASS" if ok else "FAIL")
