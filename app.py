from flask import Flask,render_template,request,json,redirect,session
import sqlite3
from datetime import date, datetime
from werkzeug import generate_password_hash, check_password_hash
import os
import uuid
app= Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'
@app.route("/")
def main():
    return render_template('index.html')

@app.route("/showsignup")
def showsignup():
    return render_template('signup.html')

@app.route('/signUp', methods = ['POST'])
def signUp():
 
    # read the posted values from the UI
    
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    _hashed_password = generate_password_hash(_password)
 
    # validate the received values
    conn=sqlite3.connect('BucketList.db')
    cur=conn.cursor()
   
    cur.execute('select * from tblr_user where username=?',(_email,))
    row=cur.fetchone()
    
    if row is None:
        cur.execute('insert into tblr_user (name,username,password) values(?,?,?)',(_name,_email, _hashed_password))
        conn.commit()
        cur.close()
        conn.close()
        return json.dumps({'status':'Success'})
    else:
        return json.dumps({'status':'Failed'})


@app.route('/showsignin')
def showSignin():
    return render_template('signin.html')
@app.route('/validateLogin',methods=['POST'])
def validate():
    try:
        
        _username=request.form['inputEmail']
        _password=request.form['inputPassword']
    
    
        print (_username)
        conn=sqlite3.connect('BucketList.db')
        cur=conn.cursor()
        
        cur.execute('select * from tblr_user where username=?',(_username,))
        row=cur.fetchone()
        
        if row is not None:
            if check_password_hash(str(row[3]),_password):
                session['user']=row[0]
                return redirect('/showDashboard')
            else:
                return render_template('error.html',error="wrong email or password")
        else:
            return render_template('error.html',error="wrong email or password")
        
    except Exception as e:
        return render_template('error.html',error=str(e))
    

@app.route('/showDashboard')
def showDashboard():
    return render_template('dashboard.html')
    
@app.route('/getAllWishes',methods=['GET'])
def getAllWishes():
    try:
        if session.get('user'):
            print("hey")
            conn = sqlite3.connect('BucketList.db')
            cur = conn.cursor()
            cur.execute('select * from wish_tbl where wish_private=0')
            print("hey")
            result = cur.fetchall()
            print("hey")
         
            
         
            wishes_dict = []
            for wish in result:
                wish_dict = {
                        'Id': wish[0],
                        'Title': wish[1],
                        'Description': wish[2],
                        'FilePath': wish[5]}
                wishes_dict.append(wish_dict)       
 
            
 
            return json.dumps(wishes_dict)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/userHome')
def userhome():
    if session.get('user'):
        return render_template('UserHome.html')
    else:
        return render_template('error.html',error="Unauthurised Acess")
@app.route('/logout')
def logout():
    session.pop('user',None)
    
    return redirect('/')

@app.route('/showaddwish')
def showaddwish():
    return render_template('addwish.html')   
    
@app.route('/addwish',methods=['POST'])
def addwish():
    #print("hey")
    try:
        if session.get('user'):
            #print("hello")
            title=request.form['inputTitle']
            
            desc=request.form['inputDescription']
            user=session.get('user')
            if request.form.get('filePath') is None:
                print("true")
                filepath=''
            else:
                
                filepath=request.form.get('filePath')
                print(filepath);
            if request.form.get('private') is None:
                    private = 0
            else:
                    private = 1   
            #print(title,desc,user)
            conn=sqlite3.connect('BucketList.db')
            cur=conn.cursor()
            
            #cur.execute('select date('now')')
            #row=cur.fetchone()
            today = date.today()
            if title and desc:
                cur.execute('insert into wish_tbl (title,desc,userid,date,wish_file,wish_private) values(?,?,?,?,?,?)',(title,desc,user,today,filepath,private))
                conn.commit()
                return redirect('/userHome')
                            
        else:
           return render_template('error.html',error="Unauthorised Access")
    
    except Exception as e:
        return render_template('error.html',error=str(e))
    
@app.route('/getwish')
def getwish():
    try:
        if session.get('user'):
            user=session.get('user')
            conn=sqlite3.connect('BucketList.db')
            cur=conn.cursor()
            
            cur.execute('select * from wish_tbl where userid=?',(user,));
            row=cur.fetchall();
            if len(row) is 0:
                print("hhhhh")
                
                return json.dumps({'status':'empty'})
            wishes_dict=[]
            for r in row:
                wish={'Id':r[0],'Title':r[1],'Description':r[2],'Date':r[4],'Path':r[5]}
                wishes_dict.append(wish)
            
            return json.dumps(wishes_dict)    
        else:
           return render_template('error.html',error="Unauthorised Access")
    
    except Exception as e:
        return render_template('error.html',error=str(e))

@app.route('/getwishid',methods=['POST'])
def getwishid():
    try:
        if session.get('user'):
            user=session.get('user')
            wid=request.form['id']
            conn=sqlite3.connect('BucketList.db')
            cur=conn.cursor()
            
            cur.execute('select * from wish_tbl where userid=? and wishid=?',(user,wid));
            row=cur.fetchall();
            
            wishes_dict=[]
            for r in row:
                wish={'Id':r[0],'Title':r[1],'Description':r[2],'FilePath':r[5],'Private':r[6]}
                wishes_dict.append(wish)
            
            return json.dumps(wishes_dict)    
        else:
           return render_template('error.html',error="Unauthorised Access")
    
    except Exception as e:
        return render_template('error.html',error=str(e))

  
@app.route('/updatewish',methods=['POST'])
def updatewish():
    try:
        if session.get('user'):
            uid=session.get('user')
            wid=request.form['id']
            title=request.form['title']
            filePath = request.form['filePath']
            private = request.form['isPrivate']
            description=request.form['description']
            
            conn=sqlite3.connect('BucketList.db')
            cur=conn.cursor()
           # print(title,description,filePath,private,wid,uid)
            cur.execute('update wish_tbl set title=?,desc=?,wish_file=?,wish_private=? where wishid=? and userid=?',
                    (title,description,filePath,private,wid,uid));
           # print("hey")
            data=cur.fetchall()
            
            if len(data) is 0:
                conn.commit()
                return json.dumps({'Status':'OK'})
            else:
                return json.commit({'status':'Error'})
                
    except Exception as e:
        return json.dumps({'status':'Unauthorized access'}) 
        


@app.route('/deletewish',methods=['POST'])
def deletewish():
    try:
        if session.get('user'):
            user=session.get('user')
            wid=request.form['id']
            conn=sqlite3.connect('BucketList.db')
            cur=conn.cursor()
            
            cur.execute('delete from wish_tbl where userid=? and wishid=?',(user,wid));
            result = cur.fetchall()
 
            if len(result) is 0:
                print("yes")

                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'An Error occured'})
        else:
            return render_template('error.html',error = 'Unauthorized Access')
    
    except Exception as e:
        return render_template('error.html',error=str(e))
              
            
@app.route('/upload',methods=['POST','GET']) 
def upload():
    print("hvh")
    if request.method=='POST':
        
        file=request.files['file']
       
        extension = os.path.splitext(file.filename)[1]
        
        f_name = str(uuid.uuid4()) + extension
        
        app.config['UPLOAD_FOLDER'] = 'static/Uploads'
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        
        return json.dumps({'filename':f_name})
        

   
if __name__=="__main__":
    app.run()
