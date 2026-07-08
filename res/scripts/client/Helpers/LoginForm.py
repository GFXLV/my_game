import BigWorld
import GUI
import Keys
import urllib2
import json

API_URL = "http://localhost/api/verify-credentials"

class LoginForm:
    LARGE_FONT = "default_medium.font"
    SMALL_FONT = "default_small.font"
    NORMAL_COLOUR = (60, 60, 180, 200)
    HOVER_COLOUR = (120, 120, 255, 230)

    def __init__(self, onLoginSuccess, onBack):
        self.onLoginSuccess = onLoginSuccess
        self.onBack = onBack
        self.email = ""
        self.password = ""
        self.currentField = 0
        self.errorText = ""
        self.loading = False

        self.background = GUI.Simple("system/maps/col_white.bmp")
        self.background.materialFX = "BLEND"
        self.background.colour = (0, 0, 0, 160)
        self.background.position = (-1, -1, 0)
        self.background.verticalAnchor = "BOTTOM"
        self.background.horizontalAnchor = "LEFT"
        self.background.width = 2
        self.background.height = 2

        self.title = GUI.Text("Login")
        self.title.font = self.LARGE_FONT
        self.title.colour = (220, 220, 255, 255)
        self.title.position = (0, 0.7, 0)
        self.title.horizontalAnchor = "CENTER"
        self.title.verticalAnchor = "CENTER"

        self.emailLabel = GUI.Text("Email:")
        self.emailLabel.font = self.SMALL_FONT
        self.emailLabel.colour = (200, 200, 200, 255)
        self.emailLabel.position = (-0.3, 0.35, 0)
        self.emailLabel.horizontalAnchor = "CENTER"
        self.emailLabel.verticalAnchor = "CENTER"

        self.emailField = GUI.Window("system/maps/col_white.bmp")
        self.emailField.materialFX = "BLEND"
        self.emailField.colour = (40, 40, 40, 200)
        self.emailField.width = 0.5
        self.emailField.height = 0.06
        self.emailField.position = (0, 0.25, 0)
        self.emailField.horizontalAnchor = "CENTER"
        self.emailField.verticalAnchor = "CENTER"
        self.emailField.script = self
        self.emailField.focus = True
        self.emailField.mouseButtonFocus = True
        self.emailField.crossFocus = True

		self.emailText = GUI.Text("")
		self.emailText.font = self.SMALL_FONT
		self.emailText.colour = (255, 255, 255, 255)
		self.emailText.horizontalPositionMode = "CLIP"
		self.emailText.verticalPositionMode = "CLIP"
		self.emailText.position = (-0.22, 0, 0)
		self.emailText.width = 0.44
		self.emailText.horizontalAnchor = "LEFT"
		self.emailText.verticalAnchor = "CENTER"
		self.emailField.addChild(self.emailText, "label")

        self.passwordLabel = GUI.Text("Password:")
        self.passwordLabel.font = self.SMALL_FONT
        self.passwordLabel.colour = (200, 200, 200, 255)
        self.passwordLabel.position = (-0.3, 0.1, 0)
        self.passwordLabel.horizontalAnchor = "CENTER"
        self.passwordLabel.verticalAnchor = "CENTER"

        self.passwordField = GUI.Window("system/maps/col_white.bmp")
        self.passwordField.materialFX = "BLEND"
        self.passwordField.colour = (40, 40, 40, 200)
        self.passwordField.width = 0.5
        self.passwordField.height = 0.06
        self.passwordField.position = (0, 0.0, 0)
        self.passwordField.horizontalAnchor = "CENTER"
        self.passwordField.verticalAnchor = "CENTER"
        self.passwordField.script = self
        self.passwordField.focus = True
        self.passwordField.mouseButtonFocus = True
        self.passwordField.crossFocus = True

		self.passwordText = GUI.Text("")
		self.passwordText.font = self.SMALL_FONT
		self.passwordText.colour = (255, 255, 255, 255)
		self.passwordText.horizontalPositionMode = "CLIP"
		self.passwordText.verticalPositionMode = "CLIP"
		self.passwordText.position = (-0.22, 0, 0)
		self.passwordText.width = 0.44
		self.passwordText.horizontalAnchor = "LEFT"
		self.passwordText.verticalAnchor = "CENTER"
		self.passwordField.addChild(self.passwordText, "label")

        self.authButton = GUI.Window("system/maps/col_white.bmp")
        self.authButton.materialFX = "BLEND"
        self.authButton.colour = self.NORMAL_COLOUR
        self.authButton.width = 0.35
        self.authButton.height = 0.07
        self.authButton.position = (0, -0.2, 0)
        self.authButton.horizontalAnchor = "CENTER"
        self.authButton.verticalAnchor = "CENTER"
        self.authButton.script = self
        self.authButton.focus = True
        self.authButton.mouseButtonFocus = True
        self.authButton.crossFocus = True

        self.authLabel = GUI.Text("Authenticate")
        self.authLabel.font = self.LARGE_FONT
        self.authLabel.colour = (255, 255, 255, 255)
        self.authLabel.horizontalPositionMode = "CLIP"
        self.authLabel.verticalPositionMode = "CLIP"
        self.authLabel.horizontalAnchor = "CENTER"
        self.authLabel.verticalAnchor = "CENTER"
        self.authButton.addChild(self.authLabel, "label")

        self.backButton = GUI.Window("system/maps/col_white.bmp")
        self.backButton.materialFX = "BLEND"
        self.backButton.colour = self.NORMAL_COLOUR
        self.backButton.width = 0.35
        self.backButton.height = 0.07
        self.backButton.position = (0, -0.33, 0)
        self.backButton.horizontalAnchor = "CENTER"
        self.backButton.verticalAnchor = "CENTER"
        self.backButton.script = self
        self.backButton.focus = True
        self.backButton.mouseButtonFocus = True
        self.backButton.crossFocus = True

        self.backLabel = GUI.Text("Back")
        self.backLabel.font = self.LARGE_FONT
        self.backLabel.colour = (255, 255, 255, 255)
        self.backLabel.horizontalPositionMode = "CLIP"
        self.backLabel.verticalPositionMode = "CLIP"
        self.backLabel.horizontalAnchor = "CENTER"
        self.backLabel.verticalAnchor = "CENTER"
        self.backButton.addChild(self.backLabel, "label")

        self.errorDisplay = GUI.Text("")
        self.errorDisplay.font = self.SMALL_FONT
        self.errorDisplay.colour = (255, 80, 80, 255)
        self.errorDisplay.position = (0, -0.45, 0)
        self.errorDisplay.horizontalAnchor = "CENTER"
        self.errorDisplay.verticalAnchor = "CENTER"

        GUI.addRoot(self.background)
        GUI.addRoot(self.title)
        GUI.addRoot(self.emailLabel)
        GUI.addRoot(self.emailField)
        GUI.addRoot(self.passwordLabel)
        GUI.addRoot(self.passwordField)
        GUI.addRoot(self.authButton)
        GUI.addRoot(self.backButton)
        GUI.addRoot(self.errorDisplay)

        mc = GUI.mcursor()
        mc.visible = True
        mc.clipped = True
        BigWorld.setCursor(mc)

    def destroy(self):
        GUI.delRoot(self.background)
        GUI.delRoot(self.title)
        GUI.delRoot(self.emailLabel)
        GUI.delRoot(self.emailField)
        GUI.delRoot(self.passwordLabel)
        GUI.delRoot(self.passwordField)
        GUI.delRoot(self.authButton)
        GUI.delRoot(self.backButton)
        GUI.delRoot(self.errorDisplay)
        self.background = None
        self.title = None
        self.emailLabel = None
        self.emailField = None
        self.passwordLabel = None
        self.passwordField = None
        self.authButton = None
        self.backButton = None
        self.errorDisplay = None

		mc = GUI.mcursor()
		mc.visible = True
		mc.clipped = True
		BigWorld.setCursor(mc)

    def setError(self, msg):
        self.errorText = msg
        self.errorDisplay.text = msg

    def _submitAuth(self):
        if self.loading:
            return

        if len(self.email) == 0:
            self.setError("Please enter your email.")
            return
        if len(self.password) == 0:
            self.setError("Please enter your password.")
            return

        self.setError("Authenticating...")
        self.loading = True

        data = json.dumps({"email": self.email, "password": self.password})

        try:
            req = urllib2.Request(API_URL, data, {"Content-Type": "application/json"})
            proxy_handler = urllib2.ProxyHandler({})
            opener = urllib2.build_opener(proxy_handler)
            response = opener.open(req, timeout=10)
            result = json.loads(response.read())

            if result.get("valid"):
                self.setError("")
                playerName = result.get("user", {}).get("name", "")
                self.destroy()
                self.onLoginSuccess(self.email, self.password, playerName)
            else:
                self.setError(result.get("message", "Authentication failed."))
                self.loading = False

        except urllib2.HTTPError as e:
            try:
                result = json.loads(e.read())
                self.setError(result.get("message", "Invalid credentials."))
            except:
                self.setError("Server error. Please try again.")
            self.loading = False

        except Exception as e:
            self.setError("Could not connect to auth server.")
            self.loading = False

    def handleKeyEvent(self, event):
        if self.loading:
            return False

        if event.isMouseButton():
            return False

        if event.isKeyDown():
            if event.key == Keys.KEY_TAB:
                self.currentField = (self.currentField + 1) % 2
                return True

            elif event.key == Keys.KEY_RETURN:
                if self.currentField == 0:
                    self.currentField = 1
                else:
                    self._submitAuth()
                return True

            elif event.key == Keys.KEY_BACKSPACE:
                if self.currentField == 0:
                    self.email = self.email[:len(self.email) - 1]
                    self.emailText.text = self.email
                else:
                    self.password = self.password[:len(self.password) - 1]
                    self.passwordText.text = "*" * len(self.password)
                return True

            elif event.character is not None:
                if self.currentField == 0:
                    self.email += event.character
                    self.emailText.text = self.email
                else:
                    self.password += event.character
                    self.passwordText.text = "*" * len(self.password)
                return True

        return False

    def handleMouseClickEvent(self, comp):
        return True

    def handleMouseButtonEvent(self, comp, event):
        if self.loading:
            return True

        if event.key == Keys.KEY_LEFTMOUSE and not event.isKeyDown():
            if comp == self.authButton:
                self._submitAuth()
            elif comp == self.backButton:
                self.destroy()
                self.onBack()
            elif comp == self.emailField:
                self.currentField = 0
            elif comp == self.passwordField:
                self.currentField = 1
        return True

    def handleMouseEnterEvent(self, comp):
        if comp in (self.authButton, self.backButton):
            comp.colour = self.HOVER_COLOUR
        return True

    def handleMouseLeaveEvent(self, comp):
        if comp == self.authButton:
            self.authButton.colour = self.NORMAL_COLOUR
        elif comp == self.backButton:
            self.backButton.colour = self.NORMAL_COLOUR
        return True
