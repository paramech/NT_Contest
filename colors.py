import cv2
import requests


red = 0
yellow = 0
green = 0
blue = 0
purple = 0
url = 'https://stepik.org/media/attachments/course/128568/color1.png'
response = requests.get(url)
if response.status_code == 200:
    with open("color.png", 'wb') as f:
        f.write(response.content)
img = cv2.imread('color.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 235, 255, cv2.THRESH_BINARY)[1]
cnts = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[1]
for c in cnts:
    x, y, w, h = cv2.boundingRect(c)
    x1 = int(x+w/2)
    y1 = int(y+h/2)
    b, g, r = (img[y1, x1])
    if r > 250 and g < 50 and b < 50:
        red += 1
    if r < 50 and g > 250 and b < 50:
        green += 1
    if r < 50 and g < 50 and b > 250:
        blue += 1
    if r > 120 and g < 50 and b > 120:
        purple += 1
    if r > 250 and g > 250 and b < 50:
        yellow += 1
output = 'red: '+str(red)+'\n'+'yellow: '+str(yellow)+'\n'+'green: '+str(green)+'\n'+'blue: '+str(blue)+'\n'+\
         'purple: '+str(purple)
print(output)
