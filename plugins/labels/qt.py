from functools import partial

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QVBoxLayout)

from electronsv.plugins import hook
from electronsv.i18n import _
from electronsv_gui.qt import EnterButton
from electronsv_gui.qt.util import ThreadedButton, Buttons
from electronsv_gui.qt.util import WindowModalDialog, OkButton

from .labels import LabelsPlugin


class QLabelsSignalObject(QObject):
    labels_changed_signal = pyqtSignal(object)


class Plugin(LabelsPlugin):

    def __init__(self, *args):
        LabelsPlugin.__init__(self, *args)
        self.obj = QLabelsSignalObject()

    def requires_settings(self):
        return True

    def settings_widget(self, window):
        return EnterButton(_('Settings'),
                           partial(self.settings_dialog, window))

    def settings_dialog(self, window):
        wallet = window.parent().wallet
        d = WindowModalDialog(window, _("Label Settings"))
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Label sync options:"))
        upload = ThreadedButton("Force upload",
                                partial(self.push_thread, wallet),
                                partial(self.done_processing, d))
        download = ThreadedButton("Force download",
                                  partial(self.pull_thread, wallet, True),
                                  partial(self.done_processing, d))
        vbox = QVBoxLayout()
        vbox.addWidget(upload)
        vbox.addWidget(download)
        hbox.addLayout(vbox)
        vbox = QVBoxLayout(d)
        vbox.addLayout(hbox)
        vbox.addSpacing(20)
        vbox.addLayout(Buttons(OkButton(d)))
        return bool(d.exec_())

    def on_pulled(self, wallet):
        self.obj.labels_changed_signal.emit(wallet)

    def done_processing(self, dialog, result):
        dialog.show_message(_("Your labels have been synchronised."))

    @hook
    def on_new_window(self, window):
        self.obj.labels_changed_signal.connect(window.update_tabs)
        self.start_wallet(window.wallet)

    @hook
    def on_close_window(self, window):
        self.stop_wallet(window.wallet)
