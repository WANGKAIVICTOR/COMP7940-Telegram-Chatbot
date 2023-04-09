import requests  # fetch source data online
import pymysql
import configparser
from log import logger
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import etree
import emoji
import re
import os
from tqdm import tqdm


def get_db_connection():
    '''
    This function is used to connect to the database, if there's no such database, create it.

    Return:
        connection of database
    '''

    logger.info("Connecting databse")
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    while True:
        try:
            if os.getenv('AM_I_IN_A_DOCKER_CONTAINER'):
                connection = pymysql.connect(host=os.getenv('HOST'), user=os.getenv('USER'), password=os.getenv('PASSWORD'), port=int(
                    os.getenv('PORT')), autocommit=True, cursorclass=pymysql.cursors.DictCursor)
            else:
                connection = pymysql.connect(host=config['SQL']['HOST'], user=config['SQL']['USER'], password=config['SQL']['PASSWORD'], port=int(
                    config['SQL']['PORT']), autocommit=True, cursorclass=pymysql.cursors.DictCursor)
        except Exception as e:
            logger.error(e)
        else:
            break

    connection.cursor().execute('CREATE DATABASE IF NOT EXISTS %s;' % "telegram_chatbot")
    connection.select_db("telegram_chatbot")
    logger.info("Database connected")
    return connection


def table_exists(connection, table_name):
    sql = "show tables;"
    cursor = connection.cursor()  # create the cursor to execute the sql sentence
    cursor.execute(sql)
    tables = cursor.fetchall()
    tables = [item[key]
              for item in tables for key in item]  # get all table names
    if table_name in tables:
        return True
    return False


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

    if(not table_exists(connection, "VIDEO")):
        cursor.execute("""CREATE TABLE IF NOT EXISTS VIDEO (ID INT PRIMARY KEY NOT NULL,recipeImageSrc VARCHAR(255) NOT NULL,videoURL VARCHAR(255) NOT NULL,recipeName VARCHAR(255) NOT NULL,servingSize VARCHAR(255) NOT NULL,prepTime VARCHAR(255) NOT NULL,calories VARCHAR(255) NOT NULL,fat VARCHAR(255) NOT NULL,carbohydrate VARCHAR(255) NOT NULL,protien VARCHAR(255) NOT NULL,tags VARCHAR(255) NOT NULL,totalTime VARCHAR(255) NOT NULL,dish VARCHAR(255) NOT NULL,ingredient TEXT NOT NULL,expertTips TEXT NOT NULL);""")  # create video table
        cursor.executemany('INSERT INTO VIDEO (ID,recipeImageSrc,videoURL,recipeName,servingSize,prepTime,calories,fat,carbohydrate,protien,tags,totalTime,dish,ingredient,expertTips) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', process_video_data())  # insert entities
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
    cursor.execute("SELECT tags from VIDEO")
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
    cursor.execute("SELECT * from VIDEO WHERE tags LIKE '%"+tag+"%'")
    data = cursor.fetchall()
    if(len(data) == 0):
        return ""
    data = random.choice(data)
    data.pop('ID')
    return str(data)


def set_chrome_options() -> None:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options


def process_review_data():
    urls = {"潜伏": "3314870", "大宅门": "2181930", "红色": "25966028", "红楼梦": "1864810", "琅琊榜": "25754848",
            "武林外传": "3882715", "黎明之前": "4894070", "战长沙": "20258941", "西游记": "2156663", "士兵突击": "2154096"}
    result = []

    pbar = tqdm(urls.keys())
    for key in pbar:
        pbar.set_description("Processing %s" % (key+" review"))
        driver = webdriver.Chrome(
            options=set_chrome_options())  # create a chrome obj
        driver.get("https://movie.douban.com/subject/" +
                   urls[key]+"/comments?status=P")  # open the website
        page_source = driver.page_source  # get the source code
        html = etree.HTML(page_source)
        data = html.xpath('//span[@class="short"]/text()')
        for d in data:
            d.replace('\n', '').replace('\r', '')
            text = emoji.demojize(d)  # delete emoji
            result.append(tuple([key, re.sub(':\S+?:', ' ', text)]))
        driver.quit()  # close the  broswer

    return result


def insert_review_data():
    connection = get_db_connection()
    cursor = connection.cursor()  # create the cursor to execute the sql sentence
    logger.info("Connected to the database in insert review part.")

    if(not table_exists(connection, "review")):  # if there is no data in video table, insert
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS review (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255) NOT NULL,content TEXT NOT NULL);""")  # create video table
        cursor.executemany(
            'INSERT INTO review (name, content) VALUES (%s,%s);', process_review_data())
        connection.commit()  # save the data
        logger.info("Review data inserted.")
    logger.info("Disconnected the database.")
    connection.close()  # disconnect


def read_tv_review_with_name(name):
    connection = get_db_connection()
    cursor = connection.cursor()  # create the cursor to execute the sql sentence
    cursor = get_db_connection().cursor()
    cursor.execute("SELECT * from review WHERE name LIKE '%"+name+"%'")
    data = cursor.fetchall()
    if(len(data) == 0):
        return ""
    data = random.choice(data)
    data.pop('id')
    return data['name']+"评论: "+data['content']


def write_tv_review(name, content):
    connection = get_db_connection()
    cursor = connection.cursor()  # create the cursor to execute the sql sentence
    logger.info([tuple([name, content])])
    cursor.executemany('INSERT INTO review (name, content) VALUES (%s,%s);', ([
                       tuple([name, content])]))
    connection.commit()  # save the data
    connection.close()  # disconnect
    return "添加成功!"


def get_tv_review_names():
    cursor = get_db_connection().cursor()
    cursor.execute("SELECT name from review")
    data = cursor.fetchall()
    names = str(set(sum(list(map(lambda x: x.split(','), [
        item[key] for item in data for key in item])), [])))
    return names
