from mysql import connector

class UseDataBase:
    def __init__(self,dbconf):
        self.dbconf=dbconf
    def __enter__(self):
        self.conn=connector.connect(**self.dbconf)
        self.cursor=self.conn.cursor()
        return self.cursor

    def __exit__(self,exc_type,exc_value,exc_trace):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

