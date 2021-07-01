"""
Lab jack GUI
"""

import datetime
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

    :return: string date 
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
    """create PySimpleGUI window
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
        
        # UP : Current position: 6.886823333333333 [mm], 8264188 [device units]
        # down : Current position: 3.2741558333333334 [mm], 3928987 [device units]
        [sg.Button(button_text='Move Up', key='-upmove-')],
        [sg.Text('Abs set upper Position [mm]', size=(22, 1)), sg.InputText('6.88', size=(5, 1), key='-up-')],

        [sg.Button(button_text='Move down', key='-downmove-')],
        [sg.Text('Abs set lower Position [mm]', size=(22, 1)), sg.InputText('3.27', size=(5, 1), key='-low-')],

        [sg.Text('--Exit Close--',font=('Helvetica', 14))],
        [sg.Button(button_text='Exit',key='-cancel-')],

        [sg.Output(size=(50, 10))],
    ]
    
    # location=(lorizontal, vertical)LT:(0,0), LB:(0,1079), RT:(1919,0),RB:(1919,1079)
    return sg.Window('Lab jack Tholabs', layout, location=(900, 50))

def main():
   
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
