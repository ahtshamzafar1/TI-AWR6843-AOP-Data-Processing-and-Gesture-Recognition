import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import juggle_axes
from radar import TI
import numpy as np
import matplotlib.pyplot as plt
import os
import cv2
MAGIC_WORD = b'\x02\x01\x04\x03\x06\x05\x08\x07'

def normalize(data):
    data=(data-np.min(data))/(np.max(data)-np.min(data))
    return data


FLOOR = -10
CEILING = 10


class Detected_Points:

    def data_stream_iterator(self, cli_loc='COM4', data_loc='COM5', total_frames=300):

        MAGIC_WORD = b'\x02\x01\x04\x03\x06\x05\x08\x07'
        ti = TI(cli_loc=cli_loc, data_loc=data_loc)
        nframe = 0
        interval = 0.05
        data = b''
        warn = 0
        while nframe < total_frames:

            time.sleep(interval)
            byte_buffer = ti._read_buffer()

            if (len(byte_buffer) == 0):
                warn += 1
            else:
                warn = 0
            if (warn > 10):  # 连续10次空读取则退出
                print("Wrong")
                break

            data += byte_buffer

            try:
                idx1 = data.index(MAGIC_WORD)
                idx2 = data.index(MAGIC_WORD, idx1 + 1)

            except:
                continue

            datatmp = data[idx1:idx2]
            data = data[idx2:]
            points = ti._process_detected_points(byte_buffer)
            ret = points[:, :3]

            yield ret
            nframe += 1

        ti.close()





ti=TI()
def capture(total_frames):
    nerror=0
    nframe=0
    interval=0.1
    data=b''
    warn=0
    rawimg=np.zeros((total_frames,12,256,2))
    plt.ion()
    start=time.time()
    while nframe<total_frames:
        print(nframe)
        time.sleep(interval)
        byte_buffer=ti._read_buffer()
        if(len(byte_buffer)==0):
            warn+=1
        else:
            warn=0
        if(warn>2):
            print("Wrong")
            break

        data+=byte_buffer


        try:
            idx1 = data.index(MAGIC_WORD)

            idx2=data.index(MAGIC_WORD,idx1+1)

        except:
            continue

        datatmp=data[idx1:idx2]
        data=data[idx2:]
        try:
            cube=doneRawfft(datatmp)
            draw_heatmap(cube)
            rawimg[nframe]=cube
            nframe+=1
        except:
            continue

    ti.close()
    print("rate=",total_frames/(time.time()-start))




def draw_heatmap(cube,HorV='H'):

    plt.ion()  
    fft_data=cube[:,:,1]+cube[:,:,0]*1j

    img=np.zeros((fft_data.shape[1],fft_data.shape[1]),dtype=complex)
    if HorV=='H':
        data=fft_data[[10,8,6,4]]
    elif HorV=='V':
        data=fft_data[[1,0,6,5]]
    img[:,0:4]=data.T



    doppler_fft = np.abs(np.fft.fft(fft_data, axis=0))
    doppler = np.fft.fftshift(doppler_fft, axes=0)
    plt.clf()
    plt.imshow(doppler, cmap=plt.get_cmap('seismic'))  
    plt.pause(0.01)





def doneRawfft(byte_buffer):

    cube=ti._process(byte_buffer)   
    return cube

#a = AnimatedScatter()
#a.show()
Detected_Points()
capture(30000)