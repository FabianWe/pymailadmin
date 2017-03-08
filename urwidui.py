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
import datetime
import mailadmin
import urwidsql
import MySQLdb
import sys

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
    ('selected', 'white', 'dark blue'),
    ('status', 'light blue', 'brown'),
    ('errstatus', 'light red', 'brown')]
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

    def handle_input(self, key):
        if key == 'q':
            top.remove_active()

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

    def set_content(self):
        content = self.get_content()
        # get the dividers
        fst, last = self.listbox.body[0], self.listbox.body[-1]
        self.listbox.body.clear()
        self.listbox.body.append(fst)
        for e in content:
            self.listbox.body.append(e)
        self.listbox.body.append(last)

def exit_program(key):
    raise urwid.ExitMainLoop()

class ExitChoice(urwid.WidgetWrap):
    def __init__(self):
        super(ExitChoice, self).__init__(
            MenuButton('Exit', self.exit))

    def exit(self, button):
        exit_program(0)

class LicenseChoice(urwid.WidgetWrap):
    def __init__(self):
        super(LicenseChoice, self).__init__(MenuButton('License', self.license))

    def license(self, button):
        box = LicenseBox()
        top.open_box(box, width=75)

class LicenseBox(SubEntryBox):
    def __init__(self):
        super(LicenseBox, self).__init__('License', '\n (q) Close')

    def get_content(self):
        res = []
        for name in ['LICENSE', 'COPYING']:
            f = open(name, 'r')
            content = f.read()
            f.close()
            if res:
                res.append(urwid.Divider())
            res.append(urwid.AttrMap(urwid.Text(name), 'heading'))
            res.append(urwid.AttrMap(urwid.Text(content), 'selected'))
        return res

class DomainChoice(urwid.WidgetWrap):
    def __init__(self):
        super(DomainChoice, self).__init__(
            MenuButton('Virtual Domains', self.open_menu))

    def open_menu(self, button):
        box = DomainBox()
        top.open_box(box, 40)

class DomainBox(SubEntryBox):
    def __init__(self):
        super(DomainBox, self).__init__('Virtual Domains',
            '\n(a) add, (d) delete entry')

    def get_content(self):
        try:
            entries = list(urwidsql.get_domains(db))
        except MySQLdb.Error as e:
            set_err_status('Access error: ' + str(e))
            return []
        entries.sort()
        res = []
        for entry in entries:
            res.append(MenuButton(entry, lambda button: None))
        return res

    def handle_input(self, key):
        if key == 'a':
            box = AddDomainBox(self)
            top.open_box(box)
        elif key == 'd':
            if self.listbox.focus is not None:
                elem = self.listbox.focus
                if isinstance(elem, MenuButton):
                    box = DeleteDomainBox(self, elem.label)
                    top.open_box(box)
        else:
            super(DomainBox, self).handle_input(key)

class AddDomainBox(SubEntryBox):
    def __init__(self, parent):
        super(AddDomainBox, self).__init__('Add new virtual domain', '')
        self.parent = parent

    def get_content(self):
        self.edit_box = AddDomainEditBox()
        ok_button = urwid.Button('Add')
        urwid.connect_signal(ok_button, 'click', self.ok_action)
        cancel_button = urwid.Button('Cancel')
        urwid.connect_signal(cancel_button, 'click', lambda button: top.remove_active())
        return [urwid.AttrMap(urwid.Text('Domain'), 'heading'),
                urwid.AttrMap(self.edit_box, 'selected'),
                ok_button,
                cancel_button]

    def ok_action(self, button):
        domain = self.edit_box.get_text()[0]
        if not domain:
            set_err_status('Domain name is empty, error!')
            return
        try:
            urwidsql.add_domain(db, domain)
            set_info('Added domain "%s"' % domain)
        except MySQLdb.Error as e:
            set_err_status('Access error: ' + str(e))
        self.parent.set_content()
        top.remove_active()

class DeleteDomainBox(SubEntryBox):
    def __init__(self, parent, domain_name):
        super(DeleteDomainBox, self).__init__('Delete domain?', '\n ' + domain_name)
        self.parent = parent
        self.domain_name = domain_name

    def get_content(self):
        remove_button = urwid.Button('Remove')
        urwid.connect_signal(remove_button, 'click', self.remove)
        cancel_button = urwid.Button('Cancel')
        urwid.connect_signal(cancel_button, 'click', lambda button: top.remove_active())
        return [remove_button, cancel_button]

    def remove(self, button):
        try:
            urwidsql.remove_domain(db, self.domain_name)
            set_info('Removed domain "%s"' % self.domain_name)
        except (MySQLdb.Error, urwidsql.SQLExecuteException) as e:
            set_err_status('Unable to remove domain: ' + str(e))
        self.parent.set_content()
        top.remove_active()


class AddDomainEditBox(urwid.Edit):
    def __init__(self):
        super(AddDomainEditBox, self).__init__('')


class UsesrsChoice(urwid.WidgetWrap):
    def __init__(self):
        super(UsesrsChoice, self).__init__(
            MenuButton('Users', self.open_menu))

    def open_menu(self, button):
        box = UserBox()
        top.open_box(box, 40)

class UserBox(SubEntryBox):
    def __init__(self):
        super(UserBox, self).__init__('Users',
            '\n(a) add, (d) delete entry, (p) change password')

    def get_content(self):
        try:
            entries = list(urwidsql.get_users(db))
        except MySQLdb.Error as e:
            set_err_status('Access error: ' + str(e))
            return []
        entries.sort()
        res = []
        for entry in entries:
            res.append(MenuButton(entry, lambda button: None))
        return res


    def handle_input(self, key):
        if key == 'a':
            box = AddUserBox(self)
            top.open_box(box)
        elif key == 'd':
            if self.listbox.focus is not None:
                elem = self.listbox.focus
                if isinstance(elem, MenuButton):
                    box = DeleteUserBox(self, elem.label)
                    top.open_box(box)
        elif key == 'p':
            if self.listbox.focus is not None:
                elem = self.listbox.focus
                if isinstance(elem, MenuButton):
                    box = EditPasswordBox(self, elem.label)
                    top.open_box(box)
        else:
            super(UserBox, self).handle_input(key)

class AddUserBox(SubEntryBox):
    def __init__(self, parent, label='Add new user', help_text=''):
        super(AddUserBox, self).__init__(label, help_text)
        self.parent = parent
        self.pw_mask = '*'

    def get_content(self):
        self.edit_box = AddUserEditBox()
        self.pw_box = PasswordBox()
        self.pw_check = PasswordBox()
        pw_vis_button = urwid.Button('Show / Hide password')
        urwid.connect_signal(pw_vis_button, 'click', self.show_hide)
        random_pw_button = urwid.Button('Random password')
        urwid.connect_signal(random_pw_button, 'click', self.random_pw)
        ok_button = urwid.Button('Add')
        urwid.connect_signal(ok_button, 'click', self.ok_action)
        cancel_button = urwid.Button('Cancel')
        urwid.connect_signal(cancel_button, 'click', lambda button: top.remove_active())
        return [urwid.AttrMap(urwid.Text('Mail'), 'heading'),
                urwid.AttrMap(self.edit_box, 'selected'),
                urwid.AttrMap(urwid.Text('Password'), 'heading'),
                urwid.AttrMap(self.pw_box, 'selected'),
                urwid.AttrMap(urwid.Text('Repeat password'), 'heading'),
                urwid.AttrMap(self.pw_check, 'selected'),
                random_pw_button,
                pw_vis_button,
                ok_button,
                cancel_button]

    def ok_action(self, button):
        mail = self.edit_box.get_text()[0]
        if not mail:
            set_err_status('Mail is empty, error!')
            return
        if not mailadmin.valid_email(mail):
            set_err_status('%s is not a valid emai, error!' % mail)
            return
        password = self.pw_box.get_edit_text()
        if not password:
            set_err_status('Password is empty, error!')
            return
        check_pw = self.pw_check.get_edit_text()
        if password != check_pw:
            set_err_status('The passwords do not match.')
            return
        _hash = mailadmin.gen_hash(password)
        assert len(_hash) == 120
        try:
            urwidsql.add_user(db, mail, _hash)
            set_info('Added mailing user "%s"' % mail)
            top.remove_active()
        except (MySQLdb.Error, urwidsql.SQLExecuteException) as e:
            set_err_status('Error while adding user: ' + str(e))
        self.parent.set_content()

    def show_hide(self, button):
        new_mask = None
        if self.pw_mask is None:
            new_mask = '*'
        self.pw_box.set_mask(new_mask)
        self.pw_check.set_mask(new_mask)
        self.pw_mask = new_mask

    def show_pw(self):
        self.pw_mask = None
        self.pw_box.set_mask(None)
        self.pw_check.set_mask(None)

    def random_pw(self, button):
        pw = mailadmin.gen_pw()
        self.pw_box.set_edit_text(pw)
        self.pw_check.set_edit_text(pw)
        self.show_pw()

# TODO maybe not so nice to inherit from this class but it provides many things
# we need...
class EditPasswordBox(AddUserBox):
    def __init__(self, parent, mail):
        super(EditPasswordBox, self).__init__(parent, '\nChange password', '\n ' + mail)
        self.mail = mail

    def get_content(self):
        self.pw_box = PasswordBox()
        self.pw_check = PasswordBox()
        pw_vis_button = urwid.Button('Show / Hide password')
        urwid.connect_signal(pw_vis_button, 'click', self.show_hide)
        random_pw_button = urwid.Button('Random password')
        urwid.connect_signal(random_pw_button, 'click', self.random_pw)
        ok_button = urwid.Button('Edit')
        urwid.connect_signal(ok_button, 'click', self.ok_action)
        cancel_button = urwid.Button('Cancel')
        urwid.connect_signal(cancel_button, 'click', lambda button: top.remove_active())
        return [urwid.AttrMap(urwid.Text('Password'), 'heading'),
                urwid.AttrMap(self.pw_box, 'selected'),
                urwid.AttrMap(urwid.Text('Repeat password'), 'heading'),
                urwid.AttrMap(self.pw_check, 'selected'),
                random_pw_button,
                pw_vis_button,
                ok_button,
                cancel_button]

    def ok_action(self, button):
        password = self.pw_box.get_edit_text()
        if not password:
            set_err_status('Password is empty, error!')
            return
        check_pw = self.pw_check.get_edit_text()
        if password != check_pw:
            set_err_status('The passwords do not match.')
            return
        _hash = mailadmin.gen_hash(password)
        assert len(_hash) == 120
        try:
            urwidsql.change_pw(db, self.mail, _hash)
            set_info('Updated password for "%s"' % self.mail)
            top.remove_active()
        except (MySQLdb.Error, urwidsql.SQLExecuteException) as e:
            set_err_status('Error while changing password: ' + str(e))

class DeleteUserBox(SubEntryBox):
    def __init__(self, parent, mail):
        super(DeleteUserBox, self).__init__('Delete mail?', '\n ' + mail)
        self.parent = parent
        self.mail = mail

    def get_content(self):
        remove_button = urwid.Button('Remove')
        urwid.connect_signal(remove_button, 'click', self.remove)
        cancel_button = urwid.Button('Cancel')
        urwid.connect_signal(cancel_button, 'click', lambda button: top.remove_active())
        return [remove_button, cancel_button]

    def remove(self, button):
        try:
            urwidsql.remove_user(db, self.mail)
            set_info('Removed user "%s"' % self.mail)
        except (MySQLdb.Error, urwidsql.SQLExecuteException) as e:
            set_err_status('Unable to remove user: ' + str(e))
        self.parent.set_content()
        top.remove_active()

class AddUserEditBox(urwid.Edit):
    def __init__(self):
        super(AddUserEditBox, self).__init__('')

class PasswordBox(urwid.Edit):
    def __init__(self):
        super(PasswordBox, self).__init__('', mask='*')

class AliasesChoice(urwid.WidgetWrap):
    def __init__(self):
        super(AliasesChoice, self).__init__(
            MenuButton('Aliases', self.open_menu))

    def open_menu(self, button):
        box = AliasesBox()
        top.open_box(box, width=75)

def alias_str(source, dest):
    return '%s    ------>    %s' % (source, dest)

class AliasButton(MenuButton):
    def __init__(self, callback, source, dest):
        super(AliasButton, self).__init__(alias_str(source, dest), callback)
        self.source = source
        self.dest = dest

class AliasesBox(SubEntryBox):
    def __init__(self):
        super(AliasesBox, self).__init__('Aliases',
            '\n(a) add, (d) delete entry')

    def get_content(self):
        try:
            entries = list(urwidsql.get_aliases(db))
        except MySQLdb.Error as e:
            set_err_status('Access error: ' + str(e))
            return []
        entries.sort()
        res = []
        for source, dest in entries:
            res.append(AliasButton(lambda button: None, source, dest))
        return res
        return []


    def handle_input(self, key):
        if key == 'a':
            box = AddAliasBox(self)
            top.open_box(box)
        elif key == 'd':
            if self.listbox.focus is not None:
                elem = self.listbox.focus
                if isinstance(elem, AliasButton):
                    box = DeleteAliasBox(self, elem.source, elem.dest)
                    top.open_box(box)
        else:
            super(AliasesBox, self).handle_input(key)

class DeleteAliasBox(SubEntryBox):
    def __init__(self, parent, source, dest):
        super(DeleteAliasBox, self).__init__('Delete alias?',
            '\n ' + alias_str(source, dest))
        self.parent = parent
        self.source = source
        self.dest = dest

    def get_content(self):
        remove_button = urwid.Button('Remove')
        urwid.connect_signal(remove_button, 'click', self.remove)
        cancel_button = urwid.Button('Cancel')
        urwid.connect_signal(cancel_button, 'click', lambda button: top.remove_active())
        return [remove_button, cancel_button]

    def remove(self, button):
        try:
            urwidsql.remove_alias(db, self.source, self.dest)
            set_info('Removed alias "%s"' % alias_str(self.source, self.dest))
        except (MySQLdb.Error, urwidsql.SQLExecuteException) as e:
            set_err_status('Unable to remove alias: ' + str(e))
        self.parent.set_content()
        top.remove_active()

class AddAliasEditBox(urwid.Edit):
    def __init__(self):
        super(AddAliasEditBox, self).__init__('')

class AddAliasBox(SubEntryBox):
    def __init__(self, parent):
        super(AddAliasBox, self).__init__('Add new alias', '')
        self.parent = parent

    def get_content(self):
        self.source_box = AddAliasEditBox()
        self.dest_box = AddAliasEditBox()
        ok_button = urwid.Button('Add')
        urwid.connect_signal(ok_button, 'click', self.ok_action)
        cancel_button = urwid.Button('Cancel')
        urwid.connect_signal(cancel_button, 'click', lambda button: top.remove_active())
        return [urwid.AttrMap(urwid.Text('Source'), 'heading'),
                urwid.AttrMap(self.source_box, 'selected'),
                urwid.AttrMap(urwid.Text('Destination'), 'heading'),
                urwid.AttrMap(self.dest_box, 'selected'),
                ok_button,
                cancel_button]

    def ok_action(self, button):
        source = self.source_box.get_edit_text()
        if not source:
            set_err_status('Source mail is empty, error!')
            return
        dest = self.dest_box.get_edit_text()
        if not dest:
            set_err_status('Destination mail is empty, error!')
            return
        try:
            urwidsql.add_alias(db, source, dest)
            set_info('Added alias %s' % alias_str(source, dest))
        except (MySQLdb.Error, urwidsql.SQLExecuteException) as e:
            set_err_status('Access error: ' + str(e))
        self.parent.set_content()
        top.remove_active()

menu_top = SubMenu('Main Menu', [
    DomainChoice(),
    UsesrsChoice(),
    AliasesChoice(),
    LicenseChoice(),
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
        if not self.contents:
            exit_program(0)

def set_status(text):
    now = datetime.datetime.now()
    status.set_text(now.strftime('%Y-%m-%d %H:%M') + ' ' + text)

def set_info(text):
    status_bar.set_attr_map({None: 'status'})
    set_status(text)

def set_err_status(text):
    status_bar.set_attr_map({None: 'errstatus'})
    set_status(text)

def handle_input(key):
    assert len(top.contents) == len(top.callbacks)
    if top.contents:
        top.callbacks[top.focus_position](key)

top = HorizontalBoxes()
top.open_box(menu_top)
status = urwid.Text('')
status_bar = urwid.AttrMap(status, 'status')
set_info('Program started')
base_elem = urwid.Pile([top, ('flow', status_bar)])
try:
    db = mailadmin.open_from_settings()
except MySQLdb.Error as e:
    print('Unable to connect to database:', e)
    sys.exit(1)
urwid.MainLoop(urwid.Filler(base_elem,'top', 40), palette, unhandled_input=handle_input).run()
