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

# ------------------------------------------------------------------------------
# Section: Required callbacks
# ------------------------------------------------------------------------------

# The init function is called as part of the BigWorld initialisation process.
# It receives the BigWorld xml config files as arguments.  This is the best
# place to configure all the application-specific BigWorld components, like
# initial camera view, etc...
def init( scriptsConfig, engineConfig, prefs ):

	global gScriptsConfig, gMainMenu
	gScriptsConfig = scriptsConfig

	# Show the main menu with Enter Game / Exit Game buttons
	from Helpers import MainMenu
	gMainMenu = MainMenu.MainMenu( _onEnterGame, _onExitGame )

	# Set up third-person camera
	try:
		cam = BigWorld.Camera( "BehindObstacle" )
		BigWorld.camera( cam )
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

	global gInGame

	# Let GUI process the event first
	if GUI.handleMouseEvent( event ):
		return True

	# Camera/player rotation with mouse movement
	if gInGame and not event.isMouseButton() and ( event.dx != 0 or event.dy != 0 ):
		sens = 0.005
		cam = BigWorld.camera()
		if cam is not None:
			try:
				rotated = False
				if event.dx != 0 and hasattr( cam, "yaw" ):
					cam.yaw += event.dx * sens
					rotated = True
				if event.dy != 0 and hasattr( cam, "pitch" ):
					cam.pitch = max( -1.5, min( 1.5, cam.pitch + event.dy * sens ) )
					rotated = True
			except:
				pass

	return False


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

def _returnToMenu():
	global gChatConsole, gInGame, gMainMenu, gPlayerEmail, gPlayerName, gHeartbeatHandle

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
		elif stage == 6:
			gChatConsole.write( "Disconnected: " + serverMsg )

	BigWorld.connect( scriptsConfig.readString( "server/host" ),
					  LoginParams(), onConnect )

# BWPersonality.py
