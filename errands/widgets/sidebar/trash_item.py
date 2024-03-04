# Copyright 2024 Vlad Krupinskii <mrvladus@yandex.ru>
# SPDX-License-Identifier: MIT

from __future__ import annotations
from typing import TYPE_CHECKING
from errands.lib.gsettings import GSettings

from errands.lib.logging import Log
from errands.widgets.task import Task
from errands.widgets.trash import Trash

if TYPE_CHECKING:
    from errands.widgets.window import Window

import os
from gi.repository import Adw, Gtk, Gio, GObject, Gdk, GLib  # type:ignore


@Gtk.Template(filename=f"{os.path.dirname(__file__)}/trash_item.ui")
class TrashItem(Adw.ActionRow):
    __gtype_name__ = "TrashItem"

    size_counter: Gtk.Label = Gtk.Template.Child()

    def __init__(self) -> None:
        super().__init__()
        self.window: Window = Adw.Application.get_default().get_active_window()
        self.name: str = "errands_trash_page"
        self.__build_ui()
        self.__create_actions()

    def __create_actions(self) -> None:
        self.group: Gio.SimpleActionGroup = Gio.SimpleActionGroup()
        self.insert_action_group(name="trash_item", group=self.group)

        def __create_action(name: str, callback: callable) -> None:
            action: Gio.SimpleAction = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            self.group.add_action(action)

        __create_action("clear", self.trash.on_trash_clear)
        __create_action("restore", self.trash.on_trash_restore)

    def __build_ui(self) -> None:
        # Create trash page
        self.trash = Trash()
        self.window.stack.add_titled(self.trash, "errands_trash_page", _("Trash"))

        # Customize internal AdwActionRow styles
        internal_box: Gtk.Box = self.get_child()
        internal_box.remove_css_class("header")
        internal_box.set_margin_start(6)
        internal_box.set_spacing(12)

    def update_ui(self) -> None:
        # Update trash
        self.trash.update_ui()

        # Get trash size
        size: int = len(self.trash.trash_items)

        # Update actions state
        self.group.lookup_action("clear").set_enabled(size > 0)
        self.group.lookup_action("restore").set_enabled(size > 0)

        # Update icon name
        self.set_icon_name(f"errands-trash{'-full' if size > 0 else ''}-symbolic")

        # Update subtitle
        self.size_counter.set_label("" if size == 0 else str(size))

    @Gtk.Template.Callback()
    def _on_row_activated(self, *args) -> None:
        Log.debug(f"Sidebar: Open Trash")

        self.window.stack.set_visible_child_name(self.name)
        self.window.split_view.set_show_content(True)
        GSettings.set("last-open-list", "s", self.name)

    @Gtk.Template.Callback()
    def _on_task_drop(self, _d, task: Task, _x, _y) -> None:
        task.delete()
