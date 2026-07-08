import BigWorld
import GUI
import Keys


BTN_COLOUR = (60, 60, 180, 200)
BTN_HOVER = (120, 120, 255, 230)
BTN_ACTIVE = (180, 180, 80, 230)
BTN_SIZE = 0.07
SPEED = 5.0


class NavButton:
    def __init__(self, parent, x, y, label, onMove):
        self.onMove = onMove
        self.pressed = False

        self.comp = GUI.Window("system/maps/col_white.bmp")
        self.comp.materialFX = "BLEND"
        self.comp.colour = BTN_COLOUR
        self.comp.width = BTN_SIZE
        self.comp.height = BTN_SIZE
        self.comp.position = (x, y, 0)
        self.comp.horizontalAnchor = "CENTER"
        self.comp.verticalAnchor = "CENTER"
        self.comp.script = self
        self.comp.focus = True
        self.comp.mouseButtonFocus = True
        self.comp.crossFocus = True

        self.text = GUI.Text(label)
        self.text.font = "default_small.font"
        self.text.colour = (255, 255, 255, 255)
        self.text.horizontalAnchor = "CENTER"
        self.text.verticalAnchor = "CENTER"
        self.text.horizontalPositionMode = "CLIP"
        self.text.verticalPositionMode = "CLIP"
        self.comp.addChild(self.text, "label")

        GUI.addRoot(self.comp)

    def handleMouseButtonEvent(self, comp, event):
        if event.key == Keys.KEY_LEFTMOUSE:
            if event.isKeyDown():
                self.pressed = True
                self.comp.colour = BTN_ACTIVE
                self.onMove(True)
            else:
                self.pressed = False
                self.comp.colour = BTN_HOVER
                self.onMove(False)
        return True

    def handleMouseEnterEvent(self, comp):
        if not self.pressed:
            self.comp.colour = BTN_HOVER
        return True

    def handleMouseLeaveEvent(self, comp):
        if not self.pressed:
            self.comp.colour = BTN_COLOUR
        return True

    def destroy(self):
        GUI.delRoot(self.comp)
        self.comp = None


class NavButtons:
    def __init__(self, avatar):
        self.avatar = avatar
        self.forward = False
        self.back = False
        self.left = False
        self.right = False

        self.fwdBtn = NavButton(self, 0.0, -0.55, "^", self._onFwd)
        self.bckBtn = NavButton(self, 0.0, -0.72, "v", self._onBck)
        self.lftBtn = NavButton(self, -0.12, -0.635, "<", self._onLft)
        self.rgtBtn = NavButton(self, 0.12, -0.635, ">", self._onRgt)

    def _onFwd(self, down):
        self.forward = down
        self._update()

    def _onBck(self, down):
        self.back = down
        self._update()

    def _onLft(self, down):
        self.left = down
        self._update()

    def _onRgt(self, down):
        self.right = down
        self._update()

    def _update(self):
        if self.avatar is None or not hasattr(self.avatar, 'physics'):
            return
        v = self.avatar.physics.velocity
        v.x = (self.right - self.left) * SPEED
        v.z = (self.forward - self.back) * SPEED
        self.avatar.physics.velocity = v

    def destroy(self):
        self.avatar = None
        self.fwdBtn.destroy()
        self.bckBtn.destroy()
        self.lftBtn.destroy()
        self.rgtBtn.destroy()
