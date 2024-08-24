import flet
import sys
import os
from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController
import time
import threading
import pickle

Moves=[]

if getattr(sys, 'frozen', False):
    ApplicationPath = str(os.path.dirname(sys.executable))
elif __file__:
    ApplicationPath = str(os.path.dirname(__file__))

def AppScreen(Page):
    Page.title = "Clear Clicker"
    Page.theme_mode = flet.ThemeMode.LIGHT
    Page.window_width = 1000
    Page.window_height = 700

    def ChangeRoute(RouteEvent):
        global Moves

        def ToggleActive(ActiveCheckbox, Checkboxes):
            if ActiveCheckbox.value==True:
                for Checkbox in Checkboxes:
                    Checkbox.value=False
                ActiveCheckbox.value=True
            else:
                ActiveCheckbox.value=True

            if ActiveCheckbox.label=="Count":
                RepeatCountSelect.disabled=False
                RepeatSecSelect.disabled=True
            elif ActiveCheckbox.label=="Time":
                RepeatCountSelect.disabled=True
                RepeatSecSelect.disabled=False

            Page.update()




        def RecordMoves():
            global Moves
            RecordButton.on_click= lambda ClickedEvent: StopRecordMoves()
            RecordButton.text="Stop Record"
            Moves=[]
            Page.update()
            
            with keyboard.Events() as KeyboardListener:
                for KeyboardEvent in KeyboardListener:
                    if KeyboardEvent.key == keyboard.Key.esc:
                        RememberMoves()
                        break


        def RememberMoves():
            global StartListenTime, RememberMoveEvent
            StartListenMessage = flet.BottomSheet(
                content=flet.Container(
                    padding=50,
                    content=flet.Text("Start Listen")
                ),
            )
            Page.dialog=StartListenMessage
            StartListenMessage.open=True
            Page.update()

            StartListenTime = time.time()

            RememberMoveEvent = threading.Event()
            threading.Thread(target=KeyboardDetect).start()
            threading.Thread(target=MouseDetect).start()


        def KeyboardDetect():
            with keyboard.Events() as KeyboardListener:
                for KeyboardEvent in KeyboardListener:
                    if RememberMoveEvent.is_set():
                        break
                    elif KeyboardEvent.key == keyboard.Key.esc and isinstance(KeyboardEvent, keyboard.Events.Press):
                        RememberMoveEvent.set()

                        StopListenMessage = flet.BottomSheet(
                            content=flet.Container(
                                padding=50,
                                content=flet.Text("Stop Listen")
                            ),
                        )
                        Page.dialog=StopListenMessage
                        StopListenMessage.open=True
                        Page.update()

                        break
                    elif isinstance(KeyboardEvent, keyboard.Events.Press):
                        Moves.append(('PressKey', KeyboardEvent.key, time.time()-StartListenTime))
                    elif isinstance(KeyboardEvent, keyboard.Events.Release) and KeyboardEvent.key != keyboard.Key.esc:
                        Moves.append(('ReleaseKey', KeyboardEvent.key, time.time()-StartListenTime))


        def MouseDetect():
            with mouse.Events() as MouseListener:
                for MouseEvent in MouseListener:
                    if RememberMoveEvent.is_set():
                        break
                    elif isinstance(MouseEvent, mouse.Events.Click):
                        if MouseEvent.pressed:
                            Moves.append(('PressButton', MouseEvent.x, MouseEvent.y, MouseEvent.button, time.time()-StartListenTime))
                        else:
                            Moves.append(('ReleaseButton', MouseEvent.x, MouseEvent.y, MouseEvent.button, time.time()-StartListenTime))
                    elif isinstance(MouseEvent, mouse.Events.Move):
                        Moves.append(('Move', MouseEvent.x, MouseEvent.y, time.time()-StartListenTime))
                    elif isinstance(MouseEvent, mouse.Events.Scroll):
                        Moves.append(('Scroll', MouseEvent.x, MouseEvent.y, MouseEvent.dx, MouseEvent.dy, time.time()-StartListenTime))


        def StopRecordMoves():
            global Moves
            RememberMoveEvent.set()
            Moves=sorted(Moves, key=lambda Move: Move[-1])

            with open(f'{ApplicationPath}/Moves.pkl', 'wb') as MovesFile:
                pickle.dump(Moves, MovesFile)
            
            RecordButton.on_click= lambda ClickedEvent: RecordMoves()
            RecordButton.text="Record"

            StopRecordMessage = flet.BottomSheet(
                content=flet.Container(
                    padding=50,
                    content=flet.Text(str([Move for Move in Moves if Move[0]!='Move']))
                ),
            )
            Page.dialog=StopRecordMessage
            StopRecordMessage.open=True
            Page.update()





        def WaitToRepeatMoves():
            global Moves, RepeatMoveEvent
            RepeatMoveEvent=True
            StartButton.on_click= lambda ClickedEvent: StopRepeat()
            StartButton.text="Stop"
            Page.update()

            if os.path.exists(f'{ApplicationPath}/Moves.pkl'):
                with open(f'{ApplicationPath}/Moves.pkl', 'rb') as MovesFile:
                    Moves = pickle.load(MovesFile)
            
            with keyboard.Events() as KeyboardListener:
                for KeyboardEvent in KeyboardListener:
                    if KeyboardEvent.key == keyboard.Key.esc:
                        RepetMovesByTime()
                        break


        def RepetMovesByTime():
            global Mouse, Keyboard

            threading.Thread(target=WaitStopButton).start()

            Mouse = MouseController()
            Keyboard = KeyboardController()
            if RepeatByCountCheckbox.value:
                for Time in range(int(RepeatCountSelect.value)):
                    if RepeatMoveEvent==False:
                        break
                    RepeatMovesGroup()
            else:
                RepeatStart=time.time()
                while time.time() - RepeatStart < int(RepeatSecSelect.value):
                    if RepeatMoveEvent==False:
                        break
                    RepeatMovesGroup()
            
            StopRepeat()



        def RepeatMovesGroup():
            for MoveIndex, Move in enumerate(Moves):
                if RepeatMoveEvent==False:
                    break
                time.sleep(Move[-1] if MoveIndex==0 else Move[-1]-Moves[MoveIndex-1][-1])
                if Move[0]=="Move":
                    Mouse.position = (Move[1], Move[2])
                elif Move[0]=="PressButton":
                    Mouse.position = (Move[1], Move[2])
                    Mouse.press(Move[3])
                elif Move[0]=="ReleaseButton":
                    Mouse.position = (Move[1], Move[2])
                    Mouse.release(Move[3])
                elif Move[0]=="Scroll":
                    Mouse.position = (Move[1], Move[2])
                    Mouse.scroll(Move[3], Move[4])
                elif Move[0]=="PressKey":
                    Keyboard.press(Move[1])
                elif Move[0]=="ReleaseKey":
                    Keyboard.release(Move[1])


        def WaitStopButton():
            with keyboard.Events() as KeyboardListener:
                for KeyboardEvent in KeyboardListener:
                    if RepeatMoveEvent==False:
                        break
                    elif KeyboardEvent.key == keyboard.Key.esc and isinstance(KeyboardEvent, keyboard.Events.Press):
                        StopRepeat()
                        break

        def StopRepeat():
            global RepeatMoveEvent
            RepeatMoveEvent=False
            StartButton.text = "Start"
            StartButton.on_click= lambda ClickedEvent: WaitToRepeatMoves()
            Page.update()


        Page.views.clear()


        RememberClickCheckbox = flet.Checkbox(label="Click", value=True)
        RememberKeyCheckbox = flet.Checkbox(label="Key")

        RepeatByCountCheckbox = flet.Checkbox(label="Count", value=True, on_change=lambda ClickedCheckbox: ToggleActive(RepeatByCountCheckbox, [RepeatByCountCheckbox, RepeatByTimeCheckbox]) )
        RepeatCountSelect = flet.TextField(value='1', hint_text="Count of repeat", suffix_text="times", input_filter=flet.InputFilter('^[0-9]*'), height=45)
        RepeatByTimeCheckbox = flet.Checkbox(label="Time", on_change=lambda ClickedCheckbox: ToggleActive(RepeatByTimeCheckbox, [RepeatByCountCheckbox, RepeatByTimeCheckbox]) )
        RepeatSecSelect = flet.TextField(value='60', hint_text="Sec of repeat", suffix_text="sec", input_filter=flet.InputFilter('^[0-9]*'), height=45, disabled=True)

        ClickRememberResponsiveCheckbox =flet.Checkbox(label="Responsive", value=True, on_change=lambda ClickedCheckbox: ToggleActive(ClickRememberResponsiveCheckbox, [ClickRememberResponsiveCheckbox, ClickRememberNotResponsiveCheckbox]) )
        ClickRememberNotResponsiveCheckbox =flet.Checkbox(label="not Responsive", on_change=lambda ClickedCheckbox: ToggleActive(ClickRememberNotResponsiveCheckbox, [ClickRememberResponsiveCheckbox, ClickRememberNotResponsiveCheckbox]) )

        Interval1Checkbox = flet.Checkbox(label="0.1", value=True, on_change=lambda ClickedCheckbox: ToggleActive(Interval1Checkbox, [Interval1Checkbox, Interval2Checkbox, IntervalOtherCheckbox]) )
        Interval2Checkbox = flet.Checkbox(label="1", on_change=lambda ClickedCheckbox: ToggleActive(Interval2Checkbox, [Interval1Checkbox, Interval2Checkbox, IntervalOtherCheckbox]) )
        IntervalOtherCheckbox = flet.Checkbox(label="Other", on_change=lambda ClickedCheckbox: ToggleActive(IntervalOtherCheckbox, [Interval1Checkbox, Interval2Checkbox, IntervalOtherCheckbox]) )

        ClickTypeLeftCheckbox =flet.Checkbox(label="Left", value=True)
        ClickTypeCenterCheckbox =flet.Checkbox(label="Center", value=True)
        ClickTypeRightCheckbox =flet.Checkbox(label="Right", value=True)
        ClickTypeScrollXCheckbox =flet.Checkbox(label="Scroll X", value=True)
        ClickTypeScrollYCheckbox =flet.Checkbox(label="Scroll Y", value=True)

        StartButton = flet.ElevatedButton(text="Start", width=200, height=50, bgcolor="#dde1e7", on_click=lambda ClickedButton: WaitToRepeatMoves())
        RecordButton = flet.ElevatedButton(text="Record", width=200, height=50, bgcolor="#dde1e7", on_click=lambda ClickedButton: RecordMoves())

        Page.views.append(
            flet.View(
                route='/',
                controls=[
                    flet.Container(flet.Row(controls=[
                                flet.Image(src=f"ClearClickerIcon.png", width=80, height=80, fit=flet.ImageFit.CONTAIN), 
                                flet.Text("ClearClicker", size=36, weight="bold", color="#4f4f51")
                            ], 
                            spacing=10
                        ), 
                        margin=flet.margin.only(left=20)
                    ),
                    flet.Row(
                        controls=[
                            flet.Container(
                                content=flet.Column(controls=[
                                        flet.Container(content=flet.Text("Repeat", size=18, weight="bold", color="4f4f51"), alignment=flet.alignment.center, margin=flet.margin.only(top=8)),
                                        flet.Container(bgcolor="#4f4f51", width=200, height=2),
                                        RepeatByCountCheckbox,
                                        RepeatCountSelect,
                                        RepeatByTimeCheckbox,
                                        RepeatSecSelect
                                    ],
                                    width=200
                                ),
                                width=200,
                                border_radius=flet.border_radius.all(5),
                                border=flet.border.all(3, "#4f4f51"),
                                margin=flet.margin.only(left=30)
                            ),
                            flet.Container(
                                content=flet.Column(controls=[
                                        flet.Container(content=flet.Text("Click remember", size=18, weight="bold", color="4f4f51"), alignment=flet.alignment.center, margin=flet.margin.only(top=8)),
                                        flet.Container(bgcolor="#4f4f51", width=200, height=2),
                                        ClickRememberResponsiveCheckbox,
                                        ClickRememberNotResponsiveCheckbox
                                    ],
                                    width=200
                                ),
                                width=200,
                                border_radius=flet.border_radius.all(5),
                                border=flet.border.all(3, "#4f4f51"),
                                margin=flet.margin.only(left=30)
                            ),
                            flet.Container(
                                content=flet.Column(controls=[
                                        flet.Container(content=flet.Text("Click type", size=18, weight="bold", color="4f4f51"), alignment=flet.alignment.center, margin=flet.margin.only(top=8)),
                                        flet.Container(bgcolor="#4f4f51", width=200, height=2),
                                        ClickTypeLeftCheckbox,
                                        ClickTypeCenterCheckbox,
                                        ClickTypeRightCheckbox,
                                        ClickTypeScrollXCheckbox,
                                        ClickTypeScrollYCheckbox
                                    ],
                                    width=200
                                ),
                                width=200,
                                border_radius=flet.border_radius.all(5),
                                border=flet.border.all(3, "#4f4f51"),
                                margin=flet.margin.only(left=30)
                            )
                        ], 
                        spacing=30,
                        wrap=True,
                        vertical_alignment=flet.CrossAxisAlignment.START
                    ),
                    flet.Container(content=flet.Row(controls=[StartButton, RecordButton], alignment=flet.MainAxisAlignment.CENTER), margin=flet.margin.only(top=20))
                ],
                scroll=flet.ScrollMode.AUTO
            )
        )
 
        PageRoute=Page.route

        Page.update()

    Page.on_route_change = ChangeRoute
    Page.on_view_pop = lambda ViewRouteDeleteEvent: (Page.views.pop(), Page.go(Page.views[-1]['route']))
    Page.go(Page.route)


flet.app(target=AppScreen, assets_dir="Assets")
sys.exit(100)

# flet pack ClearClicker.py --name "ClearClicker" --product-name "ClearClicker" --file-version 1.0  --add-data "Assets:Assets"  

# create-dmg \
#   --volname "ClearClicker" \
#   --window-pos 200 120 \
#   --window-size 600 300 \
#   --icon-size 100 \
#   --icon "ClearClicker.app" 175 120 \
#   --hide-extension "ClearClicker.app" \
#   --app-drop-link 425 120 \
#   "ClearClicker.dmg" \
#   "dmg/"
