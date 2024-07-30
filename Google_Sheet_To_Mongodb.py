import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
load_dotenv()



current_time = datetime.now()
yesterday_time = current_time - timedelta(days=1)
date_format = "%d/%m/%Y, %H:%M:%S"


key = os.getenv('key')

mongo_url = os.getenv('MONGO_URL')

cluster = MongoClient(mongo_url)
db = cluster['AEP']  
col = db['scheduler']


try:
    bangkok_timezone = pytz.timezone('Asia/Bangkok')
    timestamp = datetime.now(bangkok_timezone)
    date_format = "%d/%m/%Y, %H:%M:%S"
    # วันนี้ 8 โมง
    current_time = datetime.now().replace(hour=8, minute=0, second=0)
    # เมื่อวาน 9 โมง
    yesterday_time = current_time - timedelta(days=1)

    is_rain = False
    sec = 0

    myscope = ['https://spreadsheets.google.com/feeds', 
                'https://www.googleapis.com/auth/drive']
    mycred = ServiceAccountCredentials.from_json_keyfile_dict(key,myscope)

    client = gspread.authorize(mycred)

    mysheet = client.open("WeatherStation").get_worksheet(1)

    all_values = mysheet.get_all_values()
    for row in all_values:
        if row[0] != "" and row[0] != "Date":
            date_obj = datetime.strptime(row[0], date_format)
            print(date_obj)
            if yesterday_time <= date_obj and date_obj <= current_time:
                if row[5] != "0":
                    print("Is reain", row[5])
                    is_rain = True
                    break
                if row[6] != "":
                    sec = row[6]
                    print("work on", row[6])
                    break

    schedule_dicts = {
        "machine": "ESP32_1",
        "work_on_date": current_time.strftime("%Y-%m-%d"),
        "seconds_amount": sec,
        "is_rain": is_rain,
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S %Z%z"),
    }

    result = col.insert_one(schedule_dicts)

    if result.acknowledged:
        response = {'status': 200, 'message': f"Insertion successful. Document ID: {result.inserted_id}"}
    else:
        print("Insertion failed")
        response = {'status': 400, 'message': 'Insertion failed'}

    print(response)  # ในกรณีที่ไม่ใช่ฟังก์ชันที่คืนค่า

except Exception as e:
    response = {'status': 400, 'message': f"Error for: {str(e)}"}
    print(response)  # ในกรณีที่ไม่ใช่ฟังก์ชันที่คืนค่า
