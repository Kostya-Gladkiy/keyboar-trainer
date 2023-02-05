import urllib.request
import os

import addonHandler
import core
import globalVars

from .cnf import conf, lang, message, speakChar


PATH_TO_SERVER = "http://46.254.107.124/addons/keyboard_simulator/"


class ApplicationUpdater:
    # Перший елемент списку це версія додатку, а другий це посилання для завантаження
    is_update_available = False
    update_description = False
    
    def onCheckForUpdates():
        import versionInfo
        NVDAVersion = f"{versionInfo.version_year}.{versionInfo.version_major}.{versionInfo.version_minor}"
        NVDAVersion = int(NVDAVersion.replace(".", ""))
        fp = os.path.join(globalVars.appArgs.configPath, "keys.nvda-addon")
        addon_version = addonHandler.getCodeAddon().manifest["version"]
        addon_version = int(addon_version.replace(".", ""))
        try:
            response = urllib.request.urlopen(PATH_TO_SERVER+"version.txt").read().decode('utf-8')
        except Exception:
            return False
        response = str(response)
        str_last_version = response.split("\n")[0]
        last_version = int(str_last_version.replace(".", ""))
        minimum_version = response.split("\n")[1]
        minimum_version = int(minimum_version.replace(".", ""))
        url = response.split("\n")[-1]
        if last_version > addon_version and NVDAVersion >= minimum_version:
            ApplicationUpdater.is_update_available = (str_last_version, url)
            ApplicationUpdater.get_documentation()
            return True
        else:
            return False

    def download_update(Game):
        str_last_version = ApplicationUpdater.is_update_available[0]
        url = ApplicationUpdater.is_update_available[1]
        try:
            response_addon = urllib.request.urlopen(url).read()
        except Exception:
            message("На жаль, виникла помилка при спробі завантажити оновлення")
            ApplicationUpdater.is_update_available = False
            Game.state = Game.main_menu()
            return
        fp = os.path.join(globalVars.appArgs.configPath, "keys.nvda-addon")
        with open(fp, 'wb') as addon:
            addon.write(response_addon)
        ApplicationUpdater.setup_update(fp)

    def get_documentation():
        doc = False
        url = PATH_TO_SERVER+"documentation/"+ApplicationUpdater.is_update_available[0]+"/uk.txt"
        try:
            doc = urllib.request.urlopen(url).read().decode('utf-8')
        except Exception: pass
        if doc:
            ApplicationUpdater.update_description = str(doc)

    def setup_update(fp):
        curAddons = addonHandler.getAvailableAddons()
        bundle = addonHandler.AddonBundle(fp)
        bundleName = bundle.manifest['name']
        prevAddon = next((addon for addon in curAddons if not addon.isPendingRemove and bundleName == addon.manifest['name']), None)
        if prevAddon:
            prevAddon.requestRemove()
        addonHandler.installAddonBundle(bundle)
        core.restart()
