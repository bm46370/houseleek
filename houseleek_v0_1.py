#### TODO: reftactor code in clases...; pir senzor ; KiCad shema

#za zvuk - puštanje preko aux od raspberry-a
import pygame

import picamera
import time
import RPi.GPIO as GPIO
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from clarifai import rest
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
import sys
##print (sys.version)

GPIO.setmode(GPIO.BCM)  
# GPIO 17 set up as input. 
pir_sensor = 17 #GPIO pin 17
kill_switch=22
camera_led=18
pir_led=27

GPIO.setup(pir_sensor, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(kill_switch, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(camera_led, GPIO.OUT)
GPIO.setup(pir_led,GPIO.OUT)

##sending mail, not used at the moment
def SendMail(FileName, danger):
    msg = MIMEMultipart()
    msg['Subject'] = 'Houseleek Surveilance'
    msg['From'] = 'from@gmail.com'
    msg['To'] = 'to@gmail.com'
    msg['Date'] = formatdate(localtime=True)
    
    if danger:
        text = MIMEText("OPASNOST")
    else:
        text = MIMEText("nije prepoznat uljez")
    msg.attach(text)
    
    for f in FileName or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                f
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("from@gmail.com", "password")
    s.sendmail("from@gmail.com", "to@gmail.com", msg.as_string())
    s.quit()

def my_callback(channel):
    GPIO.output(pir_led,True) #Turn on LED
    time.sleep(0.5) # leave LED on for 0.5 seconds, just for test
    
    camera = picamera.PiCamera()
    camera.vflip = True

    GPIO.output(camera_led, GPIO.HIGH)
    camera.capture('slika.jpg')
    GPIO.output(camera_led, GPIO.LOW)
    camera.close()
    GPIO.output(pir_led,False) #turn off LED
    
    danger = False
    app = ClarifaiApp(api_key='------------key-----------')
    model = app.models.get('general-v1.3')
    image = ClImage(file_obj=open('slika.jpg', 'rb'))
    response=model.predict([image])
    concepts = response['outputs'][0]['data']['concepts']
    for concept in concepts:
        print(concept['name'], concept['value'])
        if any(x in concept['name'] for x in ["bird"]): # can be more filters: ["danger","man","people","adult","weapon","safety"]):
            danger = True
            #print('bird on camera')
    if danger:
        print('sviraj')
        #zvuk
        song = "countdown.mp3"
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)


print "During this waiting time, your computer is not"
print "wasting resources by polling for a PIR.\n"
GPIO.add_event_detect(pir_sensor, GPIO.RISING, callback=my_callback) 
try:
    GPIO.wait_for_edge(kill_switch, GPIO.RISING)
    GPIO.cleanup() 
    print "\nKill switch pressed"
except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
