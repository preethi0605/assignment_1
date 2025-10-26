import pandas as pd
import streamlit as st
import mysql.connector
from mysql.connector import Error



mydb = mysql.connector.connect(
 host="localhost",
 user="root",
 password="2296",


)


print(mydb)
mycursor = mydb.cursor(buffered=True)

def fetch_data(query):
    """
    Connects to MySQL, executes the given SQL query,
    fetches the data, and returns it as a Pandas DataFrame.
    """
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="2296",
            database="preeti"
        )

        if connection.is_connected():
            # Create cursor with dictionary output (so columns have names)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            # Fetch all rows
            results = cursor.fetchall()

            # Convert to DataFrame
            df = pd.DataFrame(results)

            # Return the DataFrame
            return df

    except Error as e:
        st.error(f"❌ Database error: {e}")
        return pd.DataFrame()  # return empty DataFrame so .empty won't fail

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

st.set_page_config(page_title="Secure check Police Dashboard", layout='wide')

st.title("👮‍♂️Check Post Digital Ledger")
st.markdown("Real-Time monitoring and insigths")

st.header("📝Check Post Logs")
query = "SELECT * FROM trafficstop"
data = fetch_data(query)
st.dataframe(data,use_container_width=True)

st.title("📈Advance Insigths")
selected_query = st.selectbox("Select your query",[
    "Top 10 vehicle numbers involved in drug-related stops",
    "Vehicles most frequently searched",
    "Driver age group with highest arrest rate",
    "Gender distribution of drivers stopped in each country",
    "Race and gender combination with highest search rate",
    "Time of day with most traffic stops",
    "Average stop duration for different violations",
    "Are stops during the night more likely to lead to arrests",
    "Violations most associated with searches or arrests",
    "Violations most common among younger drivers (<25)",
    "Violations rarely resulting in search or arrest",
    "Countries with highest rate of drug-related stops",
    "Arrest rate by country and violation",
    "Country with most stops where search was conducted",
    "Yearly breakdown of stops and arrests by country",
    "Driver violation trends based on age and race",
    "Time period analysis of stops (Year, Month, Hour)",
    "Violations with high search and arrest rates",
    "Driver demographics by country (Age, Gender, Race)",
    "Top 5 violations with highest arrest rates"
])

mapping_query = { 

    "Top 10 vehicle numbers involved in drug-related stops": """
        SELECT vehicle_number, COUNT(*) AS drug_related_count
        FROM trafficstop
        WHERE drugs_related_stop = 'True' OR drugs_related_stop = 1
        GROUP BY vehicle_number
        ORDER BY drug_related_count DESC
        LIMIT 10;
    """,

    "Vehicles most frequently searched": """
        SELECT vehicle_number, COUNT(*) AS search_count
        FROM trafficstop
        WHERE search_conducted = 'True' OR search_conducted = 1
        GROUP BY vehicle_number
        ORDER BY search_count DESC
        LIMIT 10;
    """,

    "Driver age group with highest arrest rate": """
        SELECT driver_age, 
               COUNT(*) AS total_stops,
               SUM(CASE WHEN is_arrested = 'True' OR is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests,
               ROUND(100.0 * SUM(CASE WHEN is_arrested = 'True' OR is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS arrest_rate_percent
        FROM trafficstop
        GROUP BY driver_age
        ORDER BY arrest_rate_percent DESC
        LIMIT 1;
    """,

    "Gender distribution of drivers stopped in each country": """
        SELECT country_name, driver_gender, COUNT(*) AS total_stops,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY country_name), 2) AS percent_within_country
        FROM trafficstop
        GROUP BY country_name, driver_gender
        ORDER BY country_name, total_stops DESC;
    """,

    "Race and gender combination with highest search rate": """
        SELECT driver_race, driver_gender, 
               COUNT(*) AS total_stops,
               SUM(CASE WHEN search_conducted = 'True' OR search_conducted = 1 THEN 1 ELSE 0 END) AS total_searches,
               ROUND(100.0 * SUM(CASE WHEN search_conducted = 'True' OR search_conducted = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS search_rate_percent
        FROM trafficstop
        GROUP BY driver_race, driver_gender
        ORDER BY search_rate_percent DESC
        LIMIT 1;
    """,

    "Time of day with most traffic stops": """
        SELECT CASE 
                   WHEN HOUR(stop_time) BETWEEN 5 AND 11 THEN 'Morning (5 AM - 11 AM)'
                   WHEN HOUR(stop_time) BETWEEN 12 AND 16 THEN 'Afternoon (12 PM - 4 PM)'
                   WHEN HOUR(stop_time) BETWEEN 17 AND 20 THEN 'Evening (5 PM - 8 PM)'
                   ELSE 'Night (9 PM - 4 AM)' 
               END AS time_of_day,
               COUNT(*) AS total_stops
        FROM trafficstop
        GROUP BY time_of_day
        ORDER BY total_stops DESC;
    """,

    "Average stop duration for different violations": """
        SELECT violation, ROUND(AVG(stop_duration), 2) AS avg_stop_duration
        FROM trafficstop
        GROUP BY violation
        ORDER BY avg_stop_duration DESC;
    """,

    "Are stops during the night more likely to lead to arrests": """
        SELECT CASE 
                   WHEN HOUR(stop_time) BETWEEN 5 AND 20 THEN 'Daytime (5 AM - 8 PM)'
                   ELSE 'Nighttime (9 PM - 4 AM)' 
               END AS time_period,
               COUNT(*) AS total_stops,
               SUM(CASE WHEN is_arrested = 'True' OR is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests,
               ROUND(100.0 * SUM(CASE WHEN is_arrested = 'True' OR is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS arrest_rate_percent
        FROM trafficstop
        GROUP BY time_period
        ORDER BY arrest_rate_percent DESC;
    """,

    "Violations most associated with searches or arrests": """
        SELECT violation,
               COUNT(*) AS total_stops,
               SUM(CASE WHEN search_conducted = 'True' OR search_conducted = 1 THEN 1 ELSE 0 END) AS total_searches,
               SUM(CASE WHEN is_arrested = 'True' OR is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests,
               ROUND(100.0 * SUM(CASE WHEN search_conducted = 'True' OR search_conducted = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS search_rate_percent,
               ROUND(100.0 * SUM(CASE WHEN is_arrested = 'True' OR is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS arrest_rate_percent
        FROM trafficstop
        GROUP BY violation
        ORDER BY (search_rate_percent + arrest_rate_percent) DESC
        LIMIT 10;
    """,

    "Top 5 violations with highest arrest rates": """
        SELECT violation,
               COUNT(*) AS total_stops,
               SUM(CASE WHEN is_arrested = 'True' OR is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests,
               ROUND(100.0 * SUM(CASE WHEN is_arrested = 'True' OR is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS arrest_rate_percent
        FROM trafficstop
        GROUP BY violation
        ORDER BY arrest_rate_percent DESC
        LIMIT 5;
    """
}
if st.button("Search"):
    result = fetch_data(mapping_query[selected_query])
    if not result.empty:  # <-- Correct way
        st.write(result)
    else:
        st.warning("No Results Found !")


st.markdown("---")
st.header("🔍 Custom Natural Language Filter (MySQL Version)")

with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Gender", ['Male', 'Female'])
    driver_age = st.number_input("Age", min_value=16, max_value=100, value=25)
    driver_race = st.text_input("Driver Race")
    search_conducted = st.selectbox("Was search conducted?", [True, False])
    stop_duration = st.text_input("Stop Duration")
    drug_related_stop = st.selectbox("Was it drug related?", [True, False])
    vehicle_number = st.text_input("Vehicle Number")

    submitted = st.form_submit_button("Predict Outcome and Violation")

if submitted:
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="2296",
            database="preeti"
        )
        cursor = conn.cursor(dictionary=True)

        # 🔹 Get most frequent outcome
        cursor.execute(f"""
            SELECT stop_outcome
            FROM trafficstop
            WHERE driver_age = {driver_age}
              AND driver_gender = '{driver_gender.lower()}'
              AND search_conducted = {int(search_conducted)}
              AND drugs_related_stop = {int(drug_related_stop)}
            GROUP BY stop_outcome
            ORDER BY COUNT(*) DESC
            LIMIT 1;
        """)
        outcome = cursor.fetchone()

        # 🔹 Get most frequent violation
        cursor.execute(f"""
            SELECT violation
            FROM trafficstop
            WHERE driver_age = {driver_age}
              AND driver_gender = '{driver_gender.lower()}'
              AND search_conducted = {int(search_conducted)}
              AND drugs_related_stop = {int(drug_related_stop)}
            GROUP BY violation
            ORDER BY COUNT(*) DESC
            LIMIT 1;
        """)
        violation = cursor.fetchone()

        predicted_outcome = outcome["stop_outcome"] if outcome else "warning"
        predicted_violation = violation["violation"] if violation else "speeding"

        # 🔹 Display results
        st.markdown(f"""
        **PREDICTION SUMMARY**

        🚨 **Predicted Violation:** {predicted_violation}  
        ⚠️ **Predicted Stop Outcome:** {predicted_outcome}

        A {driver_age}-year-old {driver_gender.lower()} driver {country_name or ""} 
        was stopped for {predicted_violation.lower()} at {stop_time}.  
        {"A search was conducted" if search_conducted else "No search was conducted"} and the stop {"was drug related" if drug_related_stop else "was not drug related"}.
        The stop lasted {stop_duration or "unknown"}.
        """)

    except Exception as e:
        st.error(f"MySQL Error: {e}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()



                       