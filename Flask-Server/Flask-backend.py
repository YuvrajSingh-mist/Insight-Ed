from copy import copy
import chromadb
from flask import Flask, jsonify, request, render_template
import requests, pickle
import gdown 
import shutil
import math
from tqdm import tqdm

import json 
from mtcnn.mtcnn import MTCNN
import cv2 
import os

import shutil
import numpy as np

import google.generativeai as genai

import gensim
import os

import random
from youtubesearchpython import VideosSearch
import torchvision

import moviepy.editor as mp 
import speech_recognition as sr 

import pandas as pd
import openai
import whisper

import keras
from keras.models import Sequential
from keras.layers import Lambda, Dense

import torch
# import torchvision.transforms as transforms
from PIL import Image
from torchvision import transforms

import tensorflow as tf


from detect_faces_video import detect_faces

from transformers import pipeline

from chromadb import Documents, EmbeddingFunction, Embeddings


from flask_cors import CORS


app = Flask(__name__)
CORS(app)

directory = "static/"
if(os.path.exists(directory)):
    shutil.rmtree(directory)
os.makedirs(directory)


api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

final = {}

model_ai = genai.GenerativeModel('gemini-pro')

class GeminiEmbeddingFunction(EmbeddingFunction):
  def __call__(self, input: Documents) -> Embeddings:
    model = 'models/embedding-001'
    title = "Custom query"
    return genai.embed_content(model=model,
                                content=input,
                                task_type="retrieval_document",
                                title=title)["embedding"]

    

if(os.path.exists("detected_faces_videos")):
    shutil.rmtree("detected_faces_videos")
os.makedirs("detected_faces_videos")

 
     

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/emotionAttention', methods=['GET', 'POST'])
def predict():
    
    
    flag = True
  
    # if request.method == 'POST':
    #    # check if the post request has the file part
    #    if 'file' not in request.files:
    #       return "something went wrong 1"
    #
    #    user_file = request.files['file']
    #    temp = request.files['file']
    #    if user_file.filename == '':
    #        return "file name not found ..."
    #
    #    else:
    #        # path = os.path.join(os.getcwd(), 'static/mask', user_file.filename)
    #        # user_file.save(path)
    # filename = request.args.get('query')
    full_path = request.full_path

    # Extract the 'query' parameter from the full path
    query_parameter = full_path.split('query=')[1]
    print("Filename is : ", query_parameter) 
    count= 0
    classes = []
    # //Download video
    # gdown.download(query_parameter, 'static/video.mp4', quiet=False)
    # video_path = "static/video.mp4"
    detect_faces(query_parameter)
    # with open('static/mask/mask_{}.jpg'.format(count), 'wb') as f:
    #     data = requests.get(query_parameter)
    #     f.write(data.content)
    # filename = 'https://firebasestorage.googleapis.com/v0/b/solution-challenge-app-409f6.appspot.com/o/user-images%2F2cznu8kGbtbbCZ3s22c9E1AnqG92.jpg?alt=media&token=91b2b18f-826a-4d15-bdf6-e940a6d25ec7'
    
    classes = identifyImage('detected_faces_videos')
    print(classes)

    # if classes[0] < 0.5:
    #     flag = False
    return jsonify({
        "status": "success",
        "prediction": classes,
        # "confidence": str(classes[0][0][2]),
        # "upload_time": datetime.now()
    })

def detect_faces(video_path):
    
    detector  = MTCNN()
    # print("Hi")
    interval = 20
    uuid = video_path.split('&')[0].split("/")[5]
    # print("uuid is:", uuid)
    url = "https://drive.google.com/uc?id={}".format(uuid)
    output_file = "static/video.mp4"  # Specify the name of the output file
    print(url)
    # print(timestamp1)
    # print(timestamp2)
    gdown.download(url, output_file, quiet=False)
    # response = requests.get(url))
    # with open("static/video.mp4", 'wb') as f:
    #     f.write(response.content)
        
    # cap = cv2.VideoCapture('demo-student.mp4')
    cap = cv2.VideoCapture('static/video.mp4')


    frame_count = 0
    count = 0
    timecount = []
    # unique_timecount = set()
    while True:
        
        ret, frame = cap.read()
        
        if ret != True:
            break
        
        current_time = frame_count / cap.get(cv2.CAP_PROP_FPS)
        
        # print(math.floor(current_time % interval) == 0)
        if(round(current_time, 1) % interval == 0):
            
            # print("Hi")
            print(round(current_time, 1))
            if round(current_time, 1) not in timecount:
                # continue
            
                result_list = detector.detect_faces(frame)
                for results in result_list:
                    if(results['confidence'] > 0.7):
                        print(results)
                        x, y, width, height = results['box']
                        cropped_image = frame[y:y+height, x:x+width]
                        cv2.imwrite(os.path.join("detected_faces_videos", "_{}.jpg".format(count)), cropped_image)
                
                        count += 1
                        timecount.append(round(current_time, 1))    
        
        # cv2.imshow('Video with Face Detection', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break  
        # timecount = set(timecount)
        frame_count += 1
                
    cap.release()
    cv2.destroyAllWindows()
    print(list(timecount))
    pickle.dump(timecount , open('students_timestamps_all.pkl', 'wb'))
 
def identifyImage(folder_path):
    
    dict = {}
    count = 0
    drowsiness = []
    emotion = []
    timestamps = []
    final = []
    time = pickle.load(open('students_timestamps_all.pkl', 'rb'))
    temp = []
    for img in tqdm(os.listdir(folder_path)):
        
        emt = []
        isDrowsiness = []
        timecount = []
        value = isDrowsy(os.path.join(folder_path, img))
        # value=random.randint(1,3)
        if(value == 1):
            isDrowsiness.append("Yes")
            emt.append("N/A")
            timecount.append(time[count])
            temp.append((timecount, emt, isDrowsiness))
            
        elif(value == 0):
            
            isDrowsiness.append("N/A")
            # print(os.path.join(folder_path, img))
            pred_emotions = emotions(os.path.join(folder_path, img))
            emt.append(pred_emotions)
            timecount.append(time[count])
            temp.append((timecount, emt, isDrowsiness))
        # emotion.append(emt)
        # drowsiness.append(isDrowsiness)
        # timestamps.append(time)
        
        # for key, value in zip(emotions, drowsiness, timestamps):
        #     dict[key] = value
        
        # dict['{}EmotionTimestamp_{}'.format(count)] = pred
      
        count += 1
        # break
        # i += 1
    final.append(temp)
    print(final)
    pickle.dump(final , open('students_timestamps_emotion_drowsiness.pkl', 'wb'))
    return final

def efficientnet_preprocessing(img):
    return keras.applications.efficientnet.preprocess_input(img)
    
    
def build_model():
    
    IMAGE_WIDTH = 600
    IMAGE_HEIGHT = 600
    IMAGE_CHANNELS = 3
    efficientnet = keras.applications.EfficientNetB7(include_top=False, input_shape = (IMAGE_WIDTH, IMAGE_HEIGHT,IMAGE_CHANNELS))
    model = Sequential()
    model.add(keras.Input(shape=(IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_CHANNELS)))

    for layer in efficientnet.layers:

        layer.trainable = False

    def efficientnet_preprocessing(img):
        return keras.applications.efficientnet.preprocess_input(img)

    model.add(Lambda(efficientnet_preprocessing))
    model.add(efficientnet)
    model.add(tf.keras.layers.GlobalAveragePooling2D())
    model.add(Dense(1, activation='sigmoid'))
    return model

model = build_model()
model.load_weights('my_checkpoint.weights.h5')
    
    
def isDrowsy(file_path):
    
    print(file_path)
    img = tf.keras.utils.load_img(file_path, target_size=(600, 600))
    img_array = tf.keras.utils.img_to_array(img)
    expanded_img = np.expand_dims(img_array,axis=0)
    # preprocessed_img = tf.keras.applications.efficientnet.preprocess_input(expanded_img)
  
    print(model.summary())
    result = model.predict(expanded_img, verbose=0)
    # pred = np.argmax(result, axis=1)
    if result[0] > 0.5 :
        pred = 1
    else:
        pred = 0
    print(result)
    return pred


pipe = pipeline("image-classification", model="jayanta/vit-base-patch16-224-in21k-emotion-detection")

def emotions(file_path):

    
    # image = cv2.imread("/content/sad.jpeg")
    y_pred = pipe.predict(file_path)
    # print(y_pred)
    return y_pred[0]['label']


@app.route('/speechAndKeywordsEmotionDrwosiniess', methods=['GET', 'POST'])
def speechRecognition():

    data = pickle.load(open('students_timestamps_emotion_drowsiness.pkl', 'rb'))
    print(data)
    count = 0
    full_path = request.full_path


    query_parameter = full_path.split('query=')[1]

    directory = "static/"
    shutil.rmtree(directory)
    os.makedirs(directory)


    uuid = query_parameter.split('&')[0].split("/")[5]
    print(uuid)
    url = "https://drive.google.com/uc?id={}".format(uuid)
    output_file = "static/video.mp4" 
    print(url)

    gdown.download(url, output_file, quiet=False)

    topics = []
    timecount = []
    temp =  []
    # for i in data
    while(count + 1 < len(data[0])):
        timestamp1 = data[0][count][0]
        timestamp2 = data[0][count + 1][0]
        print(timestamp1)
        print(timestamp2)
        video = mp.VideoFileClip("static/video.mp4").subclip(timestamp1, timestamp2)

        video.write_videofile("static/video_clipped_{}.mp4".format(count), codec='libx264', audio_codec='aac')
        
        audio_model = whisper.load_model('base.en')
        option = whisper.DecodingOptions(language='en')
        text = audio_model.transcribe("static/video_clipped_{}.mp4".format(count))

        topics.append(keywords(text['text']))
        timecount.append((timestamp1, timestamp2))
    
        temp.append((timecount, topics))
        count += 1
    final= {}

    final['result'] = temp
    return final



@app.route('/speechAndKeywordsIndividualParts', methods=['GET', 'POST'])
def speechRecognitionIndividualParts():

   
    count = 0
    full_path = request.full_path


    query_parameter = full_path.split('query=')[1]
    timestamp1 = query_parameter.split('&')[1]
    timestamp2 = query_parameter.split('&')[2]

    directory = "static/"
    shutil.rmtree(directory)
    os.makedirs(directory)

    uuid = query_parameter.split('&')[0].split("/")[5]
    print(uuid)
    url = "https://drive.google.com/uc?id={}".format(uuid)
    output_file = "static/video.mp4"
    print(url)
    print(timestamp1)
    print(timestamp2)
    gdown.download(url, output_file, quiet=False)

         
    video = mp.VideoFileClip("static/video.mp4").subclip(timestamp1, timestamp2)
    count += 1

    video.write_videofile("static/video_clipped_{}.mp4".format(count), codec='libx264', audio_codec='aac')
    
    audio_model = whisper.load_model('base.en')
    option = whisper.DecodingOptions(language='en')
    text = audio_model.transcribe("static/video_clipped_{}.mp4".format(count))

    text_data = []
    keywords_dict = {}
    text_data.append(text['text'])
  
    keywords_dict= {}
    keyword = keywords(text)
    keywords_dict['keywords'] = keyword
    return keywords_dict


@app.route('/speechAndKeywordsFullOneShot', methods=['GET', 'POST'])
def speechRecognitionFullOneShot():

    timecount = []
    count = 0
    full_path = request.full_path
    topics = []

    query_parameter = full_path.split('query=')[1]
    interval = query_parameter.split('&')[1]

    directory = "static/"
    shutil.rmtree(directory)
    os.makedirs(directory)

    uuid = query_parameter.split('&')[0].split("/")[5]
    print(uuid)
    url = "https://drive.google.com/uc?id={}".format(uuid)
    output_file = "static/video.mp4"  
    print(url)

    gdown.download(url, output_file, quiet=False)

    video = mp.VideoFileClip("static/video.mp4")
    length = video.duration
    timestamp2 = 0
    timestamp1 = 0
    interval = int(interval)
    temp = []

    while((timestamp1 + interval) < int(length)):

        timestamp1 += interval
        clip = video.subclip(timestamp2, timestamp1)
        
        clip.write_videofile("static/video_clipped_{}.mp4".format(count), codec='libx264', audio_codec='aac')
        
        audio_model = whisper.load_model('base.en')
        option = whisper.DecodingOptions(language='en')
        text = audio_model.transcribe("static/video_clipped_{}.mp4".format(count))

        keywords_now = keywords(text['text'])['keywords']
        topics.append((timestamp1, timestamp2, keywords_now))

        timestamp2 = timestamp1  

        count += 1
        temp.append(topics)

    final = {}
    final['result'] = temp

    return final


from chromadb.config import Settings

def create_chromadb(list_of_words, timestamps):

    
    client = chromadb.PersistentClient(path="vectorSearchForSearchWithinVideo")
    client.delete_collection(name='embeddings_topics_for_search_within_video')
    chroma_db = client.create_collection('embeddings_topics_for_search_within_video', embedding_function=GeminiEmbeddingFunction())
    
    for i, d in enumerate(list_of_words):

        chroma_db.add(
            documents=d,
            ids = str(i),
            metadatas={'Timestamp_{}'.format(i): str(timestamps[i][0]) + '_' + str(timestamps[i][1])}
        )

    return chroma_db
    
    
@app.route('/searchWitihinVideo', methods=['GET', 'POST'])
def speechRecognitionSearchWithinVideo():

    if os.path.exists('topics_videosearch.pkl'):
        os.remove('topics_videosearch.pkl')
    if os.path.exists('timestamps_videosearch.pkl'):
        os.remove('timestamps_videosearch.pkl')
        
    count = 0
    stride = 20
    full_path = request.full_path


    timestamp1 = 0
    timestamp2 = 0
    query = ' '.join(full_path.split('&')[1].split("%20"))
    num = int(full_path.split('&')[2])
    print(query)
    print(num)

    directory = "static/"
    shutil.rmtree(directory)
    os.makedirs(directory)

    query_parameter = full_path.split('query=')[1]
    uuid = query_parameter.split('&')[0].split("/")[5]
    print(uuid)
    url = "https://drive.google.com/uc?id={}".format(uuid)
    output_file = "static/video.mp4"  
    print(url)

    gdown.download(url, output_file, quiet=False)
    video = mp.VideoFileClip("static/video.mp4")
    
    temp = []
    topics = []
    timecount=  []
    while((timestamp1 + stride) < int(video.duration)):
        
        timestamp1 += stride
        clip = video.subclip(timestamp2, timestamp1)

        clip.write_videofile("static/video_clipped_{}.mp4".format(count), codec='libx264', audio_codec='aac')
        
        audio_model = whisper.load_model('base.en')
        option = whisper.DecodingOptions(language='en')
        text = audio_model.transcribe("static/video_clipped_{}.mp4".format(count))

        topics.append(' '.join(keywords(text['text'])['keywords']))
        timecount.append([timestamp2, timestamp1])

        timestamp2 = timestamp1  
       
        print(timestamp1)
        print(timestamp2)
        count += 1
        temp.append(timecount)
        
    pickle.dump(topics, open('topics_videosearch.pkl', 'wb'))
    pickle.dump(timecount, open('timestamps_videosearch.pkl', 'wb'))
    print(timecount)
    print(topics)
    chroma_db = create_chromadb(topics, timestamps=timecount)
    print(pd.DataFrame(chroma_db.peek()))
    print(pd.DataFrame(chroma_db.get()))

    result = chroma_db.query(query_texts=[query], n_results=num)
  
    json_data = '{"data":null,"distances":[[0.08081431700730621,0.10110898726031427,0.1663002628724509]],"documents":[["Machine Learning Prediction","Machine Learning Supervised Learning","Machine learning Supervised learning Label"]],"embeddings":null,"ids":[["3","0","2"]],"metadatas":[[{"Timestamp_3":"60_80"},{"Timestamp_0":"0_20"},{"Timestamp_2":"40_60"}]],"uris":null}'


    data = json.loads(json_data)

 
    timestamps = []
    for metadata in data.get("metadatas", []):
        for timestamp in metadata:
            timestamps.extend(timestamp.values())
            
    return timestamps
        
        
        
@app.route('/generateQuestionnaire', methods=['GET', 'POST'])
def generateQuestionnaire():


    full_path = request.full_path

    # Extract the 'query' parameter from the full path
    query_parameter = full_path.split('query=')[1]
    grade = full_path.split('&')[1]
    print(grade)
    
    directory = "static/"
    shutil.rmtree(directory)
    os.makedirs(directory)

    # url = query_parameter.split('&')[0]
    uuid = query_parameter.split('&')[0].split("/")[5]
    print(uuid)
    url = "https://drive.google.com/uc?id={}".format(uuid)
    output_file = "static/video.mp4"  # Specify the name of the output file
    print(url)

    gdown.download(url, output_file, quiet=False)

    audio_model = whisper.load_model('base.en')
    option = whisper.DecodingOptions(language='en')
    text = audio_model.transcribe("static/video.mp4")

    text_data = []
    text_data.append(text['text'])
    response = model_ai.generate_content(
        '''
        Generate a mcq consisting of 10 questions on the given content for a {}th grader. DO NOT try to bold any text or numbers with NO HEADING PRECEDONG the questions. The content is {}.
        '''.format(grade, text['text']),
        
    generation_config={
          # "max_output_tokens": 2048,
          "temperature": 0.5,
          "top_p": 1
      },
          
    )
    
  
    return response.text.split("\n")

    
    
def keywords(text):
       

 
    response = model_ai.generate_content('''
    Return ONLY 2-3 most relavant keywords which summarizes, has essence and captures semantic meaning of the following as instructed for the following -{}. Just generate the Keywords and DO NOT BOLD THEM OR APPLY ANY NUMBER PRECEDING THEM.
    '''
    .format(text),
          generation_config={
          # "max_output_tokens": 2048,
          "temperature": 0.9,
          "top_p": 1
      },

      ),
    # print(response)
    # print(response.text)
    # fetched = response['result']['candidates'][0]['content']['parts'][0]['text']
    response_dict = response[0]._result
    candidates = response_dict.candidates
    # fetched = candidates[0]['content']['parts'][0]['text']
    # Extracting text
    if candidates:
    # Assuming candidates is a list
        candidate = candidates[0]
        parts = candidate.content.parts
        if parts:
            fetched = parts[0].text
            # print(text)
    final['keywords'] = fetched.split("\n")
    links = fetchRecommendations(fetched)
    final['recommendations']  = links
    print(final)
    return final

# @app.route('/fetchRecommendations', methods=['GET', 'POST'])
def fetchRecommendations(keywords):
    
    for word in keywords:
        videos_search = VideosSearch(word, limit=3)

        video_urls = []
        for video in videos_search.result()["result"]:
            video_urls.append(video["link"])

        # for url in video_urls:
            # print(url)
        return video_urls

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)









