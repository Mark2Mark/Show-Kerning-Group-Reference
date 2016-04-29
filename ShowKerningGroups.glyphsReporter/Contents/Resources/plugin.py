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


from GlyphsApp.plugins import *
from vanilla import *
import traceback

class ShowKerningGroups(ReporterPlugin):

	def settings(self):

		###################################
		## Context Menu:
		self.nameLeft = 'Tab with LKG Members'
		self.nameRight = 'Tab with RKG Members'
		self.nameToggler = 'Toggle Fill/Stroke'
		self.toggle = 1

		# Create Vanilla window and group with controls
		viewWidth = 320 # 150
		viewHeight = 80
		self.contextMenu = Window((viewWidth, viewHeight))
		self.contextMenu.group = Group((0, 0, viewWidth, viewHeight)) # (0, 0, viewWidth, viewHeight)
		self.contextMenu.group.line = HorizontalLine((10, 10, -10, 1))
		self.contextMenu.group.buttonL = Button((10, 20, -10, 18), self.nameLeft, sizeStyle="small", callback=self.LKGTab)
		self.contextMenu.group.buttonR = Button((10, 40, -10, 18), self.nameRight, sizeStyle="small", callback=self.RKGTab)
		self.contextMenu.group.buttonToggle = Button((10, 60, -10, 18), self.nameToggler, sizeStyle="small", callback=self.toggleFillStroke)

		## Define the menu
		self.generalContextMenus = [
		    {"view": self.contextMenu.group.getNSView()}
		]
		###################################

		self.menuName = Glyphs.localize({'en': u'* Kerning Groups'})
		

	def background(self, layer):  # def foreground(self, layer):
		self.generateKGInfo(layer)

	def openTab( self, side ):
		if side == "left":
			# tabString = "/" + "\n/".join([g.name for g in self.LKGGlyphs])
			thisLKG = self.KGGlyphsGen(self.LKG)
			tabString = "/" + "\n/".join([g.name for g in thisLKG])
		if side == "right":
			# tabString = "/" + "\n/".join([g.name for g in self.RKGGlyphs])
			thisRKG = self.KGGlyphsGen(self.RKG)
			tabString = "/" + "\n/".join([g.name for g in thisRKG])
		self.Font.newTab(tabString)



	def LKGTab(self, sender):
		self.openTab("left")

	def RKGTab(self, sender):
		self.openTab("right")

	def toggleFillStroke(self, sender):
		try:
			self.toggle = self.toggle ^ 1
			self.RefreshView()
		except:
			print traceback.format_exc()


	def position( self, KGWidth):
		distance = 120
		self.leftPosition = -distance - self.margin, self.xHeight/2
		self.rightPosition = self.thisWidth + self.margin+10 + distance - KGWidth, self.xHeight/2

	def switcher( self, A, B, KGGlyphActiveMaster, direction ):
		if direction == 0:
			self.drawKerningGroupReference( KGGlyphActiveMaster, *A )
		if direction == 1:
			self.drawKerningGroupReference( KGGlyphActiveMaster, *B )

	def allGlyphs(self):
		for g in self.Font.glyphs:
			yield g


	def superimpose(self, group):
		if group == "leftGroup":
			KGGlyphs = self.KGGlyphsGen(self.LKG)
		if group == "rightGroup":
			KGGlyphs = self.KGGlyphsGen(self.RKG)

		try:
			thisAlpha = 0.8
			thisAlpha = .8/len(KGGlyphs)
			if thisAlpha < self.floatLimit:
				thisAlpha = self.floatLimit
			NSColor.colorWithCalibratedRed_green_blue_alpha_(self.R, self.G, self.B, thisAlpha).set()
			for KGGlyph in KGGlyphs:
				self.KGGlyphActiveMaster = KGGlyph.layers[self.activeMasterIndex]
				KGWidth = self.KGGlyphActiveMaster.width * self.scaler
				self.position( KGWidth )

				if group == "leftGroup":
					self.switcher( self.leftPosition, self.rightPosition, self.KGGlyphActiveMaster, self.direction )
				if group == "rightGroup":
					self.switcher( self.rightPosition, self.leftPosition, self.KGGlyphActiveMaster, self.direction )

		except:
			print traceback.format_exc()


	def KGGlyphsGen(self, KG):
		# Generator not working with len(list(generator)), but len is needed fpr the alpha
		glyphsOfGroup = []
		for glyph in self.allGlyphs():
			if glyph.leftKerningGroup == KG:
				glyphsOfGroup.append( self.Font.glyphForName_(glyph.name) )
			if glyph.rightKerningGroup == KG:
				glyphsOfGroup.append( self.Font.glyphForName_(glyph.name) )
		return glyphsOfGroup


	def generateKGInfo( self, layer ):

		self.Glyph = layer.parent
		self.Font = self.Glyph.parent
		masters = self.Font.masters		
		thisMaster = self.Font.selectedFontMaster
		self.activeMasterIndex = masters.index(thisMaster)
		self.direction = self.Font.tabs[-1].writingDirection() ### <-- crash issue at Line Break?


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
					print traceback.format_exc()

			### Right
			if layer.parent.rightKerningGroup:
				self.RKG = layer.parent.rightKerningGroup
				try:
					RKGGlyph = self.Font.glyphForName_(self.RKG)
					self.superimpose("rightGroup")
				except:
					print traceback.format_exc()


		except Exception as e:
			print "generateKGInfo: %s" % str(e)


	def RefreshView(self):
		try:
			Glyphs = NSApplication.sharedApplication()
			currentTabView = Glyphs.font.currentTab
			if currentTabView:
				currentTabView.graphicView().setNeedsDisplay_(True)
		except:
			pass


	def drawKerningGroupReference( self, layer, positionX, positionY ):
		try:
			thisBezierPathWithComponent = layer.copyDecomposedLayer().bezierPath()
		except:
			thisBezierPathWithComponent = layer.copyDecomposedLayer().bezierPath
		scale = NSAffineTransform.transform()
		scale.translateXBy_yBy_( positionX, positionY )
		scale.scaleBy_( .2 )
		
		thisBezierPathWithComponent.transformUsingAffineTransform_( scale )
		
		if thisBezierPathWithComponent:
			if self.toggle == 1:
				thisBezierPathWithComponent.fill()
			if self.toggle == 0:
				thisBezierPathWithComponent.stroke()

