import flask
from flask import request, jsonify, Response
import json
import os
import sklearn # This in theory could be able to load transformers
# https://stackoverflow.com/questions/67735216/after-using-pip-i-get-the-error-scikit-learn-has-not-been-built-correctly
from transformers import pipeline

# Path to save or load the model
MODEL_PATH = "./saved_model"

# Initialize the Flask app
app = flask.Flask(__name__)
app.config["DEBUG"] = True  # debug mode for easier feedback during dev

def init_classifier(model_path):
    """
    Function to download and validate the model pipeline. Exception if the pipeline couldnt be loaded.
    """
    try:
        # Load and configure the pre-trained classification model
            if os.path.exists(model_path):  # Check if the model directory already exists
                print(f"Loading model from {model_path}...")
                classifier = pipeline(model=model_path)
            else:
                print("Model not found locally. Downloading...")
                classifier = pipeline(
                    model="OpenAlex/bert-base-multilingual-cased-finetuned-openalex-topic-classification-title-abstract",
                    top_k=10,            # Return the top 10 predictions
                    truncation=True,     # Truncate input if longer than max tokens
                    max_length=512       # Maximum token length for input
                )
                print(f"Saving model to {model_path}...")
                classifier.save_pretrained(model_path)  # Save the model locally for future use
                print("Model saved, starting API.")
            return classifier
    except Exception as e:
        print(f"Failed to initialize the classifier: {e}")
        raise

# Initialize the classifier object
classifier = init_classifier(MODEL_PATH)

@app.route('/classify', methods=['POST'])
def classify():
    """
    Return a prediction for the model.
    
    Input:
    JSON of data
    
    Output:
    JSON of predictions
    """
    try:
        # Extract JSON payload from the incoming request
        data = request.get_json()
        title = data.get('title', '')        # Retrieve the 'title' field from the payload
        abstract = data.get('abstract', '')  # Retrieve the 'abstract' field from the payload

        # Validate input fields
        if not title or not abstract:
            return jsonify({"error": "Both 'title' and 'abstract' are required"}), 400

        # Format input text for the classifier
        input_text = f"<TITLE> {title}\n<ABSTRACT> {abstract}"
        
        # Perform text classification using the model
        predictions = classifier(input_text)

        # Convert the model predictions to json output
        result = json.dumps(predictions)

        # Return the predictions
        return flask.Response(response=result, status=200, mimetype='application/json')

    except Exception as e:
        # Handle any exceptions and return an error response
        error_response = {"error": str(e)}
        return flask.Response(response=json.dumps(error_response), status=500, mimetype='application/json')

@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Simple health check response
        return jsonify({"status": "healthy", "message": "API is up and running"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/version', methods=['GET'])
def get_version():
    api_version = {
        "version": "1.0.0",
        "description": "API for classifying text using OpenAlex topic classification",
        "model": "OpenAlex/bert-base-multilingual-cased-finetuned-openalex-topic-classification-title-abstract"
    }
    return jsonify(api_version), 200

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Topic Tagging API",
        "endpoints": {
            "/": "Introduction and available endpoints",
            "/classify": "POST endpoint for text classification (requires 'title' and 'abstract')",
            "/health": "GET endpoint to check the health of the API",
            "/version": "GET endpoint to get API version and metadata"
        },
        "instructions": "Use /classify with a JSON payload to classify text."
    }), 200

# Note:
# This script is an adaptation to predictor.py present in the original repo, but using the Model interface from
# HuggingFace 
# and invoked by another script or executed within a WSGI server like Gunicorn.
