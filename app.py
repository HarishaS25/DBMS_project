from flask import Flask,render_template,request

app=Flask(__name__)

@app.route("/")
def hello():
    return render_template('beds4meds.html',the_title='beds4meds')

@app.route("/hsearch",methods=['POST'])
def hsearch():
    pname=request.form['name']
    Age=request.form['age']
    cno=request.form['cno']
    wardno=request.form['wardno']
    gender=request.form.getlist('gender')
    return '{}{}{}{}{}'.format(pname,Age,cno,wardno,gender)

if __name__=="__main__":
    app.run(debug=True)
           
