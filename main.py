"""
telegram weather bot by Mezentsev Roman
"""
from __future__ import absolute_import
import os
from datetime import datetime
import time
from threading import Thread
import re
import logging
import telebot

# from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import psycopg2
from apscheduler.schedulers.blocking import BlockingScheduler
import pytz

### Start Credentials block ###
pdbn = os.environ.get("PDB")
user = os.environ.get("POSTGRES_USER")
password = os.environ.get("PPWD")
host = os.environ.get("POSTGRES_HOST")
port = os.environ.get("PGPORT")
params = (
    "dbname="
    + pdbn
    + " host="
    + host
    + " user="
    + user
    + " password="
    + password
    + " port="
    + port
)
token = os.environ.get("bottoken")
bot = telebot.TeleBot(token)

## vars
timezone = pytz.timezone("Europe/Istanbul")
DBCHECK_INTERVAL = 50

emoji = {
    "0": "Clear \u2600\ufe0f",
    "1": "Mainly clear \U0001f324\ufe0f",
    "2": "Partly cloudy \u26c5\ufe0f",
    "3": "overcast \u2601\ufe0f",
    "45": "Fog \U0001f32b",
    "48": "Depositing rime fog \U0001f32b",
    "51": "Drizzle: Light \U0001f327\ufe0f",
    "52": "Drizzle: moderate \U0001f327\ufe0f",
    "53": "Drizzle: dense intensity \U0001f327\ufe0f",
    "56": "Freezing Drizzle: Light \U0001f327\ufe0f",
    "57": "Freezing Drizzle: dense intensity \U0001f327\ufe0f",
    "61": "Rain: Slight \U0001f327\ufe0f",
    "63": "Rain: moderate \U0001f327\ufe0f",
    "65": "Rain: heavy intensity \U0001f327\ufe0f",
    "66": "Freezing Rain: Light \U0001f327\ufe0f",
    "67": "Freezing Rain: heavy intensity \U0001f327\ufe0f",
    "71": "Snow fall: Slight \U0001f328\ufe0f",
    "73": "Snow fall: moderate \U0001f328\ufe0f",
    "75": "Snow fall: heavy intensity \U0001f328\ufe0f",
    "77": "Snow grains \U0001f328\ufe0f",
    "80": "Rain showers: Sligh \U0001f327\ufe0f",
    "81": "Rain showers: moderate \U0001f327\ufe0f",
    "82": "Rain showers: violent \U0001f327\ufe0f",
    "85": "Snow showers slight \U0001f328\ufe0f",
    "86": "Snow showers heavy \U0001f328\ufe0f",
    "95": "Thunderstorm \U0001f300\ufe0f",
    "96": "Thunderstorm with slight and heavy hail \U0001f300\ufe0f",
    "99": "Thunderstorm with slight and heavy hail \U0001f300\ufe0f",
}


### End Credentials block ###

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


conn = psycopg2.connect(params)
cur = conn.cursor()

while True:
    try:
        cur.execute('SELECT * FROM information_schema.tables limit 1')
        testcont=cur.fetchone()
        if testcont[1] == 'pg_catalog' or testcont[1] == 'public':
            break
    except Exception as er:
        print(er)

    
### Start Initial Block ###
def create_table():
    """Creating 3 tables if they are not exist"""
    commands = (
        """CREATE TABLE if NOT EXISTS users (
                user_id int NOT null UNIQUE,
                user_first_name VARCHAR(255) NOT NULL,
                user_last_name VARCHAR(255) NOT NULL,
                nickname VARCHAR(255) NOT null)""",
        """create table if not exists  auto_send (
                   id serial PRIMARY KEY,
                   send_message_enabled bool not NULL,
                   user_id integer references users(user_id) unique not NULL,
                   send_time time not NULL,
                   city varchar(255) not NULL)""",
        """CREATE TABLE if NOT exists messages(
                user_id integer references users(user_id),
	            user_message_id VARCHAR(255) NOT NULL,
	            chat_type VARCHAR(255) NOT NULL,
	            date DATE NOT NULL,
	            city VARCHAR(255) NOT NULL);""",
    )
    conn = None
    try:
        conn = psycopg2.connect(params)
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error, error.pgerror, error.diag.message_detail)

    finally:
        if conn is not None:
            conn.commit()
            conn.close()

create_table()

### END Initial Block ###

### Start Functions Block ###
def addtodb(
    mes_chatid,
    mes_firstusname,
    mes_uslastname,
    mes_usnickname,
    mes_id,
    mes_chattype,
    mes_date,
    mes_text,
):
    """Function for adding user info into DB"""
    try:
        conn = psycopg2.connect(params)
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO users (user_id,user_first_name,user_last_name,nickname) \
                VALUES ({mes_chatid},'{mes_firstusname}','{mes_uslastname}','{mes_usnickname}') \
                on conflict (user_id) DO nothing".format(
                int(mes_chatid), mes_firstusname, mes_uslastname, mes_usnickname
            )
        )
        cur.execute(
            f"INSERT INTO messages (user_id,user_message_id,chat_type,date,city) \
                VALUES ({mes_chatid},{mes_id},'{mes_chattype}','{mes_date}','{mes_text}')".format(
                int(mes_chatid), mes_id, mes_chattype, mes_date, mes_text
            )
        )
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print(error.pgcode)
        print(error.pgerror)
        print(error.diag.message_detail)

    finally:
        if conn is not None:
            cur.close()
            conn.close()


def enablesending(switch, time, city, user_id):
    """Function for adding time and status for auto_send into DB"""
    conn = None
    try:
        conn = psycopg2.connect(params)
        cur = conn.cursor()
        cur.execute(
            f"""INSERT INTO auto_send (send_message_enabled,send_time,city,user_id) \
                VALUES ({switch},'{time}','{city}', {user_id}) \
                        on conflict (user_id) \
                        DO update set send_time=excluded.send_time, city=excluded.city, \
                        send_message_enabled=excluded.send_message_enabled""".format(
                {switch}, {time}, {city}, {user_id}
            )
        )
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


### Scheduler block
def run_scheduled_task():
    """Function for checking DB and sending message"""
    conn = None
    try:
        conn = psycopg2.connect(params)
        cur = conn.cursor()
        cur.execute(
            """select * from auto_send
                        join users on (auto_send.user_id = users.user_id )"""
        )
        status_data = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    time_inzone = datetime.now(timezone)
    current_time = time_inzone.strftime("%H:%M")
    for row in status_data:
        if row[1] is False:
            continue
        if row[1] is True and row[3].strftime("%H:%M") == current_time:

            class message:
                """Class for generating message object"""

                def __init__(self, city, idm, mdate):
                    # Class Variable
                    self.text = city
                    self.id = idm
                    self.date = mdate

            class chat(message):
                """Subclass for message"""

                def __init__(self, chatid, chtype):
                    self.id = chatid
                    self.type = chtype

            class from_user(message):
                """Subclass for message"""

                def __init__(self, frname, lstname, usrname):
                    self.first_name = frname
                    self.last_name = lstname
                    self.username = usrname

            message = message(
                row[4], row[0], time.mktime(datetime.now(timezone).timetuple())
            )
            message.chat = chat(row[2], "Private")
            message.from_user = from_user(row[6], row[7], row[8])

            get_weather(message)


scheduler = BlockingScheduler(
    timezone="Europe/Istanbul"
)  # You need to add a timezone, otherwise it will give you a warning
scheduler.add_job(
    run_scheduled_task, "interval", seconds=DBCHECK_INTERVAL
)  # Runs every 50 seconds


def schedule_checker():
    """Function for starting scheduler"""
    while True:
        scheduler.start()


### END Functions Block ###

### Start main BOT Block ###


@bot.message_handler(commands=["start"])
def start(message):
    """
    function for starting
    """
    bot.send_message(
        message.chat.id,
        "Hello! \nI can show you the weather today in any city and send planned notification.\nPlease send me the name of the city.\nSend 'help' for showing commands",
    )


@bot.message_handler(commands=["status"])
def status(message):
    """
    function for checking status of auto_send
    """
    conn = None
    try:
        conn = psycopg2.connect(params)
        cur = conn.cursor()
        cur.execute(
            f"""SELECT * FROM auto_send WHERE user_id ={message.chat.id}""".format(
                {message.chat.id}
            )
        )
        user_status = cur.fetchone()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    send_enabled = "Enabled" if user_status[1] == True else "Disabled"
    usr_id = user_status[2]
    set_time = user_status[3].strftime("%H:%M")
    set_city = user_status[4]

    bot.send_message(
        message.chat.id,
        f"Auto send status:\nStatus:{send_enabled},\ntime: {set_time},\
        \ncity: {set_city} \nchat_id: {usr_id}",
    )


@bot.message_handler(commands=["auto"])
def auto_send(message):
    """
    function for configuring auto_send
    """
    bot.send_message(
        message.chat.id,
        "Please send text in format for auto notification. \nFor enabling: 'yes 08:00 Paris' \nFor disabling: 'no' ",
    )

    bot.register_next_step_handler(message, get_switch)


def get_switch(message):
    """Function for reciveing meassage, for enabling auto_send"""
    message_str = message.text
    check_string = re.search("yes|no|Yes|No", message_str)
    if check_string is not None:
        switch_status = message_str[0:3]
        switch_status = switch_status.lower()
        switch_status = re.findall("no|yes", switch_status)
        switch_status = str(switch_status[0])
        if switch_status == "yes":
            switch_status = "True"
            time = str(message_str[4:9])
            city = str(message_str[10:])
            enablesending(switch_status, time, city, message.chat.id)
            bot.send_message(
                message.chat.id,
                f"Auto send is enabled: {switch_status},\n time: {time}, \n city: {city}",
            )
        elif switch_status == "no":
            switch_status = "False"
            time = "00:00"
            city = "None"
            enablesending(switch_status, time, city, message.chat.id)
            bot.send_message(
                message.chat.id,
                f"Auto send is enabled: {switch_status},\n time: {time}, \n city: {city}",
            )
    else:
        bot.send_message(message.chat.id, "Sorry didn't get you")


@bot.message_handler(content_types=["text"])
def get_weather(message):
    """
    func for get weather and sending it to user
    """
    if re.match("help|Help",str(message.text)):
        bot.reply_to(message,"/status - show details about planned notification\n/auto - activate auto notification configuration dialogue\n")

    elif re.match("Glory to Ukraine|Slava Ukraine|glory to ukraine|slava ukraine|Слава Украине|слава украине",str(message.text)):
        bot.reply_to(message,"Героям Слава!\U0001f1fa\U0001f1e6\nGlory to the Heroes!\U0001f1fa\U0001f1e6")

    else:
        ### Emoji block for weather status
        try:
            ### Retrieving city information from API according user text
            req_city = requests.get(
                f"https://geocoding-api.open-meteo.com/v1/search?name={message.text}"
            )
            data_city = req_city.json()
            latitude = data_city["results"][0]["latitude"]
            longitude = data_city["results"][0]["longitude"]
            timezone = data_city["results"][0]["timezone"]
            country = data_city["results"][0]["country"]

            ### Parsing current time from user's message
            date = datetime.fromtimestamp(int(message.date))
            date_hour = int(date.hour)  # get current hour

            ### Retrieving weather information from API according retrieved city info
            url_string = (
                "https://api.open-meteo.com/v1/forecast?latitude="
                + str(latitude)
                + "&longitude="
                + str(longitude)
                + "&hourly=temperature_2m,apparent_temperature,weathercode,surface_pressure,relativehumidity_2m&daily=weathercode,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,windspeed_10m_max&current_weather=true&timezone="
                + timezone
            )
            req = requests.get(url_string)
            data = req.json()
            city = message.text

            # Parsing Current weather  info
            cur_weather = str(data["current_weather"]["temperature"])
            cur_wind = data["current_weather"]["windspeed"]
            cur_weather_emoji = str(data["current_weather"]["weathercode"])
            cur_weath_e = emoji.get(str(cur_weather_emoji), "\U0001f50d\ufe0f")

            # daily
            day_weather_code = str(data["daily"]["weathercode"][0])
            day_wheater_min = data["daily"]["temperature_2m_min"][0]
            day_wheater_max = data["daily"]["temperature_2m_max"][0]
            day_feels_like_min = data["daily"]["apparent_temperature_min"][0]
            day_feels_like_max = data["daily"]["apparent_temperature_max"][0]
            sunrise = (str(data["daily"]["sunrise"][0]))[-5:]
            sunset = (str(data["daily"]["sunset"][0]))[-5:]
            day_windspeed_max = data["daily"]["windspeed_10m_max"][0]
            day_weath_e = emoji.get(str(day_weather_code), "\U0001f50d\ufe0f")

            # hourly wetaher
            hourly_weather_code = str(data["hourly"]["weathercode"][date_hour])
            hourly_weather = data["hourly"]["temperature_2m"][date_hour]
            hourly_feels_like = data["hourly"]["apparent_temperature"][date_hour]
            hourly_pressure = round(
                (int(data["hourly"]["surface_pressure"][date_hour]) * 0.760061), 1
            )
            hourly_humidity = data["hourly"]["relativehumidity_2m"][date_hour]
            hourly_time = (str(data["hourly"]["time"][date_hour]))[-5:]

            hour_weath_e = emoji.get(str(hourly_weather_code), "\U0001f50d\ufe0f")

            addtodb(
                message.chat.id,
                message.from_user.first_name,
                message.from_user.last_name,
                message.from_user.username,
                message.id,
                message.chat.type,
                date,
                message.text,
            )

            bot.send_message(
                message.chat.id,
                f"Current  weather in {city}/{country}\nCurrent temperature: {cur_weather} C° {cur_weath_e}\n"
                f"Wind speed: {cur_wind} m/s\n\n"
                f"Daily weather\nTemperature: from {day_wheater_min} C° to {day_wheater_max} C°, {day_weath_e}\n"
                f"Feels like: from {day_feels_like_min} C° to {day_feels_like_max} C°,\nWind speed: {day_windspeed_max} m/s\n"
                f"Sunrise/Sunset - {sunrise}/{sunset}\n\n"
                f"Hourly weather: {hourly_time}\nTemperature: {hourly_weather} C° {hour_weath_e}\nFeels like: {hourly_feels_like} C°\nPressure: {hourly_pressure} mm/Hg\n"
                f"Humidity: {hourly_humidity} %",
            )
        except Exception:
            bot.send_message(message.chat.id, "I can't find this city. Try again.")




Thread(target=schedule_checker).start()
# bot.polling(non_stop=True, interval=0)
bot.infinity_polling()
