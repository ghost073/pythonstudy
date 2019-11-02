# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Nov  1 2019)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"期末成绩统计", pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText1 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"期末成绩统计", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		bSizer2.Add( self.m_staticText1, 0, wx.ALL, 5 )

		self.m_staticText2 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"1. 只支持xlsx后缀excel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )

		bSizer2.Add( self.m_staticText2, 0, wx.ALL, 5 )

		self.m_staticText3 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"2.  输入参考demoin.xlsx  输出参考 demoout.xlsx", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )

		bSizer2.Add( self.m_staticText3, 0, wx.ALL, 5 )


		self.m_panel2.SetSizer( bSizer2 )
		self.m_panel2.Layout()
		bSizer2.Fit( self.m_panel2 )
		bSizer1.Add( self.m_panel2, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticline3 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline3, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

		self.infilename = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
		bSizer3.Add( self.infilename, 1, wx.ALL|wx.EXPAND, 5 )

		self.infilebtn = wx.Button( self, wx.ID_ANY, u"选择", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.infilebtn, 0, wx.ALL, 5 )

		self.genexcel = wx.Button( self, wx.ID_ANY, u"生成", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.genexcel, 0, wx.ALL, 5 )


		bSizer1.Add( bSizer3, 0, wx.EXPAND, 5 )

		self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"输出文件地址", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )

		bSizer5.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.outfilename = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.outfilename, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( bSizer5, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_panel2.Bind( wx.EVT_ERASE_BACKGROUND, self.OnEraseBack )
		self.infilebtn.Bind( wx.EVT_BUTTON, self.openfile )
		self.genexcel.Bind( wx.EVT_BUTTON, self.toexcel )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def OnEraseBack( self, event ):
		event.Skip()

	def openfile( self, event ):
		event.Skip()

	def toexcel( self, event ):
		event.Skip()


