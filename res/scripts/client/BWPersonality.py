# This is the client personality script for the BigWorld tutorial.  Think of it
# as the bootstrap script for the client.  It contains functions that are called
# on initialisation, shutdown, and handlers for various input events.

import GUI
import BigWorld
import Keys
import urllib2
import json

import chapters

API_BASE = "http://localhost/api"

# ------------------------------------------------------------------------------
# Section: Globals
# ------------------------------------------------------------------------------

gChatConsole = None
gScriptsConfig = None
gLoginForm = None
gMainMenu = None
gPlayerEmail = ""
gPlayerName = ""
gInGame = False
gHeartbeatHandle = None
gCameraYaw = 0.0
gCameraPitch = 0.0
_cameraTickRunning = False
_useManualCamera = False

# ------------------------------------------------------------------------------
# Section: Required callbacks
# ------------------------------------------------------------------------------

# The init function is called as part of the BigWorld initialisation process.
# It receives the BigWorld xml config files as arguments.  This is the best
# place to configure all the application-specific BigWorld components, like
# initial camera view, etc...
def init( scriptsConfig, engineConfig, prefs ):

	global gScriptsConfig, gMainMenu, _useManualCamera
	gScriptsConfig = scriptsConfig

	# Show the main menu with Enter Game / Exit Game buttons
	from Helpers import MainMenu
	gMainMenu = MainMenu.MainMenu( _onEnterGame, _onExitGame )

	# Set up third-person camera
	try:
		cam = BigWorld.Camera( "BehindObstacle" )
		BigWorld.camera( cam )
	except:
		_useManualCamera = True

	# Show cursor from the start (visible on main menu)
	try:
		mc = GUI.mcursor()
		mc.visible = True
		mc.clipped = True
		BigWorld.setCursor( mc )
	except:
		pass

# This is called immediately after init() finishes.  We're done with all our
# init code, so this is a no-op.
def start():
	pass


# This method is called just before the game shuts down.
def fini():
	pass


# This is called by BigWorld when player moves from inside to outside
# environment, or vice versa.  It should be used to adapt any personality
# related data (eg, camera position/nature, etc).
def onChangeEnvironments( inside ):
	pass

# This is called by the engine when a system generated message occurs.
def addChatMsg( msg ):
	if gChatConsole is not None:
		gChatConsole.write( msg )

# Keyboard event handler
def handleKeyEvent( event ):

	global gLoginForm, gInGame, gChatConsole

	# Let the GUI system process the event first (for menu buttons, etc.)
	if GUI.handleKeyEvent( event ):
		return True

	# If LoginForm is active, let it process keys
	if gLoginForm is not None:
		if gLoginForm.handleKeyEvent( event ):
			return True

	# ESC to return to main menu (only when not editing chat)
	if event.isKeyDown() and event.key == Keys.KEY_ESCAPE:
		if gInGame and ( gChatConsole is None or not gChatConsole.editing() ):
			_returnToMenu()
			return True

	# If the chat console isn't created yet, ignore key events
	if gChatConsole is None:
		return False

	# If the chat console is in edit mode, let it handle all keypresses
	if gChatConsole.editing():
		return gChatConsole.handleKeyEvent( event )

	# If the user hits the ENTER key, we enter chat mode
	if event.isKeyDown() and event.key == Keys.KEY_RETURN:
		gChatConsole.editing( True )
		return True

	return False


# Mouse event handler
def handleMouseEvent( event ):

	global gInGame, gCameraYaw, gCameraPitch

	# Let GUI process the event first
	if GUI.handleMouseEvent( event ):
		return True

	if gInGame and not event.isMouseButton() and ( event.dx != 0 or event.dy != 0 ):
		sens = 0.005
		cam = BigWorld.camera()
		player = BigWorld.player()

		# Strategy 1: rotate camera directly (works with BehindObstacle mode)
		if cam is not None:
			try:
				if event.dx != 0 and hasattr( cam, "yaw" ):
					cam.yaw += event.dx * sens
				if event.dy != 0 and hasattr( cam, "pitch" ):
					cam.pitch = max( -1.5, min( 1.5, cam.pitch + event.dy * sens ) )
				return False
			except:
				pass

		# Strategy 2: rotate player entity direction
		if player is not None:
			try:
				if event.dx != 0 and hasattr( player, "direction" ):
					d = player.direction
					player.direction = ( d[ 0 ], d[ 1 ], d[ 2 ] + event.dx * sens )
				return False
			except:
				pass

		# Strategy 3: manual orbit (fallback for no camera mode)
		if _useManualCamera:
			gCameraYaw += event.dx * sens
			gCameraPitch = max( -1.5, min( 1.5, gCameraPitch + event.dy * sens ) )

	return False

def _updateCamera():
	global gInGame, gCameraYaw, gCameraPitch, _useManualCamera
	if not _useManualCamera:
		return
	try:
		player = BigWorld.player()
		if player is not None and gInGame:
			import Math
			cam = BigWorld.camera()
			if cam is not None:
				dist = 5.0
				height = 1.8
				sy, cy = Math.sin( gCameraYaw ), Math.cos( gCameraYaw )
				sp, cp = Math.sin( gCameraPitch ), Math.cos( gCameraPitch )
				cx = player.position.x + dist * sy * cp
				cy2 = player.position.y + height + dist * sp
				cz = player.position.z + dist * cy * cp
				cam.position = Math.Vector3( cx, cy2, cz )
				cam.direction = Math.Vector3(
					player.position.x - cx,
					player.position.y - cy2,
					player.position.z - cz )
	except:
		pass

def _cameraTick():
	global gInGame, _cameraTickRunning
	_updateCamera()
	if gInGame:
		BigWorld.callback( 0.0, _cameraTick )
	else:
		_cameraTickRunning = False


# Joystick event handler
def handleAxisEvent( event ):
	return False


# ------------------------------------------------------------------------------
# Section: Main menu callbacks
# ------------------------------------------------------------------------------

def _callAPI( endpoint, data ):
	try:
		url = API_BASE + endpoint
		body = json.dumps( data )
		req = urllib2.Request( url, body, { "Content-Type": "application/json" } )
		proxy_handler = urllib2.ProxyHandler( {} )
		opener = urllib2.build_opener( proxy_handler )
		opener.open( req, timeout = 5 )
	except:
		pass

def _callDisconnectAPI( email ):
	if email:
		_callAPI( "/disconnect", { "email": email } )

def _heartbeatCallback( email ):
	global gHeartbeatHandle
	_callAPI( "/heartbeat", { "email": email } )
	gHeartbeatHandle = BigWorld.callback( 30.0, lambda: _heartbeatCallback( email ) )

def _startHeartbeat( email ):
	global gHeartbeatHandle
	_stopHeartbeat()
	gHeartbeatHandle = BigWorld.callback( 30.0, lambda: _heartbeatCallback( email ) )

def _stopHeartbeat():
	global gHeartbeatHandle
	if gHeartbeatHandle is not None:
		try:
			BigWorld.cancelCallback( gHeartbeatHandle )
		except:
			pass
	gHeartbeatHandle = None

def _onExitGame():
	_stopHeartbeat()
	BigWorld.quit()

def _startCameraTick():
	global _cameraTickRunning
	if not _cameraTickRunning:
		_cameraTickRunning = True
		_cameraTick()

def _returnToMenu():
	global gChatConsole, gInGame, gMainMenu, gPlayerEmail, gPlayerName, gHeartbeatHandle, gCameraYaw, gCameraPitch

	_stopHeartbeat()
	_callDisconnectAPI( gPlayerEmail )

	try:
		BigWorld.disconnect()
	except:
		pass

	gChatConsole = None
	gPlayerEmail = ""
	gPlayerName = ""
	gInGame = False
	gCameraYaw = 0.0
	gCameraPitch = 0.0

	mc = GUI.mcursor()
	mc.visible = True
	mc.clipped = True
	BigWorld.setCursor( mc )

	from Helpers import MainMenu
	gMainMenu = MainMenu.MainMenu( _onEnterGame, _onExitGame )

def _onEnterGame():
	global gLoginForm, gScriptsConfig

	if gScriptsConfig.readBool( "server/online" ):
		from Helpers import LoginForm
		gLoginForm = LoginForm.LoginForm( _onLoginSuccess, _onBackToMenu )
	else:
		initOffline( gScriptsConfig )

def _onLoginSuccess( email, password, playerName = "" ):
	global gChatConsole, gScriptsConfig, gPlayerEmail, gPlayerName, gInGame, gLoginForm

	gPlayerEmail = email
	gPlayerName = playerName if playerName else email.split( "@" )[ 0 ]
	gInGame = True
	gLoginForm = None

	from Helpers import ChatConsole
	gChatConsole = ChatConsole.ChatConsole(
		gScriptsConfig.readInt( "chat/visibleLines" ) )

	mc = GUI.mcursor()
	mc.visible = True
	mc.clipped = True
	BigWorld.setCursor( mc )

	_startHeartbeat( email )
	_startCameraTick()
	initOnline( gScriptsConfig, email )

def _onBackToMenu():
	global gLoginForm, gMainMenu, gInGame
	gLoginForm = None
	gInGame = False
	from Helpers import MainMenu
	gMainMenu = MainMenu.MainMenu( _onEnterGame, _onExitGame )

# ------------------------------------------------------------------------------
# Section: Helper methods
# ------------------------------------------------------------------------------

def initOffline( scriptsConfig ):

	global gInGame

	gInGame = True

	mc = GUI.mcursor()
	mc.visible = True
	mc.clipped = True
	BigWorld.setCursor( mc )

	_startCameraTick()

	# Create a space for the client to inhabit
	spaceID = BigWorld.createSpace()

	# Load the space that is named in scripts_config.xml
	BigWorld.addSpaceGeometryMapping(
		spaceID, None, scriptsConfig.readString( "space" ) )

	# Create the player entity, using positions from scripts_config.xml
	playerID = BigWorld.createEntity(
		scriptsConfig.readString( "player/entityType" ),
		spaceID, 0,
		scriptsConfig.readVector3( "player/startPosition" ),
		scriptsConfig.readVector3( "player/startDirection" ),
		{} )

	BigWorld.player( BigWorld.entities[ playerID ] )

def initOnline( scriptsConfig, email = "" ):

	global gChatConsole

	class LoginParams( object ):
		pass

	def onConnect( stage, status, serverMsg ):
		if stage == 1:
			if status == "LOGGED_ON":
				gChatConsole.write( "Authenticated as: " + email )
			elif status == "LOGGED_ON_OFFLINE":
				gChatConsole.write( "Offline mode." )
			else:
				gChatConsole.write( "Login failed: " + serverMsg )
		elif stage == 2:
			gChatConsole.write( "Connected to server." )
			try:
				mc = GUI.mcursor()
				mc.visible = True
				mc.clipped = True
				BigWorld.setCursor( mc )
			except:
				pass
		elif stage == 6:
			gChatConsole.write( "Disconnected: " + serverMsg )

	BigWorld.connect( scriptsConfig.readString( "server/host" ),
					  LoginParams(), onConnect )

# BWPersonality.py
