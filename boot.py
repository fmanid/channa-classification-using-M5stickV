import audio
import gc
import image
import lcd
import sensor
import time
import uos
import KPU as kpu
from fpioa_manager import *
from machine import I2C
from Maix import I2S, GPIO

#
# initialize
#
lcd.init()
lcd.rotation(2)
i2c = I2C(I2C.I2C0, freq=400000, scl=28, sda=29)

fm.register(board_info.SPK_SD, fm.fpioa.GPIO0)
spk_sd=GPIO(GPIO.GPIO0, GPIO.OUT)
spk_sd.value(1) #Enable the SPK output

fm.register(board_info.SPK_DIN,fm.fpioa.I2S0_OUT_D1)
fm.register(board_info.SPK_BCLK,fm.fpioa.I2S0_SCLK)
fm.register(board_info.SPK_LRCLK,fm.fpioa.I2S0_WS)

wav_dev = I2S(I2S.DEVICE_0)

fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

fm.register(board_info.BUTTON_B, fm.fpioa.GPIO2)
but_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

fm.register(board_info.LED_W, fm.fpioa.GPIO3)
led_w = GPIO(GPIO.GPIO3, GPIO.OUT)
led_w.value(1) #RGBW LEDs are Active Low

fm.register(board_info.LED_R, fm.fpioa.GPIO4)
led_r = GPIO(GPIO.GPIO4, GPIO.OUT)
led_r.value(1) #RGBW LEDs are Active Low

fm.register(board_info.LED_G, fm.fpioa.GPIO5)
led_g = GPIO(GPIO.GPIO5, GPIO.OUT)
led_g.value(1) #RGBW LEDs are Active Low

fm.register(board_info.LED_B, fm.fpioa.GPIO6)
led_b = GPIO(GPIO.GPIO6, GPIO.OUT)
led_b.value(1) #RGBW LEDs are Active Low



def play_sound(filename):
    try:
        player = audio.Audio(path = filename)
        player.volume(40)
        wav_info = player.play_process(wav_dev)
        wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT, align_mode = I2S.STANDARD_MODE)
        wav_dev.set_sample_rate(wav_info[1])
        while True:
            ret = player.play()
            if ret == None:
                break
            elif ret==0:
                break
        player.finish()
    except:
        pass

def set_backlight(level):
    if level > 8:
        level = 8
    if level < 0:
        level = 0
    val = (level+7) << 4
    i2c.writeto_mem(0x34, 0x91,int(val))

def show_logo():
    try:
        img = image.Image("/sd/logo.jpg")
        set_backlight(0)
        lcd.display(img)
        for i in range(9):
            set_backlight(i)
            time.sleep(0.1)
        play_sound("/sd/logo.wav")

    except:
        lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, "Error: Cannot find logo.jpg", lcd.WHITE, lcd.RED)

def initialize_camera():
    err_counter = 0
    while 1:
        try:
            sensor.reset() #Reset sensor may failed, let's try some times
            break
        except:
            err_counter = err_counter + 1
            if err_counter == 20:
                lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, "Error: Sensor Init Failed", lcd.WHITE, lcd.RED)
            time.sleep(0.1)
            continue

    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA) #QVGA=320x240
    sensor.set_windowing((224, 224))
    sensor.run(1)

def rgb888_to_rgb565(r,g,b):
    r = r >> 3
    g = g >> 2
    b = b >> 3
    return (r << 11)|(g <<5)|b

#
# main
#
show_logo()
if but_a.value() == 0: #If dont want to run the demo
    set_backlight(0)
    print('[info]: Exit by user operation')
    sys.exit()
initialize_camera()

labels = ['Ikan Channa Andrao','Ikan Channa Asiatica','Ikan Channa Auranti','Ikan Channa Limbata','Ikan Channa Maru','Ikan Channa Pulchra','Ikan Channa Red','Ikan Channa Stewarti']
task = kpu.load("/sd/model.kmodel")

print('[info]: Started.')
but_stu = 1
isButtonPressedA = 0

fore_color = rgb888_to_rgb565(119,48,48)
back_color = rgb888_to_rgb565(250,205,137)
border_color = (back_color >> 8) | ((back_color & 0xff)<<8)
try:
    while(True):
        #gc.collect()
        img = sensor.snapshot()
        #img2 = img.resize(224, 224)
        #img2.pix_to_ai()
        fmap = kpu.forward(task, img)
        plist=fmap[:]
        pmax=max(plist)
        #t = time.ticks_ms()
        #t = time.ticks_ms() - t
        #print(max_id,pmax)
        if pmax > 0.60:
            max_id=plist.index(pmax)
            print(labels[max_id])
            img.draw_string(0,160, labels[max_id],color=(51,255,51), scale=1.4)
            #img.draw_string(50, 50, text, color=(119,48,48), scale=2,mono_space=False)

            #img.draw_string(50, 50, text, color=(119,48,48), scale=2,mono_space=False)


            #img.draw_string(80, 130, "Accu:%.2f Type:%s"%(max_id, labels[max_id].strip()))
            #img.draw_rectangle(1,46,222,132,color=border_color,thickness=3)

            #img.draw_string(50, 70, "%.2f : %s" %(pmax, labels[max_id].strip()), scale=2, color=(255, 0, 0))
            #img.draw_string(50, 70, "t:%dms" %(t), scale=2, color=(255, 0, 0))

            if but_a.value() == 0 and isButtonPressedA == 0:
                play_sound("/sd/voice/ja/"+str(max_id)+".wav")

                isButtonPressedA = 1
        if but_a.value() == 1:
            isButtonPressedA = 0
        lcd.display(img)
except KeyboardInterrupt:
    kpu.deinit(task)
    sys.exit()

