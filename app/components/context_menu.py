import os
import webbrowser

from PySide6.QtGui import QGuiApplication, QAction, QKeySequence
from PySide6.QtWidgets import QMenu

from app import i18n
from app.components.download_item import open_item_folder


def build_item_menu(item, host=None, parent=None):
    menu = QMenu(parent)

    if item.state == "downloading":
        act_pause = menu.addAction(i18n.tr("pause"))
        act_pause.triggered.connect(lambda: item.pauseRequested.emit(item))
    elif item.state == "paused":
        act_resume = menu.addAction(i18n.tr("resume"))
        act_resume.triggered.connect(lambda: item.resumeRequested.emit(item))
    elif item.state == "queued":
        act_cancel_q = menu.addAction(i18n.tr("cancel"))
        act_cancel_q.triggered.connect(lambda: item.cancelRequested.emit(item))

    act_copy = menu.addAction(i18n.tr("copy_url"))
    act_copy.triggered.connect(
        lambda: QGuiApplication.clipboard().setText(item.url)
    )
    act_open = menu.addAction(i18n.tr("open_browser"))
    act_open.triggered.connect(lambda: webbrowser.open(item.url))
    act_folder = menu.addAction(i18n.tr("open_folder"))
    act_folder.triggered.connect(lambda: open_item_folder(item))

    if host is not None:
        menu.addSeparator()
        act_pause_all = menu.addAction(i18n.tr("pause_all"))
        act_pause_all.setEnabled(host.has_downloading())
        act_pause_all.triggered.connect(host.pause_all)
        act_resume_all = menu.addAction(i18n.tr("resume_all"))
        act_resume_all.setEnabled(host.has_paused())
        act_resume_all.triggered.connect(host.resume_all)

        menu.addSeparator()
        act_paste = menu.addAction(i18n.tr("paste_link"))
        act_paste.setShortcut(QKeySequence("Ctrl+V"))
        act_paste.triggered.connect(host.paste_link)

        menu.addSeparator()
        act_delete = menu.addAction(i18n.tr("delete_dots"))
        act_delete.setShortcut(QKeySequence("Del"))
        act_delete.triggered.connect(lambda: host.delete_item(item))
        act_delete_all = menu.addAction(i18n.tr("delete_all_menu"))
        act_delete_all.triggered.connect(host.delete_all)

    return menu


def show_item_menu(item, global_pos, host=None):
    menu = build_item_menu(item, host)
    menu.exec(global_pos)
