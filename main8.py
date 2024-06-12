import cv2
from stupidArtnet import StupidArtnet
import pygame
import numpy as np
from pygame.locals import *
import Button as b
import Slider as s
import Text as t 
import Coordinate as c
import Inputbox as i
import math
import wx
import json

app = wx.App(False)
def load_file(ip, universe, x_address, y_address, dimmer, shutter,x_left, y_left, x_right, y_right):
    wildcard = "AL files (*.al)|*.al"
    dialog = wx.FileDialog(None, "Select an AL file", wildcard=wildcard, style=wx.FD_OPEN)
    if dialog.ShowModal() == wx.ID_OK:
        filepath = dialog.GetPath()
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            ip.set_text(data.get("ip", ""))
            universe.set_text(data.get("universe", 0))
            x_address.set_text(data.get("x_address", 0))
            y_address.set_text(data.get("y_address", 0))
            dimmer.set_text(data.get("dimmer", 0))
            shutter.set_text(data.get("shutter", 0))
            x_left = int(data.get("x_left", 0))
            y_left = int(data.get("y_left", 0))
            x_right = int(data.get("x_right", 0))
            y_right = int(data.get("y_right", 0))
        dialog.Destroy()
        return x_left, y_left, x_right, y_right
    dialog.Destroy()
    return x_left, y_left, x_right, y_right

def save_file(ip, universe, x_address, y_address, dimmer, shutter, x_left, y_left, x_right, y_right):
    wildcard = "AL files (*.al)|*.al"
    dialog = wx.FileDialog(None, "Save AL file", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    if dialog.ShowModal() == wx.ID_OK:
        filepath = dialog.GetPath()
        data = {
            "ip": ip(),
            "universe": universe(),
            "x_address": x_address(),
            "y_address": y_address(),
            "dimmer": dimmer(),
            "shutter": shutter(),
            "x_left": x_left,
            "y_left": y_left,
            "x_right": x_right,
            "y_right": y_right
        }
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        dialog.Destroy()

#value convert to fixture position
def convert_range(value, min_in=0, max_in=1920, min_out=100, max_out=200):
    return (value - min_in) / (max_in - min_in) * (max_out - min_out) + min_out

def set_brightness(frame, brightness=0):
    if brightness != 0:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.add(v, brightness)
        v[v > 255] = 255
        v[v < 0] = 0
        final_hsv = cv2.merge((h, s, v))
        frame = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return frame

def get_brightness(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    return np.mean(v)

def main():
    #Screen init
    pygame.init()
    pygame.display.set_caption("Astute Light")
    screen = pygame.display.set_mode([1280, 720], RESIZABLE)
    screen.fill([128,128,128])
    page = "home"#定義頁面
    font = pygame.font.Font(None, 36)

    #Artnet init
    ip = '255.255.255.255'
    x_address = 1
    y_address = 2
    dimmer = 3
    shutter = 4
    universe = 0
    packet_size = max(x_address,y_address,dimmer,shutter)
    a = StupidArtnet(ip, universe, packet_size, 30, True, True)

    #Cam init
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    #Tracker init
    tracker = cv2.TrackerCSRT_create()
    tracking = False
    selecting = False
    start_point = None
    end_point = None

    #button init
    window_width, window_height = screen.get_size()
    print(window_width, window_height)
    original_width, original_height = frame.shape[1], frame.shape[0]
    track_img = pygame.image.load('img/track_img.png').convert_alpha()
    init_img = pygame.image.load('img/init_img.png').convert_alpha()
    setl_img = pygame.image.load('img/setl_img.png').convert_alpha()
    setr_img = pygame.image.load('img/setr_img.png').convert_alpha()
    done_img = pygame.image.load('img/done_img.png').convert_alpha()
    exit_img = pygame.image.load('img/exit_img.png').convert_alpha()
    setting_img = pygame.image.load('img/setting_img.png').convert_alpha()
    load_img = pygame.image.load('img/load_img.png').convert_alpha()
    save_img = pygame.image.load('img/save_img.png').convert_alpha()
    logo_img = pygame.image.load('img/logo_img.png').convert_alpha()
    auto_track_img = pygame.image.load('img/auto_track_img.png').convert_alpha()
    auto_show_img = pygame.image.load('img/auto_show_img.png').convert_alpha()
    load_long_img = pygame.image.load('img/load_long_img.png').convert_alpha()
    
    scale_o2w = window_width / 1920

    #all page init
    setting_button = b.Button(1850 * scale_o2w,50 * scale_o2w,setting_img,0.2 * scale_o2w)
    logo_button = b.Button(100 * scale_o2w, 100 * scale_o2w , logo_img ,0.2 * scale_o2w)
    bright = False
    bright_text = t.Text("ADD LIGHT",int(50 * scale_o2w),(1160 * scale_o2w, 50 * scale_o2w),(255,255,255))

    #track page init
    init_button = b.Button(150 * scale_o2w,1000 * scale_o2w,init_img,0.2 * scale_o2w)
    track_button = b.Button(690 * scale_o2w,1000 * scale_o2w,track_img,0.2 * scale_o2w)
    load_button = b.Button(1130 * scale_o2w,1000 * scale_o2w,load_img,0.2 * scale_o2w)  
    save_button = b.Button(1330 * scale_o2w,1000 * scale_o2w,save_img,0.2 * scale_o2w) 
    exit_button = b.Button( 1770 * scale_o2w,1000 * scale_o2w,exit_img,0.2 * scale_o2w)
    #c_text = c.Coordinate(48) #(font_size) 座標系統會卡

    #init page init
    x_slider = s.Slider(100 * scale_o2w,700 * scale_o2w,300 * scale_o2w,20 * scale_o2w)
    y_slider = s.Slider(100 * scale_o2w,800 * scale_o2w,300 * scale_o2w,20 * scale_o2w)
    dimmer_slider = s.Slider(100 * scale_o2w,900 * scale_o2w,300 * scale_o2w,20 * scale_o2w)
    setl_button = b.Button(150 * scale_o2w,1000 * scale_o2w,setl_img,0.2 * scale_o2w)
    setr_button = b.Button(690 * scale_o2w,1000 * scale_o2w,setr_img,0.2 * scale_o2w)
    done_button = b.Button(1230 * scale_o2w,1000 * scale_o2w,done_img,0.2 * scale_o2w)
    left = False
    right = False
    x_left = 0
    y_left = 0
    x_right = 0
    y_right = 0

    #home page init
    logo_button_1 = b.Button(960 * scale_o2w, 300 * scale_o2w , logo_img ,0.5 * scale_o2w)
    auto_track_button =  b.Button(960 * scale_o2w, 600 * scale_o2w , auto_track_img ,0.4 * scale_o2w)
    auto_show_button = b.Button(960 * scale_o2w, 750 * scale_o2w , auto_show_img ,0.4 * scale_o2w)
    load_long_button = b.Button(960 * scale_o2w, 900 * scale_o2w , load_long_img ,0.4 * scale_o2w)

    #setting page init
    artnet_text = t.Text("ArtNet",int(100 * scale_o2w),(280 * scale_o2w,100 * scale_o2w),(255,255,255))
    fixture_text = t.Text("Fixture",int(100 * scale_o2w),(860 * scale_o2w,100 * scale_o2w),(255,255,255))
    file_text = t.Text("File",int(100 * scale_o2w),(1440 * scale_o2w,100 * scale_o2w),(255,255,255))
    ip = i.Inputbox(280 * scale_o2w,200 * scale_o2w, 300 * scale_o2w, 70 * scale_o2w, font_size=int(50*scale_o2w),label='IP:',default_text='255.255.255.255')
    universe = i.Inputbox(280 * scale_o2w,350 * scale_o2w, 300 * scale_o2w, 70 * scale_o2w, font_size=int(50*scale_o2w),label='Universe:',default_text= '0')
    x_address = i.Inputbox(860 * scale_o2w,200 * scale_o2w, 300 * scale_o2w, 70 * scale_o2w, font_size=int(50*scale_o2w),label='X Address:',default_text='1')
    y_address = i.Inputbox(860 * scale_o2w,350 * scale_o2w, 300 * scale_o2w, 70 * scale_o2w, font_size=int(50*scale_o2w),label='Y Address:',default_text='2')
    dimmer = i.Inputbox(860 * scale_o2w,500 * scale_o2w, 300 * scale_o2w, 70 * scale_o2w, font_size=int(50*scale_o2w),label='Dimmer:',default_text='3')
    shutter = i.Inputbox(860 * scale_o2w,650 * scale_o2w, 300 * scale_o2w, 70 * scale_o2w, font_size=int(50*scale_o2w),label='Shutter:',default_text='4')
    load_button1 = b.Button(1540 * scale_o2w,250 * scale_o2w,load_img,0.2 * scale_o2w)  
    save_button1 = b.Button(1540 * scale_o2w,350 * scale_o2w,save_img,0.2 * scale_o2w) 

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Cannot receive frame")
            break
        original_width, original_height = frame.shape[1], frame.shape[0]
        window_width, window_height = screen.get_size()
        screen.fill([128,128,128])

        #Resize
        aspect_ratio = original_height / original_width
        #print("as",aspect_ratio)
        #print(window_height / window_width)
        if not math.isclose(aspect_ratio , window_height / window_width , rel_tol = 1e-2): #screen size change
            window_height = int(window_width * aspect_ratio)
            scale_o2w = window_width / 1920
            screen = pygame.display.set_mode([window_width, window_height], RESIZABLE) #運算效能不足 閃頻 解決

            #all page init
            setting_button = b.Button(1850 * scale_o2w,50 * scale_o2w,setting_img,0.2 * scale_o2w)
            logo_button = b.Button(100 * scale_o2w, 100 * scale_o2w , logo_img ,0.2 * scale_o2w)
            bright_text = t.Text("ADD",int(100 * scale_o2w),(1160 * scale_o2w, 100 * scale_o2w),(255,255,255))

            #track page init
            init_button = b.Button(150 * scale_o2w,1000 * scale_o2w,init_img,0.2 * scale_o2w)
            track_button = b.Button(690 * scale_o2w,1000 * scale_o2w,track_img,0.2 * scale_o2w)
            load_button = b.Button(1130 * scale_o2w,1000 * scale_o2w,load_img,0.2 * scale_o2w)  
            save_button = b.Button(1330 * scale_o2w,1000 * scale_o2w,save_img,0.2 * scale_o2w) 
            exit_button = b.Button( 1770 * scale_o2w,1000 * scale_o2w,exit_img,0.2 * scale_o2w)

            #init page init
            dimmer_slider = s.Slider(100 * scale_o2w,900 * scale_o2w,300 * scale_o2w,20 * scale_o2w)
            x_slider = s.Slider(100 * scale_o2w,700 * scale_o2w,300 * scale_o2w,20 * scale_o2w)
            y_slider = s.Slider(100 * scale_o2w,800 * scale_o2w,300 * scale_o2w,20 * scale_o2w)
            setl_button = b.Button(150 * scale_o2w,1000 * scale_o2w,setl_img,0.2 * scale_o2w)
            setr_button = b.Button(690 * scale_o2w,1000 * scale_o2w,setr_img,0.2 * scale_o2w)
            done_button = b.Button(1230 * scale_o2w,1000 * scale_o2w,done_img,0.2 * scale_o2w)
            x_value = t.Text(f"X_Value: {x_slider.get_value()}", int(48 * scale_o2w) ,(100 * scale_o2w, 650 * scale_o2w), (255, 255, 255))
            y_value = t.Text(f"Y_Value: {y_slider.get_value()}", int(48 * scale_o2w) ,(100 * scale_o2w, 750 * scale_o2w), (255, 255, 255))
            dimmer_value = t.Text(f"Dimmer: {dimmer_slider.get_value()}", int(48 * scale_o2w) ,(100 * scale_o2w, 850 * scale_o2w), (255, 255, 255))
            artnet_text = t.Text("ArtNet",int(100 * scale_o2w),(280 * scale_o2w,100 * scale_o2w),(255,255,255))
            fixture_text = t.Text("Fixture",int(100 * scale_o2w),(860 * scale_o2w,100 * scale_o2w),(255,255,255))
            file_text = t.Text("File",int(100 * scale_o2w),(1440 * scale_o2w,100 * scale_o2w),(255,255,255))
            ip = i.Inputbox(280 * scale_o2w,200 * scale_o2w, 300 * scale_o2w, 70 * scale_o2w, font_size=int(50*scale_o2w),label='IP:',default_text='255.255.255.255')
            universe = i.Inputbox(280 * scale_o2w,350 * scale_o2w, 300 * scale_o2w, 70 * scale_o2w, font_size=int(50*scale_o2w),label='Universe:',default_text= '0')
            x_address = i.Inputbox(860 * scale_o2w,200 * scale_o2w, 300 * scale_o2w, 70 * scale_o2w, font_size=int(50*scale_o2w),label='X Address:',default_text='1')
            y_address = i.Inputbox(860 * scale_o2w,350 * scale_o2w, 300 * scale_o2w, 70 * scale_o2w, font_size=int(50*scale_o2w),label='Y Address:',default_text='2')
            dimmer = i.Inputbox(860 * scale_o2w,500 * scale_o2w, 300 * scale_o2w, 70 * scale_o2w, font_size=int(50*scale_o2w),label='Dimmer:',default_text='3')
            shutter = i.Inputbox(860 * scale_o2w,650 * scale_o2w, 300 * scale_o2w, 70 * scale_o2w, font_size=int(50*scale_o2w),label='Shutter:',default_text='4')
            load_button1 = b.Button(1540 * scale_o2w,250 * scale_o2w,load_img,0.2 * scale_o2w)  
            save_button1 = b.Button(1540 * scale_o2w,350 * scale_o2w,save_img,0.2 * scale_o2w) 
            
            #home page init
            logo_button_1 = b.Button(960 * scale_o2w, 300 * scale_o2w , logo_img ,0.5 * scale_o2w)
            auto_track_button =  b.Button(960 * scale_o2w, 600 * scale_o2w , auto_track_img ,0.4 * scale_o2w)
            auto_show_button = b.Button(960 * scale_o2w, 750 * scale_o2w , auto_show_img ,0.4 * scale_o2w)
            load_long_button = b.Button(960 * scale_o2w, 900 * scale_o2w , load_long_img ,0.4 * scale_o2w)

        #brightness auto set
        brightness_threshold = 100  
        frame_brightness = get_brightness(frame)

        if frame_brightness < brightness_threshold:
            bright = True
            frame = set_brightness(frame, brightness=100)
            frame = cv2.medianBlur(frame,5)
        else:
            bright = False

        if tracking:
            success, point = tracker.update(frame)
            if success:
                p1 = [int(point[0]), int(point[1])]
                p2 = [int(point[0] + point[2]), int(point[1] + point[3])]
                cv2.rectangle(frame, p1, p2, (0, 0, 255), 3)
                m1 = int(point[0] + (point[2] / 2))
                m2 = int(point[1] + (point[3] / 2))
                #c_text.set_position(m1,m2)座標系統會卡
                cv2.circle(frame, (m1, m2), 10, (0, 0, 255), -1)
                a.set_single_value(int(x_address.get_text()), int(convert_range(m1,max_in = original_width,min_out = x_left ,max_out = x_right)))
                a.set_single_value(int(y_address.get_text()), int(convert_range(m1,max_in= original_width,min_out = y_left ,max_out = y_right)))
                a.show()
        
        #Cam draw
        frame_resized = cv2.resize(frame, (window_width, window_height))
        frame_resized = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.flip(frame_resized,1) #left right flip
        if page == "setting" or page =="home":
            frame_resized = cv2.blur(frame_resized,(25,25))
        frame_resized = np.rot90(frame_resized)
        frame_resized = pygame.surfarray.make_surface(frame_resized)#numpy.ndarray to pygame.surface.Surface
        screen.blit(frame_resized, (0,0))

        #c_text.draw(screen) 座標系統會卡

        #Button draw
        if page == "track":
            #init page init
            left = False
            right = False
            dimmer_slider.draw(screen)
            dimmer_value = t.Text(f"Dimmer: {dimmer_slider.get_value()}", int(48 * scale_o2w) ,(100 * scale_o2w, 850 * scale_o2w), (255, 255, 255))
            dimmer_value.draw(screen)
            a.set_single_value(int(shutter.get_text()), 1)
            a.set_single_value(int(dimmer.get_text()), dimmer_slider.get_value())
            a.show()
            #button draw
            if track_button.draw(screen):
                selecting = True
                print("selecting")
            elif init_button.draw(screen):
                page = "init"
                print("init")
            elif setting_button.draw(screen):
                page = "setting"
                d = "from_track"
            elif load_button.draw(screen):
                print("load")
                x_left, y_left, x_right, y_right = load_file(ip, universe, x_address, y_address, dimmer, shutter,x_left, y_left, x_right, y_right)
                packet_size = max(int(x_address.get_text()),int(y_address.get_text()),int(dimmer.get_text()),int(shutter.get_text()))
                a = StupidArtnet(ip.get_text(), int(universe.get_text()), packet_size, 30, True, True)
            elif save_button.draw(screen):
                print("save")
                save_file(ip.get_text, universe.get_text, x_address.get_text, y_address.get_text, dimmer.get_text, shutter.get_text, x_left, y_left, x_right, y_right)
            elif exit_button.draw(screen):
                page = "home"
                print("home")
            elif logo_button.draw(screen):
                page = "home"
                print("home")
            elif bright:
                bright_text.draw(screen)

        elif page == "init":
            selecting = False
            tracking = False
            start_point = False
            x_slider.draw(screen)
            y_slider.draw(screen)
            dimmer_slider.draw(screen)
            x_value = t.Text(f"X Value: {x_slider.get_value()}", int(48 * scale_o2w) ,(100 * scale_o2w, 650 * scale_o2w), (255, 255, 255))
            y_value = t.Text(f"Y Value: {y_slider.get_value()}", int(48 * scale_o2w) ,(100 * scale_o2w, 750 * scale_o2w), (255, 255, 255))
            dimmer_value = t.Text(f"Dimmer: {dimmer_slider.get_value()}", int(48 * scale_o2w) ,(100 * scale_o2w, 850 * scale_o2w), (255, 255, 255))
            dimmer_value.draw(screen)
            x_value.draw(screen)
            y_value.draw(screen)
            
            a.set_single_value(int(shutter.get_text()), 1)
            a.set_single_value(int(dimmer.get_text()), dimmer_slider.get_value())
            a.set_single_value(int(x_address.get_text()),x_slider.get_value())
            a.set_single_value(int(y_address.get_text()),y_slider.get_value())
            a.show()
            if setl_button.draw(screen):
                x_left = x_slider.get_value()
                y_left = y_slider.get_value()
                left = True
            elif setr_button.draw(screen):
                x_right = x_slider.get_value()
                y_right = y_slider.get_value()
                right = True
            elif exit_button.draw(screen):
                page = "track"
            elif setting_button.draw(screen):
                page = "setting"
                d = "from_init"
            elif logo_button.draw(screen):
                page = "home"
                print("home")
            elif left and right:
                if done_button.draw(screen):
                    page = "track"
            
        elif page =="setting":
            start_point = False
            selecting  = False
            artnet_text.draw(screen)
            fixture_text.draw(screen)
            file_text.draw(screen)
            if setting_button.draw(screen):
                packet_size = max(int(x_address.get_text()),int(y_address.get_text()),int(dimmer.get_text()),int(shutter.get_text()))
                a = StupidArtnet(ip.get_text(), int(universe.get_text()), packet_size, 30, True, True)
                if d == "from_init":
                    page = "init"
                elif d == "from_track":
                    page = "track"
                elif d == "from_home":
                    page = "home"
            elif logo_button.draw(screen):
                page = "home"
                print("home")
            elif load_button1.draw(screen):
                print("load")
                x_left, y_left, x_right, y_right = load_file(ip, universe, x_address, y_address, dimmer, shutter,x_left, y_left, x_right, y_right)
                packet_size = max(int(x_address.get_text()),int(y_address.get_text()),int(dimmer.get_text()),int(shutter.get_text()))
                a = StupidArtnet(ip.get_text(), int(universe.get_text()), packet_size, 30, True, True)
            elif save_button1.draw(screen):
                print("save")
                save_file(ip.get_text, universe.get_text, x_address.get_text, y_address.get_text, dimmer.get_text, shutter.get_text, x_left, y_left, x_right, y_right)

            ip.draw(screen)
            universe.draw(screen)
            x_address.draw(screen)
            y_address.draw(screen)
            dimmer.draw(screen)
            shutter.draw(screen)
            ip.check_ip()
            universe.check_number()
            x_address.check_number()
            dimmer.check_number()
            shutter.check_number()
        elif page =="home":
            tracking = False
            selecting = False
            start_point = False
            logo_button_1.draw(screen)
            if auto_track_button.draw(screen):
                page = "track"
            elif load_long_button.draw(screen):
                print("load")
                x_left, y_left, x_right, y_right = load_file(ip, universe, x_address, y_address, dimmer, shutter,x_left, y_left, x_right, y_right)
                packet_size = max(int(x_address.get_text()),int(y_address.get_text()),int(dimmer.get_text()),int(shutter.get_text()))
                a = StupidArtnet(ip.get_text(), int(universe.get_text()), packet_size, 30, True, True)
            elif auto_show_button.draw(screen):
                print("auto_show")
            elif setting_button.draw(screen):
                page = "setting"
                d = "from_home"
            
                


            #print("setting")


        for event in pygame.event.get():
            if event.type == QUIT:
                cap.release()
                cv2.destroyAllWindows()
                pygame.quit()
                return
            elif event.type == VIDEORESIZE:
                window_width, window_height = event.w, event.h
                screen = pygame.display.set_mode((window_width, window_height), RESIZABLE)
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    cap.release()
                    cv2.destroyAllWindows()
                    pygame.quit()
                    return
            elif page =="track" and not selecting:
                dimmer_slider.handle_event(event)
            elif page == "init":
                x_slider.handle_event(event)
                y_slider.handle_event(event)
                dimmer_slider.handle_event(event)
            elif page == "setting":
                #print(event)
                ip.handle_event(event)
                universe.handle_event(event)
                x_address.handle_event(event)
                y_address.handle_event(event)
                dimmer.handle_event(event)
                shutter.handle_event(event)

            elif event.type == MOUSEBUTTONDOWN and page == "track":
                if selecting:
                    start_point = pygame.mouse.get_pos()
                    end_point = None
                    print("down")
                else:
                    dimmer_slider.handle_event(event)

            elif event.type == MOUSEBUTTONUP and start_point and page =="track":
                    if selecting:
                        end_point = pygame.mouse.get_pos()
                        selecting = False
                        print("up")
                    if start_point and end_point:
                        x1, y1 = start_point
                        x2, y2 = end_point
                        roi_pygame = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
                        
                        scale_w2o = original_width / window_width  #window coordinate to original coordinate

                        roi = (int(roi_pygame[0] * scale_w2o), int(roi_pygame[1] * scale_w2o),
                               int(roi_pygame[2] * scale_w2o), int(roi_pygame[3] * scale_w2o))
                        if roi[1]+roi[3] >= original_height: #limit y in the correct coordinate
                            roi = (int(roi_pygame[0] * scale_w2o), int(roi_pygame[1] * scale_w2o),
                                    int(roi_pygame[2] * scale_w2o), int(original_height-roi_pygame[1] * scale_w2o))
                        print(f"Selected ROI: {roi}")
                        if roi[2] > 0 and roi[3] > 0:
                            tracking = True
                            tracker.init(frame, roi)
                            print("Tracker initialized")
                        else:
                            print("fail")
                        start_point = None
                        end_point = None
            

            
        #track page
        if start_point and pygame.mouse.get_pressed()[0] and page =="track":
            current_pos = pygame.mouse.get_pos()
            x1, y1 = start_point
            x2, y2 = current_pos
            pygame.draw.rect(screen, (255, 0, 0), (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)), 2)
        
        
        

        pygame.display.update()
    
    cap.release()
    cv2.destroyAllWindows()


if __name__=="__main__":
    main()