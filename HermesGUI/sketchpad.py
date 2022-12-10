import numpy as np
import colorsys

rgb_maxes = [150,50,150]

hsv_color2 = np.asarray(colorsys.rgb_to_hsv(rgb_maxes[0], rgb_maxes[1], rgb_maxes[2])) 
print(hsv_color2)