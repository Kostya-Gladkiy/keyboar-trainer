# -*- coding: UTF-8 -*-

import addonHandler
import gui
import wx
import os
import globalVars

addonHandler.initTranslation()

def onInstall():
	for addon in addonHandler.getAvailableAddons():
		if addon.manifest['name'] in ("keys", "Keys", "Keyboard simulator", "Keyboard trainer", "Keyboard Trainer"):
			addon.requestRemove()