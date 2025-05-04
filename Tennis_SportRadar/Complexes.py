import requests
import pymysql
import json
import pandas as pd

try:
    # 1. Fetch data from API
    url = "https://api.sportradar.com/tennis/trial/v3/en/complexes.json?api_key=rt0MyYde2deMs7Ozys2VUpjRtYj77KSATzLGpJZz"
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises HTTPError if status code != 200

    try:
        response_data = response.json()
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        response_data = {}

except requests.RequestException as e:
    print("API Request failed:", e)
    response_data = {}

# 2. Process data from API
complexes_list = []
venues_list = []

try:
    complexes_data = response_data.get("complexes", [])

    for complex_item in complexes_data:
        complex_id = complex_item.get('id')
        complex_name = complex_item.get('name')

        if complex_id and complex_name:
            complexes_list.append({
                "complex_id": complex_id,
                "complex_name": complex_name
            })

        venues = complex_item.get('venues', [])
        for venue in venues:
            venues_list.append({
                "venue_id": venue.get('id'),
                "venue_name": venue.get('name'),
                "city_name": venue.get('city_name', ''),
                "country_name": venue.get('country_name', ''),
                "country_code": venue.get('country_code', ''),
                "timezone": venue.get('timezone', ''),
                "complex_id": complex_id
            })

except Exception as e:
    print("Error while processing data:", e)

# 3. Connect to MySQL and Insert Data
try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Test@123',
        database='sportradar_tennis',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    with connection.cursor() as cursor:
        # Create complexes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complexes (
                complex_id VARCHAR(50) PRIMARY KEY,
                complex_name VARCHAR(100) NOT NULL
            )
        ''')

        # Create venues table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS venues (
                venue_id VARCHAR(50) PRIMARY KEY,
                venue_name VARCHAR(100) NOT NULL,
                city_name VARCHAR(100) NOT NULL,
                country_name VARCHAR(100) NOT NULL,
                country_code CHAR(3) NOT NULL,
                timezone VARCHAR(100) NOT NULL,
                complex_id VARCHAR(50),
                FOREIGN KEY (complex_id) REFERENCES complexes(complex_id)
            )
        ''')

        # Insert data into complexes table
        for item1 in complexes_list:
            try:
                cursor.execute('''
                    INSERT INTO complexes (complex_id, complex_name)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE
                        complex_name = VALUES(complex_name)
                ''', (
                    item1.get('complex_id'),
                    item1.get('complex_name')
                ))
            except Exception as e:
                print("Failed to insert into complexes:", e, item1)

        # Insert data into venues table
        for item in venues_list:
            try:
                cursor.execute('''
                    INSERT INTO venues (
                        venue_id, venue_name, city_name,
                        country_name, country_code, timezone, complex_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        venue_name = VALUES(venue_name),
                        city_name = VALUES(city_name),
                        country_name = VALUES(country_name),
                        country_code = VALUES(country_code),
                        timezone = VALUES(timezone),
                        complex_id = VALUES(complex_id)
                ''', (
                    item.get('venue_id'),
                    item.get('venue_name'),
                    item.get('city_name'),
                    item.get('country_name'),
                    item.get('country_code'),
                    item.get('timezone'),
                    item.get('complex_id')
                ))
            except Exception as e:
                print("Failed to insert into venues:", e, item)

        # Commit changes
        connection.commit()

except pymysql.MySQLError as e:
    print("MySQL error:", e)

except Exception as e:
    print("Unexpected error during DB operations:", e)

finally:
    try:
        connection.close()
        print("MySQL connection closed.")
    except:
        print("MySQL connection was not open or already closed.")

print("✅ Data saved to MySQL database successfully!")
