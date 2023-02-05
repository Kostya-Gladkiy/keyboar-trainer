import os

from  configobj  import  ConfigObj
from configobj.validate import Validator
import globalVars
import languageHandler
import addonHandler
import queueHandler
import speech
import ui


lang = languageHandler.getLanguage().split("_")[0]
BASE_DIR = os.path.dirname(__file__)


def message(text):
    """
    Функція, яка озвучує переданий їй текст.
    Прийшлось трохи модефікувати стандартну функцію NVDA, бо вона конфліктувала з доповненням Bluetooth Audio.
    """
    queueHandler.queueFunction(queueHandler.eventQueue, ui.message, text)


def speakChar(char, useCharacterDescriptions=False):
    if not useCharacterDescriptions:
        queueHandler.queueFunction(queueHandler.eventQueue, speech.speakSpelling, char)
    else:
        queueHandler.queueFunction(queueHandler.eventQueue, speech.speakSpelling, char, useCharacterDescriptions=True)


spec = (
    "maximum number of words in Ukrainian language of level 1 = integer(default=0)",
    "maximum number of words in Ukrainian language of level 2 = integer(default=0)",
    "maximum number of words in Ukrainian language of level 3 = integer(default=0)",
    "maximum number of words in English language of level 2 = integer(default=0)",
    "maximum number of characters in Ukrainian 1 = integer(default=0)",
    "maximum number of characters in Ukrainian 2 = integer(default=0)",
    "maximum number of characters in Ukrainian 3 = integer(default=0)",
    "maximum number of characters in Ukrainian 4 = integer(default=0)",
    "maximum number of characters in English 1 = integer(default=0)",
    "maximum number of characters in English 2 = integer(default=0)",
    "maximum number of characters in English 3 = integer(default=0)",
    "maximum number of characters in English 4 = integer(default=0)",
    "maximum number of characters in numerical dictation = integer(default=0)",
    "maximum number of characters in capital letters dictation = integer(default=0)",
    "maximum number of characters in text dictation in Ukrainian = integer(default=0)",
    "maximum number of characters in punctuation dictation = integer(default=0)",
)


class config:
    def __init__(self):
        self.path = os.path.join(globalVars.appArgs.configPath, "keyboard_simulator.ini")
        self.conf = ConfigObj(self.path, configspec=spec )
        validator = Validator()
        self.conf.validate(validator, copy=True)
        self.conf.write()
    
    def get(self, key):
        return self.conf[key]
    
    def set(self, key, value):
        self.conf[key] = value
        self.conf.write()

conf = config()