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

from action import *
from utils import *
from math import *
from draw import *
from constant import *
from keymap import *
import sys
import gtk
import pygtk
pygtk.require('2.0')

class DeepinScrot:
    '''Deepin scrot.'''
	
    def __init__(self):
        '''Init deepin scrot.'''
        # Process arguments
        self.scrotMode = SCROT_MODE_NORMAL
        for arg in sys.argv[1:]:
            if arg == "--fullscreen":
                self.scrotMode = SCROT_MODE_FULLSCREEN
            elif arg == "--window":
                self.scrotMode = SCROT_MODE_WINDOW
            elif arg == "--normal":
                self.scrotMode = SCROT_MODE_NORMAL
            else:
                print "Ignore unknown option: ", arg

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
        self.showToolbarFlag = False
        self.toolbarOffsetX = 10
        self.toolbarOffsetY = 10
        self.toolbarHeight = 50
        self.controlPressed = False
        
        # Init action list.
        self.currentAction = None
        self.actionList = []
        
        # Get desktop background.
        self.desktopBackground = self.getDesktopSnapshot() 
        
        # Init window.
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.fullscreen()
        self.window.set_keep_above(True)
        
        # Init event handle.
        self.window.add_events(gtk.gdk.KEY_PRESS_MASK)
        self.window.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.window.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self.window.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.window.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.window.connect("destroy", self.destroy)
        self.window.connect("expose-event", self.redraw)
        self.window.connect("button-press-event", self.buttonPress)
        self.window.connect("button-release-event", self.buttonRelease)
        self.window.connect("motion-notify-event", self.motionNotify)
        self.window.connect("key-press-event", self.keyPress)
        
        # Init toolbar window.
        self.initToolbar()
        
        # Init text window.
        self.initTextWindow()

        # if SCROT_MODE_FULLSCREEN
        if self.scrotMode == SCROT_MODE_FULLSCREEN:
            rootWindow = gtk.gdk.get_default_root_window() 
            [self.rectWidth, self.rectHeight] = rootWindow.get_size() 
            self.action = ACTION_SELECT
            self.showToolbar()
        if self.scrotMode == SCROT_MODE_WINDOW:
            print "Window mode screenshot is not implemented yet"
        
        # Show.
        self.window.show_all()
        
        gtk.main()
        
    def initToolbar(self):
        '''Init toolbar.'''
        # Init window.
        # Use WINDOW_POPUP to ignore Window Manager's policy,
        # otherwise toolbar window won't move to place you want, such as, desktop environment have global menu.
        self.toolbarWindow = gtk.Window(gtk.WINDOW_POPUP)
        self.toolbarWindow.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.toolbarWindow.set_keep_above(True)
        self.toolbarWindow.set_decorated(False)
        self.toolbarWindow.set_resizable(False)
        self.toolbarWindow.set_transient_for(self.window)
        self.toolbarWindow.set_default_size(100, 24)
        
        # Add action button.
        self.toolBox = gtk.HBox()
        self.toolbarWindow.add(self.toolBox)
        
        self.actionRectangleButton = self.createActionButton("rectangle.png")
        self.actionRectangleButton.connect("button-press-event", lambda w, e: self.setActionType(ACTION_RECTANGLE))
        self.actionEllipseButton = self.createActionButton("ellipse.png")
        self.actionEllipseButton.connect("button-press-event", lambda w, e: self.setActionType(ACTION_ELLIPSE))
        self.actionArrowButton = self.createActionButton("arrow.png")
        self.actionArrowButton.connect("button-press-event", lambda w, e: self.setActionType(ACTION_ARROW))
        self.actionLineButton = self.createActionButton("line.png")
        self.actionLineButton.connect("button-press-event", lambda w, e: self.setActionType(ACTION_LINE))
        self.actionTextButton = self.createActionButton("text.png")
        self.actionTextButton.connect("button-press-event", lambda w, e: self.setActionType(ACTION_TEXT))
        self.actionUndoButton = self.createActionButton("undo.png")
        self.actionUndoButton.connect("button-press-event", lambda w, e: self.undo())
        self.actionSaveButton = self.createActionButton("save.png")
        self.actionSaveButton.connect("button-press-event", lambda w, e: self.saveSnapshotToFile())
        self.actionCancelButton = self.createActionButton("cancel.png")
        self.actionCancelButton.connect("button-press-event", lambda w, e: self.destroy(self.window))
        self.actionFinishButton = self.createActionButton("finish.png")
        self.actionFinishButton.connect("button-press-event", lambda w, e: self.saveSnapshot())
        
    def initTextWindow(self):
        '''Init text window.'''
        # Init window.
        # Use WINDOW_POPUP to ignore Window Manager's policy,
        # otherwise text window won't move to place you want, such as, desktop environment have global menu.
        self.textWindow = gtk.Window(gtk.WINDOW_POPUP)
        self.textWindow.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.textWindow.set_keep_above(True)
        self.textWindow.set_decorated(False)
        self.textWindow.set_resizable(False)
        self.textWindow.set_transient_for(self.window)
        
        self.textView = gtk.TextView()
        self.textView.set_wrap_mode(gtk.WRAP_WORD)
        self.textWindow.add(self.textView)
        self.textWindow.set_focus(self.textView)
        
    def showTextWindow(self, (ex, ey)):
        '''Show text window.'''
        offset = 5
        self.textWindow.show_all()
        self.textWindow.move(ex, ey)
        self.textWindow.set_geometry_hints(
            self.textView, -1, -1, 
            self.x + self.rectWidth - ex - offset,
            self.y + self.rectHeight - ey - offset,
            self.x + self.rectWidth - ex - offset,
            self.y + self.rectHeight - ey - offset,
            100, 10, 10, 10
            )
        self.textWindow.grab_focus()
        
    def hideTextWindow(self):
        '''Hide text window.'''
        self.textView.get_buffer().set_text("")
        self.textWindow.hide_all()
    
    def getInputText(self):
        '''Get input text.'''
        textBuffer = self.textView.get_buffer()
        return (textBuffer.get_text(textBuffer.get_start_iter(), textBuffer.get_end_iter())).rstrip(" ")
        
    def setActionType(self, aType):
        '''Set action. type'''
        self.action = aType    
        self.currentAction = None
        
    def createActionButton(self, iconName):
        '''Create action button.'''
        actionButton = gtk.EventBox()
        actionButton.set_visible_window(False)
        drawSimpleButton(actionButton, iconName)
        self.toolBox.pack_start(actionButton)
        
        return actionButton
        
    def showToolbar(self):
        '''Show toolbar.'''
        self.showToolbarFlag = True
        self.toolbarWindow.show_all()
        
    def hideToolbar(self):
        '''Hide toolbar.'''
        self.showToolbarFlag = False
        self.toolbarWindow.hide_all()
        
    def adjustToolbar(self):
        '''Adjust toolbar position.'''
        toolbarWidth = self.toolbarWindow.allocation.width
        toolbarHeight = self.toolbarWindow.allocation.height
        toolbarX = self.x + self.rectWidth - toolbarWidth - self.toolbarOffsetX
        if self.y + self.rectHeight + self.toolbarOffsetY + self.toolbarHeight < self.height:
            toolbarY = self.y + self.rectHeight + self.toolbarOffsetY
        elif self.y - self.toolbarOffsetY - self.toolbarHeight > 0:
            toolbarY = self.y - self.toolbarOffsetY - toolbarHeight
        else:
            toolbarY = self.y + self.toolbarOffsetY
            
        self.toolbarWindow.move(int(toolbarX), int(toolbarY))
        
    def getEventCoord(self, event):
        '''Get event coord.'''
        (rx, ry) = event.get_root_coords()
        return (int(rx), int(ry))
        
    def buttonPress(self, widget, event):
        '''Button press.'''
        self.dragFlag = True
        # print "*****"
        # print "buttonPress: %s" % (str(event.get_root_coords()))
        
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
        elif self.action == ACTION_RECTANGLE:
            # Just create new action when drag position at inside of select area.
            if self.getPosition(event) == DRAG_INSIDE:
                self.currentAction = RectangleAction(ACTION_RECTANGLE, 2, "#FF0000")
                self.currentAction.startDraw(self.getEventCoord(event))
        elif self.action == ACTION_ELLIPSE:
            # Just create new action when drag position at inside of select area.
            if self.getPosition(event) == DRAG_INSIDE:
                self.currentAction = EllipseAction(ACTION_ELLIPSE, 2, "#FF0000")
                self.currentAction.startDraw(self.getEventCoord(event))
        elif self.action == ACTION_ARROW:
            # Just create new action when drag position at inside of select area.
            if self.getPosition(event) == DRAG_INSIDE:
                self.currentAction = ArrowAction(ACTION_ARROW, 2, "#FF0000")
                self.currentAction.startDraw(self.getEventCoord(event))
        elif self.action == ACTION_LINE:
            # Just create new action when drag position at inside of select area.
            if self.getPosition(event) == DRAG_INSIDE:
                self.currentAction = LineAction(ACTION_LINE, 2, "#FF0000")
                self.currentAction.startDraw(self.getEventCoord(event))
        elif self.action == ACTION_TEXT:
            if self.textWindow.get_visible():
                content = self.getInputText()
                if content != "":
                    textAction = TextAction(ACTION_TEXT, 15, "#FF0000", content)
                    textAction.startDraw(self.textWindow.get_window().get_origin())
                    self.actionList.append(textAction) 
                    self.hideTextWindow()
                    
                    self.window.queue_draw()
                else:
                    self.hideTextWindow()
            else:
                self.showTextWindow(self.getEventCoord(event))
    
    def motionNotify(self, widget, event):
        '''Motion notify.'''
        if self.dragFlag:
            # print "motionNotify: %s" % (str(event.get_root_coords()))
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
            elif self.action == ACTION_RECTANGLE:
                self.currentAction.drawing((ex, ey), (self.x, self.y, self.rectWidth, self.rectHeight))
                
                self.window.queue_draw()
            elif self.action == ACTION_ELLIPSE:
                self.currentAction.drawing((ex, ey), (self.x, self.y, self.rectWidth, self.rectHeight))
                
                self.window.queue_draw()
            elif self.action == ACTION_ARROW:
                self.currentAction.drawing((ex, ey), (self.x, self.y, self.rectWidth, self.rectHeight))
                
                self.window.queue_draw()
            elif self.action == ACTION_LINE:
                self.currentAction.drawing((ex, ey), (self.x, self.y, self.rectWidth, self.rectHeight))
                
                self.window.queue_draw()
        else:
            if self.action == ACTION_SELECT:
                self.setCursor(self.getPosition(event))
        
    def buttonRelease(self, widget, event):
        '''Button release.'''
        self.dragFlag = False
        # print "buttonRelease: %s" % (str(event.get_root_coords()))
    
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
            
            self.showToolbar()
        elif self.action == ACTION_SELECT:
            pass
        elif self.action == ACTION_RECTANGLE:
            self.currentAction.endDraw(self.getEventCoord(event), (self.x, self.y, self.rectWidth, self.rectHeight))
            self.actionList.append(self.currentAction)
            self.currentAction = None
            
            self.window.queue_draw()
        elif self.action == ACTION_ELLIPSE:
            self.currentAction.endDraw(self.getEventCoord(event), (self.x, self.y, self.rectWidth, self.rectHeight))
            self.actionList.append(self.currentAction)
            self.currentAction = None
            
            self.window.queue_draw()
        elif self.action == ACTION_ARROW:
            self.currentAction.endDraw(self.getEventCoord(event), (self.x, self.y, self.rectWidth, self.rectHeight))
            self.actionList.append(self.currentAction)
            self.currentAction = None
            
            self.window.queue_draw()
        elif self.action == ACTION_LINE:
            self.currentAction.endDraw(self.getEventCoord(event), (self.x, self.y, self.rectWidth, self.rectHeight))
            self.actionList.append(self.currentAction)
            self.currentAction = None
            
            self.window.queue_draw()
            
    def keyPress(self, widget, event):
        '''process key press event'''
        keyEventName = getKeyEventName(event)
        if keyEventName == "q":
            self.destroy(self.window)
        elif keyEventName == "Escape":
            self.destroy(self.window)
        elif keyEventName == "Return":
            self.saveSnapshot()
        elif keyEventName == "s":
            self.saveSnapshotToFile()
        elif keyEventName == "C-z":
            self.undo()

    def saveSnapshotToFile(self):
        '''Save file to file.'''
        dialog = gtk.FileChooserDialog(
            "Save..",
            None,
            gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
             gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name("Images")
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        filter.add_mime_type("image/gif")
        filter.add_pattern("*.png")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.gif")
        filter.add_pattern("*.tif")
        filter.add_pattern("*.xpm")
        dialog.add_filter(filter)
        
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            self.saveSnapshot(filename)
            print "Save snapshot to %s" % (filename)
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()

    def saveSnapshot(self, filename=None):
        '''Save snapshot.'''
        # Init cairo.
        cr = self.window.window.cairo_create()
        
        # Draw desktop background.
        self.drawDesktopBackground(cr)
        
        # Draw action list.
        for action in self.actionList:
            action.expose(cr)
            
        # Get snapshot.
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, self.rectWidth, self.rectHeight)
        pixbuf.get_from_drawable(
            self.window.get_window(), self.window.get_window().get_colormap(),
            self.x, self.y,
            0, 0,
            self.rectWidth, self.rectHeight)
        
        # Save snapshot.
        if filename == None:
            # Save snapshot to clipboard if filename is None.
            clipboard = gtk.clipboard_get()
            clipboard.set_image(pixbuf)
            clipboard.store()
        else:
            # Otherwise save to local file.
            pixbuf.save(filename, "png")
        
        # Exit
        self.destroy(self.window)
        
    def redraw(self, widget, event):
        '''Redraw.'''
        # Init cairo.
        cr = widget.window.cairo_create()
        
        # Draw desktop background.
        self.drawDesktopBackground(cr)
        
        # Draw mask.
        self.drawMask(cr)
        
        # Draw toolbar.
        if self.showToolbarFlag:
            self.adjustToolbar()
            
        # Draw action list.
        for action in self.actionList:
            action.expose(cr)
        
        # Draw current action.
        if self.currentAction != None:
            self.currentAction.expose(cr)
            
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
        
    def undo(self):
        '''Undo'''
        if self.textWindow.get_visible():
            self.hideTextWindow()
        
        if len(self.actionList) == 0:
            if self.action == ACTION_SELECT:
                self.destroy(self.window)
        else:
            self.actionList.pop()
            
            if len(self.actionList) == 0:
                self.action = ACTION_SELECT
            
            self.window.queue_draw()
    
if __name__ == "__main__":
    DeepinScrot()
