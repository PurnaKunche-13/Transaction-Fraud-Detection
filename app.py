from pathlib import Path
import pickle

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, jsonify

# Initialize Flask
app = Flask(__name__)

# Load trained model
MODEL_PATH = Path(__file__).parent / "transaction_fraud_detection_model.pkl"

try:
    with open(MODEL_PATH, "rb") as file:
        model = pickle.load(file)
except FileNotFoundError:
    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}"
    )


def get_prediction(time, amount):
    """
    Predict whether a transaction is fraudulent.
    """

    # Create input DataFrame
    features = pd.DataFrame({
        "Time": [time],
        "Amount": [amount]
    })

    # Predict
    prediction = int(model.predict(features)[0])

    message = "Fraud" if prediction == 1 else "Not Fraud"

    confidence = 100.0
    fraud_probability = 0.0

    # If model supports probabilities
    if hasattr(model, "predict_proba"):

        probabilities = model.predict_proba(features)[0]

        classes = list(model.classes_)

        fraud_index = classes.index(1)

        fraud_probability = float(probabilities[fraud_index] * 100)

        if prediction == 1:
            confidence = fraud_probability
        else:
            confidence = 100 - fraud_probability

    return {
        "message": message,
        "prediction": prediction,
        "confidence": round(confidence, 2),
        "fraud_probability": round(fraud_probability, 2)
    }


# ---------------- Home Page ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- Form Submit ---------------- #

@app.route("/submit", methods=["POST"])
def submit():

    try:
        time = float(request.form.get("time"))
        amount = float(request.form.get("amt"))

    except (TypeError, ValueError):

        return render_template(
            "index.html",
            error="Please enter valid transaction details."
        )

    return redirect(
        url_for(
            "result",
            time=time,
            amt=amount
        )
    )


# ---------------- Result Page ---------------- #

@app.route("/result")
def result():

    try:
        time = float(request.args.get("time"))
        amount = float(request.args.get("amt"))

    except (TypeError, ValueError):

        return render_template(
            "index.html",
            error="Please submit transaction details first."
        )

    prediction = get_prediction(time, amount)

    return render_template(
        "result.html",
        result=prediction,
        time=time,
        amount=amount
    )


# ---------------- REST API ---------------- #

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "No JSON data received."
        }), 400

    try:

        time = float(data["time"])
        amount = float(data["amt"])

    except (KeyError, TypeError, ValueError):

        return jsonify({
            "message": "Invalid input."
        }), 400

    prediction = get_prediction(time, amount)

    return jsonify(prediction)


# ---------------- Run App ---------------- #

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )