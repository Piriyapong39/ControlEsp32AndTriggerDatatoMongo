import network
import requests
import machine
import time
import utime

# เชื่อมต่อ Wi-Fi
ssid = "Natutitato"
password = "30113011"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.scan()

def connect_wifi():
    try:
        wlan.connect(ssid, password)
        if wlan.isconnected():
            print("Connected to Wi-Fi")
            return True
        else:
            print("Failed to connect to Wi-Fi")
            return False
    except Exception as e:
        print("An error occurred:", str(e))
        return False

def retrieve_time_from_sheet(i):
    current_time = utime.localtime()
    if i == 10:
        utime.sleep(60)
        print("End Process")
        return 0
    elif connect_wifi():
        print("connect_wifi sucessfuly")
        url = "https://testherokuandflask-c171ccb2b87b.herokuapp.com/"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("Pump work for:",data["seconds_amount"], "Sec")
        else:
            print("Error from request API seconds_amount:", response.status_code)
        return retrieve_time_from_sheet(10)
    else:
        print("Wi-Fi connection fail")
        # ทำงานตามค่าเริ่มต้นหรือค่าที่ต้องการเมื่อการเชื่อมต่อ Wi-Fi ไม่สำเร็จ
        return 0

def weather_station_work_on(i):
    current_time = utime.localtime()
    if i == 10:
        utime.sleep(60)
        print("End Process")
        return 0
    
    # กำหนดขา Relay
    relay_pin1 = machine.Pin(25, machine.Pin.OUT)
    
    # ลองเชื่อมต่อ Wi-Fi
    if connect_wifi():
        print("connect_wifi successfully")
        url = "https://testherokuandflask-c171ccb2b87b.herokuapp.com/"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json() 
            print("Relay")
            print("sec:", data["seconds_amount"])
            
            # ปิด Relay
            relay_pin1.off()
            time.sleep(float(data["seconds_amount"]))
            
            # เปิด Relay อีกครั้ง
            relay_pin1.on()
            
        else:
            print("Error from request API weather_station_work_on:", response.status_code)
            print("Relay on for 150 seconds")
            
            # ปิด Relay ตามค่า default 150 วินาที
            relay_pin1.off()
            time.sleep(150)
            relay_pin1.on()        
        
    else:
        print("Failed to connect WiFi")
        print("Relay on for 150 seconds")
        
        # ปิด Relay ตามค่า default 150 วินาที เมื่อไม่สามารถเชื่อมต่อ WiFi ได้
        relay_pin1.off()
        time.sleep(150)
        relay_pin1.on()
        
while True:
    current_time = utime.localtime()
    relay_pin1 = machine.Pin(25, machine.Pin.OUT)
    relay_pin1.on()
    
    if current_time[3] == 09 and current_time[4] == 00 :
        print("WORK retrieve_time_from_sheet")
        retrieve_time_from_sheet(0)
    if current_time[3] == 09 and current_time[4] == 05 :
        print("WORK weather_station_work_on")
        weather_station_work_on(0)
    
    utime.sleep(10)


