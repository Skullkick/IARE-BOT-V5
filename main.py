
import time
import requests
import uuid
import random
import json
import sqlite3
from pytz import timezone
from datetime import datetime, timedelta
from bs4 import BeautifulSoup 
from pyrogram import Client, filters
import pyqrcode
import os
import png
import asyncio


BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_DEVELOPER_CHAT_ID_re = os.environ.get("DEVELOPER_CHAT_ID")
BOT_MAINTAINER_CHAT_ID_re = os.environ.get("MAINTAINER_CHAT_ID")
bot = Client(
        "IARE BOT",
        bot_token = BOT_TOKEN,
        api_id = API_ID,
        api_hash = API_HASH
)

#Bot Devoloper ID
BOT_DEVELOPER_CHAT_ID = int(BOT_DEVELOPER_CHAT_ID_re)
#Bot Maintainer ID
BOT_MAINTAINER_CHAT_ID = int(BOT_MAINTAINER_CHAT_ID_re)

# SQLite database file
DATABASE_FILE = "user_sessions.db"

TOTAL_USERS_DATABASE_FILE = "total_users.db"

REQUESTS_DATABASE_FILE = "requests.db"


async def get_indian_time():
    return datetime.now(timezone('Asia/Kolkata'))

async def create_tables():
    """
    Create the necessary tables in the SQLite database.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        # Create a table to store user sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                chat_id INTEGER PRIMARY KEY,
                session_data TEXT,
                last_activity TIMESTAMP,
                user_id TEXT
            )
        """)
        conn.commit()
#The usernames accessed this bot
async def create_total_users_table():
    """
    Create the total_users table in the SQLite database.
    """
    with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE
            )
        """)
        conn.commit()
#Function to store the session data
async def store_user_session(chat_id, session_data, user_id):
    """
    Store the user session data in the SQLite database.

    Parameters:
        chat_id (int): The chat ID of the user.
        session_data (str): JSON-formatted string containing the session data.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()

        # Get the current time in the Indian time zone
        current_time = await get_indian_time()
        # Execute the SQL query to insert or replace the session data
        cursor.execute("INSERT OR REPLACE INTO sessions (chat_id, session_data, last_activity, user_id) VALUES (?, ?, ?, ?)",
                       (chat_id, session_data, current_time, user_id))
        
        conn.commit()
#Function to store the usernames
async def store_username(username):
    """
    Store a username in the total_users table.

    Parameters:
        username (str): The username to store.
    """
    with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)",
                       (username,))
        conn.commit()

async def load_user_session(chat_id):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT session_data FROM sessions WHERE chat_id=?", (chat_id,))
        result = cursor.fetchone()
        if result:
            session_data = json.loads(result[0])
            # Check if the session data contains the 'username'
            if 'username' in session_data:
                return session_data
    return None

async def load_username(chat_id):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE chat_id=?", (chat_id,))
        row = cursor.fetchone()
        return row

async def delete_user_session(chat_id):
    """
    Delete the user session data from the SQLite database.

    Parameters:
        chat_id (int): The chat ID of the user.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE chat_id=?", (chat_id,))
        conn.commit()

async def clear_sessions_table():
    """
    Clear all rows from the sessions table.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions")
        conn.commit()

async def create_requests_table():
    with sqlite3.connect(REQUESTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pendingreq(
                       unique_id TEXT PRIMARY KEY,
                       user_id TEXT,
                       message TEXT,
                       chat_id INTEGER
            )
        """)
        conn.commit()

async def store_requests(unique_id, user_id, message, chat_id):
    with sqlite3.connect(REQUESTS_DATABASE_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO pendingreq (unique_id, user_id, message, chat_id) VALUES (?, ?, ?, ?)",
                  (unique_id, user_id, message, chat_id))
        conn.commit()

async def load_requests(unique_id):
    with sqlite3.connect(REQUESTS_DATABASE_FILE ) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pendingreq WHERE unique_id=?",(unique_id,))
        row = cursor.fetchone()
        return row
    
async def load_allrequests():
    with sqlite3.connect(REQUESTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pendingreq")
        all_messages = cursor.fetchall()
        return all_messages

async def delete_request(unique_id):
    with sqlite3.connect(REQUESTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pendingreq WHERE unique_id=?",(unique_id,))

async def clear_requests():
    with sqlite3.connect(REQUESTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pendingreq")

@bot.on_message(filters.command('reset'))
async def reset_database(bot,message):
    if message.chat.id==BOT_DEVELOPER_CHAT_ID or message.chat.id==BOT_MAINTAINER_CHAT_ID:
        await clear_sessions_table()
        await message.reply("Reset done")

@bot.on_message(filters.command('start'))
async def get_random_greeting(bot,message):
    """
    Get a random greeting based on the time and day.
    """
    indian_time = await get_indian_time()
    current_hour = indian_time.hour
    current_weekday = indian_time.weekday()

    # List of greetings based on the time of day
    morning_greetings = ["Good morning!", "Hello, early bird!", "Rise and shine!", "Morning!"]
    afternoon_greetings = ["Good afternoon!", "Hello there!", "Afternoon vibes!", "Hey!"]
    evening_greetings = ["Good evening!", "Hello, night owl!", "Evening time!", "Hi there!"]

    # List of greetings based on the day of the week
    weekday_greetings = ["Have a productive day!", "Stay focused and have a great day!", "Wishing you a wonderful day!", "Make the most of your day!"]
    weekend_greetings = ["Enjoy your weekend!", "Relax and have a great weekend!", "Wishing you a fantastic weekend!", "Make the most of your weekend!"]

    # Get a random greeting based on the time of day
    if 5 <= current_hour < 12:  # Morning (5 AM to 11:59 AM)
        greeting = random.choice(morning_greetings)
    elif 12 <= current_hour < 18:  # Afternoon (12 PM to 5:59 PM)
        greeting = random.choice(afternoon_greetings)
    else:  # Evening (6 PM to 4:59 AM)
        greeting = random.choice(evening_greetings)

    # Add a weekday-specific greeting if it's a weekday, otherwise, add a weekend-specific greeting
    if 0 <= current_weekday < 5:  # Monday to Friday
        greeting += " " + random.choice(weekday_greetings)
    else:  # Saturday and Sunday
        greeting += " " + random.choice(weekend_greetings)

    # Send the greeting to the user
    await message.reply(greeting)
async def perform_login(chat_id, username, password):
    """
    Perform login with the provided username and password.

    Returns:
        bool: True if login is successful, False otherwise.
    """
    # Set up the necessary headers and cookies
    cookies = {'PHPSESSID': ''}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://samvidha.iare.ac.in',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://samvidha.iare.ac.in/index',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }

    data = {
        'username': username,
        'password': password,
    }

    with requests.Session() as s:
        # Send GET request to the index page to capture the PHPSESSID cookie
        index_url = "https://samvidha.iare.ac.in/index"
        login_url = "https://samvidha.iare.ac.in/pages/login/checkUser.php"
        home_url = "https://samvidha.iare.ac.in/home"

        response = s.get(index_url)
        cookie_to_extract = 'PHPSESSID'
        cookie_value = response.cookies.get(cookie_to_extract)
        cookies['PHPSESSID'] = cookie_value

        # Send POST request to the login endpoint with credentials and cookies
        s.post(login_url, cookies=cookies, headers=headers, data=data)

        # Send GET request to the home page and check if the login was successful
        response = s.get(home_url)
        if '<title>IARE - Dashboard - Student</title>' in response.text:
            # Store the session data in the database
            session_data = {
                'cookies': s.cookies.get_dict(),
                'headers': headers,
                'username': username  # Save the username in the session data
            }
            return session_data
        else:   
            return None
        
# async def is_user_logged_in(user_id):
#     return user_id in user_sessions

@bot.on_message(filters.command('login'))
async def login(bot,message):
    chat_id = message.chat.id
    # command_args = message.get_args().split()
    command_args = message.text.split()[1:]
    # if await is_user_logged_in(chat_id):  # Implement is_user_logged_in function
    if await load_user_session(chat_id):
        await message.reply("You are already logged in.")
        return

    if len(command_args) != 2:
        await message.reply("Invalid command format. Use /login {username} {password}.")
        return

    username = command_args[0]
    password = command_args[1]

    # Perform login
    session_data = await perform_login(chat_id, username, password)  # Implement perform_login function

    if session_data:
        # Store the session data in the database
        await store_user_session(chat_id, json.dumps(session_data), username)  # Implement store_user_session function

        # # Set the session for the user and save the username
        await store_username(username)

        # Delete the login command message
        await message.delete()
        await update_activity_timestamp(chat_id)
        await bot.send_message(chat_id,text="Login successful!")
    else:
        await bot.send_message(chat_id,text="Invalid username or password.")


@bot.on_message(filters.command('logout'))
async def logout(bot,message):
    chat_id = message.chat.id
    session_data = await load_user_session(chat_id)

    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        await bot.send_message(chat_id,text="Please log in using the /login command.")
        return

    # Remove the session data from the database
    await delete_user_session(chat_id)  # Implement delete_user_session function

    await message.reply("Logout successful.")

@bot.on_message(filters.command('attendance'))
async def attendance(bot,message):
    chat_id = message.chat.id
    session_data = await load_user_session(chat_id)
    if not session_data:
        await bot.send_message(chat_id,"Please log in using the /login command.")
        return

    # Access the attendance page and retrieve the content
    attendance_url = 'https://samvidha.iare.ac.in/home?action=stud_att_STD'
    
    with requests.Session() as s:
        # Set the session cookies and headers
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        headers = session_data['headers']
        await update_activity_timestamp(chat_id)

        # Send GET request to the attendance or bunk page
        attendance_response = s.get(attendance_url)
    # Parse the HTML content using BeautifulSoup
    data = BeautifulSoup(attendance_response.text, 'html.parser')
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in attendance_response.text:
        await logout_user(bot,chat_id)
        return
    # Find the table element
    table_all = data.find_all('table', class_='table table-striped table-bordered table-hover table-head-fixed responsive')
    if len(table_all) > 1:
        # Process the second table data or perform any desired operations
        req_table = table_all[1]
        # Initialize an empty list to store the table data
        table_data = []
        # Find all table rows (tr elements) within the table body (tbody)
        rows = req_table.tbody.find_all('tr')
        # Iterate over the rows and extract the text content from each cell
        for row in rows:
            # Find all table cells (td elements) within the row
            cells = row.find_all('td')

            # Extract the text content from each cell and store it in a list
            row_data = [cell.get_text(strip=True) for cell in cells]

            # Add the row data to the main table data list
            table_data.append(row_data)
        sum_attendance = 0
        count_att = 0
        # Prepare individual messages for each course
        for row in table_data[0:]:
            course_name = row[2]
            conducted = row[5]
            attended = row[6]
            attendance_percentage = row[7]
            attendance_status = row[8]
            if course_name and attendance_percentage:
                att_msg = f"""
```{course_name}

● Conducted         -  {conducted}
             
● Attended          -  {attended}  
         
● Attendance %      -  {attendance_percentage} 
            
● Status            -  {attendance_status}  
         
```
"""
                # att_msg = f"Course: {course_name}, Attendance: {attendance_percentage}"
                sum_attendance += float(attendance_percentage)
                if float(attendance_percentage) > 0:
                        count_att += 1
                await bot.send_message(chat_id,att_msg)
        aver_attendance = round(sum_attendance/count_att, 2)
        over_all_attendance = f"**Overall Attendance is {aver_attendance}**"
        await bot.send_message(chat_id,over_all_attendance)

    else:
        await bot.send_message(chat_id,"Attendance data not found.")


@bot.on_message(filters.command('biometric'))
async def biometric(_,message):
    chat_id = message.chat.id
    session_data = await load_user_session(chat_id)
    if not session_data:
        await bot.send_message(chat_id,"Please log in using the /login command.")
        return

    biometric_url = 'https://samvidha.iare.ac.in/home?action=std_bio'
    with requests.Session() as s:

        cookies = session_data['cookies']
        s.cookies.update(cookies)
        headers = session_data['headers']
        await update_activity_timestamp(chat_id)

        response = s.get(biometric_url, headers=headers)

        # Parse the HTML content using BeautifulSoup
        biodata = BeautifulSoup(response.text, 'html.parser')
    biotable = biodata.find('tbody')
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in response.text:
        await logout_user(bot,chat_id)
        return
    if not biotable:
        await message.reply("Biometric data not found.")
        return

    # Initialize counters for days present and days absent
    days_present = 0
    days_absent = 0
    total_days = 0

    biorows = biotable.find_all('tr')

    # Iterate over the rows and calculate days present and days absent
    for row in biorows:
        # Find the status cell in the row
        cells = row.find_all('td')

        # Extract the status text from the appropriate cell (in this case, the last cell)
        status = cells[9].get_text(strip=True)

        # Increment the respective counter based on the status
        if 'Present' in status:
            days_present += 1
        elif 'Absent' in status:
            days_absent += 1
    total_days = days_present + days_absent
        # total_days += 1

    # Calculate the biometric percentage
    biometric_percentage = (days_present / total_days) * 100 if total_days != 0 else 0
    biometric_percentage = round(biometric_percentage,3)
    # Prepare the biometric message
    #biometric_msg = f"Number of Days Present: {days_present}\nNumber of Days Absent: {days_absent}\nTotal Number of Days: {total_days}\nBiometric Percentage: \n{biometric_percentage}%"
    intimes = []
    outtimes = []
    time_gap_more_than_six_hours = 0
    sixintime = []
    sixoutime = []
    for row in biorows:
        cell = row.find_all('td')
        intime = cell[7].text.strip()
        outtime = cell[8].text.strip()
        if intime and outtime and ':' in intime and ':' in outtime:
            intimes.append(intime)
            outtimes.append(outtime)
            intime_hour, intime_minute = intime.split(':')
            outtime_hour, outtime_minute = outtime.split(':')
            time_difference = (int(outtime_hour) - int(intime_hour)) * 60 + (int(outtime_minute) - int(intime_minute))
            if time_difference >= 360:
                time_gap_more_than_six_hours += 1
        sixintime.append(intime)
        sixoutime.append(outtime)
    six_percentage = (time_gap_more_than_six_hours / total_days) * 100 if total_days != 0 else 0
    six_percentage = round(six_percentage, 3)
    #biometric_msg += f"\nbiometric Percentage(6 hours gap):\n{six_percentage}%"
    next_biometric_time_str = None
    if sixintime and sixintime[0] :
        next_biometric_time = datetime.strptime(sixintime[0], "%H:%M") + timedelta(hours=6)
        next_biometric_time_str = next_biometric_time.strftime("%H:%M")
        #biometric_msg += f"\nBiometric should be kept again at: {next_biometric_time_str}"
    if next_biometric_time_str==None:
        biometric_msg = f"""
    ```Biometric
⫷

● Total Days             -  {total_days}
                
● Days Present           -  {days_present}  
            
● Days Absent            -  {days_absent}
                
● Biometric %            -  {biometric_percentage}  
            
● Biometric % (6h gap)   -  {six_percentage}

⫸

@iare_unofficial_bot
    ```
    """
    else:
        biometric_msg = f"""
    ```Biometric
⫷

● Total Days             -  {total_days}
                
● Days Present           -  {days_present}  
            
● Days Absent            -  {days_absent}
                
● Biometric %            -  {biometric_percentage}  
            
● Biometric % (6h gap)   -  {six_percentage}

● Evening Biometric Time  -  {next_biometric_time_str}

⫸

@iare_unofficial_bot
    ```
    """
    await bot.send_message(chat_id,text=biometric_msg)

@bot.on_message(filters.command(commands=['bunk']))
async def bunk(bot,message):
    chat_id = message.chat.id
    session_data = await load_user_session(chat_id)
    if not session_data:
        await message.reply("Please log in using the /login command.")
        return

    # Access the attendance page and retrieve the content
    attendance_url = 'https://samvidha.iare.ac.in/home?action=stud_att_STD'
    
    with requests.Session() as s:
        # Set the session cookies and headers
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        headers = session_data['headers']
        await update_activity_timestamp(chat_id)
        # Send GET request to the attendance or bunk page
        attendance_response = s.get(attendance_url)

    # Parse the HTML content using BeautifulSoup
    data = BeautifulSoup(attendance_response.text, 'html.parser')
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in attendance_response.text:
        await logout_user(bot,chat_id)
        return
    # Find the table element
    table_all = data.find_all('table', class_='table table-striped table-bordered table-hover table-head-fixed responsive')
    if len(table_all) > 1:
        # Process the second table data or perform any desired operations
        req_table = table_all[1]
        # Initialize an empty list to store the table data
        table_data = []
        # Find all table rows (tr elements) within the table body (tbody)
        rows = req_table.tbody.find_all('tr')
        # Iterate over the rows and extract the text content from each cell
        for row in rows:
            # Find all table cells (td elements) within the row
            cells = row.find_all('td')

            # Extract the text content from each cell and store it in a list
            row_data = [cell.get_text(strip=True) for cell in cells]

            # Add the row data to the main table data list
            table_data.append(row_data)

        # Prepare individual messages for each course
        for row in table_data[0:]:
            course_name = row[2]
            attendance_percentage = row[7]
            if course_name and attendance_percentage:
                # Calculate the maximum number of classes that can be bunked
                attendance_present = float(attendance_percentage)
                attendance_threshold = 75
                total_classes = int(row[5])
                attended_classes = int(row[6])
                attendance_status = row[8]
                classes_bunked = 0
                
                if attendance_present >= attendance_threshold:
                    classes_bunked = 0
                    while (attended_classes / (total_classes + classes_bunked)) * 100 >= attendance_threshold:
                        classes_bunked += 1
                    # bunk_can_msg = f"{course_name}: {attendance_percentage}% (Can bunk {classes_bunked} classes)"
                    #await bot.send_message(chat_id,bunk_can_msg)
                    bunk_can_msg = f"""
```{course_name}
⫷

● Attendance  -  {attendance_percentage}

● You can bunk {classes_bunked} classes

⫸

```
"""
                    await bot.send_message(chat_id,bunk_can_msg)
                  
                    
                else:
                    classes_needattend = 0
                    while((attended_classes + classes_needattend) / (total_classes + classes_needattend)) * 100 < attendance_threshold:
                        classes_needattend += 1
                    # bunk_cannot_msg = f"{course_name}:Attendance below 75%"
                    # bunk_recover_msg = f"{course_name}: Attend {classes_needattend} classes for 75%"
                    # await bot.send_message(chat_id,bunk_cannot_msg)
                    
                    bunk_recover_msg = f"""
```{course_name}
⫷

● Attendance  -  Below 75%

● Attend  {classes_needattend} classes for 75%

● No Bunk Allowed

⫸

```
"""
                    await bot.send_message(chat_id,bunk_recover_msg)
              
    else:
        await message.reply("Data not found.")

async def generate_unique_id():
    """
    Generate a unique identifier using UUID version 4.

    Returns:
        str: A string representation of the UUID.
    """
    return str(uuid.uuid4())

@bot.on_message(filters.command(commands=['request']))
async def request(bot,message):
    chat_id = message.from_user.id

    # Check if the user is logged in
    # if not is_user_logged_in(user_id):
    if not await load_user_session(chat_id):
        await message.reply("Please log in using the /login command.")
        return

    # Get the user's request message
    user_request = " ".join(message.text.split()[1:])

    getuname = await load_username(chat_id)
    # Get the user's username
    username = getuname[3]
    # Get the user's unique ID
    user_unique_id = await generate_unique_id()

    # Store the request in the data structure
    await store_requests(user_unique_id,username,user_request,chat_id)

    # Forward the user's request to the bot developer (you)
    forwarded_message = f"New User Request from @{username} (ID: {user_unique_id}):\n\n{user_request}"
    await bot.send_message(BOT_DEVELOPER_CHAT_ID,text=forwarded_message)

    # Send a confirmation message to the user
    await bot.send_message(chat_id,"Thank you for your request! Your message has been forwarded to the developer.")


@bot.on_message(filters.command(commands=['reply']))
async def reply_to_user(_,message):
    # Check if the user is authorized to use the /reply command
    if message.chat.id != BOT_DEVELOPER_CHAT_ID and message.chat.id != BOT_MAINTAINER_CHAT_ID:
        return
    # Check if the message is a reply to another message
    if not message.reply_to_message:
        await message.reply("Please reply to a user's request to send a reply.")
        return

    # Check if the replied message contains the unique ID in the text
    reply_text = message.reply_to_message.text
    unique_id_keyword = "ID: "
    if unique_id_keyword not in reply_text:
        await message.reply("The replied message does not contain the unique ID.")
        return

    # Get the unique ID from the replied message
    unique_id_start_index = reply_text.find(unique_id_keyword) + len(unique_id_keyword)
    unique_id_end_index = reply_text.find(")", unique_id_start_index)
    request_id = reply_text[unique_id_start_index:unique_id_end_index].strip()
    pending_requests = await load_requests(request_id)
    # Check if the extracted unique ID is valid
    if request_id not in pending_requests:
        await message.reply("Invalid or unknown unique ID.")
        return


    # Get the user's chat ID and username from the request data
    user_chat_id = pending_requests[3]
    # Get the developer's reply message
    developer_reply = message.text.split("/reply", 1)[1].strip()

    # Compose the final reply message
    reply_message = f"{developer_reply}\n\nThis is a reply from the bot developer."

    try:
        # Send the reply message to the user using their chat ID directly
        await bot.send_message(chat_id=user_chat_id, text=reply_message)

        # Notify the developer that the message has been sent successfully
        developer_chat_id = message.chat.id
        await bot.send_message(chat_id=developer_chat_id, text="Message sent successfully.")

        # Remove the used request data to prevent using the same ID again
        await delete_request(request_id)
    except Exception as e:
        # Notify the developer if there was an error sending the message
        error_message = f"An error occurred while sending the message to the user: {e}"
        await bot.send_message(chat_id=developer_chat_id, text=error_message)

@bot.on_message(filters.command(commands=['rshow']))
async def rshow(bot,message):
    chat_id = message.from_user.id
    requests = await load_allrequests()
    if message.chat.id != BOT_DEVELOPER_CHAT_ID and message.chat.id != BOT_MAINTAINER_CHAT_ID:
        await bot.send_message(chat_id,text="You are not authorized to use this command.")
        return

    if len(requests) == 0:
        await bot.send_message(chat_id,text="There are no pending requests.")
        return
    for request in requests:
        unique_id, user_id, message, chat_id = request
        request_message = f"New User Request from user ID {user_id} (Unique ID: {unique_id}):\n\n{message}"
        await bot.send_message(BOT_DEVELOPER_CHAT_ID, text=request_message)

@bot.on_message(filters.command(commands=['lusers']))
async def list_users(bot,message):
    if message.from_user.id == BOT_DEVELOPER_CHAT_ID or message.chat.id==BOT_MAINTAINER_CHAT_ID:
        with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users")
            usernames = [row[0] for row in cursor.fetchall()]
            
            # Create a single string with usernames separated by semicolons
            users_list = ";".join(usernames)
            qr_code = pyqrcode.create(users_list)
            qr_image_path = "list_users_qr.png"
            qr_code.png(qr_image_path, scale=5)
            await bot.send_photo(message.chat.id, photo=open(qr_image_path, 'rb'))
            # await message.answer(users_list)
            os.remove(qr_image_path)

@bot.on_message(filters.command(commands=['tusers']))
async def total_users(_,message):
    if message.from_user.id == BOT_DEVELOPER_CHAT_ID or message.chat.id==BOT_MAINTAINER_CHAT_ID:
        with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total_count = cursor.fetchone()[0]
            await bot.send_message(message.chat.id,f"Total users: {total_count}")

@bot.on_message(filters.command(commands=['rclear']))
async def clean_pending_requests(bot,message):
    if message.chat.id == BOT_DEVELOPER_CHAT_ID or message.chat.id == BOT_MAINTAINER_CHAT_ID:
        await clear_requests()
        await bot.send_message(BOT_DEVELOPER_CHAT_ID,"Emptied the requests successfully")

@bot.on_message(filters.command(commands=['help']))
async def help_command(bot,message):
    """
    Handler function for the /help command.
    Provides information about the available commands.
    """
    chat_id = message.chat.id
    help_msg = """Available commands:

    /login username password - Log in with your credentials.

    /attendance - View your attendance details.

    /biometric - View your biometric details.

    /bunk - View the number of classes you can bunk.

    /logout - Log out from the current session.

    /request {your request} - Send a request to the bot devoloper.

    Note: Replace {username}, {password}, and {your request} with actual values.
    """
    help_dmsg = """Available commands:

    /login {username} {password} - Log in with your credentials.

    /attendance - View your attendance details.

    /biometric - View your biometric details.

    /bunk - View the number of classes you can bunk.

    /logout - Log out from the current session.
    
    /request {your request} - Send a request to the bot Developer.

    /reply {your reply} - Send a reply to the request by replying to it.

    /rshow - Show the requests.

    /rclear - Clear the requests.

    /lusers - Show the list of users.

    /tusers - Show the total number of users

    /reset - Reset the Database

    Note: Replace {username}, {password}, {your request} and {your reply} with actual values.
    """
    if chat_id==BOT_DEVELOPER_CHAT_ID or chat_id==BOT_MAINTAINER_CHAT_ID:
        await bot.send_message(chat_id,text=help_dmsg)
    else:
        await bot.send_message(chat_id,text=help_msg)

# Logout user and send a message
async def logout_user(bot,chat_id):
    """
    Log out the user and send a message.

    Parameters:
        chat_id (int): The chat ID of the user.
    """
    session_data = await load_user_session(chat_id)
    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        return

    # Remove the session data from the database and the in-memory dictionary
    await delete_user_session(chat_id)

    # Notify the user that they have been logged out due to inactivity
    await bot.send_message(chat_id, text="Your session has been logged out due to inactivity.")

# Check inactivity
async def check_inactivity():
    # Get the Indian timezone
    indian_timezone = timezone('Asia/Kolkata')

    # Get the current time in the Indian timezone
    now = await get_indian_time()

    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id, last_activity FROM sessions")
        results = cursor.fetchall()
        for chat_id, last_activity in results:
            # Remove the additional precision (fractions of seconds) before parsing
            last_activity = last_activity.split('.', 1)[0]

            # Convert the last_activity from string to datetime and localize it to the Indian timezone
            last_activity = indian_timezone.localize(datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S'))

            if now - last_activity > timedelta(minutes=10):
                print("Logging out")
                # Log out the user and send a message
                await logout_user(bot,chat_id)
    # Reschedule the check after 1 minute
    await asyncio.sleep(60)
    await check_inactivity()

# Update activity timestamp
async def update_activity_timestamp(chat_id):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE sessions SET last_activity=? WHERE chat_id=?", (await get_indian_time(), chat_id))
        conn.commit()    


async def main():
    await create_tables()
    await create_total_users_table()
    # Start the inactivity check loop
    while True:
        # await asyncio.sleep()  # Sleep for 60 seconds
        await check_inactivity()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    bot.run()
