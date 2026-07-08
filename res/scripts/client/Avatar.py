import BigWorld
import GUI
import Keys

import chapters

from Helpers import ChatConsole

class Avatar( BigWorld.Entity ):

	def onEnterWorld( self, prereqs ):
		# Set the position/movement filter to correspond to an avatar
		self.filter = BigWorld.AvatarFilter()

		# Load up the bipedgirl model
		self.model = BigWorld.Model( "characters/bipedgirl.model" )
	def say( self, msg ):

		ChatConsole.ChatConsole.instance().write(
			"%d says: %s" % (self.id, msg) )


class PlayerAvatar( Avatar ):

	def onEnterWorld( self, prereqs ):

		Avatar.onEnterWorld( self, prereqs )

		# Set the position/movement filter to correspond to an player avatar
		self.filter = BigWorld.PlayerAvatarFilter()

		# Setup the physics for the Avatar
		self.physics = BigWorld.STANDARD_PHYSICS
		self.physics.velocityMouse = "Direction"
		self.physics.collide = True
		self.physics.fall = True

		# Create floating name tag above the model
		self._createNameTag()

		# Show cursor so it's visible during gameplay
		try:
			mc = GUI.mcursor()
			mc.visible = True
			mc.clipped = True
			BigWorld.setCursor( mc )
		except:
			pass


	def _createNameTag( self ):
		if self.model is None:
			return

		try:
			import BWPersonality
			displayName = BWPersonality.gPlayerName
			if not displayName:
				displayName = BWPersonality.gPlayerEmail
		except:
			displayName = "Player"

		self.nameTag = GUI.Text( displayName )
		self.nameTag.font = "default_small.font"
		self.nameTag.colour = (255, 0, 0, 255)
		self.nameTag.horizontalAnchor = "CENTER"
		self.nameTag.verticalAnchor = "CENTER"
		self.nameTag.position = ( 0, self.model.height + 0.3, 0 )

		self.nameAttachment = GUI.Attachment()
		self.nameAttachment.faceCamera = True
		self.nameAttachment.component = self.nameTag
		self.model.root.attach( self.nameAttachment )


	def _destroyNameTag( self ):
		if hasattr( self, 'nameAttachment' ) and self.nameAttachment is not None:
			self.model.root.detach( self.nameAttachment )
			self.nameAttachment = None
		if hasattr( self, 'nameTag' ) and self.nameTag is not None:
			self.nameTag = None


	def onClientDeath( self ):
		self._destroyNameTag()

		mc = GUI.mcursor()
		mc.visible = False
		mc.clipped = True
		BigWorld.setCursor( None )


	def handleKeyEvent( self, event ):

		if event.isRepeatedEvent():
			return

		isDown = event.isKeyDown()

		# Get the current velocity
		v = self.physics.velocity

		# Update the velocity depending on the key input
		if event.key == Keys.KEY_W:
			v.z = isDown * 5.0
		elif event.key == Keys.KEY_S:
			v.z = isDown * -5.0
		elif event.key == Keys.KEY_A:
			v.x = isDown * -5.0
		elif event.key == Keys.KEY_D:
			v.x = isDown * 5.0

		# Save back the new velocity
		self.physics.velocity = v

# Avatar.py
