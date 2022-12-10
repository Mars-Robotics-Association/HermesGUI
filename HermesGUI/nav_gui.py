import dearpygui.dearpygui as dpg
from math import radians
from PIL import Image
import numpy as np

open = False

#load robot image for rotating it
robotActualImg = Image.open(r"robot_actual_padded.png").convert("RGBA")
robotTargetImg = Image.open(r"robot_target_padded.png").convert("RGBA")
#rotates the robot to given angle
def set_rotation(img, tag, angle):
    data = np.asfarray(img.rotate(angle), dtype='f')  # change data type to 32bit floats
    texture_data = np.true_divide(data, 255.0)  # normalize image data to prepare for GPU
    dpg.set_value(tag, texture_data) # update texture

#initializes all the textures and images it needs
def initialize_textures():
    def loadImage(filename, setTag):
        width, height, channels, data = dpg.load_image(filename)

        with dpg.texture_registry(show=False):
            dpg.add_dynamic_texture(width=width, height=height, default_value=data, tag=setTag)

    loadImage("2022-23 cropped.png", "field_image")
    loadImage("field_map_banner.png", "field_banner")
    loadImage("robot_actual_padded.png", "robot_actual_image")
    loadImage("robot_target_padded.png", "robot_target_image")

def setRobotPosition(target_x,target_y,target_a,actual_x,actual_y,actual_a):
    #move and rotate robot images
    dpg.apply_transform('robot_actual', dpg.create_translation_matrix([(5*actual_y)+360,actual_x+360]))#
    set_rotation(robotActualImg, "robot_actual_image", actual_a)
    dpg.apply_transform('robot_target', dpg.create_translation_matrix([(5*target_y)+360,target_x+360]))#
    set_rotation(robotTargetImg, "robot_target_image", target_a)
    #move velocity lines
    act_vel_x = 60
    act_vel_y = 60
    dpg.apply_transform('robot_actual_velocity', dpg.create_rotation_matrix(radians(actual_a),[0,0,1]))


def create():
    initialize_textures()
    #logo and about
    with dpg.group(label="About", horizontal=True):
        dpg.add_image("field_banner", width=450, height=75)

    with dpg.drawlist(label="Field Map", width=720, height=720, tag="field_map_drawing"):
        dpg.draw_image('field_image', [0,0], [720,720])
        #draw robot target icon
        with dpg.draw_node(tag="robot_target"):
            dpg.draw_image('robot_target_image', [-45,-45], [45,45])
            dpg.draw_circle([0,0],50)
            #dpg.draw_line([0,0],[0,-50], color=(200,50,75), tag="robot_target_velocity")
        #draw robot actual icon
        with dpg.draw_node(tag="robot_actual"):
            dpg.draw_image('robot_actual_image', [-45,-45], [45,45])
            dpg.draw_circle([0,0],50)
            #draw robot actual velocity line
            with dpg.draw_node(tag="robot_actual_velocity"):
                dpg.draw_line([0,0],[0,50], color=(200,50,75))

    global open
    open = True
        
def close():
    global open
    open = False