# find_covid_appointment
Script that continuously checks the booking sites of many clinics and prints to console when an appointment slot is available (for Swedish clinics).

## Requirements
- HTMLSession
- tkinter

## What is this stuff?
The idea is to give users a shortcut to booking their Covid-19 vaccin appointment by automatically checking the [booking sites](https://bokning.mittvaccin.se/klinik/0) for available appointments. The script does not cover every single site out there so make sure to check other options too, such as 1177 and kry. Note that no alert is built in yet, and available slots go fast, so you need to keep a close eye on the console! When an appointment is available you usually have less than 10 minutes to act, else the slot will be booked by someone else.

## What does it do?
This scripts scrapes data from the [booking site API](https://booking-api.mittvaccin.se/clinique/0), which is used by many clinics in Sweden. Every 91 seconds (default value, can be changed), the booking sites are pinged and check for available appointments. If any available appointment is found, then the URL to the booking site is posted along with the date + time of the available appointment, to simplify booking.

## How it works
There are three steps:
1. **Find local clinics (`find_local_clinics()`):** Iterates through the list of clinics listed on the top page of the API. Some clinics are not used (labelled as 'ANVÄNDS EJ'), so these are ignored. The rest are checked against the list of `CITIES` stored at the top of the file. If any clinic has a city matching any city in the list, it is stored for the next step. Since it takes a while to process all 800+ clinics, it is recommended to only do this once and then store the resulting list of clinic IDs as a global variable `LOCAL_CLINICS` at the top of the file.
2. **Check if clincs offer Covid/vaccine related appointments (`check_covid_appt(clinics)`):**  For each clinic listed in clinics (suggestion: use the list stored in `LOCAL_CLINICS`), check if the clinic has covid-related appointments. This is done by iterating over the appointments available at that clinic and checking if the phrases "covid" and "vaccin" are found in the name. It is recommended to do a manual check of the clinic ID by going to https://bokning.mittvaccin.se/klinik/CLINIC_ID and verifying that they infact do have Covid-19 vaccination (it should work, but just in case some other vaccin or other covid-related activity is caught). Store these clinics in the global variable `COVID_LOCAL_CLINICS`, which is a list of dictionaries of the following format:
`COVID_LOCAL_CLINICS = [{clinid_ID: CLINIC_ID, appt_ID: APPT_ID},...]`
Where APPT_ID is the ID for the specific covid vaccination type for that particular clinic.
3. **Find available appointment for covid vaccination (`check_availability(clinics, start_date, end_date)`):** This is the final step. For each clinic which has covid appointments, query the vaccination appointment for available slots in the calendar. If `'availability': true` for any appointment, then store the date and time of that calendar. Remember to set `START_DATE`, `END_DATE` at the top accordingly. The dates are inclusive, so `START_DATE=211231`, `END_DATE=211231` will return appointments on 2021-12-31. It seems like some calendars only are updated a certain number of days ahead, so if you put too big of a time range it might break.

The script then loops until it finds an available time. Note that the script might run into errors if the API server is queried too often from the same IP (not sure about this, but it's a theory). To prevent the script from breaking, there is a try-except clause that will keep the script running if this happens.

Happy hunting!
