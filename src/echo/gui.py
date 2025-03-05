import rumps

class EchoAssistantGUI(rumps.App):
    def __init__(self):
        super().__init__("Echo", icon="assets/icons/echo.png")

    @rumps.clicked("About")
    def about(self, _):
        rumps.alert("Echo", "Voice Assistant powered by OpenAI")

    @rumps.clicked("Quit")
    def quit(self, _):
        rumps.quit_application() 