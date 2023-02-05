# -*- coding:utf-8 -*-
import sys
import threading
from  threading import Timer

from nvwave import playWaveFile

sys.path.insert(0, ".")
from .cnf import conf, lang, message, speakChar, BASE_DIR
from .update import ApplicationUpdater
from .game import Game
from .lessons import *


class MenuUpdate:
    """Клас, який стає активним якщо доступна оновлена версія додатку"""
    
    def __init__(self):
        message("Доступна нова версія клавіатурного тренажера")
        self.report_description_menu()
    
    def report_description_menu(self):
        message("Для того щоб оновити його зараз, натисніть клавішу Enter")
        message("Для того щоб дізнатися про зміни в цій версії, натисніть клавішу пробіл")
        message("Для того щоб відкласти оновлення, натисніть клавішу Escape")
    
    def exit(self):
        ApplicationUpdater.is_update_available = False
        Game.state = MainMenu()
    
    def keys_action(self, gesture):
        if gesture.vkCode == 27: self.exit()
        elif gesture.vkCode == 32:
            if ApplicationUpdater.update_description: message(ApplicationUpdater.update_description)
            else: message("Розробник не надав інформації про це оновлення")
        elif gesture.vkCode == 13:
            message("Триває завантаження")
            threading.Thread(target=ApplicationUpdater.download_update, args=[Game]).start()
        else: self.report_description_menu()


class Menu:
    """
    Клас, в якому описана загальна поведінка меню.
    Від нього наслідуються усі інші класи меню.
    """
    items = ()
    saved_positions = {}
    name = "Головне меню"
    active_menu_item = -1
    
    def __init__(self):
        if self.name in Menu.saved_positions:
            self.active_menu_item = Menu.saved_positions[self.name]
        self.adding_description()
        message(self.name)
        self.report_item_name()
    
    def adding_description(self):
        for item in self.items:
            if item["type"] == "lesson":
                value = conf.get(item["obj"].key_in_config_max_count)
                if value:
                    item	["description"] = "Ваш рекорд: "+str(value)+" символів за хвилину"
    
    def activate_item(self):
        Menu.saved_positions[self.name] = self.active_menu_item
        playWaveFile(BASE_DIR+"/media/enterMenu.wav")
        item = self.items[self.active_menu_item]
        def s():
            type = item["type"]
            if type in ("lesson", "theory", "menu"):
                Game.state = item["obj"]()
                Game.state.parent_menu = self.__class__
            else: item["obj"]()
        Timer(.33, s).start()
    
    def next_item(self):
        if self.active_menu_item < len(self.items)-1:
            self.active_menu_item += 1
            playWaveFile(BASE_DIR+"/media/scrollMenu.wav")
            self.report_item_name()
    
    def previous_item(self):
        if self.active_menu_item > 0:
            self.active_menu_item -= 1
            playWaveFile(BASE_DIR+"/media/scrollMenu.wav")
            self.report_item_name()
    
    def report_item_name(self):
        if self.active_menu_item == -1: return
        message(self.items[self.active_menu_item]["name"])
        if "description" in self.items[self.active_menu_item]:
            message(self.items[self.active_menu_item]["description"])
    
    def exit(self): 
        if not Game.toggling or isinstance(self, MainMenu):
            playWaveFile(BASE_DIR+"/media/closing simulator.wav")
            message("Клавіатурний тренажер вимкнено")
            Menu.saved_positions = {}
            Game.toggling = False
            Game.state = False
        else:
            playWaveFile(BASE_DIR+"/media/back.wav")
            Game.state = MainMenu()
    
    def keys_action(self, gesture): 
        if gesture.vkCode == 27: self.exit()
        elif gesture.vkCode == 40: self.next_item()
        elif gesture.vkCode == 38: self.previous_item()
        elif gesture.vkCode == 13: self.activate_item()
        # else:
            # message("Для переходу між пунктами меню використовуйте стрілочку вверх і стрілочку вниз")
            # message("Для вибору пункту натисніть клавішу Enter")


class UkrainianSymbolicDictationMenu(Menu):
    name = "Меню диктанту українських літер"


class UkrainianWordsDictationMenu(Menu):
    name = "Меню диктанту українських слів"


class EnglishWordsDictationMenu(Menu):
    name = "Меню диктанту англійських слів"


class EnglishSymbolicDictationMenu(Menu):
    name = "Меню диктанту англійських літер"


class MainMenu(Menu):
    name = "Головне меню"
