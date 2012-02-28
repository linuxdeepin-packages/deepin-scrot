#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Deepin, Inc.
#               2011 Wang Yong
#
# Author:     hou shaohui <houshaohui@linuxdeepin.com>
#
# Maintainer: hou shaohui <houshaohui@linuxdeepin.com>
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

import pygtk
import gtk

pygtk.require('2.0')



class DeepinScrotSetup:
    ''' Deepin-Scrot setup Window '''

    def __init__(self):
        ''' Init. '''
        
        # Init widgets.
        self.window = self.initMainWindow()
        self.window.connect("destroy", lambda w: gtk.main_quit())
        # self.window.connect("size-allocate", lambda w, a: updateShape(w, a, 4))
        self.generalMainbox = gtk.VBox(False, 10)
        # setup 
        
        
        self.bodyAlign = gtk.Alignment()
        self.bodyAlign.set_padding(10, 20, 10, 10)
        
        imageSetupFrame = gtk.Frame("图片格式")

        imageSetupMainBox = gtk.VBox()
        imageQualityHbox = gtk.HBox(False,40)
        self.adj1 = gtk.Adjustment(0, 0, 110, 10, 10, 10)
        self.imageQualityLabel  = gtk.Label("质量:")
        self.imageQualityHscale = gtk.HScale(self.adj1)
        self.imageQualityHscale.set_size_request(190, -1)
        self.imageQualityHscale.set_value_pos(gtk.POS_RIGHT)
        self.imageQualityHscale.set_digits(0)
        self.imageQualityHscale.set_draw_value(True)
        self.imageQualityHscale.set_update_policy(gtk.UPDATE_CONTINUOUS)
        imageQualityHbox.pack_start(self.imageQualityLabel, False, False)
        imageQualityHbox.pack_start(self.imageQualityHscale, False, False)
        
        imageFormatHbox = gtk.HBox(False, 10)
        imageFormatLabel = gtk.Label("图片格式:")

        
        imageFormatList = gtk.OptionMenu()
        imageFormatList.set_size_request(180, -1)
        menu = gtk.Menu()
        pngItem = gtk.MenuItem("png - PNG 图像格式")
        jpegItem = gtk.MenuItem("jpeg - JPEG 图像格式")
        bmpItem = gtk.MenuItem("bmp - BMP 图像格式")
        menu.append(pngItem)
        menu.append(jpegItem)
        menu.append(bmpItem)
        imageFormatList.set_menu(menu)
        imageFormatHbox.pack_start(imageFormatLabel, False, False)
        imageFormatHbox.pack_start(imageFormatList, False, False)
        
        
        imageSetupMainBox.pack_start(imageQualityHbox)
        imageSetupMainBox.pack_start(imageFormatHbox)
        
        imageQualityAlign = gtk.Alignment()
        imageQualityAlign.set_padding(10, 10, 10, 10)
        imageQualityAlign.add(imageSetupMainBox)
        imageSetupFrame.add(imageQualityAlign)
        
        # save 
        saveProjectFrame = gtk.Frame("保存方案")
        saveProjectMainbox = gtk.VBox()
        self.tipsaveRadio = gtk.RadioButton(None, "提示保存")
        self.autosaveRadio = gtk.RadioButton(self.tipsaveRadio, "自动保存")
        saveFilenameHbox = gtk.HBox(False, 26)
        saveFilenameLabel = gtk.Label("文件名:")
        self.saveFilenameEntry = gtk.Entry()
        saveFilenameHbox.pack_start(saveFilenameLabel, False, False)
        saveFilenameHbox.pack_start(self.saveFilenameEntry)
        
        saveDirHbox = gtk.HBox(False, 10)
        saveDirLabel = gtk.Label("保存目录:")
        self.saveDirButton = gtk.FileChooserButton("dir")
        self.saveDirButton.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        saveDirHbox.pack_start(saveDirLabel, False, False)
        saveDirHbox.pack_start(self.saveDirButton)
        saveDirMainbox = gtk.VBox()
        
        saveDirMainbox.pack_start(saveFilenameHbox)
        saveDirMainbox.pack_start(saveDirHbox)
        saveDirAlign = gtk.Alignment()
        saveDirAlign.set_padding(0, 0, 20, 10)
        saveDirAlign.add(saveDirMainbox)
        
        saveProjectAlign = gtk.Alignment()
        saveProjectAlign.set_padding(10, 10, 10, 10)
        
        saveProjectFrame.add(saveProjectAlign)
        saveProjectAlign.add(saveProjectMainbox)
        saveProjectMainbox.pack_start(self.tipsaveRadio)
        saveProjectMainbox.pack_start(self.autosaveRadio)
        saveProjectMainbox.pack_start(saveDirAlign)
        
        # buttons
        controlBox = gtk.HBox(True, 5)
        controlAlign = gtk.Alignment()
        controlAlign.set(1.0, 0.0, 0.0, 0.0)
        controlAlign.add(controlBox)
        
        okButton = gtk.Button(None, gtk.STOCK_OK)
        cancelButton = gtk.Button(None, gtk.STOCK_CANCEL)
        applyButton = gtk.Button(None, gtk.STOCK_APPLY)
        controlBox.pack_start(okButton)
        controlBox.pack_start(cancelButton)
        controlBox.pack_start(applyButton)
        
        
        
        self.window.add(self.bodyAlign)
        self.bodyAlign.add(self.generalMainbox)
        self.generalMainbox.pack_start(imageSetupFrame)
        self.generalMainbox.pack_start(saveProjectFrame)
        self.generalMainbox.pack_start(controlAlign)
        

        

        
        self.window.show_all()
        gtk.main()
  
        
    def initMainWindow(self):
        '''init Main Window'''
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # window.set_decorated(False)
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_title("Deepin Scrot")
        window.set_default_size(300, 517)
        window.set_resizable(False)
        window.set_icon_from_file("../theme/logo/deepin-scrot.ico")
        
        return window
        
if __name__ == '__main__':
    DeepinScrotSetup()
