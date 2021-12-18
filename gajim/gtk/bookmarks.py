# This file is part of Gajim.
#
# Gajim is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; version 3 only.
#
# Gajim is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Gajim. If not, see <http://www.gnu.org/licenses/>.

import logging

from gi.repository import Gtk
from gi.repository import Gdk

from gajim.common import app
from gajim.common.i18n import _

from .builder import get_builder


log = logging.getLogger('gajim.gui.bookmarks')


class Bookmarks(Gtk.ApplicationWindow):
    def __init__(self, account):
        Gtk.ApplicationWindow.__init__(self)
        self.set_application(app.app)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_show_menubar(False)
        self.set_title(_('Bookmarks for %s') % app.get_account_label(account))
        self.set_default_size(700, 500)

        self.account = account

        self._ui = get_builder('bookmarks.ui')
        self.add(self._ui.bookmarks_grid)

        con = app.connections[account]
        for bookmark in con.get_module('Bookmarks').bookmarks:
            self._ui.bookmarks_store.append([str(bookmark.jid),
                                             bookmark.name,
                                             bookmark.nick,
                                             bookmark.password,
                                             bookmark.autojoin])

        self._ui.bookmarks_view.set_search_equal_func(self._search_func)

        self._ui.connect_signals(self)
        self.connect_after('key-press-event', self._on_key_press)

        self.show_all()

    def _on_key_press(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()

    @staticmethod
    def _search_func(model, _column, search_text, iter_):
        return search_text.lower() not in model[iter_][0].lower()
