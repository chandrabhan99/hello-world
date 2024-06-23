from flask import Flask, request, jsonify

import logging
import json
from helpers.blob_storage_utils import get_new_sas
from engine.job_navigator import get_recommendations
from engine import feedback
from helpers.app_utils import get_key

app = Flask(__name__)

@app.route('/sas_url', methods=['GET'])
def get_sas_url():
    try:
        sas_response = get_new_sas()
        resp = json.dumps(sas_response)
    except Exception as ex:
        logging.info('Failed to generate SAS token: %s', ex)
        resp = {}
    return resp


@app.route('/job_recommendations', methods=['GET','POST'])
def get_job_recommendations():
    try:
        cv_key = get_key(request, 'cv_key')
        location = get_key(request, 'location')
        recommendations = get_recommendations(cv_key, location)
        resp = json.dumps(recommendations)   
    except Exception as ex:
        logging.info('Failed to get recommendations: %s', ex)
        resp = {} #func.HttpResponse("Failed to get recommendations", status_code=500)
    return resp


@app.route('/job_recommendation_feedback', methods=['POST'])
def post_job_recommendation_feedback():
    try:
        cv_key = get_key(request, 'cv_key')
        fb = get_key(request, 'feedback')
        if (cv_key is not None) and \
            (fb is not None) and \
            ("response" in fb) and \
            (fb["response"] == "Accept" or fb["response"] == "Reject"):
            is_posted = feedback.post(cv_key, fb)
            if not is_posted:
                resp = {}#func.HttpResponse("Internal server error.", status_code=500)    
            else:
                resp = {}#func.HttpResponse("Submitted", status_code=200)
        else:
            resp = {} #func.HttpResponse("Invalid feeadback. Include a valid cv_key and allowed response are Accept/Reject.", status_code=400)
    except Exception as ex:
        logging.info('Failed to post feedback: %s', ex)
        resp = {} #func.HttpResponse("Internal server error", status_code=500)
    return resp

#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=8080, debug=True)