from flask import Flask, request
import requests
from datetime import datetime, timedelta
import calculations

token = '<INSERT TOKEN HERE>'

app = Flask(__name__)
calc = calculations.Calculations(token)

@app.route('/')
def home_page():
	return 'Please navigate to /reporting to return a report. The required query parameters are business_id, report, timeInterval, start, and end.'

@app.route('/reporting')
def report_page():
	report = request.args.get('report')
	text = 'The required query parameters are business_id, report, timeInterval, start, and end.'
	# User incorrectly inputs the report type
	if report not in ['LCP', 'FCP', 'EGS']:
		return text + 'Report can only be LCP, FCP, or EGS. Please try again with a correct report name.'
	else:
		business_id = request.args.get('business_id')
		timeInterval = request.args.get('timeInterval')
		start = request.args.get('start')
		end = request.args.get('end')
		if report=="LCP":
			output = calc.LCP(business_id, report, timeInterval, start, end)
		elif report=="FCP":
			output = calc.FCP(business_id, report, timeInterval, start, end)
		else:
			assert report=="EGS" 
			output = calc.EGS(business_id, report, timeInterval, start, end)		
		return str(output)
		