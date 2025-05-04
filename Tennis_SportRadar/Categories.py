import requests
import pymysql
import json
import pandas as pd

try:
    # 1. Fetch data from API
    url = "https://api.sportradar.com/tennis/trial/v3/en/competitions.json?api_key=rt0MyYde2deMs7Ozys2VUpjRtYj77KSATzLGpJZz"
    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # raises HTTPError if not 200

    try:
        response_data = response.json()
        competitions_data = response_data.get("competitions", [])
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        competitions_data = []

except requests.RequestException as e:
    print("Error fetching API data:", e)
    competitions_data = []

# Initialize lists
comptetions_list = []
category_list = []

# 2. Extract data
try:
    for i in competitions_data:
        comptetions_list.append({
            "competition_id": i.get('id'),
            "competition_name": i.get('name'),
            "type": i.get("type"),
            "gender": i.get("gender"),
            "category_id": i.get('category', {}).get('id'),
            "parent_id": i.get("parent_id")  # may be None
        })

    for j in competitions_data:
        category_list.append({
            "category_id": j.get('category', {}).get('id'),
            "category_name": j.get('category', {}).get('name')
        })

except Exception as e:
    print("Error parsing competition data:", e)

# 3. Connect to MySQL and insert data
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
        # Create categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id VARCHAR(50) PRIMARY KEY,
                category_name VARCHAR(100) NOT NULL
            )
        ''')

        # Create competitions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitions (
                competition_id VARCHAR(50) PRIMARY KEY,
                competition_name VARCHAR(100) NOT NULL,
                parent_id VARCHAR(50),
                type VARCHAR(20) NOT NULL,
                gender VARCHAR(10) NOT NULL,
                category_id VARCHAR(50),
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )
        ''')

        # Insert into categories
        for item in category_list:
            try:
                cursor.execute('''
                    INSERT INTO categories (category_id, category_name)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE category_name = VALUES(category_name)
                ''', (
                    item.get('category_id'),
                    item.get('category_name')
                ))
            except Exception as e:
                print("Error inserting category:", e, item)

        # Insert into competitions
        for item in comptetions_list:
            try:
                cursor.execute('''
                    INSERT INTO competitions (competition_id, competition_name, parent_id, type, gender, category_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        competition_name = VALUES(competition_name),
                        parent_id = VALUES(parent_id),
                        type = VALUES(type),
                        gender = VALUES(gender),
                        category_id = VALUES(category_id)
                ''', (
                    item.get('competition_id'),
                    item.get('competition_name'),
                    item.get('parent_id'),
                    item.get('type'),
                    item.get('gender'),
                    item.get('category_id')
                ))
            except Exception as e:
                print("Error inserting competition:", e, item)

    connection.commit()

except pymysql.MySQLError as e:
    print("Database error:", e)

except Exception as e:
    print("Unexpected error:", e)

finally:
    try:
        connection.close()
        print("Connection closed.")
    except:
        pass

print("✅ Data saved to MySQL database successfully!")
