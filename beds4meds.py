from flask import Flask,render_template,request,g,session,redirect,flash
from datetime import timedelta
import functions
import os

app=Flask(__name__)

app.secret_key=os.urandom(24)

dbconn={"host":"localhost","user":"dbms_project","password":"passwd","database":"mini_project"} #sql user and database details
ldetail=[]


@app.route("/",methods=['GET','POST'])
def entry():
    return render_template('home.html',the_title='home')

@app.route("/hsearch",methods=['GET','POST'])
def hello():
    return render_template('beds4meds.html',the_title='beds4meds')

@app.route("/home",methods=['GET','POST'])
def home():
    return redirect('/dropsession')

@app.route("/login",methods=['GET','POST'])
def login():
    if "user" in session:
        flash("Already Logged in")
        return redirect('/admin')
    else:
        return render_template('loginpage.html')

@app.route("/register",methods=['GET','POST'])
def register():
    return render_template('register.html',the_title='register')

@app.route("/success" ,methods=['post'])
def success():
    req=request.form
    try:
        functions.check_data_from_form(req)
    except Exception:
        return redirect('/register')
        
    
    hname=request.form['hname']
    haddr=request.form['haddr']
    hid=request.form['hid']
    hcno=request.form['cno']
    hwardno=request.form['wno']
    hnowov=request.form['bno_wo_v']
    hcowov=request.form['cpd_wo_v']
    hnowv=request.form['bno_w_v']
    hcowv=request.form['cpd_w_v']
    ambsrv=request.form['amb_srv']
    hpasswd=request.form['passwd']

    #checking if total no of beds is zero
    if int(hnowov)==0 and int(hnowv)==0:
        flash("no of beds cant be zero")
        return redirect('/login')
    #if not zero then add hospitalinto database
    functions.add_new_hospital((hwardno,hcno,hid,hname,haddr,ambsrv))
    functions.encrypt_password(hid,hpasswd)
    functions.add_bed_without_v((hid,hnowov,hcowov))
    functions.add_bed_with_v((hid,hnowv,hcowv))
    
    flash("hospital registered")
    return redirect('/login')

@app.route("/update",methods=['POST','GET'])
def update():
    req=request.form
    try:
        functions.check_data_from_form(req)
    except Exception:
        return redirect('/login')
    if functions.decrypt_password(int(request.form['uname']),request.form['psswd']):
        session['user']=request.form['uname']
        flash("login successful")
        return redirect('/admin')
    else:
        flash("wrong password/userid")
        return redirect('/login')

@app.route('/admin',methods=['POST','GET'])
def admin():
        if "user" in session:
            return render_template('admin.html')
        else:
            return redirect('/login')

@app.route('/add_patient')
def add_patient():
    if "user" in session:
        user=session["user"]
        bnowov=functions.bed_count_without_ventilators(user)
        bnowv=functions.bed_count_with_ventilators(user)
        return render_template('add_patient.html',bwov=bnowov,bwv=bnowv)

@app.route('/success1',methods=['POST','GET'])
def upddate_db():
    if "user" in session:
        req=request.form
        try:
            functions.check_data_from_form(req)
        except Exception:
            return redirect('/add_patient')
        user=session["user"]
        if functions.check_bed_availability(request.form['bt'],user):
            functions.update_database(request.form['bt'],request.form['name'],request.form['gender'],request.form['cno'],request.form['age'],user)
            functions.decrement_bed_count(request.form['bt'],user)
            flash("Patient was admitted successfully")
            return redirect('/admin')
        else:
            flash("No bed is available")
            return redirect('/admin')

@app.route('/view_patient')
def view():
    if "user" in session:
        user=session["user"]
        content=functions.view_patients(user)
        if len(content)==0:
            flash("No patients")
            return redirect('/admin')
        else:
            l=['patient_no','patient_name','gender','contact_no','age','ventilator','admit_date']
            return render_template('view_patient.html',row_titles=l,the_data=content)
    else:
        return redirect('/login')

@app.route('/discharge',methods=['POST','GET'])
def discharge():
    if "user" in session:
        user=session["user"]
        req=request.form
        try:
            functions.check_data_from_form(req)
        except Exception:
            return redirect('/view_patient')
        if functions.check_patient(request.form['pid'],user):
            content=functions.discharge_patient(request.form['pid'])
            flash("Patient was discharged successfully")
            return redirect('/admin')
        else:
            flash("enter correct patient id")
            return redirect('/admin')
        
    else:
        return redirect('/login')

@app.route('/about_us')
def about_us():
    return render_template('about.html')

@app.before_request
def before_request():
    g.user=None

    if 'user' in session:
        g.user=session['user']

@app.route('/dropsession')
def dropsession():
    if "user" in session:
        flash("You were logged out successfully")
    session.pop('user',None)
    return redirect('/login')


@app.route("/hlist",methods=['POST'])
def hsearch():
    l=('hospital_id','ward_no','hospital_name','no_of_beds','cost_per_day')
    message="Hurray! There are hospitals in your ward or in nearby wards."
    message1="we recommend hospital with vetilator considering your age."
    ldetail.clear()
    req = request.form
    try:
        functions.check_data_from_form(req)
    except Exception:
        return redirect('/hsearch')
    pname=request.form['name']
    Age=int(request.form['age'])
    cno=request.form['cno']
    wardno=request.form['wardno']                            #taking all details filled in form
    gender=request.form.getlist('gender')
    ge =gender[0]
    ldetail.extend([pname,Age,cno,wardno,ge])
    contents=functions.search_hospital_in_ward_without_v(int(wardno))
    contents1=functions.search_hospital_in_ward_with_v(int(wardno))
    if len(contents)==0:                                                   #checking if hospital is present or not
        return render_template('hsearch_no_hospital.html',the_name=pname,the_age=Age,the_wardno=wardno,the_gender=ge,the_contno=cno)
    elif int(Age)<60:                                                      #checking age ,if age>60 then recommend hospital with ventilators
        return render_template('hsearch_in_ward.html',the_name=pname,the_age=Age,the_wardno=wardno,the_gender=ge,the_contno=cno,row_titles=l,the_data=contents,the_message=message)
    else:
        if len(contents1)==0:
            return render_template('hsearch_in_ward.html',the_name=pname,the_age=Age,the_wardno=wardno,the_gender=ge,the_contno=cno,row_titles=l,the_data=contents,the_message=message)
        else:
            return render_template('hsearch_in_ward.html',the_name=pname,the_age=Age,the_wardno=wardno,the_gender=ge,the_contno=cno,row_titles=l,the_data=contents1,the_message=message1)
            

@app.route('/confirm',methods=['GET','POST'])
def confirm():
    contents=functions.hospital_details(request.form['hid'])
    cost_without_v=functions.avg_cost_without_v(request.form['hid'])
    cost_with_v=functions.avg_cost_with_v(request.form['hid'])
    if cost_with_v!=0:
        cost=cost_with_v
    else:
        cost=cost_without_v
    return render_template('final.html',the_name=contents[0][3],the_id=contents[0][2],the_cno=contents[0][1],the_wno=contents[0][0],the_addr=contents[0][4],the_ambs=contents[0][5],the_cost=cost)
    
if __name__=="__main__":
    app.run(debug=True)
           
