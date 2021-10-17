# -*- coding: utf-8 -*-
"""
Created on Sun Oct 17 15:21:04 2021

@author: Balazs
"""

del app

class manageTransactionCategories(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(manageTransactionCategories, self).__init__(*args, **kw)

        # create a panel in the frame
        pnl = wx.Panel(self)

        # put some text with a larger bold font on it
        st = wx.StaticText(pnl, label="Transaction Category Manager")
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)

        # and create a sizer to manage the layout of child widgets
        #sizer = wx.BoxSizer(wx.VERTICAL)
        #sizer.Add(st, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
        #pnl.SetSizer(sizer)
    





class mainFrame(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(mainFrame, self).__init__(*args, **kw)

        # create a panel in the frame
        pnl = wx.Panel(self)

        # put some text with a larger bold font on it
        st = wx.StaticText(pnl, label="Placeholder content.")
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)

        # and create a sizer to manage the layout of child widgets
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(st, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
        pnl.SetSizer(sizer)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to SmartPurse!")


    def makeMenuBar(self):
        # Make a file menu with Hello and Exit items
        myPurseMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = myPurseMenu.Append(-1, "&Hello...\tCtrl-H",
                "Help string shown in status bar for this menu item")
        myPurseMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = myPurseMenu.Append(wx.ID_EXIT)
        
        # Resources Menu
        resourcesMenu = wx.Menu()
        
        transactionCategoryItem = resourcesMenu.Append(-1, "Transaction Categories",
                "Manage transaction categories")




        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(-1,"About")

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(myPurseMenu, "&My Purse")
        menuBar.Append(resourcesMenu, "&Resources")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnTransactionCategory,  transactionCategoryItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)


    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")
        
    def OnTransactionCategory(self, event):
        trcat_frame = manageTransactionCategories(None, title='Transaction Category Manager')
        trcat_frame.Show()
        #wx.MessageBox("Manage transaction categories")


    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK|wx.ICON_INFORMATION)


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = mainFrame(None, title='Smartpurse v0.0.1')
    frm.Show()
    app.MainLoop()