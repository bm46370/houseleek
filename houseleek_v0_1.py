#### TODO: reftactor code in clases...; pir senzor ; KiCad shema

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
print (sys.version)

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

#take picture
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

#GPIO.output(18, GPIO.HIGH)
camera = picamera.PiCamera()
#camera.capture('slika.jpg')
#GPIO.output(18, GPIO.LOW)
	
camera.vflip = True

GPIO.output(18, GPIO.HIGH)
camera.capture('slika2.jpg')
GPIO.output(18, GPIO.LOW)

GPIO.output(18, GPIO.HIGH)
camera.start_recording('video.mjpeg')
time.sleep(5)
camera.stop_recording()
GPIO.output(18, GPIO.LOW)

camera.close()
GPIO.cleanup()

#recognition api
danger = False
app = ClarifaiApp(api_key='+++++++key+++++++')
model = app.models.get('general-v1.3')
image = ClImage(file_obj=open('slika2.jpg', 'rb'))
response=model.predict([image])
concepts = response['outputs'][0]['data']['concepts']
for concept in concepts:
    print(concept['name'], concept['value'])
    if any(x in concept['name'] for x in ["danger","man","people","adult","weapon","safety"]):
        danger = True
        print('OPASNOST')
if danger:
    print('OPASNOST')
    
#sent mail
SendMail(['slika2.jpg','video.mjpeg'], danger)