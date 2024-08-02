import datetime
import pymysql

class DFC_DB:
    def __init__(self,hostip,username, pw, dbname):
        self.Hostip = hostip
        self.UserName = username
        self.PW = pw
        self.DBname = dbname
        self.conn = pymysql.connect(host=self.Hostip, user=self.UserName, password=self.PW, db=self.DBname,
                                     charset='utf8', read_timeout=2, write_timeout=2, connect_timeout=2, autocommit=True)
        self.cur = self.conn.cursor()

    def Open_db(self):
        try:
            self.conn = pymysql.connect(host=self.Hostip, user=self.UserName, password=self.PW, db=self.DBname, charset='utf8')
            self.cur = self.conn.cursor()
            self.conn.ping(reconnect=True)

        except pymysql.err.InternalError as e:
            code, msg = e.args
            print("error Open_db : ")
            print(msg)
    
    def Close_db(self):
        self.conn.close()

    def Flash_db(self):
        self.Close_db()
        self.Open_db()
    
    def Get_uploaded(self):
        try:
            self.cur.execute("Select a.token_key, a.path, a.state_sn, a.model_sn, a.hef from dfc_data a, DFC_STATE b Where a.state_sn = b.State_SN and b.Title = 'Uploaded' order by a.requested_time")
            res = self.cur.fetchall()
        
            if len(res) >= 1:
                return res[0]
            else :
                return 0
        except pymysql.err.InternalError as e:
            code, msg = e.args
            print("error Get_uploaded : ")
            print(msg)

    def Get_Model(self, tokenkey):
        try:
            self.cur.execute("Select a.token_key,b.* FROM dfc_data a, Model_DFC_PaserList AS b WHERE a.Model_SN = b.Model_SN AND a.token_key=%s",tokenkey)
            res = self.cur.fetchall()
            return res[0][3:]
        except Exception as e :
            print("error Get_Model : ")
            print(e)

    def Set_finish(self,hef_name,tokenkey):
        try:
            now = datetime.datetime.now()
            sql = "Update dfc_data SET state_sn = %s, hef = %s, dfc_end_time = %s Where token_key = %s"
            
            self.cur.execute(sql, (3, hef_name,now.strftime('%Y-%m-%d %H:%M:%S'),tokenkey))
            self.conn.commit()
        except Exception as e :
            print("error Set_finish : ")
            print(e)

    def Set_start(self,tokenkey):
        try:
            now = datetime.datetime.now()
            sql = "Update dfc_data SET state_sn = %s, dfc_start_time = %s Where token_key = %s"
            
            self.cur.execute(sql, (2 ,now.strftime('%Y-%m-%d %H:%M:%S'),tokenkey))
            self.conn.commit()

            if self.cur.rowcount == 0 :
                print("적용된 업데이트 데이터가 없습니다.")
            else :
                print(self.cur.rowcount)
        except Exception as e :
            print("error Set_start : ")
            print(e)

    def Set_Error(self,tokenkey):
        try:
            now = datetime.datetime.now()
            sql = "Update dfc_data SET state_sn = %s, dfc_end_time = %s Where token_key = %s"
            
            self.cur.execute(sql, (9, now.strftime('%Y-%m-%d %H:%M:%S'),tokenkey))
            self.conn.commit()
        except Exception as e :
            print("error Set_Error : ")
            print(e)