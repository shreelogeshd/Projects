import requests
import pymysql
import json

try:
    # 1. Fetch API Data
    url = "https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings.json?api_key=rt0MyYde2deMs7Ozys2VUpjRtYj77KSATzLGpJZz"
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises HTTPError if not 200

    try:
        response_data = response.json()
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        response_data = {}

except requests.RequestException as e:
    print("Failed to fetch data from API:", e)
    response_data = {}

# 2. Parse API Response
rankings_data = response_data.get("rankings", [])

Competitor_Rankings = []
Competitor_list = []

try:
    for ranking in rankings_data:
        competitor_rankings = ranking.get('competitor_rankings', [])
        for competitor_data in competitor_rankings:
            competitor = competitor_data.get('competitor', {})
            Competitor_Rankings.append({
                "rank": competitor_data.get('rank'),
                "movement": competitor_data.get('movement'),
                "points": competitor_data.get('points'),
                "competitions_played": competitor_data.get('competitions_played'),
                "competitor_id": competitor.get('id')
            })
            Competitor_list.append({
                "competitor_id": competitor.get('id'),
                "name": competitor.get('name'),
                "country": competitor.get('country'),
                "country_code": competitor.get('country_code', ''),
                "abbreviation": competitor.get('abbreviation', '')
            })
except Exception as e:
    print("Error parsing rankings data:", e)

# 3. Connect to your MySQL database and insert data
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
        # 4. Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Competitors (
                competitor_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                country VARCHAR(100) NOT NULL,
                country_code CHAR(3) NOT NULL,
                abbreviation VARCHAR(10) NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Competitor_Rankings (
                rank_id INT PRIMARY KEY AUTO_INCREMENT,
                `rank` INT NOT NULL,
                movement INT NOT NULL,
                points INT NOT NULL,
                competitions_played INT NOT NULL,
                competitor_id VARCHAR(50),
                FOREIGN KEY (competitor_id) REFERENCES Competitors(competitor_id)
            )
        ''')

        # 5. Insert into Competitors table
        for item1 in Competitor_list:
            try:
                cursor.execute('''
                    INSERT INTO Competitors (competitor_id, name, country, country_code, abbreviation)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        name = VALUES(name),
                        country = VALUES(country),
                        country_code = VALUES(country_code),
                        abbreviation = VALUES(abbreviation)
                ''', (
                    item1.get('competitor_id'),
                    item1.get('name'),
                    item1.get('country'),
                    item1.get('country_code'),
                    item1.get('abbreviation')
                ))
            except Exception as e:
                print("Error inserting into Competitors:", e, item1)

        # 6. Insert into Competitor_Rankings table
        for item in Competitor_Rankings:
            try:
                cursor.execute('''
                    INSERT INTO Competitor_Rankings (`rank`, movement, points, competitions_played, competitor_id)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (
                    item.get('rank'),
                    item.get('movement'),
                    item.get('points'),
                    item.get('competitions_played'),
                    item.get('competitor_id')
                ))
            except Exception as e:
                print("Error inserting into Competitor_Rankings:", e, item)

        # 7. Commit changes
        connection.commit()

except pymysql.MySQLError as e:
    print("Database error:", e)

except Exception as e:
    print("Unexpected error during DB operations:", e)

finally:
    try:
        connection.close()
        print("MySQL connection closed.")
    except:
        print("MySQL connection was not open or already closed.")

print("✅ Data saved to MySQL database successfully!")
