import dearpygui.dearpygui as dpg
import demo

dpg.create_context()
dpg.create_viewport(title='The wise window', width=1200, height=1200)

demo.show_demo()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()