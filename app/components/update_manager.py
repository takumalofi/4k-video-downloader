from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QMessageBox, QProgressDialog

from app import i18n
from engine import yt_dlp_binary


class UpdateChecker(QThread):
    checked = Signal(str, str)

    def run(self):
        if yt_dlp_binary.is_cancelled():
            return
        current = yt_dlp_binary.get_version() or ""
        if yt_dlp_binary.is_cancelled():
            return
        tag, _url, _size = yt_dlp_binary.fetch_latest_release()
        if yt_dlp_binary.is_cancelled():
            return
        self.checked.emit(current, tag or "")


class UpdateRunner(QThread):
    progressed = Signal(int, str)
    done = Signal(bool, str)

    def __init__(self, force=True, parent=None):
        super().__init__(parent)
        self.force = force

    def run(self):
        def cb(pct, status):
            self.progressed.emit(pct, status)

        ok, msg = yt_dlp_binary.download_update(cb, force=self.force)
        if yt_dlp_binary.is_cancelled():
            return
        self.done.emit(ok, msg)


def is_newer(current, latest):
    latest = (latest or "").strip().lstrip("v")
    return bool(latest) and latest != (current or "").strip()


def run_update(parent, on_done=None, force=True):
    dlg = QProgressDialog(i18n.tr("update_progress_label"), None, 0, 100, parent)
    dlg.setWindowTitle(i18n.tr("update_dialog_title"))
    dlg.setWindowModality(Qt.WindowModal)
    dlg.setMinimumWidth(380)
    dlg.setMinimumDuration(0)
    dlg.setValue(1)
    dlg.show()

    def on_progress(pct, status):
        dlg.setValue(pct)
        dlg.setLabelText(f"{i18n.tr('update_progress_label')} {pct}%\n{status}")

    def on_finished(ok, msg):
        dlg.reset()
        dlg.close()
        if ok:
            QMessageBox.information(parent, i18n.tr("update_done_title"), msg)
        else:
            QMessageBox.warning(parent, i18n.tr("update_failed_title"), msg)
        if on_done:
            on_done(ok, msg)

    runner = UpdateRunner(force=force)
    runner.progressed.connect(on_progress)
    runner.done.connect(on_finished)
    runner.finished.connect(runner.deleteLater)
    runner.start()
    return runner
