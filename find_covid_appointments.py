from requests_html import HTMLSession
import json
import time
import datetime
import tkinter
from tkinter import messagebox

CITIES = ["Göteborg", "Mölndal", "Partille"]
LOCAL_CLINICS = ['166', '75', '77', '167', '229', '5', '2087', '2078', '2092', '2094', '264', '1031', '14', '22', '152',
                 '2071']
COVID_LOCAL_CLINICS = [{'clinic_ID': '2087', 'appt_ID': '16006'},
                       {'clinic_ID': '2078', 'appt_ID': '15432'},
                       {'clinic_ID': '2092', 'appt_ID': '16321'},
                       {'clinic_ID': '2094', 'appt_ID': '16447'},
                       {'clinic_ID': '2071', 'appt_ID': '17625'}]

START_DATE = "210702"
END_DATE = "210716"


def find_local_clinics():
    list_of_ids = []
    base_url = "https://booking-api.mittvaccin.se/clinique/"
    session = HTMLSession()
    r = session.get(base_url)
    counter = 0
    try:
        r.html.render()
        json_response = json.loads(r.text)

        for clinic in json_response:
            counter += 1
            print(f"Checking clinic #{counter}")
            if "ANVÄNDS EJ" in clinic["name"]:
                continue
            city_found = False
            for city in CITIES:
                if clinic['city'] == city:
                    city_found = True

            if city_found:
                list_of_ids.append(clinic["id"])
                print(f"Found clinic {clinic['id']} in the area!")
    except:
        pass

    return list_of_ids


def check_covid_appt(clinics):
    session = HTMLSession()
    list_of_covid_clinics = []

    for clinic in clinics:
        url = f"https://booking-api.mittvaccin.se/clinique/{clinic}/appointmentTypes"
        r = session.get(url)
        r.html.render()
        json_response = json.loads(r.text)
        for appointment in json_response:
            if "covid" in appointment["name"].lower() and "vaccin" in appointment["name"].lower():
                list_of_covid_clinics.append({"clinic_ID": clinic,
                                              "appt_ID": appointment["id"]})

    return list_of_covid_clinics


def check_availability(clinics, start_date, end_date):
    session = HTMLSession()
    available_times = []

    for clinic in clinics:
        url = f"https://booking-api.mittvaccin.se/clinique/{clinic['clinic_ID']}/appointments/{clinic['appt_ID']}/slots/{start_date}-{end_date}"
        r = session.get(url)
        r.html.render()
        if '"available":true' in r.text:
            jr = json.loads(r.text)
            for date_dict in jr:
                for slot in date_dict["slots"]:
                    if slot["available"]:
                        available_times.append({"clinic": clinic['clinic_ID'],
                                                "date": date_dict["date"],
                                                "time": slot["when"]})
    return available_times


def find_appt(fast_search=True):
    if not fast_search:
        local_clinics = find_local_clinics()
        print(f"Local clinics: {local_clinics}")
        covid_clincs = check_covid_appt(local_clinics)
        print(covid_clincs)

    available_times = []
    iterations = 0
    try:
        while not available_times:
            iterations += 1
            print(f"Attempt {iterations}", end=" ")
            if fast_search:
                available_times = check_availability(COVID_LOCAL_CLINICS, START_DATE, END_DATE)
            else:
                available_times = check_availability(covid_clincs, START_DATE, END_DATE)
            if not available_times:
                print("No success. Waiting 91 seconds, then trying again.")
                time.sleep(91)
            if available_times:
                print(f"Success! Slot found at {datetime.datetime.now().ctime()}")
    except:
        time.sleep(300)
        find_appt()

    # This code is to hide the main tkinter window
    root = tkinter.Tk()
    root.withdraw()
    # Message Box
    print(available_times)
    if len(available_times) > 0:
        print(f"When: {available_times[0]['date']} at {available_times[0]['time']}. "
              f"Link: https://bokning.mittvaccin.se/klinik/{available_times[0]['clinic']}")
    messagebox.showinfo("Appointment Found!", "It's time to book! See console for when and where.")
    exit(0)


find_appt()
