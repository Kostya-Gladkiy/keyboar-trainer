import sys
sys.path.insert(0, ".")
from .menu import *
from .lessons import *


UkrainianSymbolicDictationMenu.items = (
    {
        "name": "Теорія символьних диктантів",
        "obj": TheoryOfSymbolicDictation,
        "type": "theory",
    },
    {
        "name": "Диктант літер основного ряду",
        "obj": BySymbolicDictationUkraine1,
        "type": "lesson",
    },
    {
        "name": "Диктант літер з акцентом на верхній ряд",
        "obj": BySymbolicDictationUkraine2,
        "type": "lesson",
    },
    {
        "name": "Диктант літер з акцентом на нижній ряд",
        "obj": BySymbolicDictationUkraine3,
        "type": "lesson",
    },
    {
        "name": "Диктант літер трьох рядів",
        "obj": BySymbolicDictationUkraine4,
        "type": "lesson",
    },
)


UkrainianWordsDictationMenu.items = (
    {
        "name": "Словесний диктант з літер основного ряду",
        "obj": ByWordsDictationUkraine,
        "type": "lesson",
    },
    {
        "name": "Словесний диктант з літер двох рядів",
        "obj": ByWordsDictationUkraine2,
        "type": "lesson",
    },
    {
        "name": "Словесний диктант з літер трьох рядів",
        "obj": ByWordsDictationUkraine3,
        "type": "lesson",
    },
    {
        "name": "Диктант слів з великими літерами",
        "obj": WordsWithCapitalLetters,
        "type": "lesson",
    },
)


EnglishWordsDictationMenu.items = (
    {
        "name": "Словесний диктант з літер  двох рядів",
        "obj": ByWordsDictationEnglish2,
        "type": "lesson",
    },
)


EnglishSymbolicDictationMenu.items = (
    {
        "name": "Диктант літер основного ряду",
        "obj": BySymbolicDictationEnglish1,
        "type": "lesson",
    },
    {
        "name": "Диктант літер з акцентом на верхній ряд",
        "obj": BySymbolicDictationEnglish2,
        "type": "lesson",
    },
    {
        "name": "Диктант літер з акцентом на нижній ряд",
        "obj": BySymbolicDictationEnglish3,
        "type": "lesson",
    },
    {
        "name": "Диктант літер трьох рядів",
        "obj": BySymbolicDictationEnglish4,
        "type": "lesson",
    },
)


MainMenu.items = [
    {
        "name": "Освоєння правильного розташування пальців",
        "obj": PositionFingersOnKeys,
        "type": "theory",
        "description": "Вмикайте цей режим якщо ви не впевнені в тому, що усі клавіші натискаєте правильними пальцями",
    },
    {
        "name": "Диктант українських літер",
        "obj": UkrainianSymbolicDictationMenu,
        "type": "menu",
    },
    {
        "name": "Диктант англійських літер",
        "obj": EnglishSymbolicDictationMenu,
        "type": "menu",
    },
    {
        "name": "Диктант українських слів",
        "obj": UkrainianWordsDictationMenu,
        "type": "menu",
    },
    {
        "name": "Диктант англійських слів",
        "obj": EnglishWordsDictationMenu,
        "type": "menu",
    },
    {
        "name": "Числовий диктант",
        "obj": NumericalDictation,
        "type": "lesson",
    },
    {
        "name": "Диктант знаків пунктуації",
        "obj": PunctuationDictation,
        "type": "lesson",
    },
    {
        "name": "Диктант тексту",
        "obj": TextDictation,
        "type": "lesson",
    },
]