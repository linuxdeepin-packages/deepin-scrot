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

from utils import *
from math import *
from draw import *
from constant import *
import gtk
import pygtk
pygtk.require('2.0')

class DeepinScrot:
    '''Deepin scrot.'''
	
    def __init__(self):
        '''Init deepin scrot.'''
        # Init.
        self.action = ACTION_INIT
        self.width = self.height = 0
        self.x = self.y = self.rectWidth = self.rectHeight = 0
        self.frameColor = "#FFFF0"
        self.frameLineWidth = 2
        self.dragPosition = None
        self.dragStartX = self.dragStartY = self.dragStartOffsetX = self.drawStartOffsetY = 0
        self.dragPointRadius = 4
        self.dragFlag = False
        
        # Get desktop background.
        self.desktopBackground = self.getDesktopSnapshot() 
        
        # Init window.
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.fullscreen()
        self.window.set_keep_above(True)
        
        # Init event handle.
        self.window.add_events(gtk.gdk.KEY_PRESS_MASK)
        self.window.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self.window.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.window.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.window.connect("destroy", self.destroy)
        self.window.connect("expose-event", self.redraw)
        self.window.connect("button-press-event", self.buttonPress)
        self.window.connect("button-release-event", self.buttonRelease)
        self.window.connect("motion-notify-event", self.motionNotify)
        
        # Show.
        self.window.show_all()
        gtk.main()
        
    def getEventCoord(self, event):
        '''Get event coord.'''
        (rx, ry) = event.get_root_coords()
        return (int(rx), int(ry))
        
    def buttonPress(self, widget, event):
        '''Button press.'''
        self.dragFlag = True
        print "buttonPress: %s" % (str(event.get_root_coords()))
        
        if self.action == ACTION_INIT:
            (self.x, self.y) = self.getEventCoord(event)
        elif self.action == ACTION_SELECT:
            # Init drag position.
            self.dragPosition = self.getPosition(event)
            
            # Set cursor.
            self.setCursor(self.dragPosition)
            
            # Get drag coord and offset.
            (self.dragStartX, self.dragStartY) = self.getEventCoord(event)
            self.dragStartOffsetX = self.dragStartX - self.x
            self.dragStartOffsetY = self.dragStartY - self.y
    
    def motionNotify(self, widget, event):
        '''Motion notify.'''
        if self.dragFlag:
            print "motionNotify: %s" % (str(event.get_root_coords()))
            (ex, ey) = self.getEventCoord(event)
            
            if self.action == ACTION_INIT:
                (self.rectWidth, self.rectHeight) = (ex - self.x, ey - self.y)
                self.window.queue_draw()
            elif self.action == ACTION_SELECT:
                if self.dragPosition == DRAG_INSIDE:
                    self.x = min(max(ex - self.dragStartOffsetX, 0), self.width - self.rectWidth)
                    self.y = min(max(ey - self.dragStartOffsetY, 0), self.height - self.rectHeight)
                elif self.dragPosition == DRAG_TOP_SIDE:
                    self.dragFrameTop(ex, ey)
                elif self.dragPosition == DRAG_BOTTOM_SIDE:
                    self.dragFrameBottom(ex, ey)
                elif self.dragPosition == DRAG_LEFT_SIDE:
                    self.dragFrameLeft(ex, ey)
                elif self.dragPosition == DRAG_RIGHT_SIDE:
                    self.dragFrameRight(ex, ey)
                elif self.dragPosition == DRAG_TOP_LEFT_CORNER:
                    self.dragFrameTop(ex, ey)
                    self.dragFrameLeft(ex, ey)
                elif self.dragPosition == DRAG_TOP_RIGHT_CORNER:
                    self.dragFrameTop(ex, ey)
                    self.dragFrameRight(ex, ey)
                elif self.dragPosition == DRAG_BOTTOM_LEFT_CORNER:
                    self.dragFrameBottom(ex, ey)
                    self.dragFrameLeft(ex, ey)
                elif self.dragPosition == DRAG_BOTTOM_RIGHT_CORNER:
                    self.dragFrameBottom(ex, ey)
                    self.dragFrameRight(ex, ey)
                 
                self.window.queue_draw()
        else:
            if self.action == ACTION_SELECT:
                self.setCursor(self.getPosition(event))
        
    def buttonRelease(self, widget, event):
        '''Button release.'''
        self.dragFlag = False
        print "buttonRelease: %s" % (str(event.get_root_coords()))
    
        if self.action == ACTION_INIT:
            self.action = ACTION_SELECT
            (ex, ey) = self.getEventCoord(event)
            
            # Adjust value when button release.
            if ex > self.x:
                self.rectWidth = ex - self.x
            else:
                self.rectWidth = fabs(ex - self.x)
                self.x = ex
                
            if ey > self.y:
                self.rectHeight = ey - self.y
            else:
                self.rectHeight = fabs(ey - self.y)
                self.y = ey
                
            self.window.queue_draw()
            
    def redraw(self, widget, event):
        '''Redraw.'''
        # Init cairo.
        cr = widget.window.cairo_create()
        
        # Draw desktop background.
        self.drawDesktopBackground(cr)
        
        # Draw mask.
        self.drawMask(cr)
        
        if not (self.action == ACTION_INIT and self.dragFlag == False):
            # Draw frame.
            self.drawFrame(cr)
            
            # Draw drag point.
            self.drawDragPoint(cr)
            
        if widget.get_child() != None:
            widget.propagate_expose(widget.get_child(), event)
    
        return True
    
    def drawDesktopBackground(self, cr):
        '''Draw desktop.'''
        drawPixbuf(cr, self.desktopBackground)    
        
    def drawMask(self, cr):
        '''Draw mask.'''
        # Adjust value when create selection area.
        if self.rectWidth > 0:
            x = self.x
            rectWidth = self.rectWidth
        else:
            x = self.x + self.rectWidth
            rectWidth = fabs(self.rectWidth)

        if self.rectHeight > 0:
            y = self.y
            rectHeight = self.rectHeight
        else:
            y = self.y + self.rectHeight
            rectHeight = fabs(self.rectHeight)
        
        # Draw top.
        cr.set_source_rgba(0, 0, 0, 0.5)
        cr.rectangle(0, 0, self.width, y)
        cr.fill()

        # Draw bottom.
        cr.set_source_rgba(0, 0, 0, 0.5)
        cr.rectangle(0, y + rectHeight, self.width, self.height - y - rectHeight)
        cr.fill()

        # Draw left.
        cr.set_source_rgba(0, 0, 0, 0.5)
        cr.rectangle(0, y, x, rectHeight)
        cr.fill()

        # Draw right.
        cr.set_source_rgba(0, 0, 0, 0.5)
        cr.rectangle(x + rectWidth, y, self.width - x - rectWidth, rectHeight)
        cr.fill()
        
    def drawFrame(self, cr):
        '''Draw frame.'''
        cr.set_source_rgb(*colorHexToCairo(self.frameColor))
        cr.set_line_width(self.frameLineWidth)
        cr.rectangle(self.x, self.y, self.rectWidth, self.rectHeight)
        cr.stroke()
        
    def drawDragPoint(self, cr):
        '''Draw drag point.'''
        # Draw left top corner.
        cr.set_source_rgb(*colorHexToCairo(self.frameColor))
        cr.arc(self.x, self.y, self.dragPointRadius, 0, 2 * pi)
        cr.fill()
        
        # Draw right top corner.
        cr.set_source_rgb(*colorHexToCairo(self.frameColor))
        cr.arc(self.x + self.rectWidth, self.y, self.dragPointRadius, 0, 2 * pi)
        cr.fill()
        
        # Draw left bottom corner.
        cr.set_source_rgb(*colorHexToCairo(self.frameColor))
        cr.arc(self.x, self.y + self.rectHeight, self.dragPointRadius, 0, 2 * pi)
        cr.fill()
        
        # Draw right bottom corner.
        cr.set_source_rgb(*colorHexToCairo(self.frameColor))
        cr.arc(self.x + self.rectWidth, self.y + self.rectHeight, self.dragPointRadius, 0, 2 * pi)
        cr.fill()
        
        # Draw top side.
        cr.set_source_rgb(*colorHexToCairo(self.frameColor))
        cr.arc(self.x + self.rectWidth / 2, self.y, self.dragPointRadius, 0, 2 * pi)
        cr.fill()
        
        # Draw bottom side.
        cr.set_source_rgb(*colorHexToCairo(self.frameColor))
        cr.arc(self.x + self.rectWidth / 2, self.y + self.rectHeight, self.dragPointRadius, 0, 2 * pi)
        cr.fill()
        
        # Draw left side.
        cr.set_source_rgb(*colorHexToCairo(self.frameColor))
        cr.arc(self.x, self.y + self.rectHeight / 2, self.dragPointRadius, 0, 2 * pi)
        cr.fill()
        
        # Draw right side.
        cr.set_source_rgb(*colorHexToCairo(self.frameColor))
        cr.arc(self.x + self.rectWidth, self.y + self.rectHeight / 2, self.dragPointRadius, 0, 2 * pi)
        cr.fill()
        
    def getDesktopSnapshot(self):
        '''Get desktop snapshot.'''
        rootWindow = gtk.gdk.get_default_root_window() 
        [self.width, self.height] = rootWindow.get_size() 
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, self.width, self.height)
        return pixbuf.get_from_drawable(rootWindow, rootWindow.get_colormap(), 0, 0, 0, 0, self.width, self.height) 
        
    def destroy(self, widget, data=None):
        '''Destroy main window.'''
        gtk.main_quit()
        
    def getDragPointCoords(self):
        '''Get drag point coords.'''
        return (
            # Top left.
            (self.x - self.dragPointRadius, self.y - self.dragPointRadius), 
            # Top right.
            (self.x + self.rectWidth - self.dragPointRadius, self.y - self.dragPointRadius),
            # Bottom left.
            (self.x - self.dragPointRadius, self.y + self.rectHeight - self.dragPointRadius),
            # Bottom right.
            (self.x + self.rectWidth - self.dragPointRadius, self.y + self.rectHeight - self.dragPointRadius),
            # Top side.
            (self.x + self.rectWidth / 2 - self.dragPointRadius, self.y - self.dragPointRadius),
            # Bottom side.
            (self.x + self.rectWidth / 2 - self.dragPointRadius, self.y + self.rectHeight - self.dragPointRadius),
            # Left side.
            (self.x - self.dragPointRadius, self.y + self.rectHeight / 2 - self.dragPointRadius),
            # Right side.
            (self.x + self.rectWidth - self.dragPointRadius, self.y + self.rectHeight / 2 - self.dragPointRadius),
            )
        
    def getPosition(self, event):
        '''Get drag position.'''
        # Get event position.
        (ex, ey) = self.getEventCoord(event)
        
        # Get drag point coords.
        pWidth = pHeight = self.dragPointRadius * 2
        ((tlX, tlY), (trX, trY), (blX, blY), (brX, brY), (tX, tY), (bX, bY), (lX, lY), (rX, rY)) = self.getDragPointCoords()
        
        # Calcuate drag position.
        if isInRect((ex, ey), (self.x, self.y, self.rectWidth, self.rectHeight)):
            return DRAG_INSIDE
        elif isCollideRect((ex, ey), (tlX, tlY, pWidth, pHeight)):
            return DRAG_TOP_LEFT_CORNER
        elif isCollideRect((ex, ey), (trX, trY, pWidth, pHeight)):
            return DRAG_TOP_RIGHT_CORNER
        elif isCollideRect((ex, ey), (blX, blY, pWidth, pHeight)):
            return DRAG_BOTTOM_LEFT_CORNER
        elif isCollideRect((ex, ey), (brX, brY, pWidth, pHeight)):
            return DRAG_BOTTOM_RIGHT_CORNER
        elif isCollideRect((ex, ey), (tX, tY, pWidth, pHeight)) or isCollideRect((ex, ey), (self.x, self.y, self.rectWidth, self.frameLineWidth)):
            return DRAG_TOP_SIDE
        elif isCollideRect((ex, ey), (bX, bY, pWidth, pHeight)) or isCollideRect((ex, ey), (self.x, self.y + self.rectHeight, self.rectWidth, self.frameLineWidth)):
            return DRAG_BOTTOM_SIDE
        elif isCollideRect((ex, ey), (lX, lY, pWidth, pHeight)) or isCollideRect((ex, ey), (self.x, self.y, self.frameLineWidth, self.rectHeight)):
            return DRAG_LEFT_SIDE
        elif isCollideRect((ex, ey), (rX, rY, pWidth, pHeight)) or isCollideRect((ex, ey), (self.x + self.rectWidth, self.y, self.frameLineWidth, self.rectHeight)):
            return DRAG_RIGHT_SIDE
        else:
            return DRAG_OUTSIDE
        
    def setCursor(self, position):
        '''Set cursor.'''
        if position == DRAG_INSIDE:
            setCursor(self.window, gtk.gdk.FLEUR)
        elif position == DRAG_OUTSIDE:
            setCursor(self.window, gtk.gdk.TOP_LEFT_ARROW)
        elif position == DRAG_TOP_LEFT_CORNER:
            setCursor(self.window, gtk.gdk.TOP_LEFT_CORNER)
        elif position == DRAG_TOP_RIGHT_CORNER:
            setCursor(self.window, gtk.gdk.TOP_RIGHT_CORNER)
        elif position == DRAG_BOTTOM_LEFT_CORNER:
            setCursor(self.window, gtk.gdk.BOTTOM_LEFT_CORNER)
        elif position == DRAG_BOTTOM_RIGHT_CORNER:
            setCursor(self.window, gtk.gdk.BOTTOM_RIGHT_CORNER)
        elif position == DRAG_TOP_SIDE:
            setCursor(self.window, gtk.gdk.TOP_SIDE)
        elif position == DRAG_BOTTOM_SIDE:
            setCursor(self.window, gtk.gdk.BOTTOM_SIDE)
        elif position == DRAG_LEFT_SIDE:
            setCursor(self.window, gtk.gdk.LEFT_SIDE)
        elif position == DRAG_RIGHT_SIDE:
            setCursor(self.window, gtk.gdk.RIGHT_SIDE)
            
    def dragFrameTop(self, ex, ey):
        '''Drag frame top.'''
        maxY = self.y + self.rectHeight
        self.rectHeight = self.rectHeight - min(self.rectHeight, (ey - self.y))
        self.y = min(ey, maxY) 
    
    def dragFrameBottom(self, ex, ey):
        '''Drag frame bottom.'''
        self.rectHeight = max(0, ey - self.y)
    
    def dragFrameLeft(self, ex, ey):
        '''Drag frame left.'''
        maxX = self.x + self.rectWidth
        self.rectWidth = self.rectWidth - min(self.rectWidth, (ex - self.x))
        self.x = min(ex, maxX)
    
    def dragFrameRight(self, ex, ey):
        '''Drag frame right.'''
        self.rectWidth = max(0, ex - self.x)
    
if __name__ == "__main__":
    DeepinScrot()
