#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Deepin, Inc.
#               2011 Yong Wang
#
# Author:     Yong Wang <lazycat.manatee@gmail.com>
# Maintainer: Yong Wang <lazycat.manatee@gmail.com>
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
import gtk
import pygtk
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

def drawSimpleButton(widget, img):
    '''Draw simple button.'''
    simpleButtonSetBackground(
        widget,
        False, False,
        appTheme.getDynamicPixbuf(img)
        )

def simpleButtonSetBackground(widget, scaleX, scaleY, dPixbuf):
    '''Set event box's background.'''
    if scaleX:
        requestWidth = -1
    else:
        requestWidth = dPixbuf.getPixbuf().get_width()
        
    if scaleY:
        requestHeight = -1
    else:
        requestHeight = dPixbuf.getPixbuf().get_height()
    
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect("expose-event", lambda w, e: simpleButtonOnExpose(
            w, e,
            scaleX, scaleY,
            dPixbuf))
        
def simpleButtonOnExpose(widget, event, 
                         scaleX, scaleY,
                         dPixbuf):
    '''Expose function to replace event box's image.'''
    image = dPixbuf.getPixbuf()
    if scaleX:
        imageWidth = widget.allocation.width
    else:
        imageWidth = image.get_width()
        
    if scaleY:
        imageHeight = widget.allocation.height
    else:
        imageHeight = image.get_height()
    
    pixbuf = image.scale_simple(imageWidth, imageHeight, gtk.gdk.INTERP_BILINEAR)
    
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
