# -*- coding:utf-8 -*-
import sys
import threading
# from  threading import Timer
# import time
# import random
# import os
# import re
# import ctypes

import globalPluginHandler
# import addonHandler
# import keyboardHandler
# from keyboardHandler import KeyboardInputGesture
import speech
# import scriptHandler
# import api
# from scriptHandler import script
import inputCore
import queueHandler
from nvwave import playWaveFile
# import tones
# import winUser

sys.path.insert(0, ".")
from .cnf import conf, lang, message, speakChar, BASE_DIR
from .symbols_description import symbols_description
from .update import ApplicationUpdater
from .game import Game
from .lessons import *
from .menu import *
from .menu_items import *


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("Клавіатурний тренажер")
    
    def __init__(self):
        super(GlobalPlugin, self).__init__()
        # В класі Game зберігаємо посилання на клас головного меню, щоб мати доступ до основного меню в інших файлах
        Game.MainMenu = MainMenu
        # Зберігаємо посилання на оригінальний метод, який обробляє натиснення клавіш
        self._executeGesture = inputCore.manager.executeGesture
        # Перевизначаємо метод, який спрацьовує при натисненні клавіш
        inputCore.manager.executeGesture = self.executeGesture
        # В окремому потоці перевіряємо наявність оновлень
        threading.Thread(target=ApplicationUpdater.onCheckForUpdates).start()

    # Метод, який виконується при натисненні клавіш
    def executeGesture(self, gesture):
        # print(gesture.displayName)
        # print(gesture.vkCode)
        # print(gesture.scanCode)
        # print(gesture._keyNamesInDisplayOrder)
        
        # Перевіряємо чи була натиснута комбінація клавіш, яка вмикає і вимикає роботу тренажера
        # Якщо ні, тоді викликаємо стандартну функцію обробки натиснення клавіш
        if gesture._keyNamesInDisplayOrder == ("shift", "NVDA", "k"):
            speech.cancelSpeech()
            Game.toggling = not Game.toggling
            if Game.toggling:
                playWaveFile(BASE_DIR+"/media/starting simulator.wav")
                message("Клавіатурний тренажер увімкнено")
                # Якщо є доступні оновлення, тоді активуємо клас меню оновлень
                # В іншому випадку просто активуємо головне меню
                if ApplicationUpdater.is_update_available: Game.state = MenuUpdate()
                else: Game.state = MainMenu()
                return
            else:
                # Викликаємо метод виходу активного на даний момент розділу, щоб він в свою чергу викликав даний метод по ланцюжку вверх
                if Game.state: Game.state.exit()
                return
        if Game.toggling and Game.state:
            speech.cancelSpeech()
            isLanguageSwich = True if gesture._keyNamesInDisplayOrder in (("alt", "leftShift"), ("control", "leftShift")) else False
            # Якщо була натиснута комбінація клавіш для зміни мови, тоді не потрібно її перехоплювати, а виконати зміну мови навіть з увімкненим тренажером
            if isLanguageSwich:
                gesture.SPEECHEFFECT_CANCEL = False
                gesture.send()
            elif not isinstance(Game.state, PositionFingersOnKeys) and gesture._keyNamesInDisplayOrder[0] in ("leftControl", "rightControl", "leftShift", "rightShift"):
                # gesture.send()
                self._executeGesture(gesture)
            else: 
                Game.state.keys_action(gesture)
        else:
            self._executeGesture(gesture)
            # queueHandler.queueFunction(queueHandler.eventQueue, self._executeGesture, gesture)
