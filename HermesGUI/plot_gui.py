import dearpygui.dearpygui as dpg
from math import sin, cos
import time

open = False

dpg.create_context()

#data arrays
botTargYs = []
botTargXs = []
botTargAs = []
botActualXs = []
botActualYs = []
botActualAs = []
botErrorXs = []
botErrorYs = []
botErrorAs = []
times = []
startTime = time.time()
pauseTime = 0
#booleans for whether to show data
showTargets = True
showActuals = True
showErrors = True
pausePlot = False

#function for toggle button callbacks
def _button_callback(sender, app_data):
    if(sender=='show_targets'):
        global showTargets 
        showTargets = app_data
        print("showTargets", app_data)
    if(sender=='show_actuals'):
        global showActuals 
        showActuals = app_data
        print("showActuals", app_data)
    if(sender=='show_errors'):
        global showErrors 
        showErrors = app_data
        print("showErrors", app_data)

#pause sending data
def _pause_plot(sender, app_data):
    global pausePlot
    pausePlot = not pausePlot

#reset the plot
def _clear_plot(sender, app_data):
    botTargXs.clear()
    botTargYs.clear()
    botTargAs.clear()
    botActualXs.clear()
    botActualYs.clear()
    botActualAs.clear()
    botErrorXs.clear()
    botErrorYs.clear()
    botErrorAs.clear()
    times.clear()
    global startTime
    startTime = time.time()
    global pauseTime
    pauseTime = 0
    _update_plots(0,0,0,0,0,0)


#call to update all the plots
def _update_plots(targetX, targetY, targetA, actualX, actualY, actualA):
    if(pausePlot):
        return
    #update arrays
    botTargXs.append(targetX)
    botTargYs.append(targetY)
    botTargAs.append(targetA)
    botActualXs.append(actualX)
    botActualYs.append(actualY)
    botActualAs.append(actualA)
    botErrorXs.append(actualX-targetX)
    botErrorYs.append(actualY-targetY)
    botErrorAs.append(actualA-targetA)
    times.append(time.time()-startTime-pauseTime)

    #update text
    dpg.set_value('measured_x_text', "Measured X: " + str("%.1f" % actualX))
    dpg.set_value('measured_y_text', "Measured Y: " + str("%.1f" % actualY))
    dpg.set_value('measured_a_text', "Measured Angle: " + str("%.1f" % actualA))
    dpg.set_value('target_x_text', "Target X: " + str("%.1f" % targetX))
    dpg.set_value('target_y_text', "Target Y: " + str("%.1f" % targetY))
    dpg.set_value('target_a_text', "Target Angle: " + str("%.1f" % targetA))

    #apply to graphs, send no data if not to be shown
    if(showTargets):
        dpg.set_value('targ_x_plot', [times, botTargXs])
        dpg.set_value('targ_y_plot', [times, botTargYs])
        dpg.set_value('targ_a_plot', [times, botTargAs])
    else:
        dpg.set_value('targ_x_plot', [[], []])
        dpg.set_value('targ_y_plot', [[], []])
        dpg.set_value('targ_a_plot', [[], []])
        print("hiding targets")
    if(showActuals):
        dpg.set_value('actual_x_plot', [times, botActualXs])
        dpg.set_value('actual_y_plot', [times, botActualYs])
        dpg.set_value('actual_a_plot', [times, botActualAs])
    else:
        dpg.set_value('actual_x_plot', [[], []])
        dpg.set_value('actual_y_plot', [[], []])
        dpg.set_value('actual_a_plot', [[], []])
    if(showErrors):
        dpg.set_value('error_x_plot', [times, botErrorXs])
        dpg.set_value('error_y_plot', [times, botErrorYs])
        dpg.set_value('error_a_plot', [times, botErrorAs])
    else:
        dpg.set_value('error_x_plot', [[], []])
        dpg.set_value('error_y_plot', [[], []])
        dpg.set_value('error_a_plot', [[], []])

    dpg.set_axis_limits("position_axis", -80, 80)
    dpg.set_axis_limits("degrees_axis", -200, 200)

#initializes all the textures and images it needs
def initialize_textures():
    def loadImage(filename, setTag):
        width, height, channels, data = dpg.load_image(filename)

        with dpg.texture_registry(show=False):
            dpg.add_static_texture(width=width, height=height, default_value=data, tag=setTag)

    loadImage("data_logging_banner.png", "data_logging_banner")

#create the UI
def create():
    initialize_textures()
    #logo and about
    with dpg.group(label="About", horizontal=True):
        dpg.add_image("data_logging_banner", width=450, height=75)

    #plot options group
    with dpg.group(label="Plot Options", horizontal=True):
        #checkboxes for turning lines on and off
        dpg.add_checkbox(label="show targets", callback=_button_callback, tag='show_targets', default_value=True)
        dpg.add_checkbox(label="show actuals", callback=_button_callback, tag='show_actuals', default_value=True)
        dpg.add_checkbox(label="show errors", callback=_button_callback, tag='show_errors', default_value=True)
        #button for fitting x axis
        dpg.add_button(label="fit X-axis", callback=lambda: dpg.fit_axis_data('time_axis'))

    #plot the data
    with dpg.plot(label="Multi Axes Plot", height=400, width=-1):
        dpg.add_plot_legend()

        # create x axis
        dpg.add_plot_axis(dpg.mvXAxis, label="time (s)", tag="time_axis")

        # create position y axis
        dpg.add_plot_axis(dpg.mvYAxis, label="position (inches)", tag="position_axis")
        dpg.add_line_series([], times, label="X | target", parent='position_axis', tag="targ_x_plot")
        dpg.add_line_series(botActualXs, times, label="X | measured", parent='position_axis', tag="actual_x_plot")
        dpg.add_line_series(botActualYs, times, label="X | error", parent='position_axis', tag="error_x_plot")
        dpg.add_line_series(botTargYs, times, label="Y | target", parent='position_axis', tag="targ_y_plot")
        dpg.add_line_series(botActualYs, times, label="Y | measured", parent='position_axis', tag="actual_y_plot")
        dpg.add_line_series(botActualYs, times, label="Y | error", parent='position_axis', tag="error_y_plot")

        # create degrees y axis
        dpg.add_plot_axis(dpg.mvYAxis, label="degrees", tag="degrees_axis")
        dpg.add_line_series(botTargAs, times, label="Angle | target", parent='degrees_axis', tag="targ_a_plot")
        dpg.add_line_series(botActualAs, times, label="Angle | measured", parent='degrees_axis', tag="actual_a_plot")
        dpg.add_line_series(botActualYs, times, label="Angle | error", parent='degrees_axis', tag="error_a_plot")

    with dpg.group(label="Data", horizontal=True):
        dpg.add_text("Measured X: ", tag='measured_x_text')
        dpg.add_text("Measured Y: ", tag='measured_y_text')
        dpg.add_text("Measured A: ", tag='measured_a_text')
        dpg.add_text("Target X: ", tag='target_x_text')
        dpg.add_text("Target Y: ", tag='target_y_text')
        dpg.add_text("Target A: ", tag='target_a_text')
    
    # create the pause button
    with dpg.theme() as item_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (50,200,75))
            dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0))
    dpg.add_button(label="PAUSE / PLAY", callback=_pause_plot, height=50, width=-1, tag="pause_plot")
    dpg.bind_item_theme(dpg.last_item(), item_theme)

    # create the reset button
    with dpg.theme() as item_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (200,50,75))
            dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0))
    dpg.add_button(label="RESET", callback=_clear_plot, height=50, width=-1, tag="reset_plot")
    dpg.bind_item_theme(dpg.last_item(), item_theme)

    global open
    open = True


def update_plot(targX,targY,targA,actualX,actualY,actualA):
    #if paused, add to pause time
    if(pausePlot):
        global pauseTime
        pauseTime += dpg.get_delta_time()

    _update_plots(targX,targY,targA,actualX,actualY,actualA)

def close():
    global open
    open = False