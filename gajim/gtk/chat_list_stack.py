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

from __future__ import annotations

from typing import Dict
from typing import Optional
from typing import cast

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Gio
from gi.repository import GLib

from nbxmpp import JID

from gajim.common import app
from gajim.common import events

from . import structs
from .chat_filter import ChatFilter
from .chat_list import ChatList
from .chat_list import ChatRow


HANDLED_EVENTS = (
    events.MessageReceived,
    events.MamMessageReceived,
    events.GcMessageReceived,
    events.MessageUpdated,
    events.PresenceReceived,
    events.MessageSent,
    events.JingleRequestReceived,
    events.FileRequestReceivedEvent
)


class ChatListStack(Gtk.Stack):

    __gsignals__ = {
        'unread-count-changed': (GObject.SignalFlags.RUN_LAST,
                                 None,
                                 (str, int)),
        'chat-selected': (GObject.SignalFlags.RUN_LAST,
                          None,
                          (str, str, object)),
        'chat-unselected': (GObject.SignalFlags.RUN_LAST,
                            None,
                            ()),
        'chat-removed': (GObject.SignalFlags.RUN_LAST,
                         None,
                         (str, object, str)),
    }

    def __init__(self,
                 chat_filter: ChatFilter,
                 search_entry: Gtk.SearchEntry
                 ) -> None:
        Gtk.Stack.__init__(self)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_vhomogeneous(False)

        self._chat_lists: Dict[str, ChatList] = {}

        self._last_visible_child_name: str = 'default'

        self.add_named(Gtk.Box(), 'default')

        self.connect('notify::visible-child-name', self._on_visible_child_name)
        search_entry.connect('search-changed', self._on_search_changed)
        chat_filter.connect('filter-changed', self._on_filter_changed)

        self._add_actions()
        self.show_all()

    def _add_actions(self) -> None:
        actions = [
            ('toggle-chat-pinned', 'as', self._toggle_chat_pinned),
            ('move-chat-to-workspace', 'a{sv}', self._move_chat_to_workspace),
            ('mark-as-read', 'as', self._mark_as_read),
        ]

        for action in actions:
            action_name, variant, func = action
            if variant is not None:
                variant = GLib.VariantType.new(variant)
            act = Gio.SimpleAction.new(action_name, variant)
            act.connect('activate', func)
            app.window.add_action(act)

    def _on_visible_child_name(self, _stack: Gtk.Stack, _param: str) -> None:
        if self._last_visible_child_name == self.get_visible_child_name():
            return

        if self._last_visible_child_name != 'default':
            chat_list = cast(
                ChatList,
                self.get_child_by_name(self._last_visible_child_name))
            chat_list.set_filter_text('')
        last_child = self.get_visible_child_name() or 'default'
        self._last_visible_child_name = last_child

    def get_chatlist(self, workspace_id: str) -> ChatList:
        return self._chat_lists[workspace_id]

    def get_selected_chat(self) -> Optional[ChatRow]:
        chat_list = self.get_current_chat_list()
        if chat_list is None:
            return None
        return chat_list.get_selected_chat()

    def get_current_chat_list(self) -> Optional[ChatList]:
        workspace_id = self.get_visible_child_name()
        if workspace_id == 'empty' or workspace_id is None:
            return None

        return self._chat_lists[workspace_id]

    def is_chat_active(self, account: str, jid: JID) -> bool:
        chat = self.get_selected_chat()
        if chat is None:
            return False
        if chat.account != account or chat.jid != jid:
            return False
        return chat.is_active

    def _on_filter_changed(self, _filter: ChatFilter, name: str) -> None:
        chat_list = cast(ChatList, self.get_visible_child())
        chat_list.set_filter(name)

    def _on_search_changed(self, search_entry: Gtk.SearchEntry) -> None:
        chat_list = cast(ChatList, self.get_visible_child())
        chat_list.set_filter_text(search_entry.get_text())

    def add_chat_list(self, workspace_id: str) -> ChatList:
        chat_list = ChatList(workspace_id)
        chat_list.connect('row-selected', self._on_row_selected)

        self._chat_lists[workspace_id] = chat_list
        self.add_named(chat_list, workspace_id)
        return chat_list

    def remove_chat_list(self, workspace_id: str) -> None:
        chat_list = self._chat_lists[workspace_id]
        self.remove(chat_list)
        for account, jid, _, _ in chat_list.get_open_chats():
            self.remove_chat(workspace_id, account, jid)

        self._chat_lists.pop(workspace_id)
        chat_list.destroy()

    def _on_row_selected(self,
                         _chat_list: ChatList,
                         row: Optional[ChatRow]
                         ) -> None:
        if row is None:
            self.emit('chat-unselected')
            return

        self.emit('chat-selected', row.workspace_id, row.account, row.jid)

    def show_chat_list(self, workspace_id: str) -> None:
        cur_workspace_id = self.get_visible_child_name()
        if cur_workspace_id == workspace_id:
            return

        if cur_workspace_id != 'default' and cur_workspace_id is not None:
            self._chat_lists[cur_workspace_id].unselect_all()

        self.set_visible_child_name(workspace_id)

    def add_chat(self, workspace_id: str, account: str, jid: JID, type_: str,
                 pinned: bool = False) -> None:
        chat_list = self._chat_lists.get(workspace_id)
        if chat_list is None:
            chat_list = self.add_chat_list(workspace_id)
        chat_list.add_chat(account, jid, type_, pinned)

    def select_chat(self, account: str, jid: JID) -> None:
        chat_list = self.find_chat(account, jid)
        if chat_list is None:
            return

        self.show_chat_list(chat_list.workspace_id)
        chat_list.select_chat(account, jid)

    def store_open_chats(self, workspace_id: str) -> None:
        chat_list = self._chat_lists[workspace_id]
        open_chats = chat_list.get_open_chats()
        app.settings.set_workspace_setting(
            workspace_id, 'open_chats', open_chats)

    def _toggle_chat_pinned(self,
                            _action: Gio.SimpleAction,
                            param: GLib.Variant
                            ) -> None:
        workspace_id, account, jid = param.unpack()
        jid = JID.from_string(jid)

        chat_list = self._chat_lists[workspace_id]
        chat_list.toggle_chat_pinned(account, jid)
        self.store_open_chats(workspace_id)

    @structs.actionmethod
    def _move_chat_to_workspace(self,
                                _action: Gio.SimpleAction,
                                params: structs.MoveChatToWorkspaceAP
                                ) -> None:

        current_chatlist = cast(ChatList, self.get_visible_child())
        type_ = current_chatlist.get_chat_type(params.account, params.jid)
        if type_ is None:
            return
        current_chatlist.remove_chat(params.account, params.jid)

        new_chatlist = self.get_chatlist(params.workspace_id)
        new_chatlist.add_chat(params.account, params.jid, type_)
        self.store_open_chats(current_chatlist.workspace_id)
        self.store_open_chats(params.workspace_id)

    def _mark_as_read(self,
                      _action: Gio.SimpleAction,
                      param: GLib.Variant
                      ) -> None:
        _workspace_id, account, jid = param.unpack()
        self.mark_as_read(account, JID.from_string(jid))

    def remove_chat(self, workspace_id: str, account: str, jid: JID) -> None:
        chat_list = self._chat_lists[workspace_id]
        type_ = chat_list.get_chat_type(account, jid)
        chat_list.remove_chat(account, jid, emit_unread=False)
        self.store_open_chats(workspace_id)
        self.emit('chat-removed', account, jid, type_)

    def remove_chats_for_account(self, account: str) -> None:
        for workspace_id, chat_list in self._chat_lists.items():
            chat_list.remove_chats_for_account(account)
            self.store_open_chats(workspace_id)

    def find_chat(self, account: str, jid: JID) -> Optional[ChatList]:
        for chat_list in self._chat_lists.values():
            if chat_list.contains_chat(account, jid):
                return chat_list
        return None

    def contains_chat(self, account: str, jid: JID,
                      workspace_id: Optional[str] = None) -> bool:
        if workspace_id is None:
            for chat_list in self._chat_lists.values():
                if chat_list.contains_chat(account, jid):
                    return True
            return False

        chat_list = self._chat_lists[workspace_id]
        return chat_list.contains_chat(account, jid)

    def get_total_unread_count(self) -> int:
        count = 0
        for chat_list in self._chat_lists.values():
            count += chat_list.get_unread_count()
        return count

    def get_chat_unread_count(self,
                              account: str,
                              jid: JID,
                              include_silent: bool = False
                              ) -> Optional[int]:
        for chat_list in self._chat_lists.values():
            count = chat_list.get_chat_unread_count(
                account, jid, include_silent)
            if count is not None:
                return count
        return None

    def set_chat_unread_count(self,
                              account: str,
                              jid: JID,
                              count: int
                              ) -> None:
        for chat_list in self._chat_lists.values():
            chat_list.set_chat_unread_count(account, jid, count)

    def mark_as_read(self, account: str, jid: JID) -> None:
        for chat_list in self._chat_lists.values():
            chat_list.mark_as_read(account, jid)

    def process_event(self, event: events.ApplicationEvent) -> None:
        if not isinstance(event, HANDLED_EVENTS):
            return

        jid = JID.from_string(event.jid)

        chat_list = self.find_chat(event.account, jid)
        if chat_list is None:
            return
        chat_list.process_event(event)
