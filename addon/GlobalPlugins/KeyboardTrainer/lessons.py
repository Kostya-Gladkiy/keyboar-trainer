# -*- coding:utf-8 -*-
from .menu import *
from .game import Game
from .symbols_description import symbols_description
from .cnf import conf, lang, message, speakChar, BASE_DIR
import sys
from threading import Timer
import time
import random
import os
import ctypes

import speech
import api
import config
from nvwave import playWaveFile

sys.path.insert(0, ".")


def levenshtein_distance(s, t):
	"""
	Рахує мінімальну кількість редагувальних операцій, необхідних для перетворення рядка s в рядок t.
	"""
	m = len(s)
	n = len(t)
	d = [[0] * (n + 1) for i in range(m + 1)]

	for i in range(m + 1):
		d[i][0] = i

	for j in range(n + 1):
		d[0][j] = j

	for j in range(1, n + 1):
		for i in range(1, m + 1):
			if s[i-1] == t[j-1]:
				d[i][j] = d[i-1][j-1]
			else:
				d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + 1)

	return d[m][n]

class Category:
	"""
	Клас, в якому описані загальні властивості і методи, які повинні бути присутні в усіх диктантах.
	Кожен розділ диктанту унаслідується від цього класу.
	"""
	symbols_description = symbols_description
	time_start = False
	time_last_error = 0
	key_in_config_max_count = False
	mistakes = []
	successfuls = []
	lesson_duration = 180
	message_on_exit = "Диктант завершено"
	parent_menu = MainMenu

	def __init__(self):
		self.mistakes = []
		self.successfuls = []

	def start_timer(self):
		if not self.time_start:
			self.time_start = time.time()

	def check_record(self):
		if not self.time_start or time.time() - self.time_start < self.lesson_duration:
			return
		count_chars = sum([len(value) for value in self.successfuls])
		count_errors = sum([len(value) for value in self.mistakes])
		# Кількість символів за хвилину
		a = count_chars / (time.time() - self.time_start) * 60
		a = int(a)
		message("Ви в середньому набирали "+str(a)+" символів в хвилину")
		errors = str(int(count_errors))
		message("Ви допустили "+errors+" помилок")
		if not self.key_in_config_max_count:
			return
		if a > conf.get(self.key_in_config_max_count):
			message("Вітаю з перевершенням попереднього рекорду")
			conf.set(self.key_in_config_max_count, a)

	def is_finish(self):
		if not self.time_start:
			return False

		def s():
			playWaveFile(BASE_DIR+"/media/finish.wav")
			message("Вітаю, ви закінчили урок")
			self.exit(audio=False)
		if time.time() - self.time_start >= self.lesson_duration:
			Timer(.2, s).start()
			return True
		else:
			return False

	def exit(self, audio=True):
		if self.message_on_exit:
			message(self.message_on_exit)
		self.check_record()
		if Game.toggling:
			if audio:
				playWaveFile(BASE_DIR+"/media/back.wav")
			Game.state = self.parent_menu()
		else:
			MainMenu.exit(MainMenu)

	def input_action(self, ch):
		pass

	def keys_action(self, gesture):
		char = self.char_from_gesture(gesture)
		if gesture.vkCode == 27:
			self.exit()
		elif char:
			self.input_action(char)

	def char_from_gesture(self, gesture):
		labels = [8, 9, 13]
		if gesture.vkCode in labels:
			return False
		keyStates = (ctypes.c_byte*256)()
		for vk, ext in gesture.generalizedModifiers:
			try:
				keyStates[vk] = 0x80
			except Exception:
				return False
		charBuf = ctypes.create_unicode_buffer(6)
		focus = api.getFocusObject()
		hkl = ctypes.windll.user32.GetKeyboardLayout(focus.windowThreadID)
		res = ctypes.windll.user32.ToUnicodeEx(
			gesture.vkCode, gesture.scanCode, keyStates, charBuf, len(charBuf), 0x4, hkl)
		keyStates = False
		char = ""
		if res > 0:
			for ch in charBuf[:res]:
				char += ch
		return char


# Класи словесних диктантів
class ByWordsDictation(Category):
	"""
	Клас, який описує логіку словесних диктантів.
	Від нього наслідуються класи словесних диктантів різного рівня і різними мовами.
	"""
	entered_text = ""
	word = ""
	message_on_exit = "Словесний диктант завершено"
	time_last_error = 0
	is_all_words_in_lowercase_letters = True

	def __init__(self):
		super().__init__()
		self.words = []
		self.load_words()
		self.word = self.next_word()
		message("Словесний диктант увімкнено")
		message("Після кожного написаного слова натискайте клавішу пробіл.")
		message("Перше слово: "+self.word)

	def load_words(self):
		with open(BASE_DIR+self.file_name, "r", encoding="utf-8") as f:
			self.words = f.read().split("\n")
		self.words = list(set(self.words))
		random.shuffle(self.words)
		if self.is_all_words_in_lowercase_letters:
			self.words = [word.lower() for word in self.words]

	def next_word(self):
		if not self.words:
			self.load_words()
		self.word = self.words.pop(0)
		return self.word

	def report_location_of_symbol(self):
		try:
			char = self.word[len(self.entered_text)]
			char = char.lower()
		except Exception:
			return False
		if char in self.symbols_description:
			speakChar(char)
			message(self.symbols_description[char])
		else:
			message("На жаль, розташування цього символу поки невідомо")

	def get_count_errors(self, a, b):
		def recursive(i, j):
			if i == 0 or j == 0:
				# якщо один із рядків порожній, відстань до другого рядка дорівнює довжині ee
				# тобто n вставка
				return max(i, j)
			elif a[i - 1] == b[j - 1]:
				return recursive(i - 1, j - 1)
			else:
				# інакше вибираю мінімальний варіант із трьох
				return 1 + min(
					recursive(i, j - 1),  # видалення
					recursive(i - 1, j),   # вставка
					recursive(i - 1, j - 1)  # Заміна
				)
		return recursive(len(a), len(b))

	def keys_action(self, gesture):
		if gesture.vkCode == 8:
			# Видаляємо останній введений символ
			if self.entered_text:
				speakChar(self.entered_text[-1])
				message("видалено")
				self.entered_text = self.entered_text[:-1]
		elif gesture.vkCode == 112:
			# Озвучуємо підказку щодо наступного символа
			self.report_location_of_symbol()
		else:
			super().keys_action(gesture)

	def input_action(self, ch):
		speech.cancelSpeech()
		if ch == " " and self.entered_text == self.word:
			self.successfuls.append(self.entered_text)
			playWaveFile(BASE_DIR+"/media/success.wav")
			self.entered_text = ""
			self.next_word()

			def s():
				if not self.is_finish():
					message(self.word)
			Timer(.1, s).start()
		elif ch == " " and self.entered_text != self.word:
			is_second_click = True if time.time(
			) - self.time_last_error <= .5 and self.time_last_error else False
			self.time_last_error = time.time()
			if self.entered_text != "":
				def calculate_errors():
					self.mistakes.append(
					"#"*levenshtein_distance(self.word, self.entered_text))
				threading.Thread(target=calculate_errors).start()
			self.entered_text = ""
			playWaveFile(BASE_DIR+"/media/error.wav")

			def s():
				if self.is_finish():
					return
				elif is_second_click:
					speakChar(self.word)
				else:
					message(self.word)
			Timer(.1, s).start()
		else:
			self.start_timer()
			self.entered_text += ch
			speakChar(ch)


class ByWordsDictationUkraine(ByWordsDictation):
	file_name = "/text/uk/words.txt"
	key_in_config_max_count = "maximum number of words in Ukrainian language of level 1"


class ByWordsDictationUkraine2(ByWordsDictation):
	file_name = "/text/uk/words2.txt"
	key_in_config_max_count = "maximum number of words in Ukrainian language of level 2"


class ByWordsDictationUkraine3(ByWordsDictation):
	file_name = "/text/uk/words3.txt"
	key_in_config_max_count = "maximum number of words in Ukrainian language of level 3"


class ByWordsDictationEnglish2(ByWordsDictation):
	file_name = "/text/en/words2.txt"
	key_in_config_max_count = "maximum number of words in English language of level 2"


class WordsWithCapitalLetters(ByWordsDictation):
	key_in_config_max_count = "maximum number of characters in capital letters dictation"
	file_name = "/text/uk/Words with capital letters.txt"
	is_all_words_in_lowercase_letters = False


# Класи символьних диктантів
class BySymbolicDictation(Category):
	"""
	Клас, в якому описана логіка роботи символьних диктантів.
	Від цього класу наслідуються класи символьних диктантів різних рівнів і різними мовами.
	Також від нього наслідується клас диктанту знаків пунктуації.
	"""
	char = ""
	chars = ""
	message_on_startup = "Диктант літер увімкнено"

	def __init__(self):
		super().__init__()
		self.chars = list(self.chars)
		random.shuffle(self.chars)
		self.char = self.next_char()
		message(self.message_on_startup)
		message("Ставимо руки на стартову позицію і починаємо")
		speakChar(self.char)

	def next_char(self):
		self.char = random.choice(self.chars)
		return self.char

	def report_location_of_symbol(self):
		char = self.char.lower()
		if char in self.symbols_description:
			speakChar(char)
			message(self.symbols_description[char])
		else:
			message("На жаль, розташування цього символу поки невідомо")

	def keys_action(self, gesture):
		if gesture.vkCode == 112:
			self.report_location_of_symbol()
		else:
			super().keys_action(gesture)

	def input_action(self, ch):
		speech.cancelSpeech()
		if self.char == ch:
			self.start_timer()
			self.successfuls.append(ch)
			playWaveFile(BASE_DIR+"/media/success.wav")
			self.next_char()

			def s():
				if self.is_finish():
					return
				speakChar(self.char)
			Timer(.2, s).start()
		else:
			is_second_click = True if time.time(
			) - self.time_last_error <= .5 and self.time_last_error else False
			self.time_last_error = time.time()
			if ch != " ":
				self.mistakes.append(self.char)
			count_char_in_list = len(
				[item for item in self.chars if item == ch])
			if ch != " " and self.time_start and count_char_in_list < len(self.chars)/3 and count_char_in_list < 5:
				self.chars += self.char
			playWaveFile(BASE_DIR+"/media/error.wav")

			def s():
				if self.is_finish():
					return
				speakChar(self.char, is_second_click)
			Timer(.1, s).start()


class BySymbolicDictationUkraine1(BySymbolicDictation):
	key_in_config_max_count = "maximum number of characters in Ukrainian 1"
	chars = "фівапролджє"


class BySymbolicDictationUkraine2(BySymbolicDictation):
	key_in_config_max_count = "maximum number of characters in Ukrainian 2"
	chars = "йцукенгшщзхїґ"*3+"фівапролджє"


class BySymbolicDictationUkraine3(BySymbolicDictation):
	key_in_config_max_count = "maximum number of characters in Ukrainian 3"
	chars = "ячсмитьбю"*6+"йцукенгшщзхї"+"фівапролджє"


class BySymbolicDictationUkraine4(BySymbolicDictation):
	key_in_config_max_count = "maximum number of characters in Ukrainian 4"
	chars = "йцукенгшщхїфівапролджєячсмитьбюґ"


class BySymbolicDictationEnglish1(BySymbolicDictation):
	key_in_config_max_count = "maximum number of characters in English 1"
	chars = "asdfghjkl"


class BySymbolicDictationEnglish2(BySymbolicDictation):
	key_in_config_max_count = "maximum number of characters in English 2"
	chars = "qwertyuiop"*3+"asdfghjkl"


class BySymbolicDictationEnglish3(BySymbolicDictation):
	key_in_config_max_count = "maximum number of characters in English 3"
	chars = "zxcvbnm"*6+"qwertyuiop"+"asdfghjkl"


class BySymbolicDictationEnglish4(BySymbolicDictation):
	key_in_config_max_count = "maximum number of characters in English 4"
	chars = "qwertyuiopasdfghjklzxcvbnm"


class PunctuationDictation(BySymbolicDictation):
	key_in_config_max_count = "maximum number of characters in punctuation dictation"
	message_on_startup = "Диктант знаків пунктуації увімкнено"
	chars = "'!\"№;%:?*()_-=+/.,"


class NumericalDictation(ByWordsDictation):
	key_in_config_max_count = "maximum number of characters in numerical dictation"
	message_on_exit = "Числовий диктант завершено"

	def __init__(self):
		Category().__init__()
		a = list(range(10))
		b = list(range(10, 100))
		c = list(range(100, 1000))
		for item in [a, b, c]:
			random.shuffle(item)
		self.words = a + b[:25] + c[:50]
		self.words = [str(word) for word in self.words]
		self.word = self.next_word()
		message("Числовий диктант увімкнено")
		message("Після кожного написаного числа натискайте клавішу пробіл.")
		message("Перше число: "+self.word)


class DictationSentencesWithPunctuationMarks(Category):
	key_in_config_max_count = "maximum number of characters in dictation of sentences with punctuation marks"
	sentence = []
	entered_text = ""
	message_on_exit = "Текстовий диктант завершено"

	def __init__(self):
		f = open(BASE_DIR+"/text/uk/sentences with punctuation marks.txt", "r", encoding="utf-8")
		self.text = f.read()
		f.close()
		self.sentence = self.text.split("\n")
		self.sentence = [sentence+" " for sentence in self.sentence]
		random.shuffle(self.sentence)
		# Видаляємо пробіл після останнього слова в останньому рядку
		self.sentence[-1] = self.sentence[-1][-1:]
		# Зберігаємо рівень символа щоб повернути його до цього ж значення після завершення диктанту
		self.symbol_level = config.conf["speech"]["symbolLevel"]
		config.conf["speech"]["symbolLevel"] = 300
		message(self.sentence[0])

	def exit(self):
		config.conf["speech"]["symbolLevel"] = self.symbol_level
		super().exit()

	def input_action(self, ch):
		if ch == self.sentence[0][0]:
			self.start_timer()
			self.successfuls.append(ch)
			speakChar(ch)
			self.sentence[0] = self.sentence[0][1:]
		else:
			self.mistakes.append(ch)
			playWaveFile(BASE_DIR+"/media/error.wav")
			is_second_click = True if time.time(
			) - self.time_last_error <= .5 and self.time_last_error else False
			self.time_last_error = time.time()
			if is_second_click:
				speakChar(self.sentence[0][0])
			else:
				message(self.sentence[0])
		if not self.sentence[0]:
			self.sentence.pop(0)
			def s():
				if not self.is_finish():
					message(self.sentence[0])
			Timer(.1, s).start()
			# try:
				# message(self.sentence[0])
			# except Exception as e:
				# print(e)
		if not self.sentence:
			self.exit()


class DictationOfSentences(Category):
	key_in_config_max_count = "maximum number of characters in sentences dictation in Ukrainian"
	entered_text = ""
	sentence = ""
	message_on_exit = "Диктант речень завершено"
	time_last_error = 0
	file_name = "/text/uk/sentences.txt"

	def __init__(self):
		super().__init__()
		self.sentences = []
		self.load_sentences()
		self.sentence = self.next_sentence()
		message("Диктант речень увімкнено")
		message("Після кожного написаного речення натискайте клавішу enter.")
		message("Перше речення: "+self.sentence)

	def load_sentences(self):
		with open(BASE_DIR+self.file_name, "r", encoding="utf-8") as f:
			self.sentences = f.read().split("\n")
		random.shuffle(self.sentences)

	def next_sentence(self):
		if not self.sentences:
			self.load_sentence()
		self.sentence = self.sentences.pop(0)
		return self.sentence

	def next(self):
		if self.entered_text == self.sentence:
			self.successfuls.append(self.entered_text)
			playWaveFile(BASE_DIR+"/media/success.wav")
			self.entered_text = ""
			self.next_sentence()

			def s():
				if not self.is_finish():
					message(self.sentence)
			Timer(.1, s).start()

	def keys_action(self, gesture):
		if gesture.vkCode == 13:
			# Якщо було натиснуто клавішу enter
			self.next()
		elif gesture.vkCode == 8:
			# Видаляємо останній введений символ
			if self.entered_text:
				speakChar(self.entered_text[-1])
				message("видалено")
				self.entered_text = self.entered_text[:-1]
		elif gesture.vkCode == 112:
			# Озвучуємо підказку щодо наступного символа
			message(self.sentence)
		else:
			super().keys_action(gesture)

	def input_action(self, ch):
		speech.cancelSpeech()
		self.start_timer()
		word = self.entered_text.split(" ")[-1]
		if ch != " ":
			if config.conf["keyboard"]["speakTypedCharacters"]: speakChar(ch)
			self.entered_text += ch
		elif not self.entered_text:
			message(self.sentence)
		elif self.entered_text == self.sentence:
			self.next()
		elif self.entered_text.endswith(" "):
			# Озвучуємо частину речення, яку залишилось ввести
			message(self.sentence.replace(self.entered_text, ""))
		elif not self.sentence.startswith(self.entered_text+ch):
			playWaveFile(BASE_DIR+"/media/error.wav")
			count_words = len(self.entered_text.split(" "))
			last_word = self.entered_text.split(" ")[-1]
			last_word_without_fail = self.sentence.split(" ")[count_words-1]
			words = self.entered_text.split(" ")[:-1]

			def calculate_errors(a, b):
					self.mistakes.append("#"*levenshtein_distance(a, b))
			threading.Thread(target=calculate_errors, args=[last_word_without_fail, last_word]).start()
			self.entered_text = " ".join(words)
			if self.entered_text:
				# Після видалення слова пробіл потрібно залишити, але окрім випадків, коли введених слів не залишилось
				self.entered_text = self.entered_text+ch
			char_count = len(self.entered_text)
			message(self.sentence[char_count:])
		else:
			# Слово написано без помилок
			message(word)
			self.entered_text += ch


class PositionFingersOnKeys(Category):
	message_on_exit = "Режим освоєння розташування пальців вимкнено"
	fingers = {
		"Вказівний палець лівої руки": "70 82 84 71 86 66 53 54",
		"Вказівний палець правої руки": "72 74 89 85 77 78 55 56 37",
		"Середній палець лівої руки": "68 69 67 52",
		"Середній палець правої руки": "188 73 75 56 38 40 12 57",
		"Безіменний палець лівої руки": "83 87 88 51",
		"Безіменний палець правої руки": "76 79 190 39 48",
		"Мізинець лівої руки": "49 50 51 65 81 90 9 20 16 17 192 160 162",
		"Мізинець правої руки": "219 80 221 222 191 8 13 220 187 189 186 161 163",
		"Великий палець лівої рукиь": "164 91",
		"Великий палець правої рукиь": "165 93",
		"Великий палець зручної руки": "32",
		"Пальцями лівої руки": "112 113 114 115 116 117",
		"Пальцями правої руки": "118 119 120 121 122 123",
	}

	def __init__(self):
		super().__init__()
		message("Теорію розташування пальців увімкнено")
		message("Натискайте різні літери на клавіатурі, а тренажер повідомлятиме вам яким пальцем потрібно натискати дану клавішу")

	def keys_action(self, gesture):
		if gesture.vkCode == 27:
			self.exit()
			return True
		finger = next((finger for finger in self.fingers if str(
			gesture.vkCode) in self.fingers[finger].split(" ")), "Пальцями правої руки")
		if finger:
			char = self.char_from_gesture(gesture)
			if char:
				speakChar(char)
			else:
				message(gesture.displayName)
			message(finger)


class Theory():
	"""
	Клас, в якому описана загальна логіка тереотичних уроків і від якого наслідуються усі інші класи тереотичних уроків
	"""
	current_message = -1
	start_message = False
	messages = []

	def __init__(self):
		message(self.start_message)
		message(
			"Для того, щоб прослухати усі рекомендації, використовуй клавіші стрілка вгору і стрілка вниз")

	def message(self):
		message(self.messages[self.current_message])

	def next(self):
		if self.current_message == len(self.messages)-1:
			self.exit()
			return
		self.current_message += 1
		playWaveFile(BASE_DIR+"/media/scrollMenu.wav")
		self.message()

	def previous(self):
		if self.current_message > 0:
			self.current_message -= 1
			playWaveFile(BASE_DIR+"/media/scrollMenu.wav")
			self.message()

	def repeat(self):
		self.message()

	def exit(self):
		if Game.toggling:
			Game.state = self.parent_menu()
		else:
			Menu.exit(Menu)

	def keys_action(self, gesture):
		if gesture.vkCode == 40:
			self.next()
		elif gesture.vkCode == 38:
			self.previous()
		# elif gesture.vkCode == 40: self.repeat()


class TheoryOfSymbolicDictation(Theory):
	start_message = "Вітаю тебе в розділі символьних диктантів"
	messages = [
		"Перед початком диктанту руки завжди потрібно ставити на стартову позицію",
		"Переконайся, що в тебе увімкнено потрібну розкладку клавіатури. В іншому разі, при введені літер, тренажер зараховуватиме кожну літеру як помилку",
		"Якщо ти не пам'ятаєш де знаходиться якась літера, тоді можна натиснути клавішу F1 і тренажер тобі підкаже її розташування, а також підкаже яким пальцем потрібно натискати цю літеру",
		"При введені неправильної літери, тренажер називатиме ту літеру, яку потрібно ввести",
		"Якщо зробити помилку двічі, з тривалістю менш ніж пів секунди, тоді тренажер озвучить слово на ту літеру, яку слід ввести",
		"Якщо натискати клавішу пробіл, тоді можна почути літеру, яку потрібно ввести, і це не вважатиметься помилкою",
		"Також можна двічі натиснути пробіл, щоб почути слово на ту літеру, яку потрібно ввести",
		"Тепер можна приступати до диктанту символів одного ряду",
	]
