#! /usr/bin/python3
import time,board,busio
from pushbullet import Pushbullet
import numpy as np
import adafruit_mlx90640
import matplotlib.pyplot as plt
from scipy import ndimage
import argparse
pb = Pushbullet("o.h5n1DNMmwsjMJ3v5OJeCHgh6bFsTe9J0")
print(pb.devices)

# define range
human_min = 31
human_max = 43
fever_min = 37.5
drone_min = 44
drone_max = 100
#fire temp ranges from 200 to 1650 C
human = 0
fever = 0
drone = 0
fire = 0
count = 0
parser = argparse.ArgumentParser(description='Thermal Camera Program')
parser.add_argument('--mirror', dest='imageMirror', action='store_const', default='false',
                    const='imageMirror', help='Flip the image for selfie (default: false)')
args = parser.parse_args()
imageMirror = args.imageMirror

if(imageMirror == 'false'):
    print('Mirror mode: false')
else:
    imageMirror = 'true'
    print('Mirror mode: true')

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000) # setup I2C
mlx = adafruit_mlx90640.MLX90640(i2c) # begin MLX90640 with I2C comm
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ # set refresh rate
mlx_shape = (24,32) # mlx90640 shape

mlx_interp_val = 10 # interpolate # on each dimension
mlx_interp_shape = (mlx_shape[0]*mlx_interp_val,
                    mlx_shape[1]*mlx_interp_val) # new shape

fig = plt.figure(figsize=(12,9)) # start figure
ax = fig.add_subplot(111) # add subplot
fig.subplots_adjust(0.05,0.05,0.95,0.95) # get rid of unnecessary padding
therm1 = ax.imshow(np.zeros(mlx_interp_shape),interpolation='none',
                   cmap=plt.cm.bwr,vmin=25,vmax=45) # preemptive image
cbar = fig.colorbar(therm1) # setup colorbar
cbar.set_label('Temperature [$^{\circ}$C]',fontsize=14) # colorbar label

fig.canvas.draw() # draw figure to copy background
ax_background = fig.canvas.copy_from_bbox(ax.bbox) # copy background
ax.text(-75, 125, 'Max:', color='red')
textMaxValue = ax.text(-75, 150, 'test1', color='black')
fig.show() # show the figure before blitting

frame = np.zeros(mlx_shape[0]*mlx_shape[1]) # 768 pts
def plot_update():
    fig.canvas.restore_region(ax_background) # restore background
    mlx.getFrame(frame) # read mlx90640
    data_array = np.fliplr(np.reshape(frame,mlx_shape)) # reshape, flip data
    if(imageMirror == 'true'):
        data_array = np.flipud(data_array)
    data_array = ndimage.zoom(data_array,mlx_interp_val) # interpolate
    therm1.set_array(data_array) # set data
    therm1.set_clim(vmin=np.min(data_array),vmax=np.max(data_array)) # set bounds
    value = np.max(data_array)
    cbar.on_mappable_changed(therm1) # update colorbar range
    plt.pause(0.001)
    ax.draw_artist(therm1) # draw new thermal image
    textMaxValue.set_text(str(np.round(np.max(data_array), 1)))
    fig.canvas.blit(ax.bbox) # draw background
    fig.canvas.flush_events() # show the new image
    fig.show()
    return value

t_array = []
while True:
    t1 = time.monotonic() # for determining frame rate
    try:
        value = plot_update() # update plot
    except:
        continue
    # approximating frame rate
    t_array.append(time.monotonic()-t1)
    if len(t_array)>10:
        t_array = t_array[1:] # recent times for frame rate approx
    #print('Frame Rate: {0:2.1f}fps'.format(len(t_array)/np.sum(t_array)))
    #to specify what device to output to, insert name of device to be notified and replace later 'pb' with 'dev'
    #dev = pb.get_device('')
    if(value > human_min and value < human_max):
      if(value > fever_min):
        #human with fever
        fever += 1
        print(value)
      else:
        #human
        human += 1
        print(value)
    else:
      human = 0
      fever = 0
      print(value)
    if(value > drone_min and value < drone_max):
      #drone
      drone += 1
      print(value)
    else:
      drone = 0
    if(value > drone_max):
      #possible fire
      fire += 1
      print(value)
    else:
      fire = 0
    if(human == 4):
      #human: alert user
      print('Human detected')
      push = pb.push_note("Alert!","Entryway human detection")
      human = 0
    if(fever == 4):
      #human with fever: alert user
      print('Fever detected')
      push = pb.push_note("Alert!","Entryway fever detection")
      fever = 0
    if(drone == 2):
      #drone detected: alert user
      print('Drone detected')
      push = pb.push_note("Alert!","Entryway drone detection")
      drone = 0    
    if(fire == 4):
      #fire detected: alert user
      print('Fire detected')
      push = pb.push_note("Alert!","Possible fire detection")
      fire = 0    

    if(count == 100):
      human = 0
      fever = 0
      drone = 0
      fire = 0
    count += 1