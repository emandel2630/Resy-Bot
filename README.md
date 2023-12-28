# Resy Table Reservation Automation

## Overview
This script automates the process of making table reservations through the Resy platform. It allows users to specify their reservation details such as date, time, and party size, and handles the login, table finding, and booking process programmatically using Resy's API.

## Features
- **Automated Login:** Securely logs into the user's Resy account.
- **Dynamic Table Search:** Finds available tables based on user preferences like date, party size, and specific times.
- **Intelligent Booking:** Automatically books the best table according to the given criteria.
- **Address to Venue Conversion:** Uses geolocation to convert a physical address to a Resy venue ID.
- **Customizable Time Range:** Users can specify the earliest and latest times they're willing to book a table.
- **Configurable:** Users can set up their credentials and reservation preferences in a configuration file.

## Technologies Used
- Python: The entire script is written in Python.
- Requests: Used for making HTTP requests to the Resy API.
- Geopy: Utilized for geocoding addresses to latitude and longitude.
- CSV and OS modules for logging and file management.

## How to Use
1. **Set Up Configuration:**
   - Edit the `requests.config` file with your details including Resy username and password, desired reservation address, date, time, and party size.
   
2. **Running the Script:**
   - Execute the script using Python. Ensure all dependencies are installed.
   - The script will log in to Resy, convert the address to a venue, find an available table, and make the reservation.

## Dependencies
- Python 3.x
- `requests` library
- `geopy` library

## Disclaimer
This script is for educational purposes only. Ensure you have the right to automate interactions with your Resy account and understand the terms of service for Resy and any associated platforms or APIs.


The date format is mm/dd/YYYY
Enter times in military time

The config file titled requests.config is in this form:

Username|:
Password|:
Address|:
Date|:
Desired Seating Time|:
Earliest Acceptable Seating Time|:
Latest Acceptable Seating Time|:
Guests|:
