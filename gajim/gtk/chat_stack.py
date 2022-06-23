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

from typing import Any

import logging

from gi.repository import Gtk
from nbxmpp.protocol import JID

from .control_stack import ControlStack
from .util import EventHelper

log = logging.getLogger('gajim.gui.chatstack')


class ChatStack(Gtk.Stack, EventHelper):
    def __init__(self):
        Gtk.Stack.__init__(self)
        EventHelper.__init__(self)

        self.set_vexpand(True)
        self.set_hexpand(True)

        self._control_stack = ControlStack()

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.add(self._control_stack)

        self.add_named(box, 'controls')

        self.show_all()

    def get_control_stack(self) -> ControlStack:
        return self._control_stack

    def show_chat(self, account: str, jid: JID) -> None:
        self._control_stack.show_chat(account, jid)

    def clear(self) -> None:
        self._control_stack.clear()

    def process_event(self, event: Any) -> None:
        self._control_stack.process_event(event)
