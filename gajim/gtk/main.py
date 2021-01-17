
from gi.repository import Gtk

from gajim.common import app
from gajim.gui.util import get_builder
from gajim.gui.chat_list_stack import ChatListStack
from gajim.gui.chat_stack import ChatStack


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self):
        Gtk.ApplicationWindow.__init__(self)
        self.set_application(app.app)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_title('Gajim')

        # Compatibility with ChatControl
        self.window = self
        app.window = self

        self._active_workspace = None

        self._startup_finished = False

        self._ui = get_builder('main.ui')

        self.add(self._ui.main_grid)

        self._chat_stack = ChatStack()
        self._chat_list_stack = ChatListStack(self._ui, self._chat_stack)

        self._ui.left_grid.add(self._chat_list_stack)
        self._ui.right_grid.add(self._chat_stack)
        self._ui.connect_signals(self)

        self.show_all()

        self._load_chats()

    def get_widget(self, name):
        return getattr(self._ui, name)

    def redraw_tab(self, *args):
        pass

    def remove_tab(self, *args):
        pass

    def show_title(self, *args):
        pass

    def get_active_jid(self, *args):
        pass

    def get_active_workspace(self):
        # TODO
        return app.settings.get_workspaces()[0]

    def add_chat(self, account, jid):
        workspace_id = self.get_active_workspace()
        self.add_chat_for_workspace(workspace_id, account, jid)

    def add_chat_for_workspace(self, workspace_id, account, jid):
        self._chat_stack.add_chat(account, jid)
        self._chat_list_stack.add_chat(workspace_id, account, jid)

        if self._startup_finished:
            self._chat_list_stack.select_chat(workspace_id, account, jid)
            self._chat_list_stack.store_open_chats(workspace_id)

    def get_control(self, account, jid):
        return self._chat_stack.get_control(account, jid)

    def _load_chats(self):
        for workspace_id in app.settings.get_workspaces():
            open_chats = app.settings.get_workspace_setting(workspace_id,
                                                            'open_chats')
            for account, jid in open_chats:
                self.add_chat_for_workspace(workspace_id, account, jid)

        self._startup_finished = True
