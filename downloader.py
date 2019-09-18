import os
import pickle
import vk_api
import requests

from vk_api import audio

from time import time

__version__ = 'VK Music Downloader v1.0'

APP_MESSAGE = '''   __                 _           
  / _|_   _  ___ _ __| | ___  ___ 
 | |_| | | |/ _ \ '__| |/ _ \/ _ \
 |  _| |_| |  __/ |  | |  __/  __/
 |_|  \__,_|\___|_|  |_|\___|\___|
                                  '''

vk_file = "vk_config.v2.json"
REQUEST_STATUS_CODE = 200 
path = 'vk_music/'

def auth_handler(remember_device=None):
    code = input("Введите код подтверждения\n> ")
    if (remember_device == None):
        remember_device = True
    return code, remember_device

def SaveUserData(login, password, profile_id):
    USERDATA_FILE = r"AppData/UserData.datab"
    SaveData = [login, password, profile_id]

    with open(USERDATA_FILE, 'wb') as dataFile:
        pickle.dump(SaveData, dataFile)

def Auth(new=False):
    try:
        USERDATA_FILE = r"AppData/UserData.datab" #файл хранит логин, пароль и id
        global my_id
        if (os.path.exists(USERDATA_FILE) and new == False):
            with open(USERDATA_FILE, 'rb') as DataFile:
                LoadedData = pickle.load(DataFile)

            login = LoadedData[0]
            password = LoadedData[1]
            my_id = LoadedData[2]
        else:
            if (os.path.exists(USERDATA_FILE) and new == True):
                os.remove(USERDATA_FILE)

            login = str(input("Введите логин\n> ")) 
            password = str(input("Введите пароль\n> ")) 
            my_id = str(input("Введите id профиля\n> "))
            SaveUserData(login, password, my_id)

        SaveData = [login, password, my_id]
        with open(USERDATA_FILE, 'wb') as dataFile:
            pickle.dump(SaveData, dataFile)

        vk_session = vk_api.VkApi(login=login, password=password)
        try:
            vk_session.auth()
        except:
            vk_session = vk_api.VkApi(login=login, password=password, 
                auth_handler=auth_handler)
            vk_session.auth()
        print('Вы успешно авторизовались.')
        vk = vk_session.get_api()
        global vk_audio 
        vk_audio = audio.VkAudio(vk_session)
    except KeyboardInterrupt:
        print('Вы завершили выполнение программы.')

def main():
    try:
        if (not os.path.exists("AppData")):
            os.mkdir("AppData")
        if not os.path.exists(path):
            os.makedirs(path)

        auth_dialog = str(input("Авторизоваться заново? yes/no\n> "))
        if (auth_dialog == "yes"):
            Auth(new=True)
        elif (auth_dialog == "no"):
            Auth(new=False)
        else:
            print('Ошибка, неверный ответ.')
            main()
        print('Подготовка к скачиванию...')
        os.chdir(path) #меняем текущую директорию

        audio = vk_audio.get(owner_id=my_id)[0]
        print('Будет скачано:', len(vk_audio.get(owner_id=my_id)), 'аудиозаписей.')
        count = 0
        time_start = time() # сохраняем время начала скачивания
        print("Скачивание началось...\n")
                # собственно циклом загружаем нашу музыку 
        for i in vk_audio.get(owner_id=my_id):
            try:
                print('Скачивается: ' + i["artist"] + " - " + i["title"]) # выводим информацию о скачиваемой в данный момент аудиозаписи
                count += 1
                r = requests.get(audio["url"])
                if r.status_code == REQUEST_STATUS_CODE:
                    print('Скачивание завершено: ' + i["artist"] + " - " + i["title"])
                    with open(i["artist"] + ' - ' + i["title"] + '.mp3', 'wb') as output_file:
                        output_file.write(r.content)
            except OSError:
                print("!!! Не удалось скачать аудиозапись №", count)
        time_finish = time()
        print("" + vk_audio.get(owner_id=my_id) + " аудиозаписей скачано за: ", 
                                            time_finish - time_start + " сек.")
    except KeyboardInterrupt:
        print('Вы завершили выполнение программы.')

if __name__ == '__main__':
    print(APP_MESSAGE)
    print(__version__ + "\n")
    main()