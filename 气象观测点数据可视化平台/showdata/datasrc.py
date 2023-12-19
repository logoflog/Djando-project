import sqlite3
import pandas as pd


class SqliteTool:
    """
    简单sqlite数据库工具类
    编写这个类主要是为了封装sqlite，继承此类复用方法
    """

    def __init__(self, dbName="data.db"):
        """
        初始化连接——使用完需关闭连接
        :param dbName: 连接库的名字，注意，以'.db'结尾
        """
        # 连接数据库
        self._conn = sqlite3.connect(dbName)
        # 创建游标
        self._cur = self._conn.cursor()

    def close_con(self):
        """
        关闭连接对象——主动调用
        :return:
        """
        self._cur.close()
        self._conn.close()

    # 创建数据表
    def create_tabel(self, sql: str):
        """
        创建表
        :param sql: create sql语句
        :return: True表示创建表成功
        """
        try:
            self._cur.execute(sql)
            self._conn.commit()
            print("[create table success]")
            return True
        except Exception as e:
            print("[create table error]", e)

    # 删除数据表
    def drop_table(self, sql: str):
        """
        删除表
        :param sql: drop sql语句
        :return: True表示删除成功
        """
        try:
            self._cur.execute(sql)
            self._conn.commit()
            return True
        except Exception as e:
            print("[drop table error]", e)
            return False

    # 插入或更新表数据，一次插入或更新一条数据
    def operate_one(self, sql: str, value: tuple):
        """
        插入或更新单条表记录
        :param sql: insert语句或update语句
        :param value: 插入或更新的值，形如（）
        :return: True表示插入或更新成功
        """
        try:
            self._cur.execute(sql, value)
            self._conn.commit()
            if "INSERT" in sql.upper():
                print("[insert one record success]")
            if "UPDATE" in sql.upper():
                print("[update one record success]")
            return True
        except Exception as e:
            print("[insert/update one record error]", e)
            self._conn.rollback()
            return False

    # 插入或更新表数据，一次插入或更新多条数据
    def operate_many(self, sql: str, value: list):
        """
        插入或更新多条表记录
        :param sql: insert语句或update语句
        :param value: 插入或更新的字段的具体值，列表形式为list:[(),()]
        :return: True表示插入或更新成功
        """
        try:
            # 调用executemany()方法
            self._cur.executemany(sql, value)
            self._conn.commit()
            if "INSERT" in sql.upper():
                print("[insert many  records success]")
            if "UPDATE" in sql.upper():
                print("[update many  records success]")
            return True
        except Exception as e:
            print("[insert/update many  records error]", e)
            self._conn.rollback()
            return False

    # 删除表数据
    def delete_record(self, sql: str):
        """
        删除表记录
        :param sql: 删除记录SQL语句
        :return: True表示删除成功
        """
        try:
            if "DELETE" in sql.upper():
                self._cur.execute(sql)
                self._conn.commit()
                print("[detele record success]")
                return True
            else:
                print("[sql is not delete]")
                return False
        except Exception as e:
            print("[detele record error]", e)
            return False

    # 查询一条数据
    def query_one(self, sql: str, params=None):
        """
        查询单条数据
        :param sql: select语句
        :param params: 查询参数，形如()
        :return: 语句查询单条结果
        """
        try:
            if params:
                self._cur.execute(sql, params)
            else:
                self._cur.execute(sql)
            # 调用fetchone()方法
            r = self._cur.fetchone()
            print("[select one record success]")
            return r
        except Exception as e:
            print("[select one record error]", e)

    # 查询多条数据
    def query_many(self, sql: str, params=None):
        """
        查询多条数据
        :param sql: select语句
        :param params: 查询参数，形如()
        :return: 语句查询多条结果
        """
        try:
            if params:
                self._cur.execute(sql, params)
            else:
                self._cur.execute(sql)
            # 调用fetchall()方法
            r = self._cur.fetchall()
            print("[select many records success]")
            return r
        except Exception as e:
            print("[select many records error]", e)

    # 从csv文件中读取数据, 网站中能够让管理员在后台添加csv文件, 所以要有这个函数;
    # 另外, sqlite中单个文件能够存储的数据量高达140TB, 因此不用创建多个.db文件
    def csv2db(self, file):  # file示例:"数据源.csv"
        try:
            csvdf = pd.read_csv(file)
            # 插入数据
            for index, row in csvdf.iterrows():
                # 一次插入一条数据
                self.operate_one(
                    "insert into datasource values(?,?,?,?,?,?,?,?,?)",
                    (
                        str(row["STATION"]) + "," + row["DATE"],
                        row["NAME"],
                        row["LATITUDE"],
                        row["LONGITUDE"],
                        row["DEW"],
                        row["SLP"],
                        row["TMP"],
                        row["VIS"],
                        row["WND"],
                    ),
                )
            # 关闭游标和连接
            self.close_con()
        except Exception as e:
            print("[read to DB file error]", e)

    # 从db文件中读取数据出来, 返回形式为dataframe
    def db2df(self):
        try:
            # 执行查询语句
            self._cur.execute("select * from datasource")
            # 获取查询结果
            result = self._cur.fetchall()
            # 获取查询的字段名
            columns = [desc[0] for desc in self._cur.description]
            # 使用查询结果和字段名创建 DataFrame
            df = pd.DataFrame(result, columns=columns)
            print("[read to DataFrame success]")
            # 关闭游标和连接
            self.close_con()
            return df
        except Exception as e:
            print("[read to DataFrame error]", e)
# mysqlite = SqliteTool()
# df = [iter[-1] for iter in mysqlite.db2df()['tmp']]
# print(set(df))
