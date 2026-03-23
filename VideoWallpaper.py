# 本程序原本没想过开源，只是自己用用，而且我也是个编程新手，所以可读性和兼容性差点，请见谅 :P
# 本程序没有调用Windows官方的壁纸API，我觉得那样不稳定，对于MP4格式的长视频不友好，因此实质上是创建了个播放视频的窗口，所以会遮挡桌面图标（因为我平时都隐藏图标的，所以没管这个）
# 如果要使用，请安装对应的库，并在Rainmeter路径部分的代码处将路径改成你自己电脑的，或直接将相关代码删除，并将使用的所有字体改成你电脑上已经安装了的字体
# 经过实测，对于1920*1080分辨率的视频，内存占用约500Mb
import tkinter as tk
import json
import os
import threading
import time
import shutil
import ctypes
import cv2
import glob
import keyboard
import ctypes
import sys
import subprocess
import pygame
import winreg
import copy
from tkinter import ttk
from PIL import Image, ImageTk

appdata = os.path.join(os.environ['USERPROFILE'], 'AppData', 'LocalLow')
running = False
data = None
run = None
run_control = None
value = None
keep = True
SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDWININICHANGE = 0x02
user32 = ctypes.WinDLL('user32', use_last_error=True)
def audio_device():
    try:
        reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE/Microsoft/Windows/CurrentVersion/MMDevices/Audio/Render")
        for i in range(winreg.QueryInfoKey(reg)[0]):
            dev_id = winreg.EnumKey(reg, i)
            dev_key = winreg.OpenKey(reg, f"{dev_id}/Properties")
            try:
                if winreg.QueryValueEx(dev_key, "{a45c254e-df1c-4efd-8020-67d146a850e0},2")[0] == 1:
                    return winreg.QueryValueEx(dev_key, "{a45c254e-df1c-4efd-8020-67d146a850e0},14")[0]
            except: continue
            finally: winreg.CloseKey(dev_key)
        winreg.CloseKey(reg)
    except:pass
pygame.mixer.init()
audio_device()
try:
    sound = pygame.mixer.Sound(f"{appdata}/Tideling/Wallpaper/Audio/Audio.mp3")
except Exception as e:
    sound = None
    print(e)
print(sound)

class BackEnd():
    def __init__(self, frontend):
        self.image_cache = {}
        self.fe = frontend
        self.picture = None
        self.wallpaper_created = False
        if hasattr(self.fe, 'root'):
            self.fe.root.after(100, self.start_threads)
        self.jpg_num()
    def jpg_num(self):
        count = 0
        for i in os.listdir(f"{appdata}/Tideling/Wallpaper/Pictures"):
            if i.lower().endswith(('.jpg' , '.jpeg')):
                count += 1
        print(f"数量{count}")
        self.pic_num = count
        print(self.pic_num)
    def menu(self):
        def refresh_wallpaper():
            try:
                print("回桌面了")
                self.picture.wm_attributes('-topmost', True)
                subprocess.run('taskkill /f /im "Rainmeter.exe"', shell=True)
                time.sleep(1)
                self.picture.wm_attributes('-topmost', False)
                time.sleep(0.1)
                self.rainmeter_path = "D:/Rainmeter/Rainmeter.exe"
                subprocess.Popen(self.rainmeter_path)
            except:
                pass
        keyboard.add_hotkey("win+d", lambda: self.fe.root.after(0, refresh_wallpaper))
    def start_threads(self):
        set_value_thread = threading.Thread(target=self.fe.be.set_value)
        set_value_thread.daemon = True
        wallpaper_thread = threading.Thread(target=self.fe.be.wallpaper)
        wallpaper_thread.daemon = True
        wallpaper_menu_thread = threading.Thread(target=self.fe.be.menu)
        wallpaper_menu_thread.daemon = True
        set_value_thread.start()    
        wallpaper_thread.start()
        wallpaper_menu_thread.start()
    def run_fun(self):
        def rainmater_open():
            try:
                print("rainmeter启动中")
                subprocess.run('taskkill /f /im "Rainmeter.exe"', shell=True)
                time.sleep(1)
                self.rainmeter_path = "D:/Rainmeter/Rainmeter.exe"
                subprocess.Popen(self.rainmeter_path)
            except Exception as e:
                print(f"雨滴插件打开失败，错误{e}")
        print("修改")
        rainmeter_thread = threading.Thread(target=rainmater_open)
        rainmeter_thread.daemon = True
        rainmeter_thread.start()
        global running
        global appdata
        global sound
        running = not running
        try:
            if running == False:
                print("停了")
                sound.stop()
                self.picture.destroy()
                self.wallpaper_created = False
        except:
            print("错误")
        print(running)
        self.fe.run.config(
            text="关闭" if running else "打开",
            bg="#CA2929" if running else "#4CAF50"
        )
        self.fe.state.config(
            text="当前状态-开" if running else "当前状态-关"
        )
        if os.path.exists(f"{appdata}/Tideling/Wallpaper/Wallpaper/OldWallpaper.jpg"):
            os.remove(f"{appdata}/Tideling/Wallpaper/Wallpaper/OldWallpaper.jpg")
        ubuf = ctypes.create_unicode_buffer(260)
        ctypes.windll.user32.SystemParametersInfoW(0x0073, 260, ubuf, 0)
        wallpaper_file = ubuf.value
        print(wallpaper_file)
        shutil.copy2(wallpaper_file , f"{appdata}/Tideling/Wallpaper/Wallpaper/OldWallpaper.jpg")
        print("保存完成")
    def quick(self):
        print("等待")
        print(run_control + run)
        keyboard.add_hotkey(run_control + "+" + run , self.run_fun)
    def set_value(self):
        global value
        global running
        global run
        global run_control
        global keep
        self.quick_thread = threading.Thread(target=self.quick)
        self.quick_thread.daemon = True
        self.quick_thread.start()
        while True:
            time.sleep(0.1)
            if run != self.fe.quick_bar.get() or run_control != self.fe.quick_control.get():
                value = self.fe.slider.get()
                run = self.fe.quick_bar.get()
                run_control = self.fe.quick_control.get()
                self.quick_thread = threading.Thread(target=self.quick)
                self.quick_thread.daemon = True
                self.quick_thread.start()
                self.save()
                self.refresh()
            else:
                value = self.fe.slider.get()
                run = self.fe.quick_bar.get()
                run_control = self.fe.quick_control.get()
            keep = self.fe.keep_data.get()
    def wallpaper(self):
        def play_music():
            global sound
            print("有音频")
            sound.play(loops=-1)
            sound.set_volume(value / 100)
            def update_volume():
                if running and sound:
                    sound.set_volume(value / 100)
                    self.fe.root.after(100, update_volume)
            update_volume()
        def loop_wallpaper(self):
            while running:
                self.set_pictrue()
                if not running:
                    break
        def set_wallpaper(self):
            try:
                if self.jpg_num != 0:
                    global running
                    global screen_width
                    global screen_height
                    global sound
                    print("运行")
                    path = f"{appdata}/Tideling/Wallpaper/Pictures/"
                    files = os.listdir(path)
                    img_file = os.path.join(path, files[0])
                    user32 = ctypes.windll.user32
                    user32.SetProcessDPIAware()
                    screen_width = user32.GetSystemMetrics(0)
                    screen_height = user32.GetSystemMetrics(1)
                    self.picture = tk.Toplevel(self.fe.root)
                    self.picture.overrideredirect(True)
                    self.picture.geometry(f"{screen_width}x{screen_height - 1}+0+0")
                    self.picture.attributes('-alpha', 1)
                    self.picture.wm_attributes('-disabled', True)
                    self.picture.wm_attributes('-topmost', False)
                    img = Image.open(img_file)
                    img = img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
                    self.photo = ImageTk.PhotoImage(img)
                    self.label = tk.Label(self.picture, image=self.photo, bd=0)
                    self.label.pack(fill=tk.BOTH, expand=True)
                    hwnd = self.picture.winfo_id()
                    hmenu = user32.GetSystemMenu(hwnd, False)
                    if hmenu:
                        user32.DeleteMenu(hmenu, 0xF020, 0x00000400)
                    style = user32.GetWindowLongW(hwnd, -20)
                    style = style | 0x00000080 | 0x08000000 | 0x00000008
                    user32.SetWindowLongW(hwnd, -20, style)
                    user32.SetWindowPos(hwnd, 1, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0010)
                    self.music_th = threading.Thread(target=play_music)
                    self.music_th.daemon = True
                    if sound != None:
                        self.music_th.start()
                    self.fe.root.mainloop()
                else:
                    raise Exception("错误：无法读取jpg文件，请检查文件是否存在，以及格式、名称、路径是否正确")
            except Exception as e:
                print(e)
                self.fe.error.config(
                text=e,
                fg="#FF0000"
                )
        def set_pictrue(self):
            global screen_width
            global screen_height
            current_list = []
            next_list = []
            current_group = 0
            for k in range(10):
                try:
                    img_path = f"{appdata}/Tideling/Wallpaper/Pictures/0-{k}.jpg"
                    img = Image.open(img_path)
                    img = img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
                    current_list.append(ImageTk.PhotoImage(img))
                except:
                    break
            def preload_next(group):
                nonlocal next_list
                new_list = []
                for k in range(10):
                    if not running:
                        break
                    try:
                        img_path = f"{appdata}/Tideling/Wallpaper/Pictures/{group}-{k}.jpg"
                        img = Image.open(img_path)
                        img = img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
                        new_list.append(ImageTk.PhotoImage(img))
                    except:
                        break
                next_list = new_list
            preload_thread = threading.Thread(target=preload_next, args=(1,))
            preload_thread.daemon = True
            preload_thread.start()    
            i = 0
            while running:
                new_photo = current_list[i % 10]
                self.label.config(image=new_photo)
                self.photo = new_photo
                if (i + 1) % 10 == 0:
                    current_group += 1
                    while len(next_list) == 0 and running:
                        time.sleep(0.01)
                    current_list = next_list
                    next_list = []
                    if current_group + 1 < self.pic_num // 10:
                        preload_thread = threading.Thread(target=preload_next, args=(current_group + 1,))
                        preload_thread.daemon = True
                        preload_thread.start()
                    else:
                        i = -1
                        set_pictrue(self)  
                i += 1
                time.sleep(1 / 30)
            if running:
                self.fe.error.config(
                text="无法获取图片，请检查图像是否存在，或名称是否正确，检查后重新运行程序",
                fg="#FF0000"
                )
        global running
        os.makedirs(f"{appdata}/Tideling/Wallpaper/Pictures", exist_ok=True)
        while True:
            if running:
                if running == False:
                    break
                cap = cv2.VideoCapture(f"{appdata}/Tideling/Wallpaper/Wallpaper/Wallpaper.mp4")
                if not cap.isOpened():
                    print("无法打开视频文件")
                    self.fe.error.config(
                    text="错误:视频文件无法正确读取；请确保格式、命名、路径正确，并在检查后重新运行本程序",
                    fg="#FF0000"
                    )
                    break
                    self.run_fun()
                else:
                    if keep == False:
                        for i in os.listdir(f"{appdata}/Tideling/Wallpaper/Pictures"):
                            os.remove(f"{appdata}/Tideling/Wallpaper/Pictures/" + str(i))
                        self.fe.error.config(
                        text="缓冲中，请耐心等待......",
                        fg="#2F9B17"
                        )
                        frame_count = 0
                        while True:
                            ret, frame = cap.read()
                            if not ret or running == False:
                                python = sys.executable
                                os.execl(python, python, *sys.argv)
                            cv2.imwrite(f"{appdata}/Tideling/Wallpaper/Pictures/{frame_count // 10}-{frame_count % 10}.jpg", frame)
                            frame_count += 1
                        set_pictrue(self)
                    else:
                        if not hasattr(self, 'wallpaper_created') or not self.wallpaper_created:
                            self.wallpaper_created = True
                            self.fe.root.after(0, lambda: set_wallpaper(self))
                            while self.pic_num == 0:
                                time.sleep(0.1)
                                self.jpg_num()
                            set_pictrue(self)
    def save(self):
        global run
        global value
        global appdata
        self.data = {
            "quick_run" : run,
            "quick_control" : run_control,
            "value" : value
        }
        print(self.data)
        if os.path.exists(f"{appdata}/Tideling/Wallpaper/Wallpaper/Settings.json"):
            os.remove(f"{appdata}/Tideling/Wallpaper/Wallpaper/Settings.json")
        with open(appdata + "/Tideling/Wallpaper/Settings.json", 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        print("已保存")
        print(run + run_control + str(value))
    def refresh(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)
    def open(self):
        if  os.path.exists(f"{appdata}/Tideling/Wallpaper"):
            print("开了")
            os.startfile(f"{appdata}/Tideling/Wallpaper")
        else:
            self.refresh()

class FrontEnd():
    def __init__(self):
        global appdata
        global data
        global run
        global run_control
        global value
    #-----创建文件夹-----
        os.makedirs(f"{appdata}/Tideling/Wallpaper/Wallpaper", exist_ok=True)
        os.makedirs(f"{appdata}/Tideling/Wallpaper/Audio", exist_ok=True)
    #-----实例化变量并初始化-----
        self.data = {
            "quick_run" : "r",
            "value" : 80,
            "quick_control" : "ctrl+shift"
        }
        def save_settings(self):
            global value
            global run
            global run_control
            if not os.path.isfile(appdata + "/Tideling/Wallpaper/Settings.json"):
                with open(appdata + "/Tideling/Wallpaper/Settings.json", 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=4)
                data = json.load(open(appdata + "/Tideling/Wallpaper/Settings.json", 'r', encoding='utf-8'))
            else:
                data = json.load(open(appdata + "/Tideling/Wallpaper/Settings.json", 'r', encoding='utf-8'))
            print(data)
            try:
                run = data["quick_run"]
                run_control = data["quick_control"]
                value = data["value"]
            except:
                os.remove(appdata + "/Tideling/Wallpaper/Settings.json")
                save_settings(self)
        save_settings(self)
        self.be = BackEnd(self)
        self.write = self.be.save
        print(self.write)
    #-----程序-----
        self.root = tk.Tk()
        self.root.attributes('-toolwindow', True)
        self.root.title("MP4视频壁纸")
        self.root.geometry("800x1020")
    #-----标题-----
        self.title = tk.Label(
        self.root, 
        text="视频转壁纸", 
        font=("创客贴金刚体", 80),
        fg="#000000",
        pady=20
        )
        self.title.pack(pady=18)
    #-----运行按钮-----
        self.run = tk.Button(
        self.root,
        text="关闭" if running else "打开",
        command=self.be.run_fun,
        font=("Arial", 20),
        bg="#CA2929" if running else "#4CAF50",
        fg="white",
        padx=60,
        pady=20,
        cursor="hand2"
        )
        self.run.pack(pady=10)
    # -----维持数据-----
        self.keep_data = tk.BooleanVar(value=True)
        self.keep_bu = tk.Checkbutton(
        self.root,
        text="维持数据",
        variable=self.keep_data,
        font=("思源黑体 CN", 15),
        fg="#000000",
        onvalue=True,
        offvalue=False  
        )
        self.keep_bu.pack(pady=1)
    #-----当前状态-----
        self.state = tk.Label(
        self.root, 
        text="当前状态-开" if running else "当前状态-关", 
        font=("思源黑体 CN", 20),
        fg="#201C6C",
        pady=5
        )
        self.state.pack(pady=1)
    #-----音量-----
        self.audio = tk.Label(
        self.root, 
        text="当前音量", 
        font=("思源黑体 CN", 30),
        fg="#000000",
        pady=1
        )
        self.audio.pack(pady=1)
    #-----音量滑动条-----
        self.slider = tk.Scale(
        self.root,
        from_=0,
        to=100,
        orient=tk.HORIZONTAL,
        length=300,
        font=("Arial", 10),
        bg='#f0f0f0',
        troughcolor='#4CAF50',
        fg='#333333'
        )
        self.slider.set(value)
        self.slider.pack(pady=30)
    #-----快捷键-----
        self.control = tk.Label(
        self.root, 
        text="开关快捷键", 
        font=("思源黑体 CN", 30),
        fg="#000000",
        pady=1
        )
        self.control.pack(pady=1)
    #-----快捷键修改-----
        quick_options = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        self.quick_bar = tk.StringVar()
        self.quick_bar.set(run)
        self.combobox1 = ttk.Combobox(
            self.root, 
            textvariable=self.quick_bar, 
            values=quick_options,
            state="readonly"
        )
        self.combobox1.pack(pady=30)
    #-----快捷键修改-----
        quick_control = ["ctrl", "shift", "alt", "ctrl+shift", "ctrl+alt", "shift+alt", "ctrl+shift+alt"]
        self.quick_control = tk.StringVar()
        self.quick_control.set(run_control)
        self.combobox2 = ttk.Combobox(
            self.root, 
            textvariable=self.quick_control, 
            values=quick_control,
            state="readonly"
        )
        self.combobox2.pack(pady=1)
    #-----保存设置-----
        self.save = tk.Button(
        self.root,
        text="保存设置",
        command=self.write,
        font=("Arial", 20),
        bg="#2D2D2D",
        fg="white",
        padx=20,
        pady=10,
        cursor="hand2"
        )
        self.save.pack(pady=10)
    #-----打开文件夹-----
        self.open = tk.Button(
        self.root,
        text="打开目标文件夹",
        command=self.be.open,
        font=("Arial", 20),
        bg="#03B9D1",
        fg="white",
        padx=13,
        pady=1,
        cursor="hand2"
        )
        self.open.pack(pady=1)
    #-----简介-----
        self.introduction = tk.Label(
        self.root, 
        text=f"使用方法：在{appdata}\Tideling\Wallpaper内的Wallpaper子\n文件夹中放入你想设为壁纸的mp4文件,命名为[Wallpaper.mp4];可选择在Audio子文件夹内放\n入你想播放的mp3文件,命名为[Audio.mp3]", 
        font=("王汉宗中魏碑简体-免費商用", 12),
        fg="#000000", 
        pady=3
        )
        self.introduction.pack(pady=1)
    #-----错误-----
        self.error = tk.Label(
        self.root, 
        text="", 
        font=("思源黑体 CN", 8),
        fg="#FF0000", 
        pady=3
        )
        self.error.pack(pady=1)
    #-----运行-----
        time.sleep(0.15)
        self.be.run_fun()

class RunningCls():
    def __init__(self):
        fe = FrontEnd()
        be = BackEnd(fe)
        fe.root.mainloop()
ru = RunningCls()
