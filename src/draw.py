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

from math import *
from theme import *
from utils import *
import sys
from constant import DEFAULT_FONT
import cairo
import gtk
import pygtk
import glib

pygtk.require('2.0')

def drawPixbuf(cr, pixbuf, x=0, y=0):
    '''Draw pixbuf.'''
    if pixbuf != None:
        cr.set_source_pixbuf(pixbuf, x, y)
        cr.paint()
        
def colorHexToCairo(color):
    """ 
    Convert a html (hex) RGB value to cairo color. 
     
    @type color: html color string 
    @param color: The color to convert. 
    @return: A color in cairo format. 
    """ 
    if color[0] == '#': 
        color = color[1:] 
    (r, g, b) = (int(color[:2], 16), 
                    int(color[2:4], 16),  
                    int(color[4:], 16)) 
    return colorRGBToCairo((r, g, b)) 

def colorRGBToCairo(color): 
    """ 
    Convert a 8 bit RGB value to cairo color. 
     
    @type color: a triple of integers between 0 and 255 
    @param color: The color to convert. 
    @return: A color in cairo format. 
    """ 
    return (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0) 

def drawSimpleButton(widget, img, index, getIndex, helpText):
    '''Draw simple button.'''
    pixbuf = appTheme.getDynamicPixbuf(img + ".png").getPixbuf()
    widget.set_size_request(pixbuf.get_width(), pixbuf.get_height())
    
    # simpleButtonSetBackground(widget, img)
    widget.connect("expose-event", lambda w, e: simpleButtonOnExpose(w, e, img, index, getIndex))
    setHelpTooltip(widget, helpText)

def simpleButtonOnExpose(widget, event, img, index, getIndex):
    '''Expose function to replace event box's image.'''
    if widget.state == gtk.STATE_NORMAL:
        if getIndex() == index and index != 6:
            pixbuf = appTheme.getDynamicPixbuf(img + "_press.png").getPixbuf()
        else:
            pixbuf = appTheme.getDynamicPixbuf(img + ".png").getPixbuf()
    elif widget.state == gtk.STATE_PRELIGHT:
        pixbuf = appTheme.getDynamicPixbuf(img + "_hover.png").getPixbuf()
    elif widget.state == gtk.STATE_ACTIVE:
        pixbuf = appTheme.getDynamicPixbuf(img + "_press.png").getPixbuf()
    
    cr = widget.window.cairo_create()
    drawPixbuf(cr, pixbuf, 
               widget.allocation.x,
               widget.allocation.y)

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def drawEllipse(cr, ex, ey, ew, eh, color, size):
    '''Draw ellipse'''
    cr.save()
    cr.translate(ex, ey)
    cr.scale(ew / 2.0, eh / 2.0)
    cr.arc(0.0, 0.0, 1.0, 0.0, 2 * pi)
    cr.restore()
    cr.set_source_rgb(*colorHexToCairo(color))
    cr.set_line_width(size)
    cr.stroke()
    

def drawArrow(cr, (sx, sy), (ex, ey), color, size):
    '''Draw arrow.'''
    # Init.
    arrowSize = 10              # in pixel
    arrowAngle = 10             # in degree
    
    # Draw arrow body.
    lineWidth = fabs(sx - ex)
    lineHeight = fabs(sy - ey)
    lineSide = sqrt(pow(lineWidth, 2) + pow(lineHeight, 2))
    offsetSide = arrowSize * sin(arrowAngle)
    if lineSide == 0:
        offsetX = offsetY = 0
    else:
        offsetX = offsetSide / lineSide * lineWidth
        offsetY = offsetSide / lineSide * lineHeight
    
    if ex >= sx:
        offsetX = -offsetX
    if ey >= sy:
        offsetY = -offsetY
        
    cr.move_to(sx, sy)
    cr.line_to(ex - offsetX, ey - offsetY)
    cr.set_source_rgb(*colorHexToCairo(color))
    cr.set_line_width(size)
    cr.stroke()
    
    # Draw arrow head.
    angle = atan2(ey - sy, ex - sx) + pi
    x2 = ex - arrowSize * cos(angle - arrowAngle)
    y2 = ey - arrowSize * sin(angle - arrowAngle)
    x1 = ex - arrowSize * cos(angle + arrowAngle)
    y1 = ey - arrowSize * sin(angle + arrowAngle)
    
    cr.move_to(ex, ey)
    cr.line_to(x1, y1)
    cr.line_to(x2, y2)
    cr.fill()

def updateShape(widget, allocation, radius):
    '''Update shape.'''
    if allocation.width > 0 and allocation.height > 0:
        # Init.
        w, h = allocation.width, allocation.height
        bitmap = gtk.gdk.Pixmap(None, w, h, 1)
        cr = bitmap.cairo_create()
        
        # Clear the bitmap
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        
        # Draw our shape into the bitmap using cairo
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        drawRoundRectangle(cr, 0, 0, w, h, radius)
        cr.fill()
        
        widget.shape_combine_mask(bitmap, 0, 0)

def drawRoundRectangle(cr, x, y, width, height, r):
    '''Draw round rectangle.'''
    cr.move_to(x + r, y)
    cr.line_to(x + width - r, y)

    cr.move_to(x + width, y + r)
    cr.line_to(x + width, y + height - r)

    cr.move_to(x + width - r, y + height)
    cr.line_to(x + r, y + height)

    cr.move_to(x, y + height - r)
    cr.line_to(x, y + r)

    cr.arc(x + r, y + r, r, pi, 3 * pi / 2.0)
    cr.arc(x + width - r, y + r, r, 3 * pi / 2, 2 * pi)
    cr.arc(x + width - r, y + height - r, r, 0, pi / 2)
    cr.arc(x + r, y + height - r, r, pi / 2, pi)

def exposeBackground(widget, event, dPixbuf):
    '''Expose background.'''
    cr = widget.window.cairo_create()
    rect = widget.allocation

    drawPixbuf(cr, dPixbuf.getPixbuf().scale_simple(rect.width, rect.height, gtk.gdk.INTERP_BILINEAR), rect.x, rect.y)
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def drawRoundTextRectangle(cr, X, Y, Width, Height, Text, alpha=0.8):
    ''' draw Round Text Rectangle''' 
    x =  X + Width / 2 - 100
    y = Y + Height / 2 - 14
    width = 200
    height = 28
    r = height / 4.0
    cr.set_source_rgba(0.14, 0.13, 0.15, alpha)
    cr.move_to(x+r, y)
    cr.line_to(x+width-r,y)
        
    cr.move_to(x+width, y+r)
    cr.line_to(x+width, y+height - r)
        
    cr.move_to(x+width-r,y+height)
    cr.line_to(x+r, y+height)
        
    cr.move_to(x, y+height-r)
    cr.line_to(x, y+r)
    cr.arc(x+r, y+r, r, pi, 3*pi / 2)
    cr.arc(x+width-r,y+r,r, 3*pi / 2, 2*pi)
    cr.arc(x+width-r, y+height-r, r, 2*pi, pi / 2)
    cr.arc(x+r, y+height-r, r, pi / 2, pi)    
    cr.fill()
        
    drawFont(cr, Text, 14.0, "#FFFF00", x + width / 12.0, y + height / 1.5)

    

def drawFont(cr, content, fontSize, fontColor, x, y):
    '''Draw font.'''
    if DEFAULT_FONT in getFontFamilies():
        cr.select_font_face(DEFAULT_FONT,
                            cairo.FONT_SLANT_NORMAL, 
                            cairo.FONT_WEIGHT_NORMAL)
    cr.set_source_rgb(*colorHexToCairo(fontColor))
    cr.set_font_size(fontSize)
    cr.move_to(x, y)
    cr.show_text(content)


def setPixbufCursor(widget, cursorName):
    pixbuf = appTheme.getDynamicPixbuf(cursorName).getPixbuf()
    display = widget.window.get_display()
    widget.window.set_cursor(gtk.gdk.Cursor(display, pixbuf, 0, 0))


