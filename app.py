# 載入flask套件
from flask import Flask,render_template,request,redirect,session,url_for
from flask import jsonify
# 載入 pymongo、openai套件 (pip install openai)
import pymongo, openai

# mongodb連線(要先pip安裝) root是使用者名稱 root123是當初設定的密碼
client = pymongo.MongoClient("mongodb://root:root123@ac-nxhavl3-shard-00-00.kecqc4f.mongodb.net:27017,ac-nxhavl3-shard-00-01.kecqc4f.mongodb.net:27017,ac-nxhavl3-shard-00-02.kecqc4f.mongodb.net:27017/?ssl=true&replicaSet=atlas-10enrt-shard-0&authSource=admin&retryWrites=true&w=majority")

app = Flask(__name__)
app.secret_key="secret"

# 操作 madetect 資料庫
db = client.madetect

# 設定gpt apikey參數
with open('./static/doc/apikey.txt', 'r') as file:
    apikey = file.read().rstrip()
# 暫時新增
with open('./static/doc/醫療法補充二.txt', 'r', encoding="utf-8") as file:
  lawadd2_text = file.read()

#首頁頁面
@app.route('/')
def homepage():
    return render_template('homepage.html')


#--------------------------------------------
#--------------------------------------------
#--------------以下會員登入介面---------------
#--------------------------------------------
#--------------------------------------------    

#登入頁面
@app.route('/login')
def login_page():
    if 'user_name' in session:
          return redirect(url_for('home'))
    
    return render_template('userLogin.html')

#登入功能
@app.route('/login_function', methods=['POST'])
def login_function():
    user_email = request.form.get('user_email')
    user_password = request.form.get('user_password')

    # 根據接受到的資料跟資料庫互動，操作 madetect 資料庫的 user 集合
    collection = db.user

    # 檢查帳號密碼是否正確
    result = collection.find_one({
        "user_email": user_email,
        "user_password": user_password
    })
    
    if result is not None:
        # 登入成功
        session["user_name"] = result["user_name"]
        # session["user_id"] = result["_id"]
        response = {'success': True}
    else:
        # 登入失敗
        response = {'success': False}
    
    return jsonify(response)

# 註冊頁面
@app.route('/signup')
def signup_page():
    if 'user_name' in session:
        return redirect(url_for('home'))
	
    return render_template('userSignup.html')

# 註冊功能
@app.route('/signup_function', methods=['POST'])
def signup_function():

	# 接收前端資料
	user_name=request.values.get("user_name")
	user_email=request.values.get("user_email")
	user_password=request.values.get("user_password")

	# 根據接受到的資料跟資料庫互動，操作 madetect資料庫 的 user集合
	collection = db.user

    #插入資料進資料庫
	collection.insert_one({
		"user_name":user_name,
		"user_email":user_email,
		"user_password":user_password
	})
	return render_template('userLogin.html')



# 註冊功能判定帳號是否重複
@app.route('/check_email', methods=['POST'])
def check_email():
    user_email = request.form.get('email')
    
    # 根據接收到的資料與資料庫互動，操作 madetect 資料庫的 user 集合
    collection = db.user
    
    # 檢查是否有重複的 email
    result = collection.find_one({"user_email": user_email})
    
    if result is not None:
        response = {"exists": True}
    else:
        response = {"exists": False}
    
    return jsonify(response)

# 忘記密碼頁面
@app.route('/forgetpsw')
def forgetpsw():
	return render_template('userForget.html')

# 忘記密碼功能
@app.route('/forgetpsw_function', methods=['POST'])
def forgetpsw_function():
    # 接收前端資料
    user_name = request.values.get("user_name")
    user_email = request.values.get("user_email")

    # 根據接受到的資料跟資料庫互動，操作 madetect 資料庫的 user 集合
    collection = db.user

    # 檢查是否有 user 名字及郵件
    result = collection.find_one({
        "$and": [
            {"user_name": user_name},
            {"user_email": user_email}
        ]
    })

    if result is not None:
        session["user_email"] = result["user_email"]
        response = {"exists": True}
    else:
        response = {"exists": False}

    return jsonify(response)

# 重設密碼頁面
@app.route('/reset')
def resetpsw():
	return render_template('resetPassword.html')

# 重設密碼功能
@app.route('/reset_function', methods=['POST'])
def reset_function():

	# 接收前端資料
	user_password=request.values.get("user_password")

	# 根據接受到的資料跟資料庫互動，操作 madetect資料庫 的 user集合
	collection = db.user

	#更新user_password
	collection.update_one({
    	"user_email":session["user_email"]
	},{
    "$set":{
        "user_password":user_password
    	}
	})
	return render_template('userLogin.html')
#--------------------------------------------
#--------------------------------------------
#----------------以下會員主頁-----------------
#--------------------------------------------
#--------------------------------------------


#主功能頁面
@app.route('/home')
def home():
    # 確認session裡是否已有資料(在/login_function中或登入失敗就不會將資料傳入session)
    if 'user_name' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login_page'))
        
# 連接GPT辨認廣告
@app.route('/madetect', methods=['GET', 'POST'])
def madetect():
    if 'user_name' in session:
        # 設定api金鑰
        openai.api_key = apikey
        
        # 接收前端資料
        input_ad=request.values.get('input_ad')
        print(input_ad)

        # 連接GPT<違反法條>
        result_law = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo-0613",
            messages = [
                {"role": "system", "content": "你是一個專業的律師，並具有台灣的醫療法相關知識。"},
                {"role": "user", "content": "請先分析相關文件：" + lawadd2_text},
                {"role": "user", "content": "\n請用你自己的話並以繁體中文告訴我此廣告詞是否違法" + input_ad},
            ]
        )
        # 存取GPT回應<違反法條>
        resultLaw = result_law['choices'][0]['message']['content']
        print('result_law: '+resultLaw)
        # 連接GPT<修改廣告詞>
        result_advice = openai.ChatCompletion.create(
            model = 'gpt-3.5-turbo-0613',
            messages = [
                {"role": "system", "content": "你是一個專業的廣告詞家，具有台灣的醫療法相關知識。"},
                {"role": "user", "content": resultLaw + "\n請參考上述語句幫我以繁體中文建議我如何修改此廣告詞以達到不違法的目的，請只要告訴我修改後的結果就好: " + input_ad},
            ]
        )
        # 存取GPT回應<修改後廣告詞>
        resultAdvice = result_advice['choices'][0]['message']['content']

        print('result_advice: '+resultAdvice)
        response = {
            'result_advice': resultAdvice,
            'result_law': resultLaw
        }


        return jsonify(response)
    
    else:
        return redirect(url_for('login'))

# 問題回報功能
@app.route('/report', methods=['POST'])
def add_report():
    if 'user_name' in session:
        user_name = session['user_name']
        report_text = request.form.get('report')

        # 獲取當前用戶的_id
        user_collection = db.user
        user = user_collection.find_one({'user_name': user_name})
        user_id = user['_id']

        # 在 report 集合中存user_name和user_id還有回報內容
        report_collection = db.report
        report_result = report_collection.insert_one({
            'user_name': user_name,
            'user_id': user_id,
            'report_text': report_text
        })

        # 獲取插入報告後的report文檔的_id
        report_id = report_result.inserted_id

        # 同時在 user 集合中記錄該當下login的user的問題回報(report)
        user_collection.update_one({'_id': user_id}, {'$push': {'reports': report_id}})

        #完成後回主頁
        return redirect(url_for('home'))

# 登出
@app.route('/signout')
def signout():
    # 移除session中會員資訊
    del session['user_name']
    return redirect("/")

#--------------------------------------------
#--------------------------------------------
#-------------以下管理員登入介面--------------
#--------------------------------------------
#--------------------------------------------

# 管理員登入
@app.route('/adminlogin')
def adminlogin_page():
	return render_template('adminLogin.html')

# 管理員登入功能
@app.route('/adminlogin_function', methods=['POST'])
def adminlogin_function():
    admin_email = request.form.get('admin_email')
    admin_password = request.form.get('admin_password')

    # 根據接受到的資料跟資料庫互動，操作 madetect 資料庫的 admin 集合
    collection = db.admin

    # 檢查帳號密碼是否正確
    result = collection.find_one({
        "admin_email": admin_email,
        "admin_password": admin_password
    })
    
    if result is not None:
        # 登入成功
        session["admin_name"] = result["admin_name"]
        session["admin_email"] =result["admin_email"]
        response = {'success': True}
    else:
        # 登入失敗
        response = {'success': False}
    
    return jsonify(response)

# 管理員忘記密碼
@app.route('/adminforgetpsw')
def adminforgetpsw_page():
	return render_template('adminForget.html')

# 管理員重設密碼
@app.route('/adminresetpsw')
def adminresetpsw_pages():
	return render_template('adminReset.html')

#--------------------------------------------
#--------------------------------------------
#---------------以下管理員主頁----------------
#--------------------------------------------
#--------------------------------------------

# 管理員首頁
@app.route('/adminhome')
def admin_home():

    if 'admin_name' in session:
        return render_template('admin_home.html')
    else:
        return redirect('/adminlogin')
    
@app.route('/adminsignout')
def adminsignout():
    # 移除session中管理員資訊
    del session['admin_name']
    return redirect("/adminlogin")


# 管理員首頁>>>總用戶數
@app.route('/get_user_count', methods=['GET'])
def get_user_count():

    collection = db.user
    # 計算user集合中的documents數量，即使用者總數
    user_count = collection.count_documents({})  
    # 將使用者總數轉換為 JSON 格式並回傳
    return jsonify(user_count)  

# 管理員首頁>>>問題回報數量
@app.route('/get_report_count', methods=['GET'])
def get_report_count():

    collection = db.report
    # 計算report集合中的documents數量，即問題回報總數
    report_count = collection.count_documents({})  
    # 將問題回報總數轉換為 JSON 格式並回傳
    return jsonify(report_count)  

# 管理員 管理管理員
@app.route('/adminmanage')
def admin_manage():
    if 'admin_name' in session:
        return render_template('admin_manage.html')
    else:
        return redirect('/adminlogin')

# 管理員 管理會員
@app.route('/membermanage')
def member_manage():
    if 'admin_name' in session:
        return render_template('member_manage.html')
    else:
        return redirect('/adminlogin')

# 管理員 管理一般用戶
@app.route('/normalmanage')
def normal_manage():
    if 'admin_name' in session:
        return render_template('normal_manage.html')
    else:
        return redirect('/adminlogin')
    
#後端flask設定
if __name__ == '__main__':
	app.run(host='0.0.0.0',port='5000',debug=True)