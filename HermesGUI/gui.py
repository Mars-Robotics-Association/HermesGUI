from math import sin, cos, degrees, radians
import time
import dearpygui.dearpygui as dpg
import json
import websocket
from websocket import create_connection
import threading
import plot_gui as plotGUI
import nav_gui as navGUI
import open_cv_gui as openCVGUI
import base64

targetX = 0
targetY = 0
targetA = 0
actualX = 0
actualY = 0
actualA = 0
rawWebcamBase64 = ""
previousrawWebcamBase64 = ""

#WEBSOCKET CALLBACKS
# Define WebSocket callback functions
def ws_message(ws, message):
    data = json.loads(message)
    global targetX, targetY, targetA, actualX, actualY, actualA, rawWebcamBase64, previousrawWebcamBase64
    targetX = data['tx']
    targetY = data['ty']
    targetA = data['th']
    actualX = data['ax']
    actualY = data['ay']
    actualA = data['ah']
    rawWebcamBase64 = data['image']
    print("target x ", data['tx'], " target y ", data['ty'], " target a ", data['th'])
    print("actual x ", data['ax'], " actual y ", data['ay'], " actual a ", data['ah'])
    if(previousrawWebcamBase64==""):
        print("START", rawWebcamBase64, "STOP")
    previousrawWebcamBase64 = rawWebcamBase64

    ws.keep_running = True

def ws_error(ws, error):
    print(error)

def ws_close(ws, close_status_code, close_msg):
    print("### closed ###")

def ws_open(ws):
    print("websocket opened")

host = "ws://192.168.43.1:8001"
ws = websocket.WebSocketApp(host,
                            on_open= ws_open,
                            on_message=ws_message,
                            on_error=ws_error,
                            on_close=ws_close)
#connects the websocket
def start_websocket():    
    websocket.enableTrace(True)
    ws.run_forever(reconnect=0.5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    


thread = threading.Thread(None,start_websocket)
thread.start()
dpg.create_context()

#create menu bar at top of window
def create_menu_bar():
    with dpg.menu_bar():
        with dpg.menu(label="Tools"): #some tools dearpy provides
                dpg.add_menu_item(label="Show About", callback=lambda:dpg.show_tool(dpg.mvTool_About))
                dpg.add_menu_item(label="Show Metrics", callback=lambda:dpg.show_tool(dpg.mvTool_Metrics))
                dpg.add_menu_item(label="Show Documentation", callback=lambda:dpg.show_tool(dpg.mvTool_Doc))
                dpg.add_menu_item(label="Show Debug", callback=lambda:dpg.show_tool(dpg.mvTool_Debug))
                dpg.add_menu_item(label="Show Style Editor", callback=lambda:dpg.show_tool(dpg.mvTool_Style))
                dpg.add_menu_item(label="Show Font Manager", callback=lambda:dpg.show_tool(dpg.mvTool_Font))
                dpg.add_menu_item(label="Show Item Registry", callback=lambda:dpg.show_tool(dpg.mvTool_ItemRegistry))

        with dpg.menu(label="Settings"): #some basic settings
            dpg.add_menu_item(label="Wait For Input", check=True, callback=lambda s, a: dpg.configure_app(wait_for_input=a))
            dpg.add_menu_item(label="Toggle Fullscreen", callback=lambda:dpg.toggle_viewport_fullscreen())

#sets up theme colors and styles
def setup_theme():
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0), category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (25,175,50), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, (25,175,50), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (50,200,75), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (50,200,75), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (50,200,75), category=dpg.mvThemeCat_Core)
    dpg.bind_theme(global_theme)

#puts angle within good range for robot
def fix_angle(angle):
    while(angle>180):
        angle -= 360
    while(angle<=-180):
        angle += 360
    return angle

def _on_DPG_close(sender, app_data, user_data):
    ws.close()

#callbacks for launcher buttons
def _launch_module(sender, app_data):
    if(sender=='launch_field_map'):
        with dpg.window(label="FIELD MAP", width=850, height=900, pos=(0, 0), tag="field_map_window", on_close=_close_module):
            navGUI.create()
    if(sender=='data_plots'):
        with dpg.window(label="DATA PLOTS", width=800, height=1000, pos=(850, 0), tag="data_plot_window", on_close=_close_module):
            plotGUI.create()
    if(sender=='open_cv'):
        with dpg.window(label="OPEN CV", width=500, height=900, pos=(0, 0), tag="open_cv_window", on_close=_close_module):
            openCVGUI.create()

def _close_module(sender, app_data):
    if(sender=='field_map_window'):
        navGUI.close()
    if(sender=='data_plot_window'):
        plotGUI.close()
    if(sender=='open_cv_window'):
        openCVGUI.close()


# CODE TO RUN ON START
setup_theme()
# create menu of all the different available windows
with dpg.window(label="MODULE MANAGER", width=300, height=400, pos=(0, 0)):
    create_menu_bar()
    with dpg.group(label="modules"):
        dpg.add_button(label="Launch Field Map", tag="launch_field_map", callback=_launch_module)
        dpg.add_button(label="Launch Data Plots", tag="data_plots", callback=_launch_module)
        dpg.add_button(label="Launch OpenCV", tag="open_cv", callback=_launch_module)


dpg.create_viewport(title='MRA GUI', width=1000, height=1000)
dpg.setup_dearpygui()
dpg.show_viewport()

# CODE TO RUN ON LOOP
while dpg.is_dearpygui_running():
    # insert here any code you would like to run in the render loop
    # you can manually stop by using stop_dearpygui()
    runtime = time.time()-plotGUI.startTime
    #dummy values
    dum_targetX = ((sin(time.time())*0.5))*72
    dum_targetY = (cos(time.time()))*72
    dum_targetA = fix_angle(runtime * 45)
    dum_actualX = (((sin(time.time())*0.5))*72)+2
    dum_actualY = ((cos(time.time()))*72)+2
    dum_actualA = fix_angle(runtime * 45)

    if(navGUI.open):
        #navGUI.setRobotPosition(dum_targetX,dum_targetY,dum_targetA,dum_actualX,dum_actualY,dum_actualA)
        navGUI.setRobotPosition(targetX,targetY,degrees(targetA),actualX,actualY,degrees(actualA))
    if(plotGUI.open):
        #plotGUI.update_plot(dum_targetX,dum_targetY,dum_targetA,dum_actualX,dum_actualY,dum_actualA)
        plotGUI.update_plot(targetX,targetY,degrees(targetA),actualX,actualY,degrees(actualA))
    if(openCVGUI.open):
        # with open("field_map_banner.png", "rb") as img_file:
        #     b64_test = base64.b64encode(img_file.read())
        openCVGUI.update_gui(rawWebcamBase64)

    

    dpg.render_dearpygui_frame()

# SHUT EVERYTHING DOWN
dpg.destroy_context()
ws.close()
ws.keep_running=False