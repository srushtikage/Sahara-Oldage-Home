from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)


# --------------DB Connection------------------#

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'sahara'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# ---------------- HOME ------------------------#

@app.route('/')
def home():
    return render_template("home.html")


# ---------------- LOGIN ----------------------#

@app.route('/beforelogin')     # 2 Cards of Login(Admin & Guardian)
def beforelogin():
    return render_template("beforelogin.html")


@app.route('/login')           # Admin Login
def login():
    return render_template("login.html")


@app.route('/form_login', methods=['POST'])
def form_login():
    
    try:
        name = request.form['username']
        pwd = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (name, pwd))
        user = cursor.fetchone()
        
        if user is None:
            return render_template('login.html', info='Invalid User')
        else:
            if user[1] != pwd:
                return render_template('login.html', info='Invalid Password')
            else:
                return render_template('main.html')

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('login.html', info='An error occurred while processing your request')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            
@app.route('/logingua', methods=['GET'])        # Guardian Login
def logingua():
    return render_template('guardianlogin.html')
            
            
@app.route('/form_logingua', methods=['POST'])
def form_logingua():
    """Handles form submission for guardian login."""
    guardian_id = request.form['username']
    member_id = request.form['password']
   
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
       
        cursor.execute("SELECT * FROM guardian WHERE GUARDIAN_ID = %s AND MEMBER_ID = %s", (guardian_id, member_id))
        guardian = cursor.fetchone()
       
        if guardian:
            cursor.execute("SELECT * FROM member WHERE MEMBER_ID = %s", (member_id,))
            member = cursor.fetchone()
           
            if member:
                return render_template('mainguardian.html', member=member)
            else:
                return "Member not found", 404
        else:
            return "Guardian and member IDs do not align", 403

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while processing your request"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@app.route('/forgot_password', methods=['GET'])        # Guardian Login
def forgot_password():
    return render_template('security.html')

@app.route('/form_security', methods=['POST'])
def form_security():
    username = request.form.get('username')
    answer = request.form.get('answer')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
       
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        password_data = cursor.fetchone()  # Fetch the password data

        if password_data:  # Check if password_data is not None
            password = password_data['password']  # Extract the password value
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            users = cursor.fetchone()
           
            if users and answer == users['answer']:
                return render_template('security.html', password=password)
            else:
                return render_template('security.html', error='Incorrect answer. Please try again.')
        else:
            return render_template('login.html', error='User not found.')

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while processing your request"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

   
            
@app.route('/main.html', methods=['GET'])
def mainhtml():
    return render_template("/main.html")


@app.route('/mainroom', methods=['GET'])
def mainroom():
    return render_template("room/moreroom.html")



#****************************************************************************************************#




@app.route('/mainpage', methods=['POST', 'GET'])
def mainpage():
    try:
        name = request.form['username']
        member_id = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM guardian WHERE guardian_id = %s AND member_id = %s", (name, member_id))
        user = cursor.fetchone()
        
        if user is None:
            return render_template('guardianlogin.html', info='Invalid User')
        else:
            if user[2] != member_id:
                return render_template('guardianlogin.html', info='Invalid Password')
            else:
                return render_template('mainguardian.html',member_id=member_id)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('login.html', info='An error occurred while processing your request')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            



# ---------------- MEMBER DETAILS DISPLAYED TO GUARDIAN ----------------------#



@app.route('/member_details', methods=['GET','POST'])
def member_details():
    
    try:
        member_id = request.args.get('member_id')  # Retrieve the Password which is Member ID Only entered ny Guardian
    
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM member WHERE MEMBER_ID = %s", (member_id,))
        member = cursor.fetchone()

        cursor.close()
        conn.close()

        # Check if member details are found
        if member:
            return render_template('member_details.html', member=member)
        
        else:
            return render_template("mainguardian.html", member_id=member_id)
        
    
    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template("mainguardian.html", member_id=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()







# ---------------- MEDICAL RECORDS DISPLAYED TO GUARDIAN ----------------------#
 
 
@app.route('/medrecord/<member_id>')
def medrecord(member_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
       
        # Retrieve medical records for the member
        cursor.execute("""SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.NOTES 
                        FROM HAS_RECORD H 
                        LEFT JOIN MEDICAL_RECORD M ON H.MEDICALRECORD_ID = M.MEDICALRECORD_ID 
                        WHERE H.MEMBER_ID = %s 
                        ORDER BY H.LAST_CHECKUP DESC 
                        LIMIT 1""", (member_id,))
        record = cursor.fetchone()

        return render_template('memmedicalrecord.html', record=record)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while processing your request"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()




# ---------------- PAST MEDICAL RECORDS DISPLAYED TO GUARDIAN ----------------------#



@app.route('/ALLmedrecord/<member_id>')
def ALLmedrecord(member_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
      
        
        cursor.execute("SELECT M.MEDICALRECORD_ID, H.MEMBER_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.NOTES  FROM HAS_RECORD H LEFT JOIN MEDICAL_RECORD M ON H.MEDICALRECORD_ID = M.MEDICALRECORD_ID WHERE H.MEMBER_ID = %s ORDER BY H.LAST_CHECKUP DESC LIMIT 1, 18446744073709551615", (member_id,))
        record = cursor.fetchall()
        
        return render_template('ALLmedrecord.html', record=record)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while processing your request"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            
            
#-------------------DOCTOR IN GUARDIAN LOGIN----------------#
@app.route('/doc_info/<doctor_id>')
def doc_info(doctor_id):
    try:
        conn = get_db_connection()  # Establish connection to the database
        cursor = conn.cursor()  # Create a cursor object to execute SQL queries
        
        # Retrieve doctor details using the doctor ID
        cursor.execute("SELECT * FROM DOCTOR WHERE DOCTOR_ID = %s", (doctor_id,))
        doctor = cursor.fetchone()  # Fetch one doctor record
        
        # Render the 'doc_info.html' template with doctor data
        return render_template('knowthedoctor.html', doctor=doctor)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while processing your request"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

#************************************************************************************************#
    
    
    
#------------------- MEMBER DISPLAY ----------------------#

@app.route('/display', methods=['GET'])
def display():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM member")
        users = cursor.fetchall()
        return render_template("member/display.html", users=users)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('member/display.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


#-------------------- ADD MEMBER ------------------------#

@app.route('/addmem', methods=['GET'])
def addmem():
    return render_template('member/addmem.html') 


@app.route('/insertm', methods=['POST'])
def insertm():
    try:
        name = request.form['name']
        gender = request.form['gender']
        birth_date = request.form['birthdate']
        phone_no = request.form['phone']
        city = request.form['city']
        address = request.form['address']
        join_date = request.form['join_date']
        assistance = request.form['assistance']
        status = request.form['status']
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the phone number already exists
        cursor.execute("SELECT * FROM MEMBER WHERE PHONE_NUMBER = %s and status='Active'", (phone_no,))
        existing_member = cursor.fetchone()

        if existing_member:
            # If the phone number exists, render the addmem.html template with existing member details
            return render_template('member/addmem.html', message="Phone number already exists!Please renter again",
                                   name=name, gender=gender, birthdate=birth_date,
                                   city=city, address=address, join_date=join_date,
                                   assistance=assistance, status=status)
        else:
            # If the phone number doesn't exist, proceed with insertion
            cursor.callproc('INSERT_MEMBER', (name, gender, birth_date, phone_no, city, address, join_date, assistance, status))
            conn.commit() 
            return redirect(url_for('display'))

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return redirect(url_for('display'))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



#-------------------- SORT MEMBER ------------------------#  
 
@app.route('/sort_name', methods=['GET', 'POST'])
def sort_name():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sort_option = request.args.get('sort_option', 'display')
        
        if sort_option == 'name':
            cursor.execute("SELECT * FROM member ORDER BY NAME")
        elif sort_option == 'join_date':
            cursor.execute("SELECT * FROM member ORDER BY JOIN_DATE")
        else:
            cursor.execute("SELECT * FROM member")
        
        users = cursor.fetchall()
        
        return render_template("member/display.html", users=users, sort_option=sort_option)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('member/display.html', users=[], sort_option='display')
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            
            
#-------------------- GROUP BY GENDER ------------------------#


@app.route('/sort_gender', methods=['GET', 'POST'])
def sort_gender():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sort_option = request.args.get('sort_option', 'display')

        if sort_option.lower() == 'male':
            cursor.execute("""SELECT MEMBER_ID, NAME, GENDER, BIRTH_DATE, AGE, PHONE_NUMBER, CITY, ADDRESS_DETAILS, JOIN_DATE, ROOM_ID, ASSISTANCE, STATUS
                              FROM member
                              WHERE gender = 'Male'
                              GROUP BY gender, MEMBER_ID, NAME, BIRTH_DATE, AGE, PHONE_NUMBER, CITY, ADDRESS_DETAILS, JOIN_DATE, ROOM_ID, ASSISTANCE, STATUS;""")
            
        elif sort_option.lower() == 'female':
            cursor.execute("""SELECT MEMBER_ID, NAME, GENDER, BIRTH_DATE, AGE, PHONE_NUMBER, CITY, ADDRESS_DETAILS, JOIN_DATE, ROOM_ID, ASSISTANCE, STATUS
                              FROM member
                              WHERE gender = 'Female'
                              GROUP BY gender, MEMBER_ID, NAME, BIRTH_DATE, AGE, PHONE_NUMBER, CITY, ADDRESS_DETAILS, JOIN_DATE, ROOM_ID, ASSISTANCE, STATUS;""")
        else:
            cursor.execute("SELECT * FROM member")

        users = cursor.fetchall()

        return render_template("member/display.html", users=users, sort_option=sort_option)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template("member/display.html", users=[], sort_option='display', error="An error occurred while sorting members.")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()




#-------------------- SEARCH MEMBER ------------------------#

@app.route('/search', methods=['GET'])
def search():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        search_option = request.args.get('search_option')
        search_value = request.args.get('search_value')
        
        if search_option and search_value:
            if search_option in ['member_id', 'name', 'status', 'city', 'room_id']:
                if search_option == 'name':
                    cursor.execute("SELECT * FROM member WHERE NAME LIKE %s", ('%' + search_value + '%',))
                else:
                    query = "SELECT * FROM member WHERE {} = %s".format(search_option)
                    cursor.execute(query, (search_value,))
            else:
                return "Invalid search option"
        else:
            cursor.execute("SELECT * FROM member")
        
        users = cursor.fetchall()
        return render_template("member/display.html", users=users, search_option=search_option, search_value=search_value)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('member/display.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            
            
#-------------------- EDIT MEMBER ------------------------#

@app.route('/edit_member', methods=['GET','POST'])
def edit_member():
    member_id = request.args.get('member_id')
    if not member_id:
        return "Member ID is required", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM member WHERE MEMBER_ID = %s", (member_id,))
        member = cursor.fetchone()

        if not member:
            return "Member not found", 404

        return render_template('member/edit_member.html', member=member)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while processing your request", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/update_member', methods=['POST'])
def update_member():
        member_id = request.form['member_id']
        member_name = request.form['name']
        member_gender = request.form['gender']
        member_birth_date = request.form['birthdate']
        member_phone_number = request.form['phone']
        member_city = request.form['city']
        member_address_details = request.form['address']
        member_join_date = request.form['join_date']
        member_assistance = request.form['assistance']
        member_status = request.form['status']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE member SET NAME = %s, GENDER = %s, BIRTH_DATE = %s, PHONE_NUMBER = %s, CITY = %s, ADDRESS_DETAILS = %s, JOIN_DATE = %s, ASSISTANCE = %s, STATUS = %s WHERE MEMBER_ID = %s",
                           (member_name, member_gender, member_birth_date, member_phone_number, member_city, member_address_details, member_join_date, member_assistance, member_status, member_id))
            conn.commit()
            return redirect(url_for('display'))

        except mysql.connector.Error as e:
            print("An error occurred:", e)
            return "An error occurred while updating member details", 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            
            
            

#****************************************************************************************************#



#------------------- DOCTOR DISPLAY ----------------------#

@app.route('/display_doc', methods=['GET'])
def display_doc():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DOCTOR")
        users = cursor.fetchall()
        return render_template("doctor/display_doc.html", users=users)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('doctor/display_doc.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


#-------------------- ADD DOCTOR ------------------------#

@app.route('/add_doc', methods=['GET'])
def add_doc():
     return render_template('doctor/add_doc.html') 


@app.route('/insert_doc', methods=['POST'])
def insert_doc():
    
    try:
        name = request.form['name']
        phone_no = request.form['phone']
        city = request.form['city']
        address = request.form['address']
        email = request.form['email']
        specialization = request.form['specialization']
        salary = request.form['salary']
        status = request.form['status']
   
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.callproc('INSERT_DOCTOR', (name, phone_no, city, address, email, specialization, salary, status))
        conn.commit() 
        return redirect(url_for('display_doc'))

    except mysql.connector.Error as e:
        print("An error occurred:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


#-------------------- SORT DOCTOR ------------------------#  
 
@app.route('/sort_doc', methods=['GET', 'POST'])
def sort_doc():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sort_option = request.args.get('sort_option', 'display')
        
        if sort_option == 'name':
            cursor.execute("SELECT * FROM DOCTOR ORDER BY NAME")
        elif sort_option == 'salary':
            cursor.execute("SELECT * FROM DOCTOR ORDER BY SALARY DESC")
        else:
            cursor.execute("SELECT * FROM DOCTOR")
        
        users = cursor.fetchall()
        conn.close()
        
        return render_template("doctor/display_doc.html", users=users, sort_option=sort_option)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('doctor/display_doc.html', users=[], sort_option='display')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


#-------------------- SEARCH DOCTOR ------------------------#

@app.route('/search_doc', methods=['GET'])
def search_doc():
     try:
         conn = get_db_connection()
         cursor = conn.cursor()
        
         search_option = request.args.get('search_option')
         search_value = request.args.get('search_value')
        
         if search_option and search_value:
             if search_option in ['doctor_id', 'name', 'status', 'city', 'specialization']:
                 if search_option == 'name':
                     cursor.execute("SELECT * FROM DOCTOR WHERE NAME LIKE %s", ('%' + search_value + '%',))
                 else:
                     query = "SELECT * FROM DOCTOR WHERE {} = %s".format(search_option)
                     cursor.execute(query, (search_value,))
             else:
                 return "Invalid search option"
         else:
             cursor.execute("SELECT * FROM DOCTOR")
        
         users = cursor.fetchall()
         return render_template("doctor/display_doc.html", users=users, search_option=search_option, search_value=search_value)

     except mysql.connector.Error as e:
         print("An error occurred:", e)
         return render_template('doctor/display_doc.html', users=[])

     finally:
         if cursor:
             cursor.close()
         if conn:
             conn.close()
             
          
          
#-------------------- EDIT DOCTOR ------------------------#   
             
             
@app.route('/edit_doctor', methods=['GET','POST'])
def edit_doctor():
    doctor_id = request.args.get('doctor_id')
    if not doctor_id:
        return "Doctor ID is required", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctor WHERE DOCTOR_ID = %s", (doctor_id,))
        doctor = cursor.fetchone()

        if not doctor:
            return "Doctor not found", 404

        return render_template('doctor/edit_doc.html', doctor=doctor)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while processing your request", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/update_doctor', methods=['POST'])
def update_doctor():
    doctor_id = request.form['doctor_id']
    doctor_name = request.form['name']
    doctor_phone_number = request.form['phone']
    doctor_city = request.form['city']
    doctor_address_details = request.form['address']
    doctor_email = request.form['email']
    doctor_specialization = request.form['specialization']
    doctor_salary = request.form['salary']
    doctor_status = request.form['status']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE doctor SET NAME = %s, PHONE_NUMBER = %s, CITY = %s, ADDRESS_DETAILS = %s, EMAIL = %s, SPECIALIZATION = %s, SALARY = %s, STATUS = %s WHERE DOCTOR_ID = %s",
                       (doctor_name, doctor_phone_number, doctor_city, doctor_address_details, doctor_email, doctor_specialization, doctor_salary, doctor_status, doctor_id))
        conn.commit()
        return redirect(url_for('display_doc'))

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while updating doctor details", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

             

#****************************************************************************************************#



#------------------- MEDICAL RECORD DISPLAY ----------------------#

@app.route('/display_med', methods=['GET'])
def display_med():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.NOTES
FROM HAS_RECORD H
LEFT JOIN MEDICAL_RECORD M ON H.MEDICALRECORD_ID = M.MEDICALRECORD_ID
ORDER BY 
H.MEMBER_ID ASC,
H.LAST_CHECKUP DESC;
""")
        users = cursor.fetchall()
        return render_template("medical_record/display_med.html", users=users)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('medical_record/display_med.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            
            
#-------------------- ADD MEDICAL RECORD ------------------------#

@app.route('/add_med', methods=['GET'])
def add_med():
     return render_template('medical_record/add_med.html') 


@app.route('/insert_med', methods=['POST'])
def insert_med():
    
    try:
        member_id = request.form['member_id']
        doctor_id = request.form['doctor_id']
        high_bp = request.form['high_bp']
        low_bp = request.form['low_bp']
        weight = request.form['weight']
        diabetes = request.form['diabetes']
        notes = request.form['notes']
   
        conn = get_db_connection()  
        cursor = conn.cursor()
        cursor.callproc('INSERT_MEDICAL_RECORD', (member_id, doctor_id, high_bp, low_bp, weight, diabetes, notes))
        conn.commit() 
        return redirect(url_for('display_med'))

    except mysql.connector.Error as e:
        print("An error occurred:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            
            
#-------------------- SORT MEDICAL RECORD ------------------------#  
 
@app.route('/sort_med', methods=['GET', 'POST'])
def sort_med():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
   
        sort_option = request.args.get('sort_option', 'display')
        
        if sort_option == 'high_bp':
            cursor.execute("""SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.NOTES
FROM HAS_RECORD H
LEFT JOIN MEDICAL_RECORD M ON H.MEDICALRECORD_ID = M.MEDICALRECORD_ID
ORDER BY 
HIGH_BP DESC
""")
        elif sort_option == 'low_bp':
            cursor.execute("""SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.NOTES
FROM HAS_RECORD H
LEFT JOIN MEDICAL_RECORD M ON H.MEDICALRECORD_ID = M.MEDICALRECORD_ID ORDER BY LOW_BP""")
        else:
            cursor.execute("""SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.NOTES
FROM HAS_RECORD H
LEFT JOIN MEDICAL_RECORD M ON H.MEDICALRECORD_ID = M.MEDICALRECORD_ID
ORDER BY 
H.MEMBER_ID ASC,
H.LAST_CHECKUP DESC;
""")
        
        users = cursor.fetchall()
        conn.close()
        
        return render_template("medical_record/display_med.html", users=users, sort_option=sort_option)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('medical_record/display_med.html', users=[], sort_option='display')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            

#-------------------- SEARCH MEDICAL RECORD ------------------------#

@app.route('/search_med', methods=['GET'])
def search_med():
     try:
         conn = get_db_connection()
         cursor = conn.cursor()
        
         search_option = request.args.get('search_option')
         search_value = request.args.get('search_value')
        
         if search_option and search_value:
            if search_option in ['M.medicalrecord_id', 'M.member_id', 'M.doctor_id', 'M.high_bp', 'M.low_bp', 'M.diabetes']:
                query = """SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.NOTES
                FROM HAS_RECORD H
                LEFT JOIN MEDICAL_RECORD M ON H.MEDICALRECORD_ID = M.MEDICALRECORD_ID
                WHERE {} = %s
                ORDER BY 
                H.MEMBER_ID ASC,
                H.LAST_CHECKUP DESC""".format(search_option)

                cursor.execute(query, (search_value,))
            else:
                return "Invalid search option"
        
         else:
            cursor.execute("""SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.NOTES
            FROM HAS_RECORD H
            LEFT JOIN MEDICAL_RECORD M ON H.MEDICALRECORD_ID = M.MEDICALRECORD_ID
            ORDER BY 
            H.MEMBER_ID ASC,
            H.LAST_CHECKUP DESC;""")
        
         users = cursor.fetchall()
         return render_template("medical_record/display_med.html", users=users, search_option=search_option, search_value=search_value)

     except mysql.connector.Error as e:
         print("An error occurred:", e)
         return render_template('medical_record/display_med.html', users=[])

     finally:
         if cursor:
             cursor.close()
         if conn:
             conn.close()
             

             
             
#-------------------- EDIT MEDICAL RECORD ------------------------#

@app.route('/edit_medical', methods=['GET','POST'])
def edit_medical():
    medical_id = request.args.get('medical_id')
    if not medical_id:
        return "Medical record ID is required", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.NOTES
FROM HAS_RECORD H
LEFT JOIN MEDICAL_RECORD M ON H.MEDICALRECORD_ID = M.MEDICALRECORD_ID WHERE MEDICALRECORD_ID = %s""", (medical_id,))
        medical = cursor.fetchone()

        if not medical:
            return "Medical Record not found", 404

        return render_template('medical_record/edit_med.html', medical=medical)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while processing your request", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/update_medical', methods=['POST'])
def update_medical():
        medicalrecord_id = request.form['medical_id']
        member_id = request.form['member_id']
        last_checkup = request.form['last_checkup']
        doctor_id = request.form['doctor_id']
        high_bp = request.form['high_bp']
        low_bp = request.form['low_bp']
        weight = request.form['weight']
        diabetes = request.form['diabetes']
        notes = request.form['notes']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE HAS_RECORD SET LAST_CHECKUP = %s WHERE MEMBER_ID=%s",())
            cursor.execute("UPDATE medical_record SET member_id = %s, doctor_id = %s, high_bp = %s, low_bp = %s, weight = %s, diabetes = %s, notes = %s WHERE MEDICALRECORD_ID = %s",
                           (member_id, doctor_id, high_bp, low_bp, weight, diabetes, notes, medicalrecord_id))
            conn.commit()
            return redirect(url_for('display_med'))

        except mysql.connector.Error as e:
            print("An error occurred:", e)
            return "An error occurred while updating medical record details", 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
             
             

#****************************************************************************************************#



#------------------- EMPLOYEE DISPLAY ----------------------#

@app.route('/displaye', methods=['GET'])
def displaye():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM EMPLOYEE")
        users = cursor.fetchall()
        return render_template("employee/displaye.html", users=users)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('employee/displaye.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


#-------------------- ADD EMPLOYEE ------------------------#

@app.route('/addemp', methods=['GET'])
def addemp():
    return render_template('employee/addemp.html')

@app.route('/insertemp', methods=['POST'])
def insertemp():
    
    try:
        name = request.form['name']
        phone = request.form['phone']
        city = request.form['city']
        address = request.form['address']
        member_id = request.form['member_id']
        salary = request.form['salary']
        status = request.form['status']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.callproc('INSERT_EMPLOYEE', (name, phone, city, address, member_id, salary, status))
        conn.commit()  
        return redirect(url_for('displaye'))  
  
    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('employee/displaye.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



#-------------------- SORT EMPLOYEE ------------------------#  
 
@app.route('/sortemp', methods=['GET', 'POST'])
def sortemp():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sort_option = request.args.get('sort_option', 'display')
        
        if sort_option == 'name':
            cursor.execute("SELECT * FROM employee ORDER BY NAME")
        elif sort_option == 'salary':
            cursor.execute("SELECT * FROM employee ORDER BY SALARY DESC")
        else:
            cursor.execute("SELECT * FROM employee")
        
        users = cursor.fetchall()
        conn.close()
        
        return render_template("employee/displaye.html", users=users, sort_option=sort_option)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('employee/displaye.html', users=[], sort_option='displaye')



#-------------------- SEARCH EMPLOYEE ------------------------#

@app.route('/searchemp', methods=['GET'])
def searchemp():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        search_option = request.args.get('search_option')
        search_value = request.args.get('search_value')
        
        if search_option and search_value:
            if search_option in ['employee_id', 'name', 'salary', 'room_id','city', 'member_id']:
                if search_option == 'name':
                    cursor.execute("SELECT * FROM employee WHERE NAME LIKE %s", ('%' + search_value + '%',))
                else:
                    query = "SELECT * FROM employee WHERE {} = %s".format(search_option)
                    cursor.execute(query, (search_value,))
            else:
                return "Invalid search option"
        else:
            cursor.execute("SELECT * FROM employee")
        
        users = cursor.fetchall()
        return render_template("employee/displaye.html", users=users, search_option=search_option, search_value=search_value)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('employee/displaye.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            

#-------------------- EDIT EMPLOYEE ------------------------#
            
            
@app.route('/edit_employee', methods=['GET','POST'])
def edit_employee():
    
    employee_id = request.args.get('employee_id')
    
    if not employee_id:
        return "Member ID is required", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employee WHERE EMPLOYEE_ID = %s", (employee_id,))
        employee = cursor.fetchone()

        if not employee:
            return "Employee not found", 404

        return render_template('employee/editemp.html', employee=employee)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while processing your request", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/update_employee', methods=['POST'])
def update_employee():
        employee_id = request.form['employee_id']
        name = request.form['name']
        phone_number = request.form['phone']
        city = request.form['city']
        address_details = request.form['address']
        member_id = request.form['member_id']
        salary = request.form['salary']
        status = request.form['status']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE employee SET NAME = %s, PHONE_NUMBER = %s, CITY = %s, ADDRESS_DETAILS = %s, MEMBER_ID = %s, SALARY = %s, STATUS = %s WHERE employee_ID = %s",
                           (name, phone_number, city, address_details, member_id, salary, status, employee_id))
            conn.commit()
            return redirect(url_for('displaye'))

        except mysql.connector.Error as e:
            print("An error occurred:", e)
            return "An error occurred while updating member details", 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
           
        
            
            
            
            
#****************************************************************************************************#




@app.route('/moreroom', methods=['GET'])
def moreroom():
    return render_template('room/moreroom.html')


#------------------- ROOM DISPLAY ----------------------#

@app.route('/displayroom', methods=['GET'])
def displayroom():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT 
        rv.room_id, 
        rv.occupant_id,
        
        CASE 
            WHEN rv.occupant_id LIKE 'MEM%' THEN m.name
            WHEN rv.occupant_id LIKE 'EMP%' THEN e.name
            ELSE 'Unknown'
        END AS occupant_name,

        CASE
            WHEN rv.occupant_id LIKE 'MEM%' THEN A.START_DATE
            WHEN rv.occupant_id LIKE 'EMP%' THEN S.START_DATE
            ELSE 'Unknown'
        END AS START_DATE, 

        CASE
            WHEN rv.occupant_id LIKE 'MEM%' THEN A.END_DATE
            WHEN rv.occupant_id LIKE 'EMP%' THEN S.END_DATE
            ELSE 'Unknown'
        END AS END_DATE
    
        FROM 
            RoomView rv
        LEFT JOIN 
            Member m ON rv.occupant_id = m.member_id
        LEFT JOIN 
            ALLOTS A ON rv.occupant_id = A.MEMBER_ID
        LEFT JOIN 
            Employee e ON rv.occupant_id = e.employee_id
        LEFT JOIN 
            STAYS_IN S ON rv.occupant_id = S.EMPLOYEE_ID
        where A.end_date is null and s.end_date is null;

    """)
        users = cursor.fetchall()
        return render_template('room/displayroom.html', users=users)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('room/displayroom.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



#-------------------- ADD ROOM ------------------------#

@app.route('/addroom', methods=['GET'])
def addroom():
    return render_template('room/addroom.html')

@app.route('/insertroom', methods=['POST'])
def insertroom():
    try:
        room_id = request.form['room_id']
        member_id = request.form['member_id'].upper()
        employee_id = request.form['employee_id'].upper()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        
        if member_id == 'NULL':
            member_id = None
            
        if employee_id == 'NULL' :
            employee_id = None

        cursor.callproc('INSERT_ROOM', (room_id, member_id, employee_id))
        conn.commit()
        
        cursor.execute("""
        SELECT 
        rv.room_id, 
        rv.occupant_id,
        
        CASE 
            WHEN rv.occupant_id LIKE 'MEM%' THEN m.name
            WHEN rv.occupant_id LIKE 'EMP%' THEN e.name
            ELSE 'Unknown'
        END AS occupant_name,

        CASE
            WHEN rv.occupant_id LIKE 'MEM%' THEN A.START_DATE
            WHEN rv.occupant_id LIKE 'EMP%' THEN S.START_DATE
            ELSE 'Unknown'
        END AS START_DATE, 

        CASE
            WHEN rv.occupant_id LIKE 'MEM%' THEN A.END_DATE
            WHEN rv.occupant_id LIKE 'EMP%' THEN S.END_DATE
            ELSE 'Unknown'
        END AS END_DATE
    
        FROM 
            RoomView rv
        LEFT JOIN 
            Member m ON rv.occupant_id = m.member_id
        LEFT JOIN 
            ALLOTS A ON rv.occupant_id = A.MEMBER_ID
        LEFT JOIN 
            Employee e ON rv.occupant_id = e.employee_id
        LEFT JOIN 
            STAYS_IN S ON rv.occupant_id = S.EMPLOYEE_ID
        WHERE A.END_DATE IS NULL AND S.END_DATE IS NULL;
    """)
        users = cursor.fetchall()
        return render_template('room/displayroom.html', users=users)
    
    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('room/displayroom.html', users=users)
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()




#-------------------- SORT ROOM ------------------------#  
 
@app.route('/sortroom', methods=['GET', 'POST'])
def sortroom():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sort_option = request.args.get('sort_option', 'display')
        
        if sort_option == 'room_id':
            
            cursor.execute("""
            SELECT 
            rv.room_id, 
            rv.occupant_id,
            
            CASE 
                WHEN rv.occupant_id LIKE 'MEM%' THEN m.name
                WHEN rv.occupant_id LIKE 'EMP%' THEN e.name
                ELSE 'Unknown'
            END AS occupant_name,

            CASE
                WHEN rv.occupant_id LIKE 'MEM%' THEN A.START_DATE
                WHEN rv.occupant_id LIKE 'EMP%' THEN S.START_DATE
                ELSE 'Unknown'
            END AS START_DATE, 

            CASE
                WHEN rv.occupant_id LIKE 'MEM%' THEN A.END_DATE
                WHEN rv.occupant_id LIKE 'EMP%' THEN S.END_DATE
                ELSE 'Unknown'
            END AS END_DATE
        
            FROM 
                RoomView rv
            LEFT JOIN 
                Member m ON rv.occupant_id = m.member_id
            LEFT JOIN 
                ALLOTS A ON rv.occupant_id = A.MEMBER_ID
            LEFT JOIN 
                Employee e ON rv.occupant_id = e.employee_id
            LEFT JOIN 
                STAYS_IN S ON rv.occupant_id = S.EMPLOYEE_ID
            WHERE A.END_DATE IS NULL AND S.END_DATE IS NULL
            ORDER BY rv.room_id;
            
            """)
        
        else:
            
            cursor.execute("""
            SELECT 
            rv.room_id, 
            rv.occupant_id,
            
            CASE 
                WHEN rv.occupant_id LIKE 'MEM%' THEN m.name
                WHEN rv.occupant_id LIKE 'EMP%' THEN e.name
                ELSE 'Unknown'
            END AS occupant_name,

            CASE
                WHEN rv.occupant_id LIKE 'MEM%' THEN A.START_DATE
                WHEN rv.occupant_id LIKE 'EMP%' THEN S.START_DATE
                ELSE 'Unknown'
            END AS START_DATE, 

            CASE
                WHEN rv.occupant_id LIKE 'MEM%' THEN A.END_DATE
                WHEN rv.occupant_id LIKE 'EMP%' THEN S.END_DATE
                ELSE 'Unknown'
            END AS END_DATE
        
            FROM 
                RoomView rv
            LEFT JOIN 
                Member m ON rv.occupant_id = m.member_id
            LEFT JOIN 
                ALLOTS A ON rv.occupant_id = A.MEMBER_ID
            LEFT JOIN 
                Employee e ON rv.occupant_id = e.employee_id
            LEFT JOIN 
                STAYS_IN S ON rv.occupant_id = S.EMPLOYEE_ID
            WHERE A.END_DATE IS NULL AND S.END_DATE IS NULL;
        """)
        
        users = cursor.fetchall()
        conn.close()
        
        return render_template("room/displayroom.html", users=users, sort_option=sort_option)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('room/displayroom.html', users=[], sort_option='displayroom')
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            

#-------------------- SEARCH ROOM ------------------------#

@app.route('/searchroom', methods=['GET'])
def searchroom():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        search_option = request.args.get('search_option')
        search_value = request.args.get('search_value')

        if search_option and search_value:
            if search_option == 'name': 
                cursor.execute("""
                    SELECT 
                    rv.room_id, 
                    rv.occupant_id,
                    
                    CASE 
                        WHEN rv.occupant_id LIKE 'MEM%' THEN m.name
                        WHEN rv.occupant_id LIKE 'EMP%' THEN e.name
                        ELSE 'Unknown'
                    END AS occupant_name,

                    CASE
                        WHEN rv.occupant_id LIKE 'MEM%' THEN A.START_DATE
                        WHEN rv.occupant_id LIKE 'EMP%' THEN S.START_DATE
                        ELSE 'Unknown'
                    END AS START_DATE, 

                    CASE
                        WHEN rv.occupant_id LIKE 'MEM%' THEN A.END_DATE
                        WHEN rv.occupant_id LIKE 'EMP%' THEN S.END_DATE
                        ELSE 'Unknown'
                    END AS END_DATE
                
                    FROM 
                        RoomView rv
                    LEFT JOIN 
                        Member m ON rv.occupant_id = m.member_id
                    LEFT JOIN 
                        ALLOTS A ON rv.occupant_id = A.MEMBER_ID
                    LEFT JOIN 
                        Employee e ON rv.occupant_id = e.employee_id
                    LEFT JOIN 
                        STAYS_IN S ON rv.occupant_id = S.EMPLOYEE_ID
                    WHERE 
                        m.name LIKE %s OR e.name LIKE %s;
                    
                """, ('%' + search_value + '%', '%' + search_value + '%'))
            
            elif search_option == 'room_id':
                cursor.execute("""
                    SELECT 
                    rv.room_id, 
                    rv.occupant_id,
                    
                    CASE 
                        WHEN rv.occupant_id LIKE 'MEM%' THEN m.name
                        WHEN rv.occupant_id LIKE 'EMP%' THEN e.name
                        ELSE 'Unknown'
                    END AS occupant_name,

                    CASE
                        WHEN rv.occupant_id LIKE 'MEM%' THEN A.START_DATE
                        WHEN rv.occupant_id LIKE 'EMP%' THEN S.START_DATE
                        ELSE 'Unknown'
                    END AS START_DATE, 

                    CASE
                        WHEN rv.occupant_id LIKE 'MEM%' THEN A.END_DATE
                        WHEN rv.occupant_id LIKE 'EMP%' THEN S.END_DATE
                        ELSE 'Unknown'
                    END AS END_DATE
                
                    FROM 
                        RoomView rv
                    LEFT JOIN 
                        Member m ON rv.occupant_id = m.member_id
                    LEFT JOIN 
                        ALLOTS A ON rv.occupant_id = A.MEMBER_ID
                    LEFT JOIN 
                        Employee e ON rv.occupant_id = e.employee_id
                    LEFT JOIN 
                        STAYS_IN S ON rv.occupant_id = S.EMPLOYEE_ID
                    WHERE 
                        rv.room_id = %s order by end_date desc;
                """, (search_value,))
                
            elif search_option == 'occupant_id':
                cursor.execute("""
                    SELECT 
                    rv.room_id, 
                    rv.occupant_id,
                    
                    CASE 
                        WHEN rv.occupant_id LIKE 'MEM%' THEN m.name
                        WHEN rv.occupant_id LIKE 'EMP%' THEN e.name
                        ELSE 'Unknown'
                    END AS occupant_name,

                    CASE
                        WHEN rv.occupant_id LIKE 'MEM%' THEN A.START_DATE
                        WHEN rv.occupant_id LIKE 'EMP%' THEN S.START_DATE
                        ELSE 'Unknown'
                    END AS START_DATE, 

                    CASE
                        WHEN rv.occupant_id LIKE 'MEM%' THEN A.END_DATE
                        WHEN rv.occupant_id LIKE 'EMP%' THEN S.END_DATE
                        ELSE 'Unknown'
                    END AS END_DATE
                
                    FROM 
                        RoomView rv
                    LEFT JOIN 
                        Member m ON rv.occupant_id = m.member_id
                    LEFT JOIN 
                        ALLOTS A ON rv.occupant_id = A.MEMBER_ID
                    LEFT JOIN 
                        Employee e ON rv.occupant_id = e.employee_id
                    LEFT JOIN 
                        STAYS_IN S ON rv.occupant_id = S.EMPLOYEE_ID
                    WHERE 
                        rv.occupant_id = %s AND
                    A.END_DATE IS NULL AND S.END_DATE IS NULL;
                """, (search_value,))
            
            users = cursor.fetchall()
            
        else:
            cursor.execute("""
                SELECT 
                rv.room_id, 
                rv.occupant_id,
                
                CASE 
                    WHEN rv.occupant_id LIKE 'MEM%' THEN m.name
                    WHEN rv.occupant_id LIKE 'EMP%' THEN e.name
                    ELSE 'Unknown'
                END AS occupant_name,

                CASE
                    WHEN rv.occupant_id LIKE 'MEM%' THEN A.START_DATE
                    WHEN rv.occupant_id LIKE 'EMP%' THEN S.START_DATE
                    ELSE 'Unknown'
                END AS START_DATE, 

                CASE
                    WHEN rv.occupant_id LIKE 'MEM%' THEN A.END_DATE
                    WHEN rv.occupant_id LIKE 'EMP%' THEN S.END_DATE
                    ELSE 'Unknown'
                END AS END_DATE
            
            FROM 
                RoomView rv
            LEFT JOIN 
                Member m ON rv.occupant_id = m.member_id
            LEFT JOIN 
                ALLOTS A ON rv.occupant_id = A.MEMBER_ID
            LEFT JOIN 
                Employee e ON rv.occupant_id = e.employee_id
            LEFT JOIN 
                STAYS_IN S ON rv.occupant_id = S.EMPLOYEE_ID
            WHERE A.END_DATE IS NULL AND S.END_DATE IS NULL;

            """)

            users = cursor.fetchall()

        return render_template("room/displayroom.html", users=users, search_option=search_option, search_value=search_value)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('room/displayroom.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



#------------------- EDIT ROOM ----------------------#


@app.route('/editroom', methods=['GET'])
def editroom():
    
    room_number = request.args.get('room_id')
    occupant_id = request.args.get('occupant_id')
    occupant_name = request.args.get('occupant_name')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    return render_template("room/edit_room.html", room_number=room_number,occupant_id=occupant_id,occupant_name=occupant_name,start_date =start_date ,end_date=end_date)

@app.route('/update_room', methods=['POST'])
def update_room():
    room_number = request.form['room_id']
    occupant_id = request.form['occupant_id']
    new_end_date = request.form['end_date']

    # Connect to your database
    conn = get_db_connection()  
    cursor = conn.cursor()
    
    if 'MEM' in occupant_id:
        # Update the end date in the 'allots' table for occupant IDs starting with 'MEM'
        cursor.execute("UPDATE ALLOTS SET END_DATE = %s WHERE ROOM_ID = %s AND MEMBER_ID = %s", (new_end_date, room_number, occupant_id))
    elif 'EMP' in occupant_id:
        # Update the end date in the 'stays_in' table for occupant IDs starting with 'EMP'
        cursor.execute("UPDATE STAYS_IN SET END_DATE = %s WHERE ROOM_ID = %s AND EMPLOYEE_ID = %s", (new_end_date, room_number, occupant_id))
    else:
        # Handle other cases or raise an error if necessary
        pass

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

    return redirect(url_for('displayroom'))



#***********************************************************************************************#




#------------------- NEW ROOM DISPLAY ----------------------#

@app.route('/displaynewroom', methods=['GET'])
def displaynewroom():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM new_room")
        users = cursor.fetchall()
        return render_template("room/displaynewroom.html", users=users)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('room/displaynewroom.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()




#-------------------- ADD NEW ROOM ------------------------#

@app.route('/addnewroom', methods=['GET'])
def addnewroom():
    return render_template('room/addnewroom.html')

@app.route('/insertnewroom', methods=['POST'])
def insertnewroom():
    
    try:
        
        room_id = request.form['room_id']
        room_type = request.form['room_type']
        vacancy = request.form['vacancy']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.callproc('INSERT_NEW_ROOM', (room_id, room_type, vacancy))
        conn.commit() 
        return redirect(url_for('displaynewroom')) 
    
    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('room/displaynewroom.html', users=[])
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        


#-------------------- SORT NEW ROOM ------------------------#  
 
@app.route('/sortnewroom', methods=['GET', 'POST'])
def sortnewroom():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sort_option = request.args.get('sort_option', 'display')
        
        if sort_option == 'room_id':
            cursor.execute("SELECT * FROM new_room ORDER BY ROOM_ID")
        elif sort_option == 'vacancy':
            cursor.execute("SELECT * FROM new_room ORDER BY VACANCY")
        else:
            cursor.execute("SELECT * FROM new_room")
        
        users = cursor.fetchall()
        
        return render_template("room/displaynewroom.html", users=users, sort_option=sort_option)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('room/displaynewroom.html', users=[], sort_option='displaynewroom')
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



#-------------------- SEARCH NEW ROOM ------------------------#

@app.route('/searchnewroom', methods=['GET'])
def searchnewroom():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        search_option = request.args.get('search_option')
        search_value = request.args.get('search_value')
        
        if search_option and search_value:
            if search_option in ['room_id', 'room_type', 'vacancy']:
                    query = "SELECT * FROM NEW_ROOM WHERE {} = %s".format(search_option)
                    cursor.execute(query, (search_value,))
            else:
                return "Invalid search option"
        else:
            cursor.execute("SELECT * FROM NEW_ROOM")
        
        users = cursor.fetchall()
        return render_template("room/displaynewroom.html", users=users, search_option=search_option, search_value=search_value)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('room/displaynewroom.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            




#***********************************************************************************************#




#------------------- GUARDIAN DISPLAY ----------------------#

@app.route('/displayg', methods=['GET'])
def displayg():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT g.GUARDIAN_ID, g.member_id, g.name, g.phone_number, g.city, g.ADDRESS_DETAILS, g.email, g.status, v.VISIT_DATE
                          FROM visits v
                          LEFT JOIN guardian g ON v.GUARDIAN_ID = g.guardian_id""")
        users = cursor.fetchall()
        return render_template("guardian/displayg.html", users=users)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('guardian/displayg.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


#-------------------- ADD GUARDIAN ------------------------#

@app.route('/addgua', methods=['GET'])
def addgua():
    return render_template('guardian/addgua.html')

@app.route('/insertgua', methods=['POST'])
def insertgua():
    
    try:
        
        name = request.form['name']
        member_id = request.form['member_id']
        phone = request.form['phone']
        city = request.form['city']
        address = request.form['address']
        email = request.form['email']
        status = request.form['status']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.callproc('INSERT_GUARDIAN', (name, member_id, phone, city, address, email, status))
        conn.commit()  
        conn.close()   
        return redirect(url_for('displayg'))  
    
    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('guardian/displayg.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        


#-------------------- SORT GUARDIAN ------------------------#  
 
@app.route('/sortguardian', methods=['GET', 'POST'])
def sortguardian():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
       
        sort_option = request.args.get('sort_option', 'display')
       
        if sort_option == 'name':
            cursor.execute("SELECT * FROM guardian ORDER BY name")
        else:
            cursor.execute("SELECT * FROM guardian")
       
        users = cursor.fetchall()
        conn.close()
       
        return render_template("guardian/displayg.html", users=users, sort_option=sort_option)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('guardian/displayg.html', users=[], sort_option='displayg')


#-------------------- SEARCH GUARDIAN ------------------------#

@app.route('/searchguardian', methods=['GET'])
def searchguardian():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
       
        search_option = request.args.get('search_option')
        search_value = request.args.get('search_value')
       
        if search_option and search_value:
            if search_option in ['guardian_id', 'name', 'member_id','city', 'status']:
                if search_option == 'name':
                    cursor.execute("SELECT * FROM guardian WHERE NAME LIKE %s", ('%' + search_value + '%',))
                else:
                    query = "SELECT * FROM guardian WHERE {} = %s".format(search_option)
                    cursor.execute(query, (search_value,))
            else:
                return "Invalid search option"
        else:
            cursor.execute("SELECT * FROM guardian")
       
        users = cursor.fetchall()
        return render_template("guardian/displayg.html", users=users, search_option=search_option, search_value=search_value)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('guardian/displayg.html', users=[])

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    
            
#---------------------- GUARDIAN EDIT ---------------------------#


@app.route('/edit_guardian', methods=['GET','POST'])
def edit_guardian():
    
    guardian_id = request.args.get('guardian_id')
    
    if not guardian_id:
        return "Guardian ID is required", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM guardian WHERE guardian_ID = %s", (guardian_id,))
        guardian = cursor.fetchone()

        if not guardian:
            return "Guardian not found", 404

        return render_template('guardian/edit_gua.html', guardian=guardian)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while processing your request", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/update_guardian', methods=['POST'])
def update_guardian():
        
        guardian_id = request.form['guardian_id']
        name = request.form['name']
        member_id = request.form['member_id']
        phone_number = request.form['phone']
        city = request.form['city']
        address_details = request.form['address']
        email = request.form['email']
        status = request.form['status']
        visit_day = request.form['visit_date']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE VISITS SET VISIT_DATE=%s where guardian_id=%s",(visit_day,guardian_id))
            cursor.execute("UPDATE guardian SET NAME = %s, MEMBER_ID = %s, PHONE_NUMBER = %s, CITY = %s, ADDRESS_DETAILS = %s, EMAIL = %s, STATUS = %s WHERE GUARDIAN_ID = %s",
                           (name, member_id, phone_number, city, address_details, email, status, guardian_id))
            
            conn.commit()
            return redirect(url_for('displayg'))

        except mysql.connector.Error as e:
            print("An error occurred:", e)
            return "An error occurred while updating member details", 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


if __name__ == '__main__':
    app.run(debug=True)