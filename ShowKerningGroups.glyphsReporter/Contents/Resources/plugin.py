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


from __future__ import division, print_function, unicode_literals
from GlyphsApp.plugins import *
from GlyphsApp import LTR, RTL
from vanilla import *
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
		if side == "left":
			# tabString = "/" + "\n/".join([g.name for g in self.LKGGlyphs])
			thisLKG = self.KGGlyphsGen(self.LKG)
			tabString = "/" + "\n/".join([g.name for g in thisLKG])
		if side == "right":
			# tabString = "/" + "\n/".join([g.name for g in self.RKGGlyphs])
			thisRKG = self.KGGlyphsGen(self.RKG)
			tabString = "/" + "\n/".join([g.name for g in thisRKG])
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
		self.leftPosition = -distance - self.margin, self.xHeight/2
		self.rightPosition = self.thisWidth + self.margin+10 + distance - KGWidth, self.xHeight/2

	@objc.python_method
	def switcher(self, A, B, KGGlyphActiveMaster, direction):
		if direction == LTR:
			self.drawKerningGroupReference(KGGlyphActiveMaster, *A)
		if direction == RTL:
			self.drawKerningGroupReference(KGGlyphActiveMaster, *B)

	@objc.python_method
	def allGlyphs(self):
		for g in self.Font.glyphs:
			yield g


	@objc.python_method
	def superimpose(self, group):
		if group == "leftGroup":
			KGGlyphs = self.KGGlyphsGen(self.LKG)
		if group == "rightGroup":
			KGGlyphs = self.KGGlyphsGen(self.RKG)

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

				if group == "leftGroup":
					self.switcher(self.leftPosition, self.rightPosition, self.KGGlyphActiveMaster, self.direction)
				if group == "rightGroup":
					self.switcher(self.rightPosition, self.leftPosition, self.KGGlyphActiveMaster, self.direction)

		except:
			print(traceback.format_exc())


	@objc.python_method
	def KGGlyphsGen(self, KG):
		# Generator not working with len(list(generator)), but len is needed fpr the alpha
		glyphsOfGroup = []
		for glyph in self.allGlyphs():
			if glyph.leftKerningGroup == KG:
				glyphsOfGroup.append(self.Font.glyphForName_(glyph.name))
			if glyph.rightKerningGroup == KG:
				glyphsOfGroup.append(self.Font.glyphForName_(glyph.name))
		return glyphsOfGroup


	@objc.python_method
	def generateKGInfo(self, layer):

		self.Glyph = layer.parent
		self.Font = self.Glyph.parent
		masters = self.Font.masters
		thisMaster = self.Font.selectedFontMaster
		self.activeMasterId = thisMaster.id
		self.direction = self.Font.currentTab.writingDirection()
		try:
			self.thisWidth = layer.width
			self.xHeight = thisMaster.xHeight
			self.margin = 30
			self.scaler = .2
			self.R, self.G, self.B = 0, 0.5, 0.5
			self.floatLimit = 0.04
			
			### LEFT
			if layer.parent.leftKerningGroup:
				self.LKG = layer.parent.leftKerningGroup

				try:
					LKGGlyph = self.Font.glyphForName_(self.LKG)
					self.superimpose("leftGroup")
				except:
					print(traceback.format_exc())
		
			### Right
			if layer.parent.rightKerningGroup:
				self.RKG = layer.parent.rightKerningGroup
				try:
					RKGGlyph = self.Font.glyphForName_(self.RKG)
					self.superimpose("rightGroup")
				except:
					print(traceback.format_exc())
	
		except:
			print(traceback.format_exc())


	@objc.python_method
	def RefreshView(self):
		try:
			Glyphs = NSApplication.sharedApplication()
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

