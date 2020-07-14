import time
import epics

acq = epics.PV('XF:17IDB-ES:AMX{Cam:14}cam1:Acquire')
img_mode = epics.PV('XF:17IDB-ES:AMX{Cam:14}cam1:ImageMode')
data_type = epics.PV('XF:17IDB-ES:AMX{Cam:14}cam1:DataType')
save_file = epics.PV('XF:17IDB-ES:AMX{Cam:14}JPEG1:WriteFile')

position_goal = epics.PV('XF:17IDB-ES:AMX{Dew:1-Ax:R}Mtr.VAL').get()


class plate_check:
    def __init__(self, plate, degree):
        self.plate = plate
        self.degree = degree


class Watcher:
    def __init__(self, value):
        self.variable = value

    def set_value(self, new_value):
        if self.variable != new_value:
            self.pre_change()
            self.variable = new_value
            self.post_change()

    def pre_change(self):
        # A one and a half minute buffer to allow the robot to rotate
        plates = (plate_check(1, 180),
                  plate_check(2, 135),
                  plate_check(3, 90),
                  plate_check(4, 45),
                  plate_check(5, 0),
                  plate_check(6, 315),
                  plate_check(7, 270),
                  plate_check(8, 225))
        holder = 0
        for plate in plates:
            if (epics.PV('XF:17IDB-ES:AMX{Dew:1-Ax:R}Mtr.VAL').get() + 135) == plate.degree or (epics.PV('XF:17IDB-ES:AMX{Dew:1-Ax:R}Mtr.VAL').get() - 225) == plate.degree:
                holder = plate.plate
        if epics.PV('XF:17IDB-ES:AMX{Wago:1}Puck' + str(holder) + 'C-Sts').get() == 1:
            puck_present = True
        else:
            puck_present = False
        time.sleep(90)
        if puck_present:
            for i in range(1, 11):
                print('Taking image: ' + str(i) + ' of 10')
                fill_level = epics.PV('XF:17IDB-ES:AMX{CS8}Ln2Level-I').get()
                if fill_level >= 85:
                    # Change the settings to take the picture and capture the image
                    acq.put(0)
                    img_mode.put(0)
                    data_type.put(0)
                    time.sleep(2)
                    acq.put(1)
                    time.sleep(2)
                    save_file.put(1)

                    # Put the camera back to the original settings
                    time.sleep(2)
                    img_mode.put(2)
                    data_type.put(1)
                    acq.put(1)

                    # A one minute wait to allow conditions to change
                    time.sleep(60)
        self.post_change()

    def post_change(self):
        # Ensure the camera is returned to its normal status
        time.sleep(2)
        img_mode.put(2)
        data_type.put(1)
        acq.put(1)
        check_for_change(epics.PV('XF:17IDB-ES:AMX{Dew:1-Ax:R}Mtr.VAL').get())


def check_for_change(goal):
    while True:
        time.sleep(5)
        Watcher(goal).set_value(
            epics.PV('XF:17IDB-ES:AMX{Dew:1-Ax:R}Mtr.VAL').get())


check_for_change(position_goal)
