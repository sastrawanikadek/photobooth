import gphoto2 as gp

camera = gp.Camera()

port_info_list = gp.PortInfoList()
port_info_list.load()

abilities_list = gp.CameraAbilitiesList()
abilities_list.load()

cameras = list(gp.Camera.autodetect())
name, addr = cameras[0]

idx = port_info_list.lookup_path(addr)
camera.set_port_info(port_info_list[idx])

idx = abilities_list.lookup_model(name)
camera.set_abilities(abilities_list[idx])

print(camera.get_summary())

print("================\n")

config = camera.get_config()

print("Text Widget: ", gp.GP_WIDGET_TEXT)
print("Range Widget: ", gp.GP_WIDGET_RANGE)
print("Toggle Widget: ", gp.GP_WIDGET_TOGGLE)
print("Radio Widget: ", gp.GP_WIDGET_RADIO)
print("Menu Widget: ", gp.GP_WIDGET_MENU)
print("Date Widget: ", gp.GP_WIDGET_DATE)
print("Button Widget: ", gp.GP_WIDGET_BUTTON)
print("Section Widget: ", gp.GP_WIDGET_SECTION)
print("Window Widget: ", gp.GP_WIDGET_WINDOW)
print()

for child in config.get_children():
    print(child.get_name(), child.get_type())

    if child.get_type() == gp.GP_WIDGET_SECTION:
        for subchild in child.get_children():
            print("\t", subchild.get_name(), subchild.get_type())

while True:
    capture = camera.capture_preview()
    print(capture)
