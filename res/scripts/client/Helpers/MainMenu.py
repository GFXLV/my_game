import BigWorld
import GUI
import Keys


class MenuButton:
    normalColour = ( 60, 60, 180, 200 )
    hoverColour = ( 120, 120, 255, 230 )

    def __init__( self, component, label, onClick ):
        self.component = component
        self.component.script = self
        self.onClick = onClick
        self.hovering = False

        self.component.focus = True
        self.component.mouseButtonFocus = True
        self.component.crossFocus = True

        self.component.colour = self.normalColour

        self.label = GUI.Text( label )
        self.label.colour = ( 255, 255, 255, 255 )
        self.label.font = "default_medium.font"
        self.label.horizontalPositionMode = "CLIP"
        self.label.verticalPositionMode = "CLIP"
        self.label.horizontalAnchor = "CENTER"
        self.label.verticalAnchor = "CENTER"
        self.component.addChild( self.label, "label" )

    def handleMouseClickEvent( self, comp ):
        return True

    def handleMouseButtonEvent( self, comp, event ):
        if event.key == Keys.KEY_LEFTMOUSE and not event.isKeyDown():
            self.onClick()
        return True

    def handleMouseEnterEvent( self, comp ):
        self.hovering = True
        self.component.colour = self.hoverColour
        return True

    def handleMouseLeaveEvent( self, comp ):
        self.hovering = False
        self.component.colour = self.normalColour
        return True


class MainMenu:
    def __init__( self, onEnterGame, onExitGame ):
        self.onEnterGame = onEnterGame
        self.onExitGame = onExitGame

        self.background = GUI.Simple( "system/maps/col_white.bmp" )
        self.background.materialFX = "BLEND"
        self.background.colour = ( 0, 0, 0, 160 )
        self.background.position = ( -1, -1, 0 )
        self.background.verticalAnchor = "BOTTOM"
        self.background.horizontalAnchor = "LEFT"
        self.background.width = 2
        self.background.height = 2

        self.title = GUI.Text( "My Game" )
        self.title.font = "default_medium.font"
        self.title.colour = ( 220, 220, 255, 255 )
        self.title.position = ( 0, 0.6, 0 )
        self.title.horizontalAnchor = "CENTER"
        self.title.verticalAnchor = "CENTER"

        self.enterButton = GUI.Window( "system/maps/col_white.bmp" )
        self.enterButton.materialFX = "BLEND"
        self.enterButton.width = 0.35
        self.enterButton.height = 0.08
        self.enterButton.position = ( 0, 0.1, 0 )
        self.enterButton.horizontalAnchor = "CENTER"
        self.enterButton.verticalAnchor = "CENTER"
        MenuButton( self.enterButton, "Enter Game", self._onEnterGame )

        self.exitButton = GUI.Window( "system/maps/col_white.bmp" )
        self.exitButton.materialFX = "BLEND"
        self.exitButton.width = 0.35
        self.exitButton.height = 0.08
        self.exitButton.position = ( 0, -0.05, 0 )
        self.exitButton.horizontalAnchor = "CENTER"
        self.exitButton.verticalAnchor = "CENTER"
        MenuButton( self.exitButton, "Exit Game", self._onExitGame )

        GUI.addRoot( self.background )
        GUI.addRoot( self.title )
        GUI.addRoot( self.enterButton )
        GUI.addRoot( self.exitButton )

        mc = GUI.mcursor()
        mc.visible = True
        mc.clipped = True
        BigWorld.setCursor( mc )

    def _onEnterGame( self ):
        if self.background is None:
            return

        GUI.delRoot( self.background )
        GUI.delRoot( self.title )
        GUI.delRoot( self.enterButton )
        GUI.delRoot( self.exitButton )
        self.background = None
        self.title = None
        self.enterButton = None
        self.exitButton = None

        mc = GUI.mcursor()
        mc.visible = False
        mc.clipped = True
        BigWorld.setCursor( None )

        self.onEnterGame()

    def _onExitGame( self ):
        BigWorld.quit()
