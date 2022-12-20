import cv2
import numpy as np
import requests


def rows_columns_counter(contours):
    rws = 1
    cls = 1
    setup = True
    for c in contours:
        if setup:
            x0, y0, _, _ = cv2.boundingRect(c)
            setup = False
            continue
        x1, y1, _, _ = cv2.boundingRect(c)
        if abs(y1 - y0) < 5:
            rws += 1
        if abs(x1 - x0) < 5:
            cls += 1
    return rws, cls


def qr_decoding(contours, strings, image):
    i = 0
    j = 0
    detect = cv2.QRCodeDetector()
    for c in contours:
        x1, y1, w1, h1 = cv2.boundingRect(c)
        scan = image[y1:y1 + h1, x1:x1 + w1]
        blur1 = cv2.GaussianBlur(image[y1:y1 + h1, x1:x1 + w1], (21, 21), 125)
        temp = cv2.threshold(blur1, 195, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        qrs = cv2.findContours(temp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        qrs = [q for q in qrs if (cv2.contourArea(q) > 90 * 90) and (cv2.contourArea(q) < 105 * 105)]
        for q in qrs:
            x2, y2, w2, h2 = cv2.boundingRect(q)
            scan = scan[y2:y2 + h2, x2:x2 + w2]
            scan = cv2.resize(scan, (int(scan.shape[1]*1.64), int(scan.shape[0]*1.64)))
            scan = cv2.threshold(scan, 145, 255, cv2.THRESH_TOZERO + cv2.THRESH_BINARY)[1]
            scan = cv2.threshold(scan, 195, 255, cv2.THRESH_TOZERO + cv2.THRESH_BINARY)[1]
            kernel = np.array([[-1, -1, -1], [-1, 11, -1], [-1, -1, -1]])
            scan = cv2.filter2D(scan, -1, kernel)
            decoded, _, _ = detect.detectAndDecode(scan)
            if ";" in decoded:
                strings[i][j] = decoded
                break
        j += 1
        if j == rows:
            j = 0
            i += 1
    return strings


url = input()
response = requests.get(url)
if response.status_code == 200:
    with open("shelf.png", 'wb') as f:
        f.write(response.content)
raw = cv2.imread('shelf.png')
raw = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)
img_ = 255*(raw < 128).astype(np.uint8)
coords = cv2.findNonZero(img_)
x, y, w, h = cv2.boundingRect(coords)
img = raw[y:y+h, x:x+w]
cnts = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[1]
cnts = [c for c in cnts if (cv2.contourArea(c) > 110*110) and (cv2.contourArea(c) < 300*300)]
cnts = cnts[::-1]
rows, cols = rows_columns_counter(cnts)
strs = [["Товар отсутствует." for i in range(rows)] for j in range(cols)]
strs = qr_decoding(cnts, strs, img)
for i in range(cols):
    for j in range(rows):
        if ';' in strs[i][j]:
            text = strs[i][j].split(';')
            if int(text[1]) == rows-i+1 and int(text[2]) == j+1:
                strs[i][j] = text[0]+". Расположение верное."
            else:
                strs[i][j] = text[0] + ". Расположение неверное."
        strs[i][j] = str(rows-i+1)+"-я полка "+str(j+1)+"-й ряд. "+strs[i][j]
strs.sort(key=lambda xi: xi[1])
output = ''
for i in range(cols):
    for j in range(rows):
        output += strs[i][j]
        if i != cols-1 or j != rows-1:
            output += '\n'
print(output)
