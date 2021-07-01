# Thorlabs_ML150M 
### ThorlabsのラボジャッキMLJ150/MをPythonで制御

Thorlab Lab-jack-ML150M control
ラボジャッキの上下移動を制御。

#### 環境

Win10

Python 3.7以上

Anaconda（必須ではない）

#### インストール

https://qiita.com/opto-line/items/68e144b2ee2e5b733f3d

1．MSL-Equipmentのインストール

MLJ150/Mを制御するためのモジュールをインストール。

2．kinesisのインストール

THORLABSのライブラリ群であるkinesisをダウンロード。

ダウンロードしたフォルダがC:/Program Files/Thorlabs/Kinesisにあるか確認。

3．シリアル番号の確認

使用する機器の本体に記載されている8桁のシリアルナンバーを確認。

Python プログラムに記載されているserial=''を使用する機器のシリアルナンバーを入力。

### 制御プログラム

```python
# lab_jack_lib.py
import datetime
import os
import sys
import time 

from msl.equipment import Backend, ConnectionRecord, EquipmentRecord
from msl.equipment.resources.thorlabs import MotionControl

# ensure that the Kinesis folder is available on PATH
os.environ['PATH'] += os.pathsep + 'C:/Program Files/Thorlabs/Kinesis'


# rather than reading the EquipmentRecord from a database we can create it manually
RECORD = EquipmentRecord(
    manufacturer='Thorlabs',
    model='MLJ150/M',  # update the model number for your Integrated Stepper Motor
    serial='XXXXXX',  # update the serial number for your Integrated Stepper Motor
    connection=ConnectionRecord(
        backend=Backend.MSL,
        address='SDK::Thorlabs.MotionControl.IntegratedStepperMotors.dll',),)

# When device position is 30000000, absolute position from home is 25mm
# Update your device
CONVFACTOR = 30000000/25

def abs_to_dev_pos(abs_pos):
    """
    convert absolute position [mm] to device position [dp]
    When device position is 30000000, absolute position from home is 25mm
    factor = 30000000/25
    """
    global CONVFACTOR
    dev_pos = round(abs_pos*CONVFACTOR)
    
    return dev_pos

def dev_to_abs_pos(dev_pos):
    """
    convert device position [dp] to absolute position [mm]
    When device position is 30000000, absolute position from home is 25mm
    factor = 30000000/25
    """
    global CONVFACTOR
    abs_pos = dev_pos*(1/CONVFACTOR)
    
    return abs_pos

def logprint(message=''):
    """
    printing ='on'
    print and return None
    """
    form = '[{}, {}]'.format(datetime.datetime.now(), message)
    print(form)

def jack_status():
    """
    check current position 
    
    """
    global RECORD
    motor = RECORD.connect()
    motor.start_polling(200)
    logprint(f'Current position: {dev_to_abs_pos(motor.get_position())} [mm]')
    logprint(f'Current position: {motor.get_position()} [device units]')
    motor.stop_polling()
    motor.disconnect()

    return motor.get_position(), dev_to_abs_pos(motor.get_position())
    
def jack_move(abs_pos):
    """
    move to absolute position [mm]
    abs_pos: absolute position from home at unit mm.

    """
    global RECORD
    dev_pos = abs_to_dev_pos(abs_pos)
    # connect to the Integrated Stepper Motor
    motor = RECORD.connect()
    logprint('connected is success')
  
    # start polling at 200 ms
    motor.start_polling(200)
    logprint('jack move..')
    # move to position(machine unit)
    logprint(f'Current position: {dev_to_abs_pos(motor.get_position())} [mm]')
    logprint(f'Current position: {motor.get_position()} [device units]')

    motor.move_to_position(dev_pos)

    # position = motor.get_position()
    # real = motor.get_real_value_from_device_unit(position, 'DISTANCE')
    # print('  at position {} [device units] {:.3f} [real-world units]'.format(position, real))
    # wait(1)
    print('Moving jack move done.')

    motor.stop_polling()
    motor.disconnect()

def jack_relative_move(abs_shift):
    """
    abs_shift: absolute shift from current position at unit mm.
    direction toword home is negative
    
    """
    global RECORD
    motor = RECORD.connect()
    current_dev_pos = motor.get_position()
    
    dev_shift= abs_to_dev_pos(abs_shift)

    dev_pos = current_dev_pos + dev_shift

    logprint(f'Current position: {dev_to_abs_pos(motor.get_position())} [mm]')
    logprint(f'Current position: {motor.get_position()} [device units]')
    logprint(f'Shift Value: {dev_shift}[device units]:  Goto {dev_pos}[device units]')


    motor.start_polling(200)
    logprint('move...')
    # move to position(machine unit)
    motor.move_to_position(dev_pos)

    # wait(1)
    print('Moving jack move done.')
   

    motor.stop_polling()
    motor.disconnect()
        

def jack_home():
    """
    Jack home. Jack move to the home position.
    :return:
    """
    global RECORD
    print('[', datetime.datetime.now(), ']', 'homing...')
    # connect to the Integrated Stepper Motor
    motor = RECORD.connect()
    # start polling at 200 ms
    motor.start_polling(200)
    # home the device
    motor.home()

    motor.stop_polling()
    logprint(f'homing done. at position {motor.get_position()} [device units]')
    
    motor.disconnect()


def check_device_info():
    """
    Get device info including serial number.
    :return:
    """
    print('Building the device list...')
    MotionControl.build_device_list()

    n_devices = MotionControl.get_device_list_size()
    if n_devices == 0:
        print('There are no devices in the device list')
        sys.exit(0)
    elif n_devices == 1:
        print('There is 1 device in the device list')
    else:
        print('There are {} devices in the device list'.format(n_devices))

    all_devices = MotionControl.get_device_list()
    print('The serial numbers of all the devices are: {}'.format(all_devices))

    filter_flippers = MotionControl.get_device_list(MotionControl.Filter_Flipper)
    print('The Filter Flipper\'s that are connected are: {}'.format(filter_flippers))

    lts = MotionControl.get_device_list(MotionControl.Long_Travel_Stage)
    print('The Long Travel Stage\'s that are connected are: {}'.format(lts))

    devices = MotionControl.get_device_list(MotionControl.Filter_Flipper, MotionControl.Long_Travel_Stage)
    print('The Filter Flipper\'s and Long Travel Stage\'s that are connected are: {}'.format(devices))

    info = MotionControl.get_device_info(all_devices[0])
    print('The device info for the device with serial# {} is:'.format(all_devices[0]))
    for item in dir(info):
        if item.startswith('_'):
            continue
        print('  {}: {}'.format(item, getattr(info, item)))
    pass


if __name__ == '__main__':
    check_device_info()
    jack_home()
    jack_status()
    jack_move(6.2)
    jack_status()
```



### GUI

pysimpleGUIをインストール。

```python
#anacond
conda install -c conda-forge pysimplegui

# pure python
pip install pysimplegui
```



```python
# lab_jack_gui.py
import datetime
from pathlib import Path
import os

import matplotlib.pyplot as plt
import time

import lab_jack_lib as lj
import PySimpleGUI as sg


def logprint(message=''):
    """
    printing ='on'
    print and return None
    """
    form = '[{}, {}]'.format(datetime.datetime.now(), message)
    print(form)
    
def now_datetime(type=1):
    """
    type1:"%Y-%m-%d %H:%M:%S"
    type2:"%Y%m%d%H%M%S"
    type3:"%Y%m%d_%H%M%S"
    type4:"%Y%m%d%H%M"
    elae: "%Y%m%d"
    """
    now = datetime.datetime.now()
    if type == 1:
        now_string = now.strftime("%Y-%m-%d %H:%M:%S")
    elif type == 2:
        now_string = now.strftime("%Y%m%d%H%M%S")
    elif type == 3:
        now_string = now.strftime("%Y%m%d_%H%M%S")
    elif type == 4:
        now_string = now.strftime("%Y%m%d%H%M")
    elif type == 5:
        now_string = now.strftime("%m%d_%H:%M:%S")
    elif type == 6:
        now_string = now.strftime("%Y%m%d")
    else:
        now_string = now

    return now_string
 

def create_window():
    """create PySimpleGUI Window
    """
    # sg.theme('Light Blue 1')
    sg.theme('Dark Blue 3')
    # sg.theme('Black')

    layout = [
        
        [sg.Text('Current Position [mm]', size=(20, 1)), sg.Text('', 
                                                  font=('Helvetica', 20), size=(10, 1), key='-cpA-')],
        [sg.Text('Current Position [dp]', size=(20, 1)), sg.Text('', 
                                                  font=('Helvetica', 20), size=(10, 1), key='-cpD-')],
        [sg.Button(button_text='Current Positon',size=(7,3),key='-cp-')],
       
        [sg.Button(button_text='Move Abs', key='-absmove-')],
        [sg.Text('Abs Position [mm]', size=(20, 1)), sg.InputText('3', size=(5, 1), key='-abP-')],

        [sg.Button(button_text='Move Shift', key='-shiftmove-')],
        [sg.Text('Shift position [mm]', size=(20, 1)), sg.InputText('1', size=(5, 1), key='-abS-')],
        [sg.Button(button_text='Move Home', key='-homemove-')],
        
        [sg.Button(button_text='Move Up', key='-upmove-')],
        [sg.Text('Abs set upper Position [mm]', size=(22, 1)), sg.InputText('6.22', size=(5, 1), key='-up-')],

        [sg.Button(button_text='Move down', key='-downmove-')],
        [sg.Text('Abs set lower Position [mm]', size=(22, 1)), sg.InputText('3.1', size=(5, 1), key='-low-')],

        [sg.Text('--Exit Close--',font=('Helvetica', 14))],
        [sg.Button(button_text='Exit',key='-cancel-')],

        [sg.Output(size=(50, 10))],
    ]
#location=(Horizontal, vertical )LT:(0,0), LB:(0,1079), RT:(1919,0),RB:(1919,1079)

    return sg.Window('Lab jack Tholabs', layout, location=(900, 50))


def main():

    # make Window
    window = create_window()
    
    
    while True:
        event, values = window.read(timeout=100, timeout_key='-timeout-')

        if event in (None, '-cancel-',):
            logprint('Exit')
            break
        
        elif event in '-cp-':
            dp,ap = lj.jack_status()
           
            window['-cpA-'].update(ap)
            window['-cpD-'].update(dp)
            logprint(ap,dp)

        elif event in '-absmove-':
            abs_pos = float(values['-abP-'])
            lj.jack_move(abs_pos)

            dp,ap = lj.jack_status()
            window['-cpA-'].update(ap)
            window['-cpD-'].update(dp)


        elif event in '-shiftmove-':
            abs_shift = float(values['-abS-'])
            lj.jack_relative_move(abs_shift)

            dp,ap = lj.jack_status()
            window['-cpA-'].update(ap)
            window['-cpD-'].update(dp)

        elif event in '-homemove-':
            lj.jack_home()

            dp,ap = lj.jack_status()
            window['-cpA-'].update(ap)
            window['-cpD-'].update(dp)

        elif event in '-upmove-':
            abs_pos_up = float(values['-up-'])
            lj.jack_move(abs_pos_up)

            dp,ap = lj.jack_status()
            window['-cpA-'].update(ap)
            window['-cpD-'].update(dp)

        elif event in '-downmove-':
            abs_pos_low = float(values['-low-'])
            lj.jack_move(abs_pos_low)

            dp,ap = lj.jack_status()
            window['-cpA-'].update(ap)
            window['-cpD-'].update(dp)

        elif event in '-timeout-':
            pass
        	# dp,ap = lj.jack_status()
            # window['-cpA-'].update(ap)
            # window['-cpD-'].update(dp)

    window.close()

if __name__ == '__main__':
    main()

```


