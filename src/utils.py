#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Deepin, Inc.
#               2011 Wang Yong
#
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk
import pygtk
import gobject

pygtk.require('2.0')

def isCollideRect((cx, cy), (x, y, w, h)):
    '''Whether coordinate collide with rectangle.'''
    return (x <= cx <= x + w and y <= cy <= y + h)

def isInRect((cx, cy), (x, y, w, h)):
    '''Whether coordinate in rectangle.'''
    return (x < cx < x + w and y < cy < y + h)

def setCursor(widget, cursorType):
    '''Set cursor.'''
    widget.window.set_cursor(gtk.gdk.Cursor(cursorType))
    
    return False

def getScreenSize():
    '''Get screen size.'''
    return gtk.gdk.get_default_root_window().get_size()

def isDoubleClick(event):
    '''Whether an event is double click?'''
    return event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS
