import requests  # fetch source data online
import pymysql
import configparser


def processVideoData():
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
    return data  # the data could be inserted into the database


def inserVideoData():
    '''
    This function is used to create the video table in the database and also insert the processed data into the table.
    '''

    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    connection = pymysql.connect(host=config['SQL']['HOST'], user=config['SQL']['USER'], password=config['SQL']['PASSWORD'], port=int(
        config['SQL']['PORT']), database=config['SQL']['DBNAME'])  # create/connect the database
    cursor = connection.cursor()  # create the cursor to execute the sql sentence

    query = "SELECT * FROM VIDEO"
    cursor.execute(query)
    rows = cursor.fetchall()

    if(len(rows) == 0):  # if there is no data in video table, insert
        cursor.execute('''CREATE TABLE IF NOT EXISTS VIDEO 
        (ID INT PRIMARY KEY NOT NULL,recipeImageSrc VARCHAR(255) NOT NULL,videoURL VARCHAR(255) NOT NULL,recipeName VARCHAR(255) NOT NULL,servingSize VARCHAR(255) NOT NULL,prepTime VARCHAR(255) NOT NULL,calories VARCHAR(255) NOT NULL,fat VARCHAR(255) NOT NULL,carbohydrate VARCHAR(255) NOT NULL,protien VARCHAR(255) NOT NULL,tags VARCHAR(255) NOT NULL,totalTime VARCHAR(255) NOT NULL,dish VARCHAR(255) NOT NULL,ingredient TEXT NOT NULL,expertTips TEXT NOT NULL);''')  # create video table
        cursor.executemany('INSERT INTO video (ID,recipeImageSrc,videoURL,recipeName,servingSize,prepTime,calories,fat,carbohydrate,protien,tags,totalTime,dish,ingredient,expertTips) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', processVideoData())  # insert entities
        connection.commit()  # save the data

    connection.close()  # disconnect
