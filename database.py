import pymysql
import configparser

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')


db = pymysql.connect(host=config['SQL']['HOST'], user=config['SQL']['USER'],
                     password=config['SQL']['PASSWORD'], port = int(config['SQL']['PORT']),
                     database=config['SQL']['DBNAME'])
 
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()
 
# 使用 execute()  方法执行 SQL 查询 
cursor.execute("SELECT VERSION()")
 
# 使用 fetchone() 方法获取单条数据.
data = cursor.fetchone()
 
print ("Database version : %s " % data)
 
# 关闭数据库连接
db.close()