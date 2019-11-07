from edgetpu.detection.engine import DetectionEngine
import subprocess
import os
import time
from PIL import Image
from google.cloud import automl_v1beta1 as automl
import csv
from playsound import playsound

# Function to read emotion labels from text files
# WELCHES LABEL FILE?
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
    emotion_model = "modelpath"
    emotion_label = "labelpath"
    emotion_engine = DetectionEngine(emotion_model)
    emotion_labels = ReadLabelFile(emotion_label)

    # Arguments for AutoML Tables classification
    project_id = "nemo-life-assistant"
    compute_region = "us-central1"
    model_id = "heartrates_v1"
    file_path = "/local/path/to/file"  # anpassen!
    score_threshold = 0.5

    # Get full model path and create prediction client for AutoML Tables
    automl_client = automl.AutoMlClient()
    model_full_id = automl_client.model_path(project_id, compute_region, model_id)
    prediction_client = automl.PredictionServiceClient()

    # Initialize params
    params = {}
    if score_threshold:
        params = {"score_threshold": score_threshold}

    # Initialize variables
    modus = "fall"
    count = 0
    # Coral Camera macht alle x Sekunden ein Bild, das an Object Detection Modell geschickt wird, solange modus == "fall"
    while modus == "fall":
        count += 1

        # Take picture
        subprocess.run("cd richtiger_path && snapshot --oneshot --prefix face")
        print("----------took picture----------")
        # Open image
        path = # Bilder Ordner
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
            playsound("./sounds/no_nemo.mp3")
            # Nachfragen, ob alles okay
            # an Assistant weiter geben

        if count%10 == 0:
            modus = "hr"

        # evtl. Bilder wieder aus Ordner löschen?
        time.sleep(5)

    while modus == "hr":
        # Open CSV-file input
        print("----------read heartrate----------")
        #with open(file_path, "rt") as csv_file:
            # Read each row of csv
            #content = csv.reader(csv_file)
            #for row in content:
                # Create payload
                #values = []
                #for column in row:
                    #values.append({'number_value': float(column)})
                #payload = {
                    #'row': {'values': values}
                #}
        row = int(str(count)[-2:-1])
        with open(file_path, "rt") as csv_file:
            values = [float(i) for i in list(csv.reader(csv_file))[row]]
            request = {"payload": {"row": {"values": values}}}
        # Query AutoML Tables model
        response = prediction_client.predict(model_full_id, payload, params)
        print("----------analyze heartrate----------")
        for result in response.payload:
        # laut Doku result.display_name; nicht sicher was display_name ist    
            if result.ok == 1:
                print("heartrate is okay")
                print("score = {}".format(result.classification.score))
            elif result.ok == 0:
                print("heartrate is not okay")
                print("score = {}".format(result.classification.score))
                # Predictions an Assistant schicken
            else:
                print("not able to analyze heartrate")
        # Return to fall detection mode
        modus = "fall"

if __name__ == '__main__':
  main()