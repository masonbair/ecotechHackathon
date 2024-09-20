import matplotlib
matplotlib.use('Agg')  # Set non-GUI backend for Matplotlib
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, send_file, session, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ecotech'  # Required for using Flask sessions

# Directory to store uploaded files
UPLOAD_FOLDER = 'static/uploads/'
faulty_time_data = []

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route for the homepage (frontend)
@app.route('/')
def index():
    print("Erasing data")
    faulty_time_data = []
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'timedata.txt')
    print(f"Reading file from: {file_path}")

    
    with open(file_path, 'r') as file:
        print('File opened successfully!')
        for line in file:
            print(f"Line: {line}")  # Debugging each line
            index, start, end, time = line.strip().split(',')
            faulty_time_data.append((start, end, time, index))

    session['faulty_time_data'] = faulty_time_data
    # Pass the faulty time data to the HTML template
    return render_template('index.html', faulty_time_data=faulty_time_data)

@app.route('/upload', methods=['POST'])
def upload_file():
    data_quality = {}
    print("Creating graph")
    parameter = request.form['parameter']
    print("P graph")

    threshold_from = float(request.form['threshold_from'])
    threshold_to = float(request.form['threshold_to'])
    disruption_time_value = float(request.form['disruption_time_value'])
    print("Building graph")

    disruption_time_unit = request.form['disruption_time_unit']
    file = request.files['file']

    # Save the uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Analyze the file (CSV assumed)
    df = pd.read_csv(file_path)
    print("Reading data")


    # Perform basic analysis (e.g., filter by parameter)
    if parameter in df.columns:
        df_filtered = df[[parameter]]

        # Check data quality based on the threshold range
        mean_value = df_filtered[parameter].mean()
        if threshold_from <= mean_value <= threshold_to:
            data_quality = {
                'quality': "Good",
                'parameter': parameter
            } 
        else:
            data_quality = {
                'quality': "Bad",
                'parameter': parameter
            } 
        print("Analyzing graph")

        print("Updating the quality")
        data_quality.update({
            "plots": ["../static/uploads/plot.png", "../static/uploads/plot.png", "../static/uploads/plot.png"]
        })


        # Prepare data for Chart.js
        chart_data = {
            'labels': list(df.index),
            'data': list(df_filtered[parameter]),
            'threshold_from': threshold_from,
            'threshold_to': threshold_to
        }
        print(data_quality)


        return jsonify({
            'data_quality': data_quality,
            'chart_data': chart_data
        })
    else:
        return jsonify({'error': 'Parameter not found in the uploaded file'}), 400




if __name__ == '__main__':
    app.run(debug=False)
