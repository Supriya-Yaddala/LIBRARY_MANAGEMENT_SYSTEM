from flask import Flask,render_template,url_for,request,session,redirect
import sqlite3

app=Flask(__name__)
app.secret_key='secret'

#************************************************************library DATABASE CREATING******************************************************#
#************************************************************Library database is created*******************************************************
conn=sqlite3.connect('library.db') 
cur=conn.cursor()

#**********************************************************USERS TABLE creation***********************************************************
cur.execute("select name from sqlite_master where type='table' and name='users';")
if cur.fetchone() is None:
	createuser="create table users(uid integer primary key,uname text(25),branch text,password text,fine integer default 0);"
	cur.execute(createuser)

#*********************************************************BOOKS TABLE CREATION*****************************************************************
cur.execute("select name from sqlite_master where type='table' and name='books';")
if cur.fetchone() is None:
	c_books="create table books(bid integer NOT NULL primary key ,book_name text(50) NOT NULL,author_name text,category text(20) NOT NULL,quantity check(quantity>=0));"
	cur.execute(c_books) 

#*******************************************************ISSUED TABLE CREATION*****************************************************************
cur.execute("select name from sqlite_master where type='table' and name='issued';")
if cur.fetchone() is None:
	createissue="create table issued(iid integer primary key AUTOINCREMENT,uid integer,bid integer,issuedate date,returndate date,fine int default 0);"
	cur.execute(createissue)

#*****************************************************closing of connection to database*********************************************************
conn.close()

#*************************************************************home page display****************************************************************
@app.route('/')
def home():
	return render_template('index.html')

#**************takes to admin login page*******************************************
@app.route('/adlogin')
def adminlogin():
	return render_template('adminlogin.html',flag=0)

#*********************verifies admin login values************************************** 
@app.route('/adverify',methods=['post','get'])
def adminverify():

    if request.method=="POST":
    	uname=request.form['nm']
    	pwd=request.form['pd']
    	#**********checks for admin authentication*****************
    	if uname=='admin' and pwd=='admin':
    		session['admin']='admin'
    		#******USED TO MAKE SURE ON REFRESHING FORM VAKUES DOESN't submit *************
    		return redirect(url_for('adminverify'))
    		

    	else:
    		return redirect(url_for('adminlogin'))
    else:
    	#*******************CHECKS FOR ADMIN  in SESSION*************
    	if 'admin' in session:
    		return render_template('adminpage.html')
    	else:
    		return redirect(url_for('adminlogin'))

#***********Take to addbook page**********************
@app.route('/addbook',methods=['post','get'])
def addbookupdate():
	return render_template('addbook.html')

#*****************Update book details to library*********************
@app.route('/updatebook',methods=['post','get'])
def updatebook():
	#*************opens database connection*******************
	conn=sqlite3.connect('library.db') 
	cur=conn.cursor()

	#**************************Get details from form*******************
	bname=request.form['bn']
	aname=request.form['an'] 
	cat=request.form['cg']
	bid=request.form['bid']
	qty=request.form['qty']

	#**********************insert values into books table**************************
	try:
		query="insert into books(bid ,book_name ,author_name ,category ,quantity ) values(?,?,?,?,?);"
		cur.execute(query,(bid,bname,aname,cat,qty))
		res=cur.fetchall()
		conn.commit()
		msg="BOOK UPDATED SUCCESSFULLY."
		
	except:
		msg="BOOK UPDATE FAILED"
		pass
	conn.close()
		
	return render_template('addbook.html',msg=msg,flag=6)
@app.route('/viewbooks')
def viewbooks():
	conn=sqlite3.connect('library.db')
	cur=conn.cursor()
	cur.execute('select * from books')
	res=cur.fetchall()
	conn.close()
	return render_template('bookview.html',res=res)


#*****************Take to adduser page*********************

@app.route('/adduser')
def adduser():
	return render_template('adduser.html')

#*************************Update user details into library**************************
@app.route('/updateuser',methods=["post","get"])
def updateuser():
	#*********************Get form data**************************************8
	uid=request.form['rn'] 
	uname=request.form['un']
	branch=request.form['bh'] 
	pwd=request.form['pd']
	
	#****************opens database connection*************************
	conn=sqlite3.connect('library.db')
	cur=conn.cursor()

	#**************insert data innto users table***************************
	add_user_db="insert into users(uid,uname,branch,password) values(?,?,?,?)"
	cur.execute(add_user_db,(uid,uname,branch,pwd))
	conn.commit()
	results=[(uid,uname,branch,pwd)]
	conn.close()
	return render_template('addbook.html',msg="SUCCESSFULLY "+uname+" added",flag=6)


#*******************view users in library***************
@app.route('/viewuser')
def viewuser():
	conn=sqlite3.connect('library.db')
	cur=conn.cursor()
	cur.execute('select * from users')
	res=cur.fetchall()
	conn.close()
	return render_template('viewuser.html',res=res)

#**********************Take to issue page***************
@app.route('/issue')
def issue():
	return render_template('issue.html')

#**************8issue book to user*******************

@app.route('/issuebook',methods=["post","get"])
def issuebook():
	#************GETTING FORM DETAILS************
	uid=request.form['rn'] 
	bid=request.form['bid']
	issdate=request.form['dt'] 
	retdate="NOT RETURN"

	#******************CONNECTING TO DATABASE**************
	conn=sqlite3.connect('library.db') 
	cur=conn.cursor()

	#*************************GET USER DETAILS*****************
	cur.execute("select * from users where uid=?;",(uid,))
	res=cur.fetchone() 

	#**********************GET BOOK DETAILS****************************
	cur.execute("select * from books where bid=? and quantity>0;",(bid,))
	bookin=cur.fetchone()

	



 #***************IF user and books are available****************
	if res!=None and bookin!=None:
		#*************************CHECK ALREADY SAME book IS TAKEN OR NOT**********************
		cur.execute("select * from issued where uid=? and bid=? and returndate=?;",(uid,bid,"NOT RETURN"))
		already_taken=cur.fetchall()
		if len(already_taken)!=0 :
			return render_template('issue.html',msg="already_taken",flag=3)
	    #********************update issue details**************
		ibook="insert into issued(uid,bid,issuedate,returndate) values(?,?,?,?)"
		cur.execute(ibook,(uid,bid,issdate,retdate)) 
		conn.commit()
		#**************************GET YOUR ISSUED ID***********************
		cur.execute('select count(*) from issued')
		n=cur.fetchone()
		cur.execute('select iid from issued limit ?,1',(n[0]-1,))
		iid =cur.fetchone()
		#*****************HERE iid represents your issue id***************
		iid=iid[0]
		cur.execute('select quantity-1 from books where bid=? and quantity>=1',(bid,))
		qty=cur.fetchone()

		#**********************decrease book quantity in library******************************
		if qty!=None:
		    ubooks="update books set quantity=(select quantity-1 from books where bid=? and quantity>=1) where bid=?;"
		    cur.execute(ubooks,(bid,bid))
		    conn.commit()
		else:
			ubooks="update books set quantity=0 where bid=?;"
			cur.execute(ubooks,(bid,))
			conn.commit()
		
		conn.commit()
		conn.close()
		return render_template('addbook.html' ,msg="ISSUED SUCCESSFULLY",flag=6)
	#*********************IF book or user is not available in library*******************
	else:
		conn.close()
		if bookin!=None:
			return render_template('issue.html',msg="enter valid rollno",flag=3)
		else:
		    return render_template('issue.html',msg="enter valid input or book not available",flag=3)

#****************View issued books*********************
@app.route('/viewissue')
def viewissue():
	conn=sqlite3.connect('library.db')
	cur=conn.cursor()
	cur.execute('select * from issued;')
	results=cur.fetchall()
	
	return render_template('viewissue.html',res=results,flag=4)

#******************Take to return page***********
@app.route('/return')
def returnb():
	return render_template('return.html')

#*********************8return book to library**********************8
@app.route('/returnbook',methods=["post","get"])
def returnbook():
	#***************get iid details*******************
	retd=request.form["rd"]
	iid=request.form["iid"]


	#**************opens database connection********************
	conn=sqlite3.connect('library.db')
	cur=conn.cursor()
	cur.execute('select uid,bid,returndate from issued where iid=?',(iid,))
	val=cur.fetchone()

	#*************checks for valid or invalid input**********************
	if val==None:
		return render_template('return.html',flag=5,fine="INVALID INPUT")

	#**************8GETS uid and bid*********************
	uid=val[0]
	bid=val[1]
	returnverify=val[2]

	#*******************checks book  is already returned or not*****************************
	if returnverify=="NOT RETURN":

		#******************Updates return date********************************
		cur.execute('update issued set returndate=? where bid=? and uid=?;',(retd,bid,uid))
		conn.commit()

		#*****************increase quantity of book returned in library by 1********************
		cur.execute('update books set quantity=(select quantity+1 from books where bid=?) where bid=?',(bid,bid))
		conn.commit()

		#*****************8get issuebook date************************8
		cur.execute('select issuedate from issued where iid=?',(iid,))
		todate=cur.fetchone()
		conn.commit()

		#*******************get How many days did user keep book with him************************
		cur.execute("Select Cast ((JulianDay(?) - JulianDay(?)) As Integer);",(retd,todate[0]))
		res=cur.fetchone()

		#*********************IF he keeps morethan 10 days he will get fine 1 rs /day********************
		if res[0]-10>0:
			#*****************update fine of that user****************************
			cur.execute('update users set fine=(select fine from users where uid=?)+? where uid=?',(uid,res[0]-10,uid))
			conn.commit()
			conn.close()
			fine="YOUR fine is"+str(res[0]-10)
			return render_template('addbook.html',fine=fine,flag=5)
		else:
			return render_template('addbook.html',fine="NO FINE",flag=5) 
	else:
		return render_template('addbook.html',flag=5,fine="BOOK IS ALREADY RETURNED")

#****************Takes to payfine page*******************

@app.route('/gopay')
def gopay():
	return render_template('payfine.html')

#*******************88Takes to check fine page********************

@app.route('/gocheck')	
def gocheck():
	return render_template('check.html')

#************************returns fine*******************8

@app.route('/checkfine',methods=["post","get"]) 
def checkfine():
	#****************gets user id**********************
	uid=request.form['rn']
	conn=sqlite3.connect('library.db') 
	cur=conn.cursor()

	#*****************gets fine of user***************
	cur.execute('select fine from users where uid=?',(uid,))
	res=cur.fetchone()
	if res!=None:
	   msg="YOUR FINE IS " + str(res[0])+" RS"
	else:
		msg="INVALID INPUT"
	conn.commit()
	conn.close()
	return render_template('addbook.html',fine=msg,flag=5)

#*******************pay fine***************************
@app.route('/payfine',methods=["post","get"])
def payfine():
	#**********************GET form details******************
	uid=request.form["ui"]
	fine=request.form["fn"]
	#*****************opens database connection****************
	conn=sqlite3.connect('library.db') 
	cur=conn.cursor()
	cur.execute('select * from users where uid=?',(uid,))
	res=cur.fetchone()
	msg="PAYMENT SUCCESSFUL"
	#**************update payment in users table***********************
	if res!=None:
		if int(fine)-int(res[4])<=0:
			cur.execute('update users set fine=(select fine from users where uid=?)-? where uid=?',(uid,fine,uid))
			conn.commit()
		else:
			msg="YOU ARE PAYING MORE"
	else:
		msg="Enter Valid input"
	
	conn.close()
	return render_template('addbook.html',flag=6,msg=msg)

#***************Admin session logout*********************

@app.route('/adlogout',methods=["post","get"])
def adlogout():
	if 'admin' in session:
		session.pop('admin',None)
		return redirect(url_for('adminverify'))
	else:
		return redirect(url_for('home'))

#*****************************REDIRECT TO STUDENT LOGIN PAGE********************88
@app.route('/stdlogin')
def gotostudentlogin():
	return render_template('studentlogin.html') 

#****************************VERIFIES STUDENT LOGIN DETAILS AND REDIRECT TO STUDENTS PAGE***************	
@app.route('/studentverify',methods=["post","get"]) 
def stdverify():
	if request.method=="POST":
		#****************GEt details from form****************************
	    uname=request.form["un"]
	    pwd=request.form["pd"]
	    #********************opens database connection*********************
	    conn=sqlite3.connect('library.db')
	    cur=conn.cursor()

	    #*********************GETS original password of user***************8
	    cur.execute("select password from users where uname=?",(uname,))
	    res=cur.fetchone()
	    conn.close()
	    #**********************IF user in library**********************
	    if res!=None:
	    	#******************USER AUTHENTICATION AND AaaaDD user  session**********************
	    	if res[0]==pwd:
	    		session['user']=uname
	    		#*******************EMPTIES FORM DETAILS********************
	    		return redirect(url_for('stdverify'))
	    	else:
	    		return render_template('studentlogin.html',flag=1)
	    else:
	    	return render_template('studentlogin.html',flag=1) 
	elif 'user' in session:
		uname=session['user']
		conn=sqlite3.connect('library.db')
		cur=conn.cursor()
		#****************GET user taken book details***********8
		cur.execute("select i.bid,b.book_name,i.issuedate from issued as i,books as b where i.uid=(select uid from users where uname=?) and i.bid=b.bid;",(uname,))
		ibooks=cur.fetchall()

		#******************get user  details********************
		cur.execute("select uid,uname,branch,fine from users where uname=?",(uname,))
		profile=cur.fetchone()
		conn.close()
		return render_template('studentpage.html',uname=uname,issbooks=ibooks,profile=profile)
	else:
		return render_template('studentlogin.html',flag=1)
    
#****************8EXPIRES USER SESSIOn*************************8
@app.route('/stdlogout',methods=["post","get"])
def stdlogout():
	if 'user' in session:
		session.pop('user',None)
		return redirect(url_for('stdverify'))
	else:
		return "Already logout" 

#**********SERVER STARTS AT HERE*****************8

if __name__=='__main__':
	app.run(debug=True)