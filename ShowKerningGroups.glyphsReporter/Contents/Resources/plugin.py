# encoding: utf-8

###########################################################################################################
#
#
#	Reporter Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################


import objc
from GlyphsApp.plugins import ReporterPlugin
from GlyphsApp import Glyphs
try:
	from GlyphsApp import GSLTR, GSRTL
except:
	from GlyphsApp import LTR as GSLTR, RTL as GSRTL  # type: ignore

from Foundation import NSAffineTransform
from AppKit import NSColor
import traceback


class ShowKerningGroups(ReporterPlugin):

	@objc.python_method
	def settings(self):

		# ###################################
		# ## Context Menu:
		self.nameLeft = 'Tab with LKG Members'
		self.nameRight = 'Tab with RKG Members'
		self.nameToggler = 'Toggle Fill/Stroke'
		self.toggle = 1

		try:
			self.generalContextMenus = [
				{"name": self.nameLeft, "action": self.LKGTab_},
				{"name": self.nameRight, "action": self.RKGTab_},
				{"name": self.nameToggler, "action": self.toggleFillStroke_},
			]
		except:
			print(traceback.format_exc())

		self.menuName = Glyphs.localize({'en': u'Kerning Groups'})

	@objc.python_method
	def background(self, layer):  # def foreground(self, layer):
		self.generateKGInfo(layer)

	@objc.python_method
	def openTab(self, side):
		thisLKG, thisRKG = self.KGGlyphsGen()
		if side == "left" and thisLKG:
			# tabString = "/" + "\n/".join([g.name for g in self.LKGGlyphs])
			tabString = "/" + "\n/".join([g.name for g in thisLKG])
		if side == "right" and thisRKG:
			# tabString = "/" + "\n/".join([g.name for g in self.RKGGlyphs])
			tabString = "/" + "\n/".join([g.name for g in thisRKG])
		if tabString:
			self.Font.newTab(tabString)

	def LKGTab_(self, sender):
		self.openTab("left")

	def RKGTab_(self, sender):
		self.openTab("right")

	def toggleFillStroke_(self, sender):
		try:
			self.toggle = self.toggle ^ 1
			self.RefreshView()
		except:
			print(traceback.format_exc())


	@objc.python_method
	def position(self, KGWidth):
		distance = 120
		self.leftPosition = -distance - self.margin, self.xHeight / 2
		self.rightPosition = self.thisWidth + self.margin + 10 + distance - KGWidth, self.xHeight / 2

	@objc.python_method
	def switcher(self, A, B, KGGlyphActiveMaster, direction):
		if direction == GSLTR:
			self.drawKerningGroupReference(KGGlyphActiveMaster, *A)
		if direction == GSRTL:
			self.drawKerningGroupReference(KGGlyphActiveMaster, *B)

	@objc.python_method
	def superimpose(self, KGGlyphs, group):

		try:
			thisAlpha = 0.8
			thisAlpha = .8 / len(KGGlyphs)
			if thisAlpha < self.floatLimit:
				thisAlpha = self.floatLimit
			NSColor.colorWithCalibratedRed_green_blue_alpha_(self.R, self.G, self.B, thisAlpha).set()
			for KGGlyph in KGGlyphs:
				self.KGGlyphActiveMaster = KGGlyph.layers[self.activeMasterId]
				KGWidth = self.KGGlyphActiveMaster.width * self.scaler
				self.position(KGWidth)

				if group == "left":
					self.switcher(self.leftPosition, self.rightPosition, self.KGGlyphActiveMaster, self.direction)
				if group == "right":
					self.switcher(self.rightPosition, self.leftPosition, self.KGGlyphActiveMaster, self.direction)

		except:
			print(traceback.format_exc())


	@objc.python_method
	def KGGlyphsGen(self):
		glyphsOfGroupLeft = []
		glyphsOfGroupRight = []
		for glyph in self.Font.glyphs:
			if self.LKG and glyph.leftKerningGroup == self.LKG:
				glyphsOfGroupLeft.append(self.Font.glyphForName_(glyph.name))
			if self.RKG and glyph.rightKerningGroup == self.RKG:
				glyphsOfGroupRight.append(self.Font.glyphForName_(glyph.name))
		return glyphsOfGroupLeft, glyphsOfGroupRight


	@objc.python_method
	def generateKGInfo(self, layer):

		self.Glyph = layer.parent
		self.Font = self.controller.parent
		thisMaster = self.controller.activeMaster()
		self.activeMasterId = thisMaster.id
		self.direction = self.controller.direction
		try:
			self.thisWidth = layer.width
			self.xHeight = thisMaster.xHeight
			self.margin = 30
			self.scaler = .2
			self.R, self.G, self.B = 0, 0.5, 0.5
			self.floatLimit = 0.04

			### LEFT
			self.LKG = layer.parent.leftKerningGroup
			self.RKG = layer.parent.rightKerningGroup
			if self.LKG or self.RKG:
				KGGlyphsLeft, KGGlyphsRight = self.KGGlyphsGen()
				try:
					if KGGlyphsLeft:
						self.superimpose(KGGlyphsLeft, "left")
					if KGGlyphsRight:
						self.superimpose(KGGlyphsRight, "right")
				except:
					print(traceback.format_exc())
		except:
			print(traceback.format_exc())


	@objc.python_method
	def RefreshView(self):
		try:
			currentTabView = Glyphs.font.currentTab
			if currentTabView:
				currentTabView.graphicView().setNeedsDisplay_(True)
		except:
			pass


	@objc.python_method
	def drawKerningGroupReference(self, layer, positionX, positionY):
		try:
			thisBezierPathWithComponent = layer.copyDecomposedLayer().bezierPath()
		except:
			thisBezierPathWithComponent = layer.copyDecomposedLayer().bezierPath
		scale = NSAffineTransform.transform()
		scale.translateXBy_yBy_(positionX, positionY)
		scale.scaleBy_(0.2)

		thisBezierPathWithComponent.transformUsingAffineTransform_(scale)

		if thisBezierPathWithComponent:
			if self.toggle == 1:
				thisBezierPathWithComponent.fill()
			if self.toggle == 0:
				thisBezierPathWithComponent.stroke()
