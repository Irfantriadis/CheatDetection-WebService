from flask import Flask, render_template, Response, jsonify
import torch
import cv2
from PIL import Image
import mysql.connector
import pandas as pd

app = Flask(__name__)

@app.route('/realtime')
def index():
    return render_template('video.html')

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="dbcheatdetec"
)

# Create a cursor object to execute SQL queries
cursor = cnx.cursor()

# Define the SQL query to insert a label into the table
insert_query = "INSERT INTO labels (label_name) VALUES (%s)"



def detect_objects():
    # Load the YOLOv5 model with .pt weights
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='model/menyontek.pt', force_reload=True)

    counter = 0
    threshold = 30

    # Open camera
    cap = cv2.VideoCapture(0)

    while True:
        # Read frame from the camera
        ret, frame = cap.read()

        if ret:
            frame = cv2.flip(frame, 1)

            # Convert frame to PIL Image
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Perform inference on the image
            results = model(image)

            # Get detection results
            pred_boxes = results.xyxy[0]

            # Draw bounding boxes and labels on the frame
            for *xyxy, conf, cls in pred_boxes:
                x1, y1, x2, y2 = map(int, xyxy)
                label = f'{model.names[int(cls)]} {conf:.2f}'
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                # Check if the label is "menyontek"
                if model.names[int(cls)] == "mencontek":
                    counter += 1
                else:
                    counter = 0

                # Check if the threshold is reached
                if counter >= threshold:
                    cv2.putText(frame, "Anda terdeteksi mencontek", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                # Insert the label into the database
                label_name = model.names[int(cls)]
                cursor.execute(insert_query, (label_name,))
                cnx.commit()

            # Convert the frame back to BGR format
            frame = cv2.cvtColor(frame, cv2.WINDOW_NORMAL)

            # Encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)

            if not ret:
                continue

            # Yield the frame as a byte array
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'

        else:
            break

    # Release the camera and clean up
    cap.release()
    cursor.close()
    cnx.close()


@app.route('/video_feed')
def video_feed():
    return Response(detect_objects(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/export-csv')
def export_csv():
    # Execute the SQL query to retrieve data from the "labels" table
    query = "SELECT * FROM labels"
    cursor = cnx.cursor()
    cursor.execute(query)
    data = cursor.fetchall()

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data, columns=[column[0] for column in cursor.description])

    # Export DataFrame to a CSV file
    csv_file = 'dataset/labels.csv'
    df.to_csv(csv_file, index=False)

    return f'CSV file exported: {csv_file}'

@app.route('/data', methods=['GET'])
def get_data():
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM labels")  # Ganti nama_tabel dengan nama tabel yang sesuai

    columns = cursor.description
    result = []
    for value in cursor.fetchall():
        row = {}
        for (index, column) in enumerate(columns):
            row[column[0]] = value[index]
        result.append(row)

    cursor.close()
    return jsonify(result)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='192.168.43.170', port='5000', debug=True)
