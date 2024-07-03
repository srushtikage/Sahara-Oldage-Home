from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
import mysql.connector
import secrets
import string

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='rishita.khandagale@cumminscollege.in',
    MAIL_PASSWORD='rnk@04251024'
)

app.secret_key = 'rishita'
mail = Mail(app)


#-------------- DB Connection ------------------#

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
        cursor = conn.cursor()
       
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
   
            
@app.route('/main.html', methods=['GET'])
def mainhtml():
    return render_template("/main.html")


# ---------------- FORGOT PASSWORD ----------------------#

@app.route('/forgot_password')
def forget_passwordd():
    return render_template("forgot_password.html") 


@app.route('/reset_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        guardian_id = request.form['username']  # Assuming guardian_id is used for login
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Fetch the associated member ID from the database
            cursor.execute("SELECT member_id FROM guardian WHERE guardian_id = %s", (guardian_id,))
            member_id = cursor.fetchone()[0]
            conn.commit()

            # Send member ID as the password reset email
            recipient_email = fetch_guardian_email(guardian_id)  # Fetch guardian's email address
            send_password_reset_email(recipient_email, member_id)  # Send password reset email

            # Flash success message only after email is sent successfully
            flash('Password reset email sent. Check your email for further instructions.', 'success')
            app.logger.debug('Password reset email sent successfully.')  # Debug statement

            return redirect(url_for('forgot_password.html'))  # Redirect to login page after sending email
        except Exception as e:
            flash('An error occurred while processing your request. Please try again later.', 'error')
            print("An error occurred:", e)
            return render_template('forgot_password.html')  # Render the form template in case of error
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('forget_password.html')  # Render the initial form template for GET requests



def fetch_guardian_email(guardian_id):
    """Fetches the email address associated with the guardian ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM guardian WHERE guardian_id = %s", (guardian_id,))
    guardian_email = cursor.fetchone()
    cursor.close()
    conn.close()
    return guardian_email[0] if guardian_email is not None else None



def send_password_reset_email(recipient_email, new_password):
    """Sends the member ID as the password reset email to the guardian's email address."""
    subject = "Password Reset"
    sender = "rishita.khandagale@cumminscollege.in" 
    recipients = [recipient_email]
    body = f"Your new password is: {new_password}. Please login and change your password."
    
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = body
    
    mail.send(msg)


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
        cursor.execute("SELECT * FROM MEMBER WHERE PHONE_NUMBER = %s AND STATUS = 'Active'", (phone_no,))
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

@app.route('/search', methods=['GET', 'POST'])
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

@app.route('/edit_member', methods=['GET'])
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

        # Check for duplicate phone number
        cursor.execute("SELECT * FROM member WHERE PHONE_NUMBER = %s AND MEMBER_ID != %s", (member_phone_number, member_id))
        existing_member = cursor.fetchone()

        if existing_member:
            return render_template('member/phone.html', 
                                   message="Phone number already exists! Please re-enter again",
                                   member=(member_id, member_name, member_gender, member_birth_date,
                                           member_phone_number, member_city, member_address_details, 
                                           member_join_date, member_assistance, member_status))

            
        # Update member details
        cursor.execute(
            "UPDATE member SET NAME = %s, GENDER = %s, BIRTH_DATE = %s, PHONE_NUMBER = %s, CITY = %s, ADDRESS_DETAILS = %s, JOIN_DATE = %s, ASSISTANCE = %s, STATUS = %s WHERE MEMBER_ID = %s",
            (member_name, member_gender, member_birth_date, member_phone_number, member_city, member_address_details, member_join_date, member_assistance, member_status, member_id)
        )
        conn.commit()

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while updating member details", 500

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('display'))



            
            
            

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
        
        # Check if the phone number already exists
        cursor.execute("SELECT * FROM DOCTOR WHERE PHONE_NUMBER = %s", (phone_no,))
        existing_doctor = cursor.fetchone()

        if existing_doctor:
            # If the phone number exists, render the addmem.html template with existing member details
            return render_template('doctor/add_doc.html', message="Phone number already exists! Please re-enter again",
                                   name=name, city=city, address=address, email=email, specialization=specialization, salary=salary, status=status)
        
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
    name = request.form['name']
    phone = request.form['phone']
    city = request.form['city']
    address = request.form['address']
    email = request.form['email']
    specialization = request.form['specialization']
    salary = request.form['salary']
    status = request.form['status']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check for duplicate phone number
        cursor.execute("SELECT * FROM doctor WHERE phone_number = %s AND doctor_id != %s", (phone, doctor_id))
        existing_doctor = cursor.fetchone()

        if existing_doctor:
            message = "Phone number already exists! Please re-enter."
            return render_template('doctor/edit_doc.html', doctor=(doctor_id, name, "", city, address, email, specialization, salary, status), message=message)
        
        cursor.execute("UPDATE doctor SET NAME = %s, PHONE_NUMBER = %s, CITY = %s, ADDRESS_DETAILS = %s, EMAIL = %s, SPECIALIZATION = %s, SALARY = %s, STATUS = %s WHERE DOCTOR_ID = %s",
                       (name, phone, city, address, email, specialization, salary, status, doctor_id))
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
        cursor.execute("""SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.MEDICINES, M.NOTES
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



def fetch_member_name(member_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM member WHERE member_id = %s", (member_id,))
    member_name = cursor.fetchone()
    cursor.close()
    conn.close()
    return member_name[0] if member_name else None



# Function to fetch all guardian emails associated with a member
def fetch_guardian_emails(member_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM guardian WHERE member_id = %s", (member_id,))
    guardian_emails = cursor.fetchall()
    cursor.close()
    conn.close()
    return [email[0] for email in guardian_emails]  # Extract emails from the fetched records



# Function to send medical record email to all guardians
def send_medical_record_email(guardian_emails, member_name, member_id):
    subject = "New Medical Record Added"
    sender = "your_email@example.com"  # Replace with your email
    body = f"A new medical record has been added for {member_name} (Member ID: {member_id}). Please login to check details."

    msg = Message(subject, sender=sender, recipients=guardian_emails)
    msg.body = body

    mail.send(msg)
    print(f"Email sent to {', '.join(guardian_emails)} for member {member_name} (Member ID: {member_id})")



@app.route('/insert_med', methods=['POST'])
def insert_med():
    try:
        member_id = request.form['member_id']
        doctor_id = request.form['doctor_id']
        high_bp = request.form['high_bp']
        low_bp = request.form['low_bp']
        weight = request.form['weight']
        diabetes = request.form['diabetes']
        medicines = request.form['medicines']
        notes = request.form['notes']
   
        conn = get_db_connection()  
        cursor = conn.cursor()
        cursor.callproc('INSERT_MEDICAL_RECORD', (member_id, doctor_id, high_bp, low_bp, weight, diabetes, medicines, notes))
        conn.commit() 
        
        # Fetch member name based on member_id from the database
        member_name = fetch_member_name(member_id)
        
        # Fetch guardian emails based on member_id from the database
        guardian_emails = fetch_guardian_emails(member_id)
        
        # Send email to guardians about the new medical record entry
        send_medical_record_email(guardian_emails, member_name, member_id)

        flash('Medical record added successfully!', 'success')
        return redirect(url_for('display_med'))

    except mysql.connector.Error as e:
        flash('An error occurred while adding medical record. Please try again later.', 'error')
        print("An error occurred:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('add_med'))  # Redirect to add_med page or any other appropriate route
            
            
            
#-------------------- SORT MEDICAL RECORD ------------------------#  
 
@app.route('/sort_med', methods=['GET', 'POST'])
def sort_med():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
   
        sort_option = request.args.get('sort_option', 'display')
        
        if sort_option == 'high_bp':
            cursor.execute("""SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.MEDICINES, M.NOTES
                            FROM HAS_RECORD H
                            LEFT JOIN MEDICAL_RECORD M ON H.MEDICALRECORD_ID = M.MEDICALRECORD_ID
                            ORDER BY 
                            HIGH_BP DESC
                            """)
        
        elif sort_option == 'low_bp':
            cursor.execute("""SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.MEDICINES, M.NOTES
                            FROM HAS_RECORD H
                            LEFT JOIN MEDICAL_RECORD M ON H.MEDICALRECORD_ID = M.MEDICALRECORD_ID ORDER BY M.LOW_BP""")
        
        else:
            cursor.execute("""SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.MEDICINES, M.NOTES
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
            if search_option in ['M.medicalrecord_id', 'M.member_id', 'M.doctor_id', 'M.high_bp', 'M.low_bp', 'M.diabetes', 'M.medicines']:
                if search_option == 'M.medicines':
                    query = """SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.MEDICINES, M.NOTES
                               FROM HAS_RECORD H
                               LEFT JOIN MEDICAL_RECORD M ON H.MEDICALRECORD_ID = M.MEDICALRECORD_ID
                               WHERE {} LIKE %s
                               ORDER BY 
                               H.MEMBER_ID ASC,
                               H.LAST_CHECKUP DESC""".format(search_option)
                    cursor.execute(query, ('%' + search_value + '%',))
                else:
                    query = """SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.MEDICINES, M.NOTES
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
            cursor.execute("""SELECT H.MEMBER_ID, M.MEDICALRECORD_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.MEDICINES, M.NOTES
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
        cursor.execute("""SELECT M.MEDICALRECORD_ID, H.MEMBER_ID, H.LAST_CHECKUP, M.DOCTOR_ID, M.HIGH_BP, M.LOW_BP, M.WEIGHT, M.DIABETES, M.MEDICINES, M.NOTES
                        FROM HAS_RECORD H
                        LEFT JOIN MEDICAL_RECORD M ON H.MEDICALRECORD_ID = M.MEDICALRECORD_ID WHERE M.MEDICALRECORD_ID = %s""", (medical_id,))
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
    medicines = request.form['medicines']
    notes = request.form['notes']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update HAS_RECORD table
        cursor.execute("UPDATE HAS_RECORD SET LAST_CHECKUP = %s WHERE MEMBER_ID = %s",
                       (last_checkup, member_id))

        # Update MEDICAL_RECORD table
        cursor.execute("""
            UPDATE MEDICAL_RECORD 
            SET MEMBER_ID = %s, DOCTOR_ID = %s, HIGH_BP = %s, LOW_BP = %s, 
                WEIGHT = %s, DIABETES = %s, MEDICINES = %s, NOTES = %s 
            WHERE MEDICALRECORD_ID = %s
        """, (member_id, doctor_id, high_bp, low_bp, weight, diabetes, medicines, notes, medicalrecord_id))

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
        salary = request.form['salary']
        status = request.form['status']

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the phone number already exists
        cursor.execute("SELECT * FROM EMPLOYEE WHERE PHONE_NUMBER = %s", (phone,))
        existing_employee = cursor.fetchone()

        if existing_employee:
            # If the phone number exists, render the addmem.html template with existing member details
            return render_template('employee/addemp.html', message="PhPone number already exists! Please re-enter again",
                                   name=name, city=city, 
                                   address=address, salary=salary, status=status)
        
        cursor.callproc('INSERT_EMPLOYEE', (name, phone, city, address, salary, status))
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
            if search_option in ['employee_id', 'name', 'salary', 'room_id','city']:
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
    salary = request.form['salary']
    status = request.form['status']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ensure data types are correct
        employee_id = str(employee_id)
        name = str(name)
        phone_number = int(phone_number)
        city = str(city)
        address_details = str(address_details)
        salary = int(salary)
        status = str(status)
        
        # Check for duplicate phone number
        cursor.execute("SELECT * FROM employee WHERE PHONE_NUMBER = %s AND EMPLOYEE_ID != %s", (phone_number, employee_id))
        existing_employee = cursor.fetchone()

        if existing_employee:
            message = "Phone number already exists! Please re-enter."
            modified_employee = (
                employee_id,
                name,
                "",  # Set phone number to empty string
                city,
                address_details,
                salary,
                status
            )
            return render_template('employee/editemp.html', employee=modified_employee, message=message)
        
        cursor.execute("""
            UPDATE employee 
            SET NAME = %s, PHONE_NUMBER = %s, CITY = %s, ADDRESS_DETAILS = %s, SALARY = %s, STATUS = %s 
            WHERE EMPLOYEE_ID = %s
        """, (name, phone_number, city, address_details, salary, status, employee_id))
        
        conn.commit()
        return redirect(url_for('displaye'))

    except ValueError as ve:
        print("Value error occurred:", ve)
        return "Invalid input value", 400

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
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
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
        return "An error occurred while fetching room details", 500

    finally:
        cursor.close()
        conn.close()



#-------------------- ADD ROOM ------------------------#

@app.route('/addroom', methods=['GET'])
def addroom():
    return render_template('room/addroom.html')

@app.route('/insertroom', methods=['POST'])
def insertroom():
    try:
        room_id = request.form['room_id']
        member_id = request.form['member_id'].upper() if request.form['member_id'].upper() != 'NULL' else None
        employee_id = request.form['employee_id'].upper() if request.form['employee_id'].upper() != 'NULL' else None
        
        conn = get_db_connection()
        cursor = conn.cursor()

        
        cursor.execute("SELECT ROOM_ID FROM NEW_ROOM WHERE ROOM_ID = %s", (room_id,))
        available = cursor.fetchone()

        if available is None:
            return render_template('room/addroom.html', message='Room not available!',)
        
        
        cursor.execute("SELECT VACANCY FROM NEW_ROOM WHERE ROOM_ID = %s", (room_id,))
        vacancy = cursor.fetchone()

        if vacancy and vacancy[0] == 0:
            return render_template('room/addroom.html', message='Room is not vacant!',)
        
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
        return render_template('room/displayroom.html', users=[])
    
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

    return render_template("room/edit_room.html", room_number=room_number, occupant_id=occupant_id, occupant_name=occupant_name, start_date=start_date, end_date=end_date)

@app.route('/update_room', methods=['POST'])
def update_room():
    room_number = request.form['room_id']
    occupant_id = request.form['occupant_id']
    new_end_date = request.form['end_date']

    if not new_end_date:
        return redirect(url_for('displayroom'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if 'MEM' in occupant_id:
            cursor.execute("UPDATE ALLOTS SET END_DATE = %s WHERE ROOM_ID = %s AND MEMBER_ID = %s", (new_end_date, room_number, occupant_id))
        elif 'EMP' in occupant_id:
            cursor.execute("UPDATE STAYS_IN SET END_DATE = %s WHERE ROOM_ID = %s AND EMPLOYEE_ID = %s", (new_end_date, room_number, occupant_id))
        else:
            return "Invalid occupant ID", 400

        conn.commit()

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while updating the room details", 500

    finally:
        cursor.close()
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
        cursor = conn.cursor()  # Use dictionary cursor for easier handling of results
        cursor.execute("""SELECT g.GUARDIAN_ID, g.name, g.member_id, g.phone_number, g.city, g.ADDRESS_DETAILS, g.email, g.status, v.VISIT_DATE
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
        
        # Check if the phone number already exists
        cursor.execute("SELECT * FROM GUARDIAN WHERE PHONE_NUMBER = %s", (phone,))
        existing_member = cursor.fetchone()

        if existing_member:
            # If the phone number exists, render the addmem.html template with existing member details
            return render_template('guardian/addgua.html', message="Phone number already exists! Please re-enter again",
                                   name=name, member_id=member_id,city=city, 
                                   address=address, email=email, status=status)
        
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
            cursor.execute("""SELECT g.GUARDIAN_ID, g.name, g.member_id, g.phone_number, g.city, g.ADDRESS_DETAILS, g.email, g.status, v.VISIT_DATE
                          FROM visits v
                          LEFT JOIN guardian g ON v.GUARDIAN_ID = g.guardian_id
                          ORDER BY name""")
        else:
             cursor.execute("""SELECT g.GUARDIAN_ID, g.name, g.member_id, g.phone_number, g.city, g.ADDRESS_DETAILS, g.email, g.status, v.VISIT_DATE
                          FROM visits v
                          LEFT JOIN guardian g ON v.GUARDIAN_ID = g.guardian_id""")
       
        users = cursor.fetchall()
        conn.close()
       
        return render_template("guardian/displayg.html", users=users, sort_option=sort_option)

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return render_template('guardian/displayg.html', users=[], sort_option='displayg')


#-------------------- SEARCH GUARDIAN ------------------------#

@app.route('/searchguardian', methods=['GET'])
def searchguardian():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()  

        search_option = request.args.get('search_option')
        search_value = request.args.get('search_value')

        if search_option and search_value:
            if search_option in ['guardian_id', 'name', 'member_id', 'city', 'status']:
                if search_option == 'name':
                    cursor.execute("""SELECT g.GUARDIAN_ID, g.name, g.member_id, g.phone_number, g.city, g.ADDRESS_DETAILS, g.email, g.status, v.VISIT_DATE
                                      FROM visits v
                                      LEFT JOIN guardian g ON v.GUARDIAN_ID = g.guardian_id
                                      WHERE g.name LIKE %s""", ('%' + search_value + '%',))
                else:
                    query = """SELECT g.GUARDIAN_ID, g.name, g.member_id, g.phone_number, g.city, g.ADDRESS_DETAILS, g.email, g.status, v.VISIT_DATE
                               FROM visits v
                               LEFT JOIN guardian g ON v.GUARDIAN_ID = g.guardian_id 
                               WHERE g.{} = %s""".format(search_option)
                    cursor.execute(query, (search_value,))
            else:
                return "Invalid search option"
        else:
            cursor.execute("""SELECT g.GUARDIAN_ID, g.name, g.member_id, g.phone_number, g.city, g.ADDRESS_DETAILS, g.email, g.status, v.VISIT_DATE
                              FROM visits v
                              LEFT JOIN guardian g ON v.GUARDIAN_ID = g.guardian_id""")
        
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
    
    
            
#---------------------- EDIT GUARDIAN ---------------------------#

@app.route('/edit_guardian', methods=['GET'])
def edit_guardian():
    guardian_id = request.args.get('guardian_id')
    
    if not guardian_id:
        return "Guardian ID is required", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()  
        cursor.execute("""SELECT g.GUARDIAN_ID, g.name, g.member_id, g.phone_number, g.city, g.ADDRESS_DETAILS, g.email, g.status, v.VISIT_DATE
                          FROM guardian g
                          LEFT JOIN visits v ON v.GUARDIAN_ID = g.guardian_id
                          WHERE g.GUARDIAN_ID = %s""", (guardian_id,))
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
    visit_date = request.form['visit_date'] if request.form['visit_date'] else None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for duplicate phone number
        cursor.execute("SELECT * FROM guardian WHERE phone_number = %s AND guardian_id != %s", (phone_number, guardian_id))
        existing_guardian = cursor.fetchone()

        if existing_guardian:
            message = "Phone number already exists! Please re-enter."
            return render_template('guardian/edit_gua.html', guardian=(guardian_id, name, member_id, "", city, address_details, email, status, visit_date), message=message)

        if visit_date:
            cursor.execute("UPDATE visits SET visit_date = %s WHERE guardian_id = %s", (visit_date, guardian_id))
        else:
            cursor.execute("UPDATE visits SET visit_date = NULL WHERE guardian_id = %s", (guardian_id,))

        cursor.execute(
            "UPDATE guardian SET name = %s, member_id = %s, phone_number = %s, city = %s, address_details = %s, email = %s, status = %s WHERE guardian_id = %s",
            (name, member_id, phone_number, city, address_details, email, status, guardian_id)
        )

        conn.commit()
        return redirect(url_for('displayg'))

    except mysql.connector.Error as e:
        print("An error occurred:", e)
        return "An error occurred while updating guardian details", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



if __name__ == '__main__':
    app.run(debug=True)