import sqlite3  # python build in database
import requests  # fetch source data online
import pandas as pd
import json  # convert json source data to dict


def videoData():
    url = "https://radiant-island-16688.herokuapp.com/getRecipe/4fbc68d6-de7d-437f-a017-e4f99afb4471"  # source data url
    headers = {
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    }
    response = requests.get(url, headers=headers)  # fetch data in json file
    items = response.json()  # extract data
    data = []
    for item in items:
        del item['UUID'], item['directions'], item['shortDescription'], item['showRecipe']
        entity = []
        for key in item:
            if key == 'recipeImageSrc':
                entity.append(item[key][0])
            elif key == 'nutrition':
                for sub_key in item[key]:
                    if sub_key != 'disclaimer':
                        entity.append(item[key][sub_key])
            elif key == 'tags':
                entity.append(','.join(map(str, item[key])))
            elif key == 'ingredients':
                entity.append(item[key][0]['dish'])
                entity.append(','.join(map(str, item[key][0]['ingredient'])))
            elif key == 'expertTips':
                entity.append(','.join(map(str, item[key])))
            else:
                entity.append(item[key])
        data.append(tuple(entity))
    return data


data = videoData()

connection = sqlite3.connect("video.db")  # create/connect the database
cursor = connection.cursor()  # create the cursor to execute the sql sentence
cursor.execute('''CREATE TABLE IF NOT EXISTS VIDEO 
(ID INT PRIMARY KEY NOT NULL,
recipeImageSrc VARCHAR NOT NULL,
videoURL VARCHAR NOT NULL,
recipeName VARCHAR NOT NULL,
servingSize VARCHAR NOT NULL,
prepTime VARCHAR NOT NULL,
calories VARCHAR NOT NULL,
fat VARCHAR NOT NULL,
carbohydrate VARCHAR NOT NULL,
protien VARCHAR NOT NULL,
tags VARCHAR NOT NULL,
totalTime VARCHAR NOT NULL,
dish VARCHAR NOT NULL,
ingredient VARCHAR NOT NULL,
expertTips TEXT NOT NULL);''')
cursor.executemany(
    'insert into video values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);', data)
connection.commit()
connection.close()
