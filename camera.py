import cv2
import numpy as np
import dlib
from PIL import ImageColor

webcam = True
onlyLipsColor = True
# Lips_Color = "d2e603"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("./cascade/shape_predictor_68_face_landmarks.dat")

class VideoCamera(object):
    def __init__(self , hexCode):
       #capturing video
       self.video = cv2.VideoCapture(0)
       self.hexCode = hexCode
       
    
    def __del__(self):
        #releasing camera
        self.video.release()
    
    def Hex2rgb(self):
        hex = self.hexCode
        print(hex)
        if hex.startswith("#"):
            rgb = ImageColor.getcolor(hex, "RGB")
        else:
            hex = "#"+hex
            rgb = ImageColor.getcolor(hex, "RGB")
            
        r, g, b = rgb[0], rgb[1], rgb[2]
        return rgb, r, g, b

    def createBox(self, img,points,scale=5,masked= False,cropped= True):
        if masked:
            mask = np.zeros_like(img)
            mask = cv2.fillPoly(mask,[points],(255,255,255))
            img = cv2.bitwise_and(img,mask)
            #cv2.imshow('Mask',mask)

        if cropped:
            bbox = cv2.boundingRect(points)
            x, y, w, h = bbox
            imgCrop = img[y:y+h,x:x+w]
            imgCrop = cv2.resize(imgCrop,(0,0),None,scale,scale)
            cv2.imwrite("Mask.jpg",imgCrop)
            return imgCrop
        else:
            return mask


    def get_frame(self):
        #extracting frames
        ret, img = self.video.read()

        img = cv2.resize(img,(0,0),None,0.6,0.6)
        imgOriginal = img.copy()
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = detector(imgOriginal)
        imgColorLips = None
        for face in faces:
            x1,y1 = face.left(),face.top()
            x2,y2 = face.right(),face.bottom()
            #imgOriginal=cv2.rectangle(imgOriginal, (x1, y1), (x2, y2), (0, 255, 0), 2)
            landmarks = predictor(imgGray, face)

            myPoints =[]
            for n in range(68):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                myPoints.append([x,y])
                #cv2.circle(imgOriginal, (x, y), 5, (50,50,255),cv2.FILLED)
                #cv2.putText(imgOriginal,str(n),(x,y-10),cv2.FONT_HERSHEY_COMPLEX_SMALL,0.8,(0,0,255),1)
            #print(myPoints)

            imgOriginal2 = imgOriginal.copy()
        
            if len(myPoints) != 0:
                        try:
                            myPoints = np.array(myPoints)
                            imgLips = self.createBox(img, myPoints[48:61], 3, masked=True, cropped=False)

                            imgColorLips = np.zeros_like(imgLips)
                            rgb, r, g, b = self.Hex2rgb()  # color converter 
                            imgColorLips[:] = b, g, r
                            imgOriginal = cv2.bitwise_and(imgLips, imgColorLips)
                            imgOriginal = cv2.GaussianBlur(imgOriginal, (7, 7), 10)


                            if onlyLipsColor:
                                imgOriginalGray = cv2.cvtColor(imgOriginal2,cv2.COLOR_BGR2GRAY)
                                imgOriginalGray = cv2.cvtColor(imgOriginalGray, cv2.COLOR_GRAY2BGR)
                                imgOriginal = cv2.addWeighted(imgOriginalGray ,1,imgOriginal,0.4,0)
                            else: 
                                imgOriginal = cv2.addWeighted(imgOriginal2, 1, imgOriginal, 0.4, 0)
                            
                            # encode OpenCV raw frame to jpg and displaying it
                            ret, jpeg = cv2.imencode('.jpg', imgOriginal)
                            return jpeg.tobytes()
                            
                        except:
                            pass
        ret, jpeg = cv2.imencode('.jpg', imgOriginal)
        return jpeg.tobytes()