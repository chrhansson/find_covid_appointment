# find_covid_appointment
Script that continuously checks the booking sites of many clinics and prints to console when an appointment slot is available (for Swedish clinics).

## Requirements
- HTMLSession
- tkinter

## What is this stuff?
The idea is to give users a shortcut to booking their Covid-19 vaccin appointment by automatically checking the booking sites for available appointments. The script does not cover every site, so make sure to check other options too, such as 1177 and kry. Note that no alert is built in yet, and available slots go fast, so you need to keep a close eye on the console! When an appointment is available you usually have less than 10 minutes to act, else the slot will be booked by someone else.

## What does it do?
This scripts scrapes data from the site bokning.mittvaccin.se, which is used by many clinics in Sweden. Every 91 seconds (default value, can be changed), the booking sites are pinged and check for available appointments. If any available appointment is found, then the URL to the booking site is posted along with the date + time of the available appointment, to simplify booking.

## How it works
There are three steps:
1. **Find local clinics (`find_local_clinics()`):** Each clinic as a number in the range 0 to 3000 (approximate, I haven't found the exact end of the range). The clinic is queried and the resulting JSON data is scanned to check if the cities/towns specified on line 37 match. Since it takes a while to process all 3000 clinics, it is recommended to only do this once and then store the resulting list of clinic IDs as a global variable `LOCAL_CLINICS` at the top of the file.
2. **Check if clincs offer Covid/vaccine related appointments (`check_covid_appt(clinics)`):**  For each clinic listed in clinics (suggestion: use the list stored in `LOCAL_CLINICS`), check if the clinic has covid-related appointments. I did this by checking if the phrases "covid" and "vaccin" are found on the page. Note that this sometimes returns bullshit, for example if you have a clinic with "Covid Antikropstest" and "TBE vaccin", the clinic will be returned although there is no covid 19 vaccin available. It is therefore recommended to do a manual check of the clinic ID by going to https://bokning.mittvaccin.se/klinik/CLINIC_ID. Store these clinics in the global variable `ACTUAL_COVID_CLINICS`.
4. **Store appointmentID for each clinic ID:** Every clinic uses a different appointment ID for covid-19 vaccination. For example, maybe clinic 1337 uses ID 10000 for covid 19 vaccination appointments, but clinic 1448 uses ID 12000. Therefore we need to store this correlation in the global dictionary `APP_ID`, so we can look up e.g. `APP_ID['1337']` to return `'10000'`. The appointmend ID can be found on the booking page of each clinic by checking the JSON query response in the browser inspector. Go to Network > Update > open one of the JSON requests > go to the tab Response > here you should find the correct ID that the clinic uses for covid 19 vaccination.
5. **Find available appointment for covid vaccination (`check_availability(clinics, start_date, end_date)`):** This is the final step. For each clinic which has covid appointments, query the vaccination appointment for available slots in the calendar. If `'availability': true` for any appointment, then store the date and time of that calendar. Remember to set `START_DATE`, `END_DATE` at the top accordingly. The dates are inclusive, so `START_DATE=211231`, `END_DATE=211231` will return appointments on 2021-12-31. It seems like some calendars only are updated a certain number of days ahead, so if you put too big of a time range it might break.

The script might run into errors if the API server is queried too often from the same IP (not sure about this, but it's a theory). To prevent the script from breaking, there is a try-except clause that will keep the script running if this happens.
