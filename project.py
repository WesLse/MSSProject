import os
import glob
import subprocess
from time import sleep
import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD # 16x2 LCD Control

# GPIO basic Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Button Setup
buttonIncreaseVol = 12
buttonDecreaseVol = 13
buttonPlayPause = 19
buttonQuit = 20
buttonNextSong = 21

GPIO.setup(buttonIncreaseVol, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(buttonDecreaseVol, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(buttonPlayPause, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(buttonQuit, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(buttonNextSong, GPIO.IN, GPIO.PUD_UP)

# LCD Setup
lcd_rs = 25
lcd_en = 24
lcd_d4 = 23
lcd_d5 = 17
lcd_d6 = 27
lcd_d7 = 22
lcd_columns = 16
lcd_rows = 2
lcd_backlight = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)
os.chdir('/home/pi/Desktop/MPi3')
songList = glob.glob('*.mp3')
lenList = len(songList)
songIndex = 0

# StartMessage on LCD
startMessage = 'Hello MPi3\nPress PlayButton'
lcd.message(startMessage)
while True :
    if GPIO.input(buttonPlayPause) == False :
        lcd.clear()
        sleep(1)
        break

# Player Setup
player = None         # Play song Object
playFlag = True       # Start Song Flag
playNextFlag = False  # Play Next Song Flag

# Repetition Constant
PAUSE_NEXT = 1
PAUSE_REP = 0.5

# Main Loop
while True :
    
    if playFlag : # Play Song Setup
    
        # Renew Song list
        tmp = glob.glob('*.mp3')
        # print(tmp)
        tmpLen = len(tmp)
        if tmp != songList :
            songList = tmp
            lenList = len(songList)
        # print(songList)
        
        # Quit This Song to Play Next Song
        if playNextFlag : 
            playNextFlag = False
            player.stdin.write('q')
            lcd.clear()
        
        # Play Song
        if songIndex > lenList - 1 :
            songIndex = 0
        text = songList[songIndex]
        player = subprocess.Popen(['omxplayer', '-o', 'both', text], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, close_fds = True)
        isPlayerAlive = player.poll()
        playFlag = False
        
        # Repetition Song Name Setup
        lcd.message('Now Playing\n' + text)
        rows = [text[i:i+lcd_columns] for i in range(0, len(text), 1)]
        n_rows = len(rows)
        x = 0
      
    
    # Repetition SongName on LCD 
    lcd.home()
    lcd.clear()
    lcd.message('Now Playing\n' + rows[x])
    x = x + PAUSE_NEXT
    nxt = x
    if nxt == len(text) :
        sleep(PAUSE_REP)
        x = 0
    else:
        sleep(PAUSE_REP)

    # Play / Pause
    if (GPIO.input(buttonPlayPause) == False) :
        sleep(0.5)
        isPlayerAlive = player.poll()
        if isPlayerAlive != 0 :
            player.stdin.write('p')      
    
    # Quit
    elif (GPIO.input(buttonQuit) == False) :
        sleep(0.5)
        isPlayerAlive = player.poll()
        if isPlayerAlive != 0:
            lcd.clear()
            lcd.message('GoodBye\nMPi3!')
            sleep(2)
            lcd.clear()
            player.stdin.write('q')      
            break
    
    # Next Song
    elif (GPIO.input(buttonNextSong) == False) :
        playFlag = True
        playNextFlag = True
        songIndex = songIndex + 1
        sleep(0.5)
    
    # Increase Volume
    elif (GPIO.input(buttonIncreaseVol) == False) :
        player.stdin.write('+')      
        lcd.clear()
        lcd.message('Volume UP')
        sleep(0.5)
    
    # Decrease Volume
    elif (GPIO.input(buttonDecreaseVol) == False) :
        player.stdin.write('-')       
        lcd.clear()
        lcd.message('Volume DOWN')
        sleep(0.5)
    
    # if End song
    #   Next song
    else :
        isPlayerAlive = player.poll()
        if isPlayerAlive == 0 :
            playFlag = True
            songIndex = songIndex + 1
            if songIndex > lenList - 1 :
                songIndex = 0
    lcd.clear()