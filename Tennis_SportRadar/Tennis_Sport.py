import streamlit as st
import pandas as pd
import pymysql

st.set_page_config(page_title="Tennis Dashboard", layout="wide")

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Test@123',
        database='sportradar_tennis',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        mycursor = connection.cursor()

        def fetch_dataframe(query):
            try:
                mycursor.execute(query)
                result = mycursor.fetchall()
                column_names = [i[0] for i in mycursor.description]
                return pd.DataFrame(result, columns=column_names)
            except Exception as e:
                st.error(f"Error fetching data: {e}")
                return pd.DataFrame()

        competitors_df = fetch_dataframe("SELECT * FROM Competitors")
        rankings_df = fetch_dataframe("SELECT * FROM Competitor_Rankings")
        countrylist_df = fetch_dataframe("SELECT DISTINCT country FROM Competitors")
        categories_df = fetch_dataframe("SELECT * FROM categories")
        competitions_df = fetch_dataframe("SELECT * FROM competitions")
        complexes_df = fetch_dataframe("SELECT * FROM complexes")
        venues_df = fetch_dataframe("SELECT * FROM venues")

    finally:
        connection.close()

except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# Safe DataFrame merges
try:
    competitor_merged_df = pd.merge(competitors_df, rankings_df, on='competitor_id')
    categories_merged_df = pd.merge(categories_df, competitions_df, on='category_id')
    complexes_merged_df = pd.merge(complexes_df, venues_df, on='complex_id')
except Exception as e:
    st.error(f"Error merging dataframes: {e}")
    st.stop()

# Dropdown options with fallback
country_options = ["Select"] + countrylist_df['country'].dropna().unique().tolist() if not countrylist_df.empty else ["Select"]
city_options = ["Select"] + complexes_merged_df["city_name"].dropna().unique().tolist() if not complexes_merged_df.empty else ["Select"]
type_options = ["Select"] + categories_merged_df["type"].dropna().unique().tolist() if not categories_merged_df.empty else ["Select"]
gender_options = ["Select"] + categories_merged_df["gender"].dropna().unique().tolist() if not categories_merged_df.empty else ["Select"]

st.title("🎾 Tennis Competitors Dashboard")

st.sidebar.title("Filters")
country = st.sidebar.selectbox("Country", country_options)
competitor_name = st.sidebar.text_input("Name")

try:
    min_rank = int(competitor_merged_df['rank'].min())
    max_rank = int(competitor_merged_df['rank'].max())
except:
    min_rank, max_rank = 1, 1000

selected_rank_range = st.sidebar.slider("Rank", min_rank, max_rank, (min_rank, max_rank))
points_threshold = st.sidebar.number_input("Minimum Points", value=200)
city = st.sidebar.selectbox("City", city_options)
type = st.sidebar.selectbox("Type", type_options)
gender = st.sidebar.selectbox("Gender", gender_options)
filter_button = st.sidebar.button("Apply")

# Stats
st.subheader("📊 Summary Statistics")


col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Competitors", competitor_merged_df['competitor_id'].nunique())
with col2:
    st.metric("Countries Represented", competitor_merged_df['country'].nunique())
with col3:
    st.metric("Highest Points", competitor_merged_df['points'].max())

# Leaderboards
st.subheader("Leaderboards")
try:
    top_by_points = competitor_merged_df.sort_values(by='points', ascending=False).head(3)
    st.subheader("🏆 Top 3 Competitors by Points")
    df = top_by_points.reset_index(drop=True)
    st.dataframe(df[['name', 'points']].rename(columns={'name': 'Name', 'points': 'Points'}), use_container_width=True)

    top_by_rank = competitor_merged_df[(competitor_merged_df['rank'] >= 1) & (competitor_merged_df['rank'] <= 3)].sort_values(by='rank')
    st.subheader("🏆 Top 3 Competitors by Rank")
    df = top_by_rank.reset_index(drop=True)
    st.dataframe(df[['name', 'rank']].rename(columns={'name': 'Name', 'rank': 'Rank'}), use_container_width=True)
except Exception as e:
    st.warning(f"Error generating leaderboard: {e}")

# Filtering
if filter_button:
    try:
        filtered_data = competitor_merged_df
        if country.lower() != "select":
            filtered_data = filtered_data[filtered_data['country'] == country]
        elif competitor_name:
            filtered_data = filtered_data[filtered_data['name'].str.contains(competitor_name, case=False)]
        elif points_threshold and selected_rank_range:
            filtered_data = filtered_data[
                (filtered_data['points'] >= points_threshold) &
                (filtered_data['rank'] >= selected_rank_range[0]) &
                (filtered_data['rank'] <= selected_rank_range[1])
                ]
        elif points_threshold:
            filtered_data = filtered_data[filtered_data['points'] >= points_threshold]
        elif selected_rank_range:
            filtered_data = filtered_data[
                (filtered_data['rank'] >= selected_rank_range[0]) & 
                (filtered_data['rank'] <= selected_rank_range[1])
            ]

        filtered_data = filtered_data.sort_values(by='rank', ascending=True)
            
        st.subheader("Filtered Rankings")
        df = filtered_data[['name', 'country', 'rank', 'movement', 'points', 'competitions_played']]
        df.columns = ['Name', 'Country', 'Rank', 'Movement', 'Points', 'Competitions Played']
        st.dataframe(df.reset_index(drop=True), use_container_width=True)
    except Exception as e:
        st.error(f"Error filtering competitor data: {e}")

    try:
        st.subheader("Venues and Complexes")
        venues_filtered = complexes_merged_df
        if (country.lower() != "select") and (city.lower() != "select"):
            venues_filtered = venues_filtered[(venues_filtered['country_name'] == country) & (venues_filtered['city_name'] == city)]
        elif country.lower() != "select":
            venues_filtered = venues_filtered[venues_filtered['country_name'] == country]
        elif city.lower() != "select":
            venues_filtered = venues_filtered[venues_filtered['city_name'] == city]
        df = venues_filtered[['complex_name', 'venue_name', 'city_name', 'country_name', 'timezone']]
        df.columns = ['Complex', 'Venue', 'City', 'Country', 'Timezone']
        st.dataframe(df.reset_index(drop=True), use_container_width=True)
    except Exception as e:
        st.error(f"Error filtering venues: {e}")

    try:
        st.subheader("Competitions")
        competitions_filtered = categories_merged_df
        if (type.lower() != "select") and (gender.lower() != "select"):
            competitions_filtered = competitions_filtered[(competitions_filtered['type'] == type) & (competitions_filtered['gender'] == gender.lower())]
        elif type.lower() != "select":
            competitions_filtered = competitions_filtered[competitions_filtered['type'] == type]
        elif gender.lower() != "select":
            competitions_filtered = competitions_filtered[competitions_filtered['gender'] == gender.lower()]
        df = competitions_filtered[['category_name', 'competition_name', 'type','gender']]
        df.columns = ['Category', 'Competition', 'Type','Gender']
        st.dataframe(df.reset_index(drop=True), use_container_width=True)
    except Exception as e:
        st.error(f"Error filtering competitions: {e}")
