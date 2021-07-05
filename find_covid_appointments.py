from requests_html import HTMLSession
import json
import time
import datetime
import tkinter
from tkinter import messagebox

TIME_BETWEEN_ATTEMPTS = 91  # in seconds 
TIME_AFTER_ERROR = 300  # in seconds
LOCAL_CLINICS = ['5', '14', '22', '75', '77', '152', '167', '229', '264', '1031', '2078', '2087', '2092']
COVID_LOCAL_CLINICS = ['75', '77', '167', '2078', '2087', '2092']
ACTUAL_COVID_CLINICS = ['2078', '2087', '2092']
MANUALLY_FOUND_CLINICS = ["2071"]
START_DATE = "210702"
END_DATE = "210716"
APP_ID = {"2078": "15432",
          "2087": "16006",
          "2092": "16321",
          "2071": "17625"}



def find_local_clinics():
    list_of_ids = []
    base_url = "https://booking-api.mittvaccin.se/clinique/"
    session = HTMLSession()

    for i in range(0, 3000):
        print(f"Checking clinic {i}")
        url = base_url + str(i)
        query_found = False

        r = session.get(url)
        try:
            r.html.render()
            if len(r.text) > 0:
                if '"city":"Göteborg"' in r.text or '"city":"Mölndal"' in r.text:
                    query_found = True

            if query_found:
                list_of_ids.append(str(i))
                print(f"Found clinic {i} in the area!")

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
        if "covid" in r.text.lower() and "vaccin" in r.text.lower():
            # if not "covid-19 antikroppstest" in r.text.lower() or "antikroppstest covid-19":
            list_of_covid_clinics.append(clinic)
            print(f"Found clinic {clinic} with covid appointments!")

    return list_of_covid_clinics

def check_availability(clinics, start_date, end_date):
    session = HTMLSession()
    available_times = []

    for clinic in clinics:
        url = f"https://booking-api.mittvaccin.se/clinique/{clinic}/appointments/{APP_ID[clinic]}/slots/{start_date}-{end_date}"
        r = session.get(url)
        r.html.render()
        if '"available":true' in r.text:
            jr = json.loads(r.text)
            for date_dict in jr:
                for slot in date_dict["slots"]:
                    if slot["available"]:
                        available_times.append({"clinic": clinic,
                                                "date": date_dict["date"],
                                                "time": slot["when"]})
    return available_times






def find_appt():
    #local_clinics = find_local_clinics()
    #print(f"Local clinics: {local_clinics}")
    # covid_clincs = check_covid_appt(LOCAL_CLINICS)
    # print(covid_clincs)
    available_times = []
    iterations = 0
    try:
        while not available_times:
            iterations += 1
            print(f"Attempt {iterations}", end=" ")
            available_times = check_availability(ACTUAL_COVID_CLINICS + MANUALLY_FOUND_CLINICS, START_DATE, END_DATE)
            if not available_times:
                print(f"No success. Waiting {TIME_BETWEEN_ATTEMPTS} seconds, then trying again.")
                time.sleep(TIME_BETWEEN_ATTEMPTS)
            if available_times:
                print(f"Success! Slot found at {datetime.datetime.now().ctime()}")
    except:
        time.sleep(TIME_AFTER_ERROR)
        print(f"Error encountered. Waiting for {TIME_AFTER_ERROR} seconds, then trying to reconnect.")
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
