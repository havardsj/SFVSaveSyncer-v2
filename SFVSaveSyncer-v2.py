import shutil
import os
import winreg
import time
import hashlib
import subprocess

appdata = os.getenv('LOCALAPPDATA')
filePath = appdata + r'\StreetFighterV\Saved\SaveGames'
var = 1

print("Sync is currently active. Switching steam accounts should automatically load backup files.")
print("As long as this application is running the sync will always be active in the background.")

def checkSum(file):
    try:
        md5_hash = hashlib.md5()

        a_file = open(file, "rb")
        content = a_file.read()
        md5_hash.update(content)
        digest = md5_hash.hexdigest()

        return digest
    except:
        pass


def findActiveUser():
    keys = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\Valve\Steam\ActiveProcess', access=winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
    activeUserKey = winreg.EnumValue(keys, 4)
    return str(activeUserKey[1])


def runBackup(user):
    # try to create backup dir
    try:
        if not os.path.exists(filePath + r"\backup_" + user):
            os.makedirs(filePath + r"\backup_" + user)
    except Exception as ex:
        print(ex)

    # backing up gamesave
    try:
        original1 = filePath + r'\GameSystemSave.sav'
        target1 = filePath + r'\backup_' + user + r'\GameSystemSave_copy.sav'
        original2 = filePath + r'\GameProgressSave.sav'
        target2 = filePath + r'\backup_' + user + r'\GameProgressSave_copy.sav'

        #os.remove(filePath + r'\GameProgressSave.old')
        #os.remove(filePath + r'\GameSystemSave.old')

        shutil.copy(original1, target1)
        shutil.copy(original2, target2)

        print("Backup successful.")
    except Exception as ex:
        print(ex)


def syncSaveFiles(steamID):
    try:
        if not os.path.exists(filePath + r"\backup_" + steamID):
            os.makedirs(filePath + r"\backup_" + steamID)
    except:
        pass

    # rename current save
    try:
        os.rename(filePath + r'\GameSystemSave.sav', filePath + r'\GameSystemSave.old')
        os.rename(filePath + r'\GameProgressSave.sav',filePath + r'\GameProgressSave.old')
    except:
        pass

    # load backed up save
    try:
        shutil.copy(filePath + r'\backup_' + steamID + r'\GameSystemSave_copy.sav', filePath + r'\GameSystemSave.sav')
        shutil.copy(filePath + r'\backup_' + steamID + r'\GameProgressSave_copy.sav', filePath + r'\GameProgressSave.sav')
    except:
        os.rename(filePath + r'\GameSystemSave.old', filePath + r'\GameSystemSave.sav')
        os.rename(filePath + r'\GameProgressSave.old',filePath + r'\GameProgressSave.sav')

        print("No backups found. Initial sync cancelled.")

    gameSystemSave = checkSum(filePath + r'\GameSystemSave.sav')
    gameSystemSave_copy = checkSum(filePath + r'\backup_' + steamID + r'\GameSystemSave_copy.sav')
    gameProgressSave = checkSum(filePath + r'\GameProgressSave.sav')
    gameProgressSave_copy = checkSum(filePath + r'\backup_' + steamID + r'\GameProgressSave_copy.sav')

    if gameSystemSave == gameSystemSave_copy and gameProgressSave == gameProgressSave_copy:
        print("Sync successful, current files match backup.")

        # delete old save
        try:
            os.remove(filePath + r'\GameProgressSave.old')
            os.remove(filePath + r'\GameSystemSave.old')
        except:
            pass


def SFVRunning():
    s = subprocess.check_output('tasklist', shell=True)
    if b"StreetFighterV.exe" in s:
        return True
    else:
        return False


initialUser = findActiveUser()

if not os.path.exists(filePath + r"\backup_" + initialUser):
    runBackup(initialUser)

try:
    syncSaveFiles(initialUser)
except:
    pass

while var == 1 :
    # reading current logged in user
    oldUser = findActiveUser()
    gameRunning = SFVRunning()

    time.sleep(2)

    # checking if there is a new user
    currentUser = findActiveUser()
    gameStillRunning = SFVRunning()

    if gameRunning == True and gameStillRunning == False:
        print("game was recently shut down, backing up")
        runBackup(currentUser)

    if currentUser != oldUser and int(currentUser) != 0:
        print("New user detected, steamID = "+ currentUser + " running sync." )

        time.sleep(1)

        syncSaveFiles(currentUser)
