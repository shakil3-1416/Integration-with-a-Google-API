from flask import Flask, request, jsonify, render_template
import joblib
from flask_cors import CORS
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import warnings

warnings.simplefilter(action='ignore', category=UserWarning)

app = Flask(__name__, static_folder="./build/static", template_folder="./build")

CORS(app, resources={r"/*": {"origins": "*"}})

# Set up credentials
scope = ["https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("myProject.json", scope)
client = gspread.authorize(creds)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=['GET', 'POST'])
def predict():
    data = request.json
    gender = int(data['gender'])
    religion = int(data['religion'])
    caste = int(data['caste'])
    mother_tongue = int(data['mother_tongue'])
    country = int(data['country'])
    height_cms = float(data['height_cms'])

    inputs = [gender, religion, caste, mother_tongue, country, height_cms]
    model = joblib.load("marriage_age_predictor.ml")
    age_pred = model.predict([inputs])
    return str(age_pred[0])

@app.route("/add_data", methods=['POST'])
def add_data():
    print("add_data endpoint was called.")  # Debugging
    try:
        data = request.json
        print(f"Data to be written: {data}")
        sheet = client.open("Myproject").worksheet("Sheet1")  # or whatever your sheet's name is

        # Check for column headers
        headers = ['gender', 'religion', 'caste', 'mother_tongue', 'country', 'height_cms']
        first_row = sheet.row_values(1)  # gets the first row
        if not first_row or first_row != headers:
            sheet.insert_row(headers, 1)  # insert headers at first row

        sheet.append_row([
            data['gender'], 
            data['religion'], 
            data["caste"], 
            data['mother_tongue'],
            data['country'], 
            data['height_cms']
        ])

        return jsonify({"success": True, "message": "Data added to Google Sheet!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
