from pdf2image import convert_from_path
import cv2
import numpy as np
import imutils
import img2pdf
import os
from PIL import Image
import sys
from pyzbar.pyzbar import decode
from skimage import measure


max_width = 400
def get_contour_precedence(contour, cols):
    tolerance_factor = 10
    origin = cv2.boundingRect(contour)
    return ((origin[1] // tolerance_factor) * tolerance_factor) * cols + origin[0]

# get qr info and answers
def extract_data(page):
    
    page.save('pdf_temp.jpg', 'JPEG')
    
    # rotate rectangle 90 
    rotate_image()
    image_origin = cv2.imread("pdf_temp.jpg")
    
    qr_info = ";;;"
    # get qr info by using zbar (python library)
    decodedObjects = decode(Image.open('pdf_temp.jpg'))
    for obj in decodedObjects:
        qr_info =  obj.data.decode("utf-8")
    
    # get anwers part
    img_answer = get_answer_part(image_origin)

    height, width, channels = img_answer.shape
    multiple = max_width/width

    # image resize and remove noise 
    image = cv2.resize(img_answer, (int(multiple*width), int(multiple*height)), interpolation = cv2.INTER_AREA)
    #cv2.imshow("Image",image)
    gray_origin = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray_origin, (1, 1), 0)
    thresh = cv2.threshold(gray_origin, 180, 255, cv2.THRESH_BINARY)[1]
    
    # dilate edges , 
    kernel = np.ones((2,3), np.uint8)
    edges = cv2.Canny(thresh, 100, 200)
    #cv2.imshow("edges ", edges)
    thresh = cv2.dilate(edges, kernel, iterations=3)
    
    
    labels = measure.label(thresh, neighbors=8, background=0)
    mask = np.zeros(thresh.shape, dtype="uint8")
    
    masks = []
    # loop over the unique components
    for label in np.unique(labels):
        # if this is the background label, ignore it
        if label == 0:
            continue
     
        # otherwise, construct the label mask and count the
        # number of pixels 
        labelMask = np.zeros(thresh.shape, dtype="uint8")
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)
     
        if numPixels > 1000:
            
            mask = cv2.add(mask, labelMask)
            #cv2.imshow(str(label), labelMask)
    #cv2.imshow("mask ", mask)
    #cv2.waitKey(0)
    # so get region one by one from anwers part
    cnts, h = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #cnts = imutils.grab_contours(cnts)
    cnts_sorted = sorted(cnts, key=lambda ctr: cv2.boundingRect(ctr)[0] + (cv2.boundingRect(ctr)[1])  * image.shape[1] )
    
    result_1_10 = []
    result_11_20 = []
    
    # loop over the contours
    for (i, cnt) in enumerate(cnts_sorted):
        x,y,w,h = cv2.boundingRect(cnt)
        #print(x + y * image.shape[1], "aaaa", x, y, image.shape[1])
        if i == 0:
            x_0, w_0 = x, w
        elif i == 1:
            x_1, w_1 = x, w
        if i%2 == 0:
            x, w = x_0, w_0
            cv2.rectangle(image, (x, y), (x+w, y+h), (0,0,255), 2)
            x = int(x/multiple) 
            y = int(y/multiple)
            w = int(w/multiple)
            h = int(h/multiple)
            crop_img = img_answer[y:y+h, x:x+w]
            result_11_20.append(get_answer(crop_img))
        elif i%2 == 1:
            x, w = x_1, w_1
            cv2.rectangle(image, (x, y), (x+w, y+h), (0,0,255), 2)
            x = int(x/multiple) 
            y = int(y/multiple)
            w = int(w/multiple)
            h = int(h/multiple)
            crop_img = img_answer[y:y+h, x:x+w]
            result_1_10.append(get_answer(crop_img))
        
    answer = ",".join(result_11_20) + "," + ",".join(result_1_10)
    result = qr_info.replace(",", ";") + ";" + answer
    print(result)

    #cv2.imshow("AAAAA", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    os.remove("pdf_temp.jpg")
    return result

def rotate_image():
    image_origin = cv2.imread("pdf_temp.jpg")
    gray_origin = cv2.cvtColor(image_origin, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray_origin, (1, 1), 0)
    thresh = cv2.threshold(gray_origin, 180, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.bitwise_not(thresh)

    kernel = np.ones((5,5),np.uint8)
    erosion = cv2.erode(thresh,kernel,iterations = 1)
    cnts = cv2.findContours(erosion.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    rows, cols, channels = image_origin.shape

    cnts = imutils.grab_contours(cnts)
    
    if len (cnts) != 0:
        cnt = max(cnts, key = cv2.contourArea)
        rect = cv2.minAreaRect(cnt)
        center = rect[0]
        angle = rect[2]
        x,y,w,h = cv2.boundingRect(cnt)

        x, y, w, h = x - 20, y - 20, w + 20, h + 20
        # draw the book contour (in green)
        if angle > -45 :
            angle = -90 - angle
        
        rot = cv2.getRotationMatrix2D(center, angle+90, 1)
        image_origin = cv2.warpAffine(image_origin, rot, (cols,rows))
        crop_img = image_origin[y:y+h, x:x+w]
        #cv2.imshow("tse", crop_img)
        
        
        cv2.imwrite("pdf_temp.jpg", crop_img)
# get correct answer per line
def get_answer(img):
    
    # preprocessing image 
    height, width, channels = img.shape
    multiple = max_width/width

    # resize image with max_width
    image = cv2.resize(img, (int(multiple*width), int(multiple*height)), interpolation = cv2.INTER_AREA)
    gray_origin = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray_origin, (1, 1), 0)
    thresh = cv2.threshold(gray_origin, 180, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.bitwise_not(thresh)
    
    
    kernel = np.ones((13,13), np.uint8)
    kernel_1 = np.ones((10,10), np.uint8)
    
    # remove not answered options
    erode = cv2.erode(thresh, kernel, iterations=1)
    dilate = cv2.dilate(erode, kernel_1, iterations=1)
    #cv2.imshow("anser", thresh)
    cv2.waitKey(0)
    cnts = cv2.findContours(dilate.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cnts = imutils.grab_contours(cnts)
    #

    if len(cnts) is not 1:
        # cv2.imshow("aaa", gray_origin)
        # cv2.imshow("erode", erode)
        # cv2.imshow("dilate", dilate)
        # cv2.waitKey(0)
        # print(len(cnts), "N?A")
        return 'N'
    position = [('A', 30, 100), ('B', 101, 170), ('C', 171, 250), ('D', 251, 325), ('E', 326, 400)]

    for (j, cnt) in enumerate(cnts):
        rect = cv2.minAreaRect(cnt)
        center = rect[0]
        x = center[0]
        for pos in position:
            if x >= pos[1] * max_width/400 and x <= pos[2] * max_width/400:
                return pos[0]
    # cv2.imshow("aaa", thresh)
    # cv2.waitKey(0)
    # print(len(cnts), "N?A")
    return 'N'


# get region image with answers part , without qr info   
def get_answer_part(image_origin):
    height, width, channels = image_origin.shape
    multiple = max_width/width

    image = cv2.resize(image_origin, (int(multiple*width), int(multiple*height)), interpolation = cv2.INTER_AREA)
    gray_origin = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    kernel = np.ones((2,2), np.uint8)
    img_erosion = cv2.dilate(gray_origin, kernel, iterations=1)
    #cv2.imshow("Erosion", img_erosion)

    blurred = cv2.GaussianBlur(img_erosion, (1, 1), 0)
    
    thresh = cv2.threshold(blurred, 180, 255, cv2.THRESH_BINARY)[1]
    kernel = np.ones((1,1), np.uint8)
    edges = cv2.Canny(thresh, 100, 200)

    thresh = cv2.dilate(edges, kernel, iterations=1)
    #cv2.imshow("Thresh", thresh)
    labels = measure.label(thresh, neighbors=8, background=0)
    mask = np.zeros(thresh.shape, dtype="uint8")
    
    masks = []
    # loop over the unique components
    for label in np.unique(labels):
        # if this is the background label, ignore it
        if label == 0:
            continue
     
        # otherwise, construct the label mask and count the
        # number of pixels 
        labelMask = np.zeros(thresh.shape, dtype="uint8")
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)
     
        if numPixels > 100:
            
            mask = cv2.add(mask, labelMask)
            #cv2.imshow(str(label), labelMask)
    

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    print(len(cnts), "answer")
    # loop over the contours
    if len (cnts) != 0:
        cnt = max(cnts, key = cv2.contourArea)
        x,y,w,h = cv2.boundingRect(cnt)
        x = x + 15
        y = y + 15
        w = w - 30
        h = h - 30
        
        x = int(x/multiple) 
        y = int(y/multiple) + int(h/multiple*1/6 )
        w = int(w/multiple)
        h = int(h/multiple) - int(h/multiple*1/6 )
        # get only anwers part , remove qr code part
        crop_img = image_origin[y:y+h, x:x+w]
    #cv2.imshow("Crop", crop_img)
    
    return crop_img
if __name__ == '__main__':

    if len(sys.argv) == 2:
    
        # input_file = "adjgmxtpjad400-2.pdf"
        input_file = sys.argv[1]
        
        print('[+].... start ')
        #try:
        if input_file.endswith(".pdf"):
            pages = convert_from_path(input_file)
            
            with open('answers.csv', 'w') as the_file:
                the_file.write('id;"studant_id";"school_id";"ava_id";"answers"\n')
                # loop page in pdf pages
                for page in pages:    
                    the_file.write(input_file + ";" +extract_data(page)+ "\n")
        print('[+].... Sucess end')
        #except Exception as e:
        #   print('please enter correct path', e)
    else:
       print("please enter input path and output path")
        
    