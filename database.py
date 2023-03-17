import pymysql
import configparser

import requests

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')


# db = pymysql.connect(host=config['SQL']['HOST'], user=config['SQL']['USER'],
#                      password=config['SQL']['PASSWORD'], port = int(config['SQL']['PORT']),
#                      database=config['SQL']['DBNAME'])
 
# # craete cursor
# cursor = db.cursor()
 
# # 使用 execute()  方法执行 SQL 查询 
# cursor.execute("SELECT VERSION()")
 
# # 使用 fetchone() 方法获取单条数据.
# data = cursor.fetchone()
 
# print ("Database version : %s " % data)
 
# # 关闭数据库连接
# db.close()

def processVideoData():
    '''
    This function is used to fetch and process video data, so that it can be inserted into database.

    return:
        the list of tuples
    '''

    url = "https://radiant-island-16688.herokuapp.com/getRecipe/4fbc68d6-de7d-437f-a017-e4f99afb4471"  # source data url
    headers = {
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    } # define headers, it's used to fetch data
    response = requests.get(url, headers=headers)  # fetch data in json file
    items = response.json()  # extract data
    data = []
    for item in items: # process data one by one accroding to the key value
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
        data.append(tuple(entity)) # convert the list to tuple and insert it into a list
    return data # the data could be inserted into the database

print(processVideoData()[0])