# Avero-reporting-api-exercise

This repository is the implementation of the exercise that can be found at https://github.com/AveroLLC/reporting-api-exercise


## Requirements
Python 2.7 and pip

Make sure that the pip is for Python 2.7 and not Python 3

## Installation
Install virtualenv to have a virtual environment for the required python libraries

`pip install virtualenv`

`python -m virtualenv venv`

Activate the virutal environment and install the required libraries

`source venv/bin/activate`

`pip install -r requirements.txt`

## Deployment 
Input your token at the begining of app.py where it says '<INSERT TOKEN HERE>'. Make sure to replace everything, including the brackets (<>).

From the command line do `flask run`

Navigate to `http://127.0.0.1:5000/reporting` to run the desired report

Example FCP: `http://127.0.0.1:5000/reporting?business_id=f21c2579-b95e-4a5b-aead-a3cf9d60d43b&report=FCP&timeInterval=week&start=2018-06-02T14:00:00.000Z&end=2018-06-16T14:00:00.000Z`

Example LCP: `http://127.0.0.1:5000/reporting?business_id=f21c2579-b95e-4a5b-aead-a3cf9d60d43b&report=LCP&timeInterval=day&start=2018-06-02T14:00:00.000Z&end=2018-06-04T14:00:00.000Z`

Example EGS: `http://127.0.0.1:5000/reporting?business_id=f21c2579-b95e-4a5b-aead-a3cf9d60d43b&report=EGS&timeInterval=hour&start=2018-06-02T15:00:00.000Z&end=2018-06-02T19:00:00.000Z`


## Assumptions 
* When timeInterval is a month, it is assumed to be 30 day increments.
* Start and end are given as precicesly integer timeInterval aparts. For example, if timeInterval is days, end will be start time plus some interger number of days and no extra hours. 
* Order item created time is the time that should be allocated to a particular timestep the for a given item. Assume that modification time is not the cruicial time for the calculations.

## Next steps
* Convert order item created time to be datetime format and not string format upon first lookup so as to not need to convert it for comparisons everytime the order item is looked up
* Optimize calculations so it is not as iterative to better optimize time complexity. Currently it is slow!
	* Ideas: determine if item list for a business is ordered by creation time (it likely is because it is a list) and can then stop iterating once an item has a creation time larger than the end time.
	* Parallelize computations in LCP to determine total labor costs in parallel with total sales for a given timestep.  
* Handle edge cases for start, end, and timeInterval. Example: end is 2 days and 2 hours past start but timeInterval is days
* Implement database to store cached results so it can handle larger datasets.
* Implement more checks that request is in correct format.
* Split calculations into seperate classes so it easier for different people to develop/modify the different reports concurrently. 
* Integrate with webserver (ex. heroku) so that a person does not have to build this repository to get reports. 
* Use Flask templates to make a more standard format for the output and give the webpage a better UI. 