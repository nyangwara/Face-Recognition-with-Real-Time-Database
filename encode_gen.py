import os
import cv2 as cv
import face_recognition
import pickle #cPickle is faster than pickle for serializing
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


#importing student  images
folder_path='Images'
path_list=os.listdir(folder_path)
images_list=[]
studentIds=[]
# if not os.path.isdir(folder):
#     print(f'this file{folder} is not a directory')
for img in path_list:
    images_list.append(cv.imread(os.path.join(folder_path,img)))
    studentIds.append(os.path.splitext(img)[0])
    '''
    Creates a folder called images in our firebase storage 
    and then it will add all those images 
    
    '''
    fileName = f'{folder_path}/{img}'
    bucket=storage.bucket()
    blob=bucket.blob(fileName)
    blob.upload_from_filename(fileName)
#print(studentIds)


def find_encodings(imgs):
    encodings_list=[]
    for img in imgs:
        img=cv.cvtColor(img,cv.COLOR_BGR2RGB)
        encode=face_recognition.face_encodings(img)[0]
        encodings_list.append(encode)
    return encodings_list
print("Encoding started ......")
encode_list_known=find_encodings(images_list)
'''
-We need to safe the encodings 
-As well as the names and ids as well -Which id belongs to which encodinbg
'''
encode_list_with_Ids=[encode_list_known,studentIds]
print("Encoding complete ......")
#print(encode_list_known)
file=open("EncodeFile.p",'wb')
pickle.dump(encode_list_with_Ids,file)
file.close()
print("File saved")





















