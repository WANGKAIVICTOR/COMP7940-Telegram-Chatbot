import requests  # fetch source data online
import pymysql
import configparser
from log import logger
import random


def get_db_connection():
    '''
    This function is used to connect to the database, if there's no such database, create it.

    Return:
        connection of database
    '''

    logger.info("Connecting databse")
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    connection = pymysql.connect(host=config['SQL']['HOST'], user=config['SQL']['USER'], password=config['SQL']['PASSWORD'], port=int(
        config['SQL']['PORT']), autocommit=True, cursorclass=pymysql.cursors.DictCursor)
    connection.cursor().execute('CREATE DATABASE IF NOT EXISTS %s;' % "telegram_chatbot")
    connection.select_db("telegram_chatbot")
    logger.info("Database connected")
    return connection


def process_video_data():
    '''
    This function is used to fetch and process video data, so that it can be inserted into database.

    return:
        the list of tuples
    '''

    url = "https://radiant-island-16688.herokuapp.com/getRecipe/4fbc68d6-de7d-437f-a017-e4f99afb4471"  # source data url
    headers = {
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    }  # define headers, it's used to fetch data
    response = requests.get(url, headers=headers)  # fetch data in json file
    items = response.json()  # extract data
    data = []
    logger.info("Video data fetched.")
    for item in items:  # process data one by one accroding to the key value
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
        # convert the list to tuple and insert it into a list
        data.append(tuple(entity))
    logger.info("Video data processed.")
    return data  # the data could be inserted into the database


def insert_video_data():
    '''
    This function is used to create the video table in the database and also insert the processed data into the table.
    '''

    connection = get_db_connection()
    cursor = connection.cursor()  # create the cursor to execute the sql sentence

    logger.info("Connected to the database in video part.")
    query = "SELECT * FROM VIDEO"
    cursor.execute(query)
    rows = cursor.fetchall()

    if(len(rows) == 0):  # if there is no data in video table, insert
        logger.info("The table is empty, inserting the video data.")
        cursor.execute("""CREATE TABLE IF NOT EXISTS VIDEO (ID INT PRIMARY KEY NOT NULL,recipeImageSrc VARCHAR(255) NOT NULL,videoURL VARCHAR(255) NOT NULL,recipeName VARCHAR(255) NOT NULL,servingSize VARCHAR(255) NOT NULL,prepTime VARCHAR(255) NOT NULL,calories VARCHAR(255) NOT NULL,fat VARCHAR(255) NOT NULL,carbohydrate VARCHAR(255) NOT NULL,protien VARCHAR(255) NOT NULL,tags VARCHAR(255) NOT NULL,totalTime VARCHAR(255) NOT NULL,dish VARCHAR(255) NOT NULL,ingredient TEXT NOT NULL,expertTips TEXT NOT NULL);""")  # create video table
        cursor.executemany('INSERT INTO video (ID,recipeImageSrc,videoURL,recipeName,servingSize,prepTime,calories,fat,carbohydrate,protien,tags,totalTime,dish,ingredient,expertTips) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', process_video_data())  # insert entities
        connection.commit()  # save the data
        logger.info("Video data inserted.")

    logger.info("Disconnected the database.")
    connection.close()  # disconnect


def get_meals_tags():
    '''
    This function is used to get the tags of meals video, so that the users can choose the specific meals they what

    Return:
        tags of meal
    '''

    cursor = get_db_connection().cursor()
    cursor.execute("SELECT tags from video")
    data = cursor.fetchall()
    # process the data and get the unique set
    tags = str(set(sum(list(map(lambda x: x.split(','), [
               item[key] for item in data for key in item])), [])))
    return tags


def get_info_with_tag(tag):
    '''
    This function is used to select the video according to the tag.

    Return the first one
    '''

    cursor = get_db_connection().cursor()
    cursor.execute("SELECT * from video WHERE tags LIKE '%"+tag+"%'")
    data = cursor.fetchall()
    return str(random.choice(data))
