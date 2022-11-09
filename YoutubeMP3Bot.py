
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from pytube import YouTube
import re
from pathlib import Path
import os
from pydub import AudioSegment
import time

def downloadPlaylist(link):
    # try:
    print(link)
    browser = webdriver.Chrome('chromedriver')
    browser.implicitly_wait(60)
    browser.get(link)  
    length = browser.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[2]/div/ytd-playlist-panel-renderer/div/div[1]/div/div[1]/div[1]/div/div/yt-formatted-string/span[3]').text
    for i in range(0, int(length)):
        currentUrl = browser.current_url
        download_youtube_mp3_from_video_id(currentUrl)
        browser.find_element(By.XPATH, '/html/body').send_keys(Keys.SHIFT, 'n')
        time.sleep(1)


def download_youtube_mp3_from_video_id(id):
    url = id
    yt = YouTube(url)
    status = yt.vid_info['playabilityStatus']['status']
    if status == "UNPLAYABLE":
        print(f"video_id {id} is not playable, cannot download.")
        return

    try: isinstance(yt.length, int)
    except:
        print(f"Could not get video length for {id}. Skipping download.")
        return

    # create condition - if the yt.length > 600 (10 mins), then don't download it
    # if yt.length > 600:
    #     print(f"video_id {id} is longer than 10 minutes, will not download.")
    #     return

    # video = yt.streams.filter(only_audio=True).first()
    video = yt.streams.get_audio_only()

    try: song_title_raw = yt.title
    except:
        print(f'Unable to get title for id {id}. Skipping download.')
        return
    song_title = re.sub('[/".|\'*]','', song_title_raw).strip()
    # song_title = re.sub(' +',' ', song_title)
    print(song_title)
    print(song_title_raw)
    song_path = f"{song_title}"

    download_path = f"saved_mp3s/{song_path}"
    out_file = video.download(download_path)

    # save the file (which will be mp4 format)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)

    # move the mp3 to the root dir
    p = Path(new_file).absolute()
    parent_dir = p.parents[1]
    p.rename(parent_dir / p.name)

    # delete the child dir
    os.rmdir(download_path)

    # rename the mp3 to remove the bad chars
    source_name = f"saved_mp3s/{song_title}.mp3"
    dest_name = f"saved_mp3s/{song_path}.mp3"
    try: os.rename(source_name,dest_name)
    except: print(f"Failed to rename the file: {song_title_raw}")
    setBitrate(Path(f"{dest_name}").absolute())


    # result of success
    print(f"{song_path} has been successfully downloaded. Video id: {id}")
    print(Path(f"{dest_name}").absolute())
    

def setBitrate(file):
    sound = AudioSegment.from_file(file)
   
    sound.export(file, format="mp3", bitrate='320k')

def setDirectoryBitrate(directory):
    for filename in os.listdir(directory):
        file = os.path.join(directory, filename)
        setBitrate(file)

def increaseVolume(song):
    temp = song
    song = AudioSegment.from_file(song)
    while True:
        choice = int(input("1: Normalize\n2: Increase DB"))
        if(choice == 1):
            song = song.normalize()
            break
        if(choice == 2):
            increase = int(input("Increase level DB: "))
            song = song + increase
            break
    song.export(temp, format="mp3", bitrate='320k')

while(True):
    choice = input("1: Single MP3\n2: Playlist MP3\n3: Set Bitrate\n4: Set directory Bitrate\n5: Single MP4\n6: Increase audio volume")
    if(choice == "1"):
        link = input("Link: ")
        download_youtube_mp3_from_video_id(link)
        break
    if(choice == "2"):
        link = input("Link: ")
        downloadPlaylist(link)
        break
    if(choice == "3"):
        file = input("File: ")
        setBitrate(file)
        break
    if(choice == "4"):
        directory = input("Directory: ")
        setDirectoryBitrate(directory)
        break
    if(choice == "5"):
        url = input("URL: ")
        video = YouTube(url)
        video = video.streams.get_highest_resolution()
        video.download()
        break
    if(choice == "6"):
        song = input("song: ")
        increaseVolume(song)
        break
    else:
        print("Invalid choice")
