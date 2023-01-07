import os, sys
import signal
import threading

from PySide6 import QtCore, QtGui, QtWidgets

from PIL import Image, ImageGrab, ImageFilter

import ctypes

from pynput import mouse
import keyboard

import time


mov_rect = None
fin_rect = None
class MOUSE():
    def __init__(self):
        super(MOUSE, self).__init__()

        # globals
        self.START_POINT = None
        self.END_POINT = None

    def on_move(self, x, y):
        if (self.START_POINT is not None):
            self.END_POINT = (x, y)

            global mov_rect
            mov_rect = (*self.START_POINT, *self.END_POINT)

    def on_click(self, x, y, button, pressed):
        if 'right' in str(button):
            return False

        if (self.START_POINT is None) & (pressed is True):
            self.START_POINT = (x, y)
        if (self.START_POINT is not None) & (pressed is False):
            self.END_POINT = (x, y)

            global fin_rect
            fin_rect = (*self.START_POINT, *self.END_POINT)
            return False

    def listen(self):
        with mouse.Listener(
                on_click=self.on_click,
                on_move=self.on_move,
        ) as listener:
            listener.join()


class SCREENER(QtWidgets.QMainWindow):
    def __init__(self):
        super(SCREENER, self).__init__()

        self.rect = QtWidgets.QWidget(self)
        self.rect.setStyleSheet('background:rgba(255,255,255,0.2)')
        self.rect.setGeometry(0,0,0,0)

        # globals
        self.DARK_SIZE = 15

        # logical funcs init
        self.screen_processing()
        self.frame_build()
        self.select_area_rect()
        self.draw_area_rect()

        # run
        self.run()

    def screen_processing(self):
        img = ImageGrab.grab()
        pixels = img.load()
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                rgb_darked = tuple(color - self.DARK_SIZE for color in pixels[i, j])
                pixels[i, j] = (rgb_darked[0], rgb_darked[1], rgb_darked[2])
        img.save('temp/bg.jpeg')

    def frame_build(self):
        self.setFixedSize(user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet('background: url(\'temp/bg.jpeg\')')
    
    def select_area_rect(self):
        mouse = MOUSE()
        listen = threading.Thread(target=mouse.listen, args=[], daemon=True)
        listen.start()
    
    def draw_area_rect(self):
        if threading.current_thread().name == 'MainThread':
            threading.Thread(target=self.draw_area_rect, args=[], daemon=True).start()
        else:
            global mov_rect, fin_rect
            while True:
                time.sleep(0.01)
                if mov_rect != None:

                    x, y, w, h = mov_rect[0], mov_rect[1], mov_rect[2] - mov_rect[0], mov_rect[3] - mov_rect[1]
                    self.rect.setGeometry(x, y, w, h)
                
                if fin_rect != None:
                    self.save()
                    keyboard.press_and_release('alt+f4')
                    break
    
    def save(self):
        pic_num = len(os.listdir('save/'))
        img = ImageGrab.grab(bbox=fin_rect)

        pixels = img.load()
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                rgb_darked = tuple(color - self.DARK_SIZE for color in pixels[i, j])
                pixels[i, j] = (rgb_darked[0], rgb_darked[1], rgb_darked[2])
        img.save(f'save/{pic_num}.jpeg')

    def run(self):
        self.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    user32 = ctypes.windll.user32

    wnd = SCREENER()

    os.remove('temp/bg.jpeg')
    sys.exit(app.exec())
    
    