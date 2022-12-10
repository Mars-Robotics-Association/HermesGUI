import io
import dearpygui.dearpygui as dpg
from math import radians
from PIL import Image
import numpy as np
import cv2 as opencv
import base64
from io import BytesIO
import colorsys

open = False

basicBackground = Image.open(r"480_270_BG.png").convert("RGBA")
basicBackground = basicBackground.resize((480,270))
streamNotFoundBackground = Image.open(r"no_data.png").convert("RGBA")
streamNotFoundBackground = streamNotFoundBackground.resize((480,270))

rgb_mins = [0,0,0]
rgb_maxes = [150,150,150]

def convert_image_to_array(image):
    data = np.asfarray(image, dtype='f')  # change data type to 32bit floats
    return np.true_divide(data, 255.0)  # normalize image data to prepare for GPU

def update_gui(base64_image):
    #set default image to stream not found
    img = streamNotFoundBackground
    if(base64_image == ""):
        #converts image to array for proccessing
        dpg.set_value("raw_footage", convert_image_to_array(img)) # update texture
    else:
        #decode and resize the image
        img_bytes = base64.b64decode(base64_image)   # img_bytes is a binary image
        img_file = BytesIO(img_bytes)  # convert image to file-like object
        img = Image.open(img_file)   # img is now PIL Image object
        img = img.resize((480,270))
        dpg.set_value('raw_footage', convert_image_to_array(img)) # update raw footage window
    
    #open cv proccessing
    img_rgb = opencv.cvtColor(np.array(img), opencv.COLOR_RGB2BGR)
    img_hsv = opencv.cvtColor(img_rgb, opencv.COLOR_BGR2HSV)
    hsv_color1 = np.asarray(colorsys.rgb_to_hsv(rgb_mins[0], rgb_mins[1], rgb_mins[2]))*255
    hsv_color2 = np.asarray(colorsys.rgb_to_hsv(rgb_maxes[0], rgb_maxes[1], rgb_maxes[2]))*255
    #print("Colors between ", hsv_color1, " and ", hsv_color2)
    #creates mask of all pixels in given range and applies it
    mask = opencv.inRange(img_hsv, hsv_color1, hsv_color2)
    masked = opencv.bitwise_and(img_rgb,img_rgb,mask = mask)
    opencv.imwrite("_filtered_img.png", masked)
    img_editied = Image.open(r"_filtered_img.png").convert("RGBA")

    dpg.set_value('edited_footage', convert_image_to_array(img_editied)) # update editied footage window



#initializes all the textures and images it needs
def initialize_textures():
    def loadImage(filename, setTag):
        width, height, channels, data = dpg.load_image(filename)
        with dpg.texture_registry(show=False):
            dpg.add_dynamic_texture(width=width, height=height, default_value=data, tag=setTag)
    loadImage("480_270_BG.png", "raw_footage")
    loadImage("no_data.png", "edited_footage")

def _color_changed(sender, app_data):
    global rgb_mins, rgb_maxes
    if(sender=='color_picker_1'):
        rgb_mins = app_data
        #print("Color Changer 1", rgb_mins)
    if(sender=='color_picker_2'):
        rgb_maxes = app_data
        #print("Color Changer 2", rgb_mins)

def create():
    initialize_textures()

    with dpg.drawlist(label="OpenCV GUI", width=500, height=550, tag="open_cv_drawing"):
        dpg.draw_image('raw_footage', [0,0], [480,270], tag="raw_footage_window")
        dpg.draw_image('edited_footage', [0,280], [480,270+280], tag="edited_footage_window")
    with dpg.group(label="Settings", horizontal=True):
        dpg.add_color_picker((0, 0, 0, 255), label="Min Color", 
            width=200, callback=_color_changed, tag='color_picker_1')
        dpg.add_color_picker((255, 255, 255, 255), label="Max Color", 
            width=200, callback=_color_changed, tag='color_picker_2')

    global open
    open = True

def close():
    global open
    open = False
