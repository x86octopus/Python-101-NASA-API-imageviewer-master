import csv
from flask import Flask, render_template, request, redirect, url_for
import requests
from collections import OrderedDict
from pager import Pager
from dotenv import load_dotenv
import os
import glob
import urllib.request
import random

APPNAME = "PrettyGalaxies"
STATIC_FOLDER = 'example'


# get_api_key: This function pulls your API key from your .env file
# If you do not have a .env file, create a file with the file name .env and the below contents:
# api_key="Replace this with your API key"
def get_api_key():
    load_dotenv()
    api_key = os.getenv("api_key")
    if api_key is "Replace this with your API key":
        print("You need to replace the variable api_key in the .env file with your API key from the NASA API.")
    return api_key


# set_table: This function uses your API key to pull an image set from the Mars rover on a random date.
def set_table():
    # Get the API key from the .env file
    apikey = get_api_key()
    return_list = []                                        # Set a list to hold the return values
    rand_sol_str = str(random.randint(1, 1000))             # Choose a random number as string
    files_to_delete = glob.glob("example\\images\\*.jpg")   # Make a list of files in the images folder
    for file in files_to_delete:
        os.remove(file)                                     # Delete any existing files

    # Pull the data from the nasa link (returns as JSON)
    nasa_api_response = requests.get(
            "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol="
            + rand_sol_str
            + "&page=2&api_key="
            + apikey)
    # Set this data up as an Ordered Dict instead
    nasa_api_dict = nasa_api_response.json(object_pairs_hook=OrderedDict)

    # For each of these returned data sets
    for listing in nasa_api_dict['photos']:
        jpg_name = listing['img_src'].split('/')[-1]        # Parse the image name from its URL
        # Save the file into the images directory
        urllib.request.urlretrieve(listing['img_src'], "example\\images\\"+jpg_name)
        # Get only the items we want from the returned object
        display_object = OrderedDict([
            ('name', jpg_name.split('.')[0]),
            ('id', listing['id']),
            ('sol', listing['sol']),
            ('camera', listing['camera']['name']),
            ('link', listing['img_src']),
            ('date', listing['earth_date']),
            ('rover', listing['rover']['name'])
        ])
        return_list.append(display_object)                  # Save the flattened format into the list
    return return_list


table = set_table()
pager = Pager(len(table))

app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config.update(
    APPNAME=APPNAME,
    )


@app.route('/')
def index():
    return redirect('/0')


@app.route('/<int:ind>/')
def image_view(ind=None):
    if ind >= pager.count:
        return render_template("404.html"), 404
    else:
        pager.current = ind
        return render_template(
            'imageview.html',
            index=ind,
            pager=pager,
            data=table[ind])


@app.route('/goto', methods=['POST', 'GET'])    
def goto():
    return redirect('/' + request.form['index'])


if __name__ == '__main__':
    app.run(debug=True)
