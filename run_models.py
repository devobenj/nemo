from edgetpu.detection.engine import DetectionEngine
import subprocess
import os
import time
from PIL import Image
from google.cloud import automl_v1beta1 as automl
import csv
from playsound import playsound
from google.oauth2 import service_account

# Function to read emotion labels from text files
def ReadLabelFile(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    ret = {}
    for line in lines:
        pair = line.strip().split(maxsplit=1)
        ret[int(pair[0])] = pair[1].strip()
    return ret

def main():
    # Initialize engine for emotion detection
    emotion_model = "./emotion_model/emotion_model.tflite"
    emotion_label = "./emotion_model/emotion_labels.txt"
    emotion_engine = DetectionEngine(emotion_model)
    emotion_labels = ReadLabelFile(emotion_label)

    # Arguments for AutoML Tables classification
    project_id = "nemo-life-assistant"
    compute_region = "us-central1"
    model_id = "heartrates_v1"
    file_path = "./hr_model/sample_data.CSV"
    score_threshold = "0.5"

    # Create prediction client for AutoML Tables using service account credentials
    try:
        client = automl.TablesClient(credentials=service_account.Credentials.from_service_account_file('nemo-hrml-key.json'),
                                 project=project_id, region=compute_region)
    except:
        print("Failure creating an AutoML Tables client")

    # Initialize params
    params = {}
    if score_threshold:
        params = {"score_threshold": score_threshold}
    path = "./pictures"

    # Initialize variables
    modus = "fall"
    count = 0

    while True:
        while modus == "fall":
            count += 1
            # Take picture
            subprocess.run("cd {} && snapshot --oneshot --prefix face".format(path), shell=True)
            print("----------took picture----------")
            # Open image
            paths = []
            for file in os.listdir(path):
                paths.append(os.path.join(path, file))
            paths.sort()

            img = Image.open(paths[-1])
            print("----------opened image----------")
            print(paths[-1])
            # Run inference
            try:
        	    ans = emotion_engine.detect_with_image(img, threshold=0.5, keep_aspect_ratio=True, relative_coord=True, top_k=1)
            except:
                print("An failure calling the detection model occured")

            if ans:
                print("----------face detected----------")
                for obj in ans:
                  print('score = ', obj.score)
                  print("emotion = ", emotion_labels[obj.label_id])
            else:
                print("----------no face detected----------")
                try:
                    playsound("./audio/no_nemo.mp3")
                except:
                    print("Cannot play audio")

            if count%10 == 0:
                modus = "hr"

            # evtl. Bilder wieder aus Ordner löschen?
            time.sleep(5)

        while modus == "hr":
            # Open CSV-file input
            print("----------read heartrate----------")
            row = int(str(count)[-2:-1])
            with open(file_path, "rt") as csv_file:
                values = [float(i) for i in list(csv.reader(csv_file))[row]]
                #request = {"payload": {"row": {"values": values}}}
                inputs= {'male': str(values[0]),
                        'age': values[1],
                        'heartRate':values[2]
                }

            # Query AutoML Tables model
            try:
                response = client.predict(model_display_name=model_id, inputs=inputs)
            except:
                print("An failure calling the cloud-based model occured")
                break

            print("----------analyze heartrate----------")
            result =  response.payload[0].tables if (response.payload[0].tables.score > response.payload[1].tables.score) else response.payload[1].tables
            if(result.value.string_value == '1'):
                print("heartrate is okay")
                print("score = {}".format(result.score))
            elif(result.value.string_value == '0'):
                print("heartrate is not okay")
                print("score = {}".format(result.score))
                try:
                    playsound("./sounds/bad_hr.mp3")
                except:
                    print("Cannot play audio")
            else:
                print("not able to analyze heartrate")

            # #Return to fall detection mode
            count = 0
            modus = "fall"

if __name__ == '__main__':
  main()