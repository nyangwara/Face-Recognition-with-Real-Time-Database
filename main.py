import os
import pickle
import cvzone
import face_recognition
import numpy as np
from datetime import datetime
import cv2 as cv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
cred = credentials.Certificate("face-attendance-realtime-service-acc-key.json")
#print(cred)  # Add this line to print the credential object
firebase_admin.initialize_app(cred,{
    'databaseURL':"",
    'storageBucket':"" #rem to remove the "gs://"
})

bucket=storage.bucket()
#WEBCAM
cap = cv.VideoCapture(0)
cap.set(3,640) #part where we add our image background
cap.set(4,480)
#GRAPHICS
img_bg=cv.imread('Resources/background.png')
#importing mode image into a list
folder_modes = 'Resources/Modes'
if not os.path.isdir(folder_modes):
    print(f"Error: {folder_modes} is not a directory.")
img_path_list = os.listdir(folder_modes)
img_mode_list=[]
for path in img_path_list:
    img_mode_list.append(cv.imread(os.path.join(folder_modes,path)))
# print(len(img_mode_list))
# print(img_path_list)
#Load the encoded file
file=open('EncodeFile.p','rb')
encode_list_with_Ids=pickle.load(file)
file.close()
encode_list_known,studentIds=encode_list_with_Ids
#print(studentIds)
modeType=0
counter=0
Id=-1
image_student=[]
while True:
    success,img=cap.read()
    #Resize the image due to computation power
    resize_img=cv.resize(img,(0,0),None,fx=0.25, fy=0.25)
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    small_frame = np.ascontiguousarray(resize_img[:, :, ::-1])
    '''
    We need the faces in the current frame and the encodings in the current frame 
    '''
    face_curr_frame=face_recognition.face_locations(small_frame)
    encode_curr_frame=np.ascontiguousarray(face_recognition.face_encodings(small_frame,face_curr_frame))

    #take webcam and overlay it on the background ,we do not want to display them separately
    img_bg[162:162+480,55:55+640]=img
    img_bg[44:44 + 633, 808:808 + 414] = img_mode_list[modeType]

    #Loop through all the encodings
    if face_curr_frame:
        for encode_face,face_loc in zip(encode_curr_frame,face_curr_frame):
            matches=face_recognition.compare_faces(encode_list_known,encode_face)
            face_dist=face_recognition.face_distance(encode_list_known,encode_face)
            # print("Matches",matches)
            # print("face distance",face_dist)
            matchIndex=np.argmin(face_dist)
            if matches[matchIndex]:
                # print("Known face detected")
                # print(studentIds[matchIndex])

                y1,x2,y2,x1=face_loc
                y1, x2, y2, x1= y1*4,x2*4,y2*4,x1*4
                # #bounding box
                bbox=55+x1,162+y1,x2-x1,y2-y1
                img_bg=cvzone.cornerRect(img_bg,bbox,rt=0)
                Id=studentIds[matchIndex]
                if counter==0:
                    counter=1
                    modeType = 1
        if counter!=0:
            if counter==1:
                #GettheData
                studentInfo=db.reference(f'Students/{Id}').get()
                blob = bucket.get_blob(f'Images/{Id}.jpeg')
                if blob is not None:
                    # Тут логика если он не равен None
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    image_student = cv.imdecode(array, cv.COLOR_BGRA2BGR)
                else:
                    # Тут если он равен None
                    print(f"Image for student {id} not found in storage")
                # arr=np.frombuffer(blob.download_as_string(),np.uint8)
                # image_student = cv.imdecode(arr, cv.COLOR_BGRA2BGR)

                #Update data of attendance
                date_time_object=datetime.strptime(studentInfo['last_attendance_time'],"%Y-%m-%d %H:%M:%S")
                seconds_elapsed=(datetime.now()-date_time_object).total_seconds()
                print(seconds_elapsed)
                if seconds_elapsed >30:

                    ref=db.reference(f'Students/{Id}')
                    studentInfo['total attendance'] +=1
                    ref.child('total attendance').set(studentInfo['total attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType=3
                    counter=0
                    img_bg[44:44 + 633, 808:808 + 414] = img_mode_list[modeType]
                #print(studentInfo)
            if modeType != 3:

                if 10<counter <= 20:
                    modeType=2
                img_bg[44:44 + 633, 808:808 + 414] = img_mode_list[modeType]
                if counter <= 10:

                    cv.putText(img_bg,str(studentInfo['total attendance']),(861,125),cv.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv.putText(img_bg, str(studentInfo['Major']), (1006, 550), cv.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv.putText(img_bg, str(Id), (1006, 493), cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv.putText(img_bg, str(studentInfo['standing']), (918, 625), cv.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv.putText(img_bg, str(studentInfo['Year']), (1025, 625), cv.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv.putText(img_bg, str(studentInfo['starting Year']), (1125, 550), cv.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    '''
                    To center the name we must find the width of this length 
                    width i.e total width-50px=ans/2 and start from there and keep varying it 
                    '''
                    (w,h),_ = cv.getTextSize(studentInfo['Name'], cv.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414-w)//2
                    cv.putText(img_bg, str(studentInfo['Name']), (808+offset, 445), cv.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                    #img_bg[175:175+216, 909:909 +216 ] = image_student
                counter += 1
                if counter>=20:
                    counter=0
                    modeType=0
                    studentInfo=[]
                    image_student=[]
                    img_bg[44:44 + 633, 808:808 + 414] = img_mode_list[modeType]
    else:
        modeType=0
        counter=0
    # Frame processing here (e.g., displaying, processing, etc
    #cv.imshow('Webcam', img)
    cv.imshow('Face Attendance', img_bg)
    if cv.waitKey(1) == ord('q'):
        break
# img_bg=cv.imread()























