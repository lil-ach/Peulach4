import pyrebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


from flask import Flask, render_template, request
from flask import url_for

app = Flask(__name__)

config={'apiKey': "AIzaSyCXBR_0_UQhRsq9_Z75rKY9Z8gO7f-FYh0",
  'authDomain': "test-fcfc1.firebaseapp.com",
  'databaseURL': "",
  'projectId': "test-fcfc1",
  'storageBucket': "test-fcfc1.appspot.com",
  'messagingSenderId': "475633284013",
  'appId': "1:475633284013:web:412f26593b6b38ceffe724"}
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
firebase = pyrebase.initialize_app(config)

auths = {}

db = firestore.client()
def sign_in_form(email, password, request):
    try:
        auth = firebase.auth()
        auth.sign_in_with_email_and_password(email,password)
        auths[request.remote_addr] = auth
        print("signed in succesfully")
        return render_template("index.html", msg="התחברת בהצלחה!")
        
    except:
        return render_template("sign_in.html", error="אימייל או סיסמה לא נכונים")

def sign_up_form(email, password, confirmpass):
    if password==confirmpass:
        try:
            auth = firebase.auth()
            auth.create_user_with_email_and_password(email, password)
            auth.sign_in_with_email_and_password(email,password)
            auths[request.remote_addr] = auth
            return render_template("index.html", msg="נרשמת והתחברת בהצלחה!")
        except:
            return render_template("sign_up.html", error="אימייל או סיסמה לא תקניים")
    else:
        return render_template("sign_up.html", error="הסיסמאות לא תואמות")
        

def fetch_peulot(user_addr):
    mypeulot_ref = db.collection('peulot')
    print("fetch_peulot/got collections")
    userid = auths[user_addr].current_user['localId']
    print("fetch_peulot/got user id")
    mypeulot_ref = mypeulot_ref.where("ownerId", "==", userid).get()
    print(mypeulot_ref)
    print("fetch_peulot/got my peulot")
    return mypeulot_ref
    
def is_logged_in(user_addr):
    return auths.get(user_addr) != None
    
class Peula():#########
    def __init__(self, title, matarot, ownerId):
        self.title = title
        self.matarot = matarot
        self.ownerId = ownerId

    def from_dict(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])


class Method():###########
    def __init__(self, name, desc, time, azarim, comments):
        self.name = name
        self.desc = desc
        self.time = time
        self.azarim = azarim
        self.comments = comments
    

    
    def from_dict(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
     
@app.route('/handle_data', methods=['POST'])
def handle_data():
    email = request.form['email']
    password = request.form['password']
    return sign_in_form(email, password, request)
    
@app.route('/handle_newacc_data', methods=['POST'])
def handle_newacc_data():
    email = request.form['email']
    password = request.form['password']
    confpass = request.form['confpass']

    return sign_up_form(email, password, confpass)
    
@app.route('/sign_in')
def sign_in():
    return render_template("sign_in.html")
    
@app.route('/sign_up')
def sign_up():
    return render_template("sign_up.html")
    
@app.route('/mypeulot')
def mypeulot():
    addr = request.remote_addr
    peulot = fetch_peulot(addr)
    print("fetched succesfully")
 #   return "hello"
 #   ids = []
 #   for peula in peulot:
  #      ids.append(url_for(peula.id))
  
    return render_template("mypeulot.html", peulot=peulot) #, peulot = peulot (arr)
    

@app.route('/mypeulot/<peulaId>')
def mypeula(peulaId):
    addr = request.remote_addr
    peula = db.collection('peulot').document(peulaId).get()
    methods = db.collection('peulot').document(peulaId).collection('methods').get()
    if (is_logged_in(addr)):
        if (peula._data['ownerId'] == auths[request.remote_addr].current_user['localId']):
            return render_template("p_template.html", peula=peula, methods=methods)
    print(peula)
    return render_template("p_template.html", peula=None, methods=None, message="אין לך גישה לפעולה הזאת")

@app.route('/new_peula')
def new_peula():
    print("app root path:")
    print(app.root_path)
    print("app instance path:")
    print(app.instance_path)
    return render_template("new_peula.html") #########
    
@app.route('/create_new', methods=['POST'])
def create_new():
    addr = request.remote_addr
    peula = request.form
    methods = []
    matarot = []
    for element in peula:
        
        if (element.split('-')[0]=="matarot"):
            matarot.append(peula[element])

        elif (element.split('-')[0]=="method"):
            num=element.split('-')[1]
            print ("method" + "-" + num)
            name = peula["method" + "-" + num]
            desc = peula["desc" + "-" + num]
            time = peula["time" + "-" + num]
            azarim = peula["azarim" + "-" + num]
            comments = peula["comments" + "-" + num]
            method = Method(name, desc, time, azarim, comments)
            methods.append(method.__dict__)
            
        elif (element=="title"):
            title = peula[element]
            

    if (is_logged_in(addr)==True):
        userid = auths[request.remote_addr].current_user['localId']
        new_peula = Peula(title, matarot, userid)
        print(new_peula.__dict__)
        peula_ref = db.collection("peulot").document(peula['title'])
        peula_ref.set(new_peula.__dict__)
        methods_ref = peula_ref.collection("methods")
        for m in methods:
            methods_ref.add(m)
    
    
    return render_template("new_success.html", peulaId=peula_ref.id)

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)
    
@app.route('/')
def index():
    addr = request.remote_addr
    return render_template("index.html", is_logged=is_logged_in(addr))
    

if __name__ == '__main__':
   app.run(host="0.0.0.0")