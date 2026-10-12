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
        # Реєструємо обробник у точці розширення decide_executeGesture замість підміни inputCore.manager.executeGesture.
        # Інші додатки (наприклад NVDAExtensionGlobalPlugin) підміняють executeGesture і не викликають попередній обробник,
        # а decide_executeGesture викликають і ядро NVDA, і вони.
        inputCore.decide_executeGesture.register(self.executeGesture)
        # В окремому потоці перевіряємо наявність оновлень
        threading.Thread(target=ApplicationUpdater.onCheckForUpdates).start()

    def terminate(self):
        inputCore.decide_executeGesture.unregister(self.executeGesture)
        super(GlobalPlugin, self).terminate()

    # Метод, який виконується при натисненні клавіш.
    # Повертає True, якщо NVDA має обробити жест як звичайно, і False, якщо тренажер його перехопив
    def executeGesture(self, gesture):
        # В жестах, які виконуються на сенсорному екрані немає властивості _keyNamesInDisplayOrder, тому ми додаємо її щоб не було помилок
        if not hasattr(gesture, "_keyNamesInDisplayOrder"):
            gesture._keyNamesInDisplayOrder = None
        # print(gesture.displayName)
        # print(gesture.vkCode)
        # print(gesture.scanCode)
        # print(gesture._keyNamesInDisplayOrder)
        
        # Перевіряємо чи була натиснута комбінація клавіш, яка вмикає і вимикає роботу тренажера
        # Якщо ні, тоді викликаємо стандартну функцію обробки натиснення клавіш
        if gesture._keyNamesInDisplayOrder == ("NVDA", "shift", "k"):
            speech.cancelSpeech()
            Game.toggling = not Game.toggling
            if Game.toggling:
                playWaveFile(BASE_DIR+"/media/starting simulator.wav")
                message("Клавіатурний тренажер увімкнено")
                # Якщо є доступні оновлення, тоді активуємо клас меню оновлень
                # В іншому випадку просто активуємо головне меню
                if ApplicationUpdater.is_update_available: Game.state = MenuUpdate()
                else: Game.state = MainMenu()
                return False
            else:
                # Викликаємо метод виходу активного на даний момент розділу, щоб він в свою чергу викликав даний метод по ланцюжку вверх
                if Game.state: Game.state.exit()
                return False
        if Game.toggling and Game.state:
            speech.cancelSpeech()
            isLanguageSwich = True if gesture._keyNamesInDisplayOrder in (("alt", "leftShift"), ("control", "leftShift")) else False
            # Якщо була натиснута комбінація клавіш для зміни мови, тоді не потрібно її перехоплювати, а виконати зміну мови навіть з увімкненим тренажером
            if isLanguageSwich:
                gesture.SPEECHEFFECT_CANCEL = False
                gesture.send()
                return False
            elif not isinstance(Game.state, PositionFingersOnKeys) and gesture._keyNamesInDisplayOrder[0] in ("leftControl", "rightControl", "leftShift", "rightShift"):
                return True
            else: 
                Game.state.keys_action(gesture)
                return False
        return True

