import matplotlib
matplotlib.use('Agg')  # Set non-GUI backend for Matplotlib
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import os

app = Flask(__name__)

# Directory to store uploaded files
UPLOAD_FOLDER = 'static/uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route for the homepage (frontend)
@app.route('/')
def index():
    faulty_time_data = []

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'timedata.txt')
    print(f"Reading file from: {file_path}")

    try:
        with open(file_path, 'r') as file:
            print('File opened successfully!')
            for line in file:
                print(f"Line: {line}")  # Debugging each line
                start, end, time = line.strip().split(',')
                faulty_time_data.append((start, end, time))
    except FileNotFoundError:
        print(f"File not found at {file_path}")
        return "Error: timedata.txt file not found", 404
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Error reading file: {e}", 500

    # Pass the faulty time data to the HTML template
    return render_template('index.html', faulty_time_data=faulty_time_data)

# Route to handle the file upload and data processing
@app.route('/upload', methods=['POST'])
def upload_file():
    # Get the form data
    parameter = request.form['parameter']
    threshold_from = float(request.form['threshold_from'])
    threshold_to = float(request.form['threshold_to'])
    disruption_time_value = float(request.form['disruption_time_value'])
    disruption_time_unit = request.form['disruption_time_unit']
    file = request.files['file']

    # Save the uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Analyze the file (CSV assumed)
    df = pd.read_csv(file_path)

    # Perform basic analysis (e.g., filter by parameter)
    if parameter in df.columns:
        df_filtered = df[[parameter]]

        # Check data quality based on the threshold range
        mean_value = df_filtered[parameter].mean()
        if threshold_from <= mean_value <= threshold_to:
            data_quality = "Good"
        else:
            data_quality = "Bad"

        # Generate a time series plot
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df_filtered[parameter], label=parameter)
        plt.axhline(y=threshold_from, color='r', linestyle='--', label=f'Threshold From: {threshold_from}')
        plt.axhline(y=threshold_to, color='g', linestyle='--', label=f'Threshold To: {threshold_to}')
        plt.title(f'Time Series of {parameter}')
        plt.xlabel('Time')
        plt.ylabel(parameter)
        plt.legend()

        # Save the plot
        plot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'plot.png')
        plt.savefig(plot_path)

        # Return plot and data quality result
        return render_template('index.html', plot_url=plot_path, data_quality=data_quality)
    else:
        return "Parameter not found in the uploaded file", 400

if __name__ == '__main__':
    app.run(debug=False)
