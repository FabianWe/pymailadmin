#! /usr/bin/env python3

# Copyright (c) 2017 Fabian Wenzelmann

# MIT License
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import urwid

# from the urwid tutorial: http://urwid.org/tutorial/
# seems to look nice
palette = [
    (None,  'light gray', 'black'),
    ('heading', 'black', 'light gray'),
    ('line', 'black', 'light gray'),
    ('options', 'dark gray', 'black'),
    ('focus heading', 'white', 'dark red'),
    ('focus line', 'black', 'dark red'),
    ('focus options', 'black', 'light gray'),
    ('selected', 'white', 'dark blue')]
focus_map = {
    'heading': 'focus heading',
    'options': 'focus options',
    'line': 'focus line'}


class MenuButton(urwid.Button):
    def __init__(self, caption, callback):
        super(MenuButton, self).__init__(caption)
        urwid.connect_signal(self, 'click', callback)
        self._w = urwid.AttrMap(urwid.SelectableIcon(
            ['  \N{BULLET} ', caption], 2), None, 'selected')


class SubMenu(urwid.WidgetWrap):
    def __init__(self, caption, choices):
        super(SubMenu, self).__init__(MenuButton(
            [caption, u"\N{HORIZONTAL ELLIPSIS}"], self.open_menu))
        line = urwid.Divider('\N{LOWER ONE QUARTER BLOCK}')
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
            urwid.AttrMap(urwid.Text([u"\n  ", caption]), 'heading'),
            urwid.AttrMap(line, 'line'),
            urwid.Divider()] + choices + [urwid.Divider()]))
        self.menu = urwid.AttrMap(listbox, 'options')

    def open_menu(self, button):
        top.open_box(self)

def exit_program(key):
    raise urwid.ExitMainLoop()

class ExitChoice(urwid.WidgetWrap):
    def __init__(self):
        super(ExitChoice, self).__init__(
            MenuButton('Exit', self.exit))

    def exit(self, button):
        exit_program(0)

class DomainChoice(urwid.WidgetWrap):
    def __init__(self):
        super(DomainChoice, self).__init__(
            MenuButton('Virtual Domains', self.open_menu))

    def open_menu(self, button):
        # TODO
        box = DomainBox()
        # exit_program(0)
        top.open_box(box, 100)

class SubEntryBox(urwid.WidgetWrap):
    def __init__(self, caption, help_text=''):
        # TODO what is this even for, well works
        super(SubEntryBox, self).__init__(MenuButton(
            ["XXX", u"\N{HORIZONTAL ELLIPSIS}"], self.open_menu))
        line = urwid.Divider('\N{LOWER ONE QUARTER BLOCK}')
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
            urwid.Divider()] + self.get_content() + [urwid.Divider()]))
        head = urwid.AttrMap(urwid.Text(['\n   ', caption]), 'heading')
        head_line = urwid.AttrMap(line, 'line')
        pile = urwid.Pile([('flow', head),
                           ('flow', head_line),
                           ('flow', urwid.Text(help_text)),
                           ('flow', urwid.Divider('\N{LOWER ONE QUARTER BLOCK}')),
                           listbox])
        self.menu = urwid.AttrMap(pile, 'options')
        self.listbox = listbox

    def open_menu(self):
        # TODO
        exit_program()

    def handle_input(self, key):
        if key == 'q':
            top.remove_active()

class DomainBox(SubEntryBox):
    def __init__(self):
        super(DomainBox, self).__init__('Virtual Domains',
            '\n(a) add, (d) delete entry')

    def get_content(self):
        res = []
        for i in range(100):
            res.append(MenuButton('a' if i % 2 == 0 else 'b', lambda button: None))
        return res

    def handle_input(self, key):
        if key == 'a':
            box = AddDomainBox()
            top.open_box(box)
        elif key == 'd':
            if self.listbox.focus is not None:
                elem = self.listbox.focus
                if type(elem) == MenuButton:
                    raise ValueError(self.listbox.focus.get_label())
        else:
            super(DomainBox, self).handle_input(key)

class AddDomainBox(SubEntryBox):
    def __init__(self):
        super(AddDomainBox, self).__init__('Add new virtual domain', '')

    def get_content(self):
        ok_button = urwid.Button('Add')
        urwid.connect_signal(ok_button, 'click', lambda x:42)
        cancel_button = urwid.Button('Cancel')
        urwid.connect_signal(cancel_button, 'click', lambda button: top.remove_active())
        return [urwid.AttrMap(urwid.Text('Domain'), 'heading'),
                urwid.AttrMap(AddDomainEditBox(), 'selected'),
                ok_button,
                cancel_button]

class AddDomainEditBox(urwid.Edit):
    def __init__(self):
        super(AddDomainEditBox, self).__init__('')


class UsesrsChoice(urwid.WidgetWrap):
    def __init__(self):
        super(UsesrsChoice, self).__init__(
            MenuButton('Users', self.open_menu))

    def open_menu(self, button):
        # TODO
        exit_program(0)


class AliasesChoice(urwid.WidgetWrap):
    def __init__(self):
        super(AliasesChoice, self).__init__(
            MenuButton('Aliases', self.open_menu))

    def open_menu(self, button):
        # TODO
        exit_program(0)

menu_top = SubMenu('Main Menu', [
    DomainChoice(),
    UsesrsChoice(),
    AliasesChoice(),
    ExitChoice(),
])

class HorizontalBoxes(urwid.Columns):
    def __init__(self):
        super(HorizontalBoxes, self).__init__([], dividechars=1)
        self.callbacks = []

    def open_box(self, widget, width=30):
        assert len(self.contents) == len(self.callbacks)
        box = widget.menu
        if self.contents:
            focus_pos = self.focus_position
            del self.contents[focus_pos + 1:]
            del self.callbacks[focus_pos + 1:]
        self.contents.append((urwid.AttrMap(box, 'options', focus_map),
            self.options('given', width)))
        box_callback = getattr(widget, 'handle_input', lambda key: None)
        self.callbacks.append(box_callback)
        self.focus_position = len(self.contents) - 1

    def remove_active(self):
        assert len(self.contents) == len(self.callbacks)
        if self.contents:
            focus_pos = self.focus_position
            del self.contents[focus_pos:]
            del self.callbacks[focus_pos:]


def handle_input(key):
    f = open('test.txt','w')
    print(top.contents[0], file=f)
    f.close()
    assert len(top.contents) == len(top.callbacks)
    if top.contents:
        top.callbacks[top.focus_position](key)

top = HorizontalBoxes()
top.open_box(menu_top)
urwid.MainLoop(urwid.Filler(top, 'top', 30), palette, unhandled_input=handle_input).run()
