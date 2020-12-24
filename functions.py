from dbconn import UseDataBase
from passlib.hash import sha256_crypt
from datetime import date


dbconn={"host":"localhost","user":"dbms_project","password":"passwd","database":"mini_project"}

def search_hospital_in_ward_without_v(i:int):
    with UseDataBase(dbconn) as cursor:
        _sql="""select * from display_without_v where ward_no=%s and not no_of_beds=0;"""   #display_without_v is view created in sql 
        cursor.execute(_sql,(i,))
        contents=cursor.fetchall()
        if(len(contents)!=0):
            return contents
        else:
            _sql="""select * from display_without_v where (ward_no=%s or ward_no=%s) and not no_of_beds=0;"""
            if i>1 and i<8:
                cursor.execute(_sql,(i-1,i+1,))
                contents=cursor.fetchall()
            elif i==1:
                cursor.execute(_sql,(i+1,i+2,))
                contents=cursor.fetchall()
            else:
                cursor.execute(_sql,(i-1,i-2,))
                contents=cursor.fetchall()
    return contents

def search_hospital_in_ward_with_v(i:int):
    with UseDataBase(dbconn) as cursor:
        _sql="""select * from display_with_v where ward_no=%s and not no_of_beds=0;"""
        cursor.execute(_sql,(i,))
        contents=cursor.fetchall()
        if(len(contents)!=0):
            return contents
        else:
            _sql="""select * from display_with_v where (ward_no=%s or ward_no=%s) and not no_of_beds=0;""" #display_with_v is a view created in sql
            if i>1 and i<8:
                cursor.execute(_sql,(i-1,i+1,))
                contents=cursor.fetchall()
            elif i==1:
                cursor.execute(_sql,(i+1,i+2,))
                contents=cursor.fetchall()
            else:
                cursor.execute(_sql,(i-1,i-2,))
                contents=cursor.fetchall()
    return contents

def add_new_hospital(l:tuple):
    with UseDataBase(dbconn) as cursor:
        _sql="""insert into hospitals
                values                                                      
                (%s,%s,%s,%s,%s,%s)"""                                   #inserting new hospital to hospital list
        cursor.execute(_sql,l)

def add_bed_without_v(l:tuple):
    with UseDataBase(dbconn) as cursor:
        _sql="""insert into hospital_without_v
                values
                (%s,%s,%s)"""                                           #adding no of beds without ventilators to the hospital details
        cursor.execute(_sql,l)

def add_bed_with_v(l:tuple):
    with UseDataBase(dbconn) as cursor:
        _sql="""insert into hospital_with_v
                values
                (%s,%s,%s)"""                                            #adding no of beds with ventilators to the hospital details
        cursor.execute(_sql,l)

def check_data_from_form(req):
    missing = list()

    for k, v in req.items():
        if v == "":
            missing.append(k)                                #checking if all details are entered

    if missing:
        raise Exception('please enter all details')


def encrypt_password(user,password):
    encrypted=sha256_crypt.hash(password)
    _sql="""
         INSERT INTO users
         VALUES
         (%s,%s)
         """
    with UseDataBase(dbconn) as cursor:
        cursor.execute(_sql,(user,encrypted))
        

def decrypt_password(user,password):
    _sql="""SELECT password from users where user_id=%s"""
    with UseDataBase(dbconn) as cursor:
        cursor.execute(_sql,(user,))
        content=cursor.fetchall()
    return sha256_crypt.verify(password,content[0][0])

def update_database(btype,patient_name,gender,cno,age,hid):
    _sql="""INSERT INTO patient_list(patient_name,gender,hospital_id,contact_no,age,ventilator,admit_date)
            VALUES
            (%s,%s,%s,%s,%s,%s,%s);"""
    today=date.today()
    today=today.strftime("%Y-%m-%d")
    with UseDataBase(dbconn) as cursor:
        cursor.execute(_sql,(patient_name,gender,hid,cno,age,btype,today))


def check_bed_availability(btype,hid):
    if btype=='y':
        _sql="""select  count(*) from hospital_with_v where hospital_id=%s and not no_of_beds=0;"""
    else:
        _sql="""select  count(*) from hospital_without_v where hospital_id=%s and not no_of_beds=0;"""

    with UseDataBase(dbconn) as cursor:
        cursor.execute(_sql,(hid,))
        content=cursor.fetchall()
    return content[0][0]

def bed_count_without_ventilators(hid):
    _sql="""select no_of_beds from hospital_without_v where hospital_id=%s;"""
    with UseDataBase(dbconn) as cursor:
        cursor.execute(_sql,(hid,))
        content=cursor.fetchall()
    return content[0][0]

def bed_count_with_ventilators(hid):
    _sql="""select no_of_beds from hospital_with_v where hospital_id=%s;"""
    with UseDataBase(dbconn) as cursor:
        cursor.execute(_sql,(hid,))
        content=cursor.fetchall()
    return content[0][0]

def decrement_bed_count(btype,hid):
    if btype=='y':
        _sql="""update hospital_with_v
                set no_of_beds=no_of_beds-1 where no_of_beds>0 and hospital_id=%s"""
    else:
        _sql="""update hospital_without_v
                set no_of_beds=no_of_beds-1 where no_of_beds>0 and hospital_id=%s"""
    with UseDataBase(dbconn) as cursor:
        cursor.execute(_sql,(hid,))

def increment_bed_count(btype,hid):
    if btype=='y':
        _sql="""update hospital_with_v
                set no_of_beds=no_of_beds+1 where no_of_beds>0 and hospital_id=%s"""
    else:
        _sql="""update hospital_without_v
                set no_of_beds=no_of_beds+1 where no_of_beds>0 and hospital_id=%s"""
    with UseDataBase(dbconn) as cursor:
        cursor.execute(_sql,(hid,))

def view_patients(hid):
    c=list()
    _sql="""select * from patient_list where hospital_id=%s and status='a';"""
    with UseDataBase(dbconn) as cursor:
        cursor.execute(_sql,(hid,))
        contents=cursor.fetchall()
    for i in contents:
        i=list(i)
        i[7]=i[7].strftime("%d-%m-%Y")
        c.append(i)
    return c

def discharge_patient(pid):
    _sql="""update patient_list
            set status='d' where patient_no=%s;"""
    with UseDataBase(dbconn) as cursor:
        cursor.execute(_sql,(pid,))
        _sql="""select ventilator from patient_list where patient_no=%s;"""
        cursor.execute(_sql,(pid,))
        content=cursor.fetchall()
    return content

def hospital_details(hid):
    _sql="""select * from hospitals where hospital_id=%s;"""
    with UseDataBase(dbconn) as cursor:
        cursor.execute(_sql,(hid,))
        contents=cursor.fetchall()
    return contents

content=hospital_details(1001)
print(content[0][5])



      
    

        














    
    
    
    
    
    


 







                
                
            
            
