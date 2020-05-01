import numpy as np
import cv2
import sys


def decoder(file):
    img = []
    search = 0
    for tag in file:
        if tag[0] == 0:
            img.append(tag[2])
        else:
            search = len(img) - tag[0]
            for letter in range(tag[1]):
                img.append(img[search])
                search += 1
            img.append(tag[2])
    return img


def LZ77_search(search, look_ahead):

    ls = len(search)
    llh = len(look_ahead)
    if(ls == 0):
        return (0, 0, look_ahead[0])
    length = 0
    offset = 0
    buf = []
    for i in range(ls+llh):
        buf.append('0')
    for i in range(0, ls):
        buf[i] = search[i]
    for i in range(0, llh):
        buf[i + ls] = look_ahead[i]

    search_pointer = ls
    for i in range(0, ls):
        match = 0
        while buf[i + match] == buf[search_pointer + match]:
            match = match + 1
            if search_pointer+match == len(buf):
                break
        if match > length:
            offset = ls - i
            length = match
    if (length + search_pointer) <= (len(buf)):
        search_pointer = search_pointer - 1
    return (offset, length, buf[search_pointer+length])


WindoSize = int(sys.argv[2])
LookAheadSize = int(sys.argv[3])
SearchSize = WindoSize - LookAheadSize
img = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
flattened_img = img.flatten()
searchiterator = 0
lhiterator = 0
codes = []
while lhiterator < len(flattened_img):
    search = flattened_img[searchiterator:lhiterator]
    look_ahead = flattened_img[lhiterator:lhiterator+LookAheadSize]
    (offset, length, char) = LZ77_search(search, look_ahead)
    codes.append((offset, length, char))
    lhiterator = lhiterator + length + 1
    searchiterator = max(lhiterator - SearchSize, 0)
codes = np.array(codes, np.uint8)
np.save('encoded.npy', codes)

image = decoder(np.load('encoded.npy'))
if len(image) > (len(img[0]) * len(img)):
    image.remove(image[len(image)-1])
elif len(image) < (len(img[0]) * len(img)):
    image.append(0)
image = np.array(image)
image = image.reshape(len(img[0]), len(img))
cv2.imwrite('output.bmp', image)
