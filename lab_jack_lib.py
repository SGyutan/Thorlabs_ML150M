"""
ThorlabsのラボジャッキMLJ150/Mを制御するプログラム。
ラボジャッキの上下を行う。使用する前にnoticeを確認してください。
notice:
１．シリアル番号の確認
使用する機器の本体に記載されている8桁のシリアルナンバーを確認し、
21行目に記載されているserial=''を更新してください。
２．MSL-Equipmentのインストール
MLJ150/Mを制御するためのモジュールをインストールしてください。
３．kinesisのインストール
THORLABSのライブラリ群であるkinesisをダウンロードしてください。
ダウンロードしたフォルダがC:/Program Files/Thorlabs/Kinesisにあるか確認してください。

以上の1~3の手順は以下の記事を参照してください。
https://qiita.com/opto-line/items/68e144b2ee2e5b733f3d
"""
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
    serial='49907500',  # update the serial number for your Integrated Stepper Motor
    connection=ConnectionRecord(
        backend=Backend.MSL,
        address='SDK::Thorlabs.MotionControl.IntegratedStepperMotors.dll',),)

# When device position is 30000000, absolute position from home is 25mm
CONVFACTOR = 30000000/25

def abs_to_dev_pos(abs_pos):
    """
    When device position is 30000000, absolute position from home is 25mm
    factor = 30000000/25
    """
    global CONVFACTOR
    dev_pos = round(abs_pos*CONVFACTOR)
    
    return dev_pos

def dev_to_abs_pos(dev_pos):
    """
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
    
    logprint(f'Current position: {dev_to_abs_pos(motor.get_position())} [mm]')
    logprint(f'Current position: {motor.get_position()} [device units]')

    # move to position(machine unit)
    motor.move_to_position(dev_pos)
    print('Moving jack move done.')

    motor.stop_polling()

    # position = motor.get_position()
    # real = motor.get_real_value_from_device_unit(position, 'DISTANCE')
    # print('  at position {} [device units] {:.3f} [real-world units]'.format(position, real))

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


# def _wait(obj):
#     obj.clear_message_queue()
#     while True:
#         status = obj.convert_message(*obj.wait_for_message())['id']
#         if status == 'Homed' or status == 'Moved':
#             break
#         position = obj.get_position()
#         real = obj.get_real_value_from_device_unit(position, 'DISTANCE')
#         print('  at position {} [device units] {:.3f} [real-world units]'.format(position, real))


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
    # jack_home()
    # jack_status()
    # jack_move(6.88)

    # jack_status()
    # jack_relative_move(1)
    # jack_status()
    # jack_move(3.27)
    

        
  
