import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from firebase_admin import initialize_app
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://attendence-system-8e085-default-rtdb.firebaseio.com/',
    'storageBucket':"attendence-system-8e085.appspot.com"
})

bucket=storage.bucket()
blob = bucket.blob('attendence-system-8e085.appspot.com')

cap=cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)
imgBackground= cv2.imread('Resources/cu.png')

folderModePath='Resources/Modes'
modePathList=os.listdir(folderModePath)
imgModeList=[]
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))

# print(len(imgModeList))


#load the encoding file
file=open('EncodeFile.p','rb')
encodeListKnownWithIds=pickle.load(file)
file.close()
encodeListKnown,studentIds =encodeListKnownWithIds
# print(studentIds)
print("encode file loaded......")

modeType=0
counter=0
id=-1
imgStudent=[]
while True:
    success,img=cap.read()

    imgS=cv2.resize(img,(0,0),None,0.25,0.25)
    imgS=cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

    faceCurFrame=face_recognition.face_locations(imgS)
    encodeCurFrame=face_recognition.face_encodings(imgS,faceCurFrame)

    imgBackground[162:162+480,55:55+640]=img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    # cv2.imshow("Webcam",img)

    if faceCurFrame:
       for encodeFace,faceLoc in zip(encodeCurFrame,faceCurFrame):
          matches=face_recognition.compare_faces(encodeListKnown,encodeFace)
          faceDis=face_recognition.face_distance(encodeListKnown,encodeFace)
        # print("matches",matches)
        # print("faceDis",faceDis)

          matchIndex=np.argmin(faceDis)
        # print("Match Index",matchIndex)

          if matches[matchIndex]:
              # Get the student's name
           
            # print("known face detection")
            # print(studentIds[matchIndex])
             y1,x2,y2,x1=faceLoc
             y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
             bbox=  55+x1,162+y1,x2-x1,y2-y1
             imgBackground=cvzone.cornerRect(imgBackground,bbox,rt=2)
             id=studentIds[matchIndex]
             if counter == 0:
                 cvzone.putTextRect(imgBackground,"loading",(275,400))
                 # cv2.imshow("face Attendence",imgBackground)
                 cv2.waitKey(1)
                 counter=1
                 modeType=1

       if counter!=0:

          if counter==1:
                studentInfo=db.reference(f'Students/{id}').get()
                # print(studentInfo)
                blob = bucket.get_blob(f'Images/{id}.png')
                if blob and blob.exists():
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                else:
                    print(f"Blob Images/{id}.png does not exist.")
                datetimeObject=datetime.strptime(studentInfo['last_attendence_time'],"%Y-%m-%d %H:%M:%S")

                secondsElapsed=(datetime.now()-datetimeObject).total_seconds()
                # print(secondsElapsed)
                if secondsElapsed>30:



                  ref=db.reference(f'Students/{id}')
                  print(studentInfo)  # Check the content of studentInfo before and after the update
                  studentInfo['total_attendence'] += 1
                  print(studentInfo)  # Verify that studentInfo has the updated value
                  # studentInfo['total_attendence'] +=1
                  ref.child('total_attendence').set(studentInfo['total_attendence'])
                  ref.child('last_attendence-time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                  modeType=3
                  counter=0
                  imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

          if modeType !=3:

               if 10<counter<20:
                  modeType=2

               imgBackground[44:44 +633,808:808 +414]=imgModeList[modeType]
               if counter<=10:

                  cv2.putText(imgBackground,str(studentInfo['total_attendence']),(861,125),
                        cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)


                  cv2.putText(imgBackground, str(studentInfo['Branch']), (1006, 550),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                  cv2.putText(imgBackground, str(id), (1006, 493),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                  cv2.putText(imgBackground, str(studentInfo['standing']), (910,625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)

                  cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)

                  cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125,625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                  (w,h),_ =cv2.getTextSize(studentInfo['Name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                  offset = (414 - w) // 2
                  cv2.putText(imgBackground, str(studentInfo['Name']), (808+offset, 445),   cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                  imgBackground[175:175+216,909:909+216]=imgStudent

               counter+=1

               if counter>=30:
                 counter=0
                 modeType=0
                 studentInfo=[]

                 imgStudent=[]
                 imgBackground[44:44 +633,808:808 +414]=imgModeList[modeType]


    else:
        modeType=0
        counter=0
    cv2.imshow("Face Attendence",imgBackground)
    cv2.waitKey(1)
