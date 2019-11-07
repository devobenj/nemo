from edgetpu.detection.engine import DetectionEngine
import subprocess
import os
import time
from PIL import Image
from google.cloud import automl_v1beta1 as automl
import csv
from playsound import playsound

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
    model_display_name = "heartrates_v1"

    # Get full model path and create prediction client for AutoML Tables
    # REQUIRES CREDENTIALS AND AUTHENTICATION (OAuth)
    automl_client = automl.AutoMlClient()
    model_full_id = automl_client.model_path(project_id, compute_region, model_id)
    #prediction_client = automl.PredictionServiceClient()
    client = automl.TablesClient(project=project_id, region=compute_region)

    # Initialize params
    params = {}
    if score_threshold:
        params = {"score_threshold": score_threshold}

    # Initialize variables
    modus = "fall"
    count = 0
    while modus == "fall":
        count += 5

        # Take picture
        path = "./pictures"
        subprocess.run("cd {} && snapshot --oneshot --prefix face".format(path), shell=True)
        print("----------took picture----------")
        # Open image
        paths = []
        for file in os.listdir(path):
            paths.append(os.path.join(path, file))
        img = Image.open(paths[-1])
        print("----------opened image----------")
        # Run inference
        ans = emotion_engine.detect_with_image(img, threshold=0.5, keep_aspect_ratio=True, relative_coord=True, top_k=1)

        if ans:
            print("----------face detected----------")
            current_emotion = emotion_labels[ans.label_id]
            print("emotion = ", current_emotion)
            print("score = ", ans.score)
        else:
            print("----------no face detected----------")
            #playsound("/audio/no_nemo.mp3")

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
                    'heartRate': values[1],
                    'age':values[2]
            }

        print(inputs)
        # Query AutoML Tables model
        #response = prediction_client.predict(model_full_id, payload, params)
        response = client.predict(model_display_name=model_display_name, inputs=inputs)
        print("----------analyze heartrate----------")
        for result in response.payload:
        # laut Doku result.display_name; nicht sicher was display_name ist    
            if result.ok == 1:
                print("heartrate is okay")
                print("score = {}".format(result.classification.score))
            elif result.ok == 0:
                print("heartrate is not okay")
                print("score = {}".format(result.classification.score))
                playsound("./sounds/bad_hr.mp3")
            else:
                print("not able to analyze heartrate")
        #Return to fall detection mode
        modus = "fall"

if __name__ == '__main__':
  main()