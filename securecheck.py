import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  
    database="violations"  
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS check_post_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(20),
    driver_id VARCHAR(100),
    officer_id VARCHAR(50),
    timestamp DATETIME,
    status VARCHAR(50)
)
""")


st.set_page_config(page_title="SecureCheck", layout="wide")
st.markdown("<center><h1>SecureCheck for Police Post Logs</h1></center>", unsafe_allow_html=True)
st.title("🚨 Police Stop Dashboard")

csv_path = "D:/POLICELOG/env/Scripts/Police_Dataset.csv"
df = pd.read_csv(csv_path)
df.dropna(axis=1, how='all', inplace=True)
for column in df.columns:
    if df[column].dtype == 'object':
        df[column].fillna("Unknown", inplace=True)
    else:
        df[column].fillna(0, inplace=True)


df["vehicle_number"] = ["MH12AB" + str(1000 + i) for i in range(len(df))]
df["officer_id"] = ["O" + str(100 + (i % 5)) for i in range(len(df))]
df["driver_id"] = df["driver_gender"] + "_" + df["driver_age"].astype(str)
df["timestamp"] = pd.to_datetime(df["stop_date"] + ' ' + df["stop_time"], errors='coerce')
df["status"] = df["stop_outcome"]


cursor = conn.cursor()
for _, row in df.iterrows():
    try:
        cursor.execute("""
        INSERT INTO check_post_logs (vehicle_number, driver_id, officer_id, timestamp, status)
        VALUES (%s, %s, %s, %s, %s)
        """, (
            row["vehicle_number"],
            row["driver_id"],
            row["officer_id"],
            row["timestamp"].strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(row["timestamp"]) else None,
            row["status"]
        ))
    except Exception as e:
        print("Insert error:", e)
conn.commit()


st.subheader("📅 Check Post Logs")
cursor.execute("SELECT * FROM check_post_logs")
logs = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in cursor.description])
st.dataframe(logs.head(50))


st.subheader("🔍 Search Vehicle")
search = st.text_input("Enter vehicle number:")
if search:
    cursor.execute("SELECT * FROM check_post_logs WHERE vehicle_number = %s", (search,))
    result = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in cursor.description])
    st.dataframe(result)


st.subheader("📊 Violation Stats")
queries = {
    "Total Stops": "SELECT COUNT(*) AS total_stops FROM check_post_logs",
    "Stops by Officer": "SELECT officer_id, COUNT(*) AS stop_count FROM check_post_logs GROUP BY officer_id",
    "Arrest vs Warning": "SELECT status, COUNT(*) AS count FROM check_post_logs GROUP BY status",
    "Top Officers": "SELECT officer_id, COUNT(*) AS count FROM check_post_logs GROUP BY officer_id ORDER BY count DESC LIMIT 5",
    "Stops by Hour": "SELECT HOUR(timestamp) AS hour, COUNT(*) AS count FROM check_post_logs GROUP BY hour ORDER BY hour"
}


for name, query in queries.items():
    st.markdown(f"**{name}**")
    cursor.execute(query)
    result = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in cursor.description])
    st.dataframe(result)

st.subheader("🧠 Predict Stop Outcome & Violation Type")

with st.form("predict_form"):
    driver_age = st.slider("Driver Age", min_value=16, max_value=100, value=30)
    driver_gender = st.selectbox("Driver Gender", ["M", "F"])
    stop_hour = st.slider("Stop Hour (24h format)", min_value=0, max_value=23, value=14)
    submit_btn = st.form_submit_button("Predict")

if submit_btn:
    
    if stop_hour >= 22 or stop_hour <= 5:
        outcome = "Warning"
        violation = "Speeding"
    elif driver_age < 21:
        outcome = "Arrest - drugs"
        violation = "Drug-related"
    elif driver_gender == "M" and driver_age > 50:
        outcome = "Citation"
        violation = "Seatbelt"
    else:
        outcome = "Warning"
        violation = "Documentation"

    st.success("✅ Prediction Complete!")
    st.write(f"**Predicted Stop Outcome:** {outcome}")
    st.write(f"**Likely Violation Type:** {violation}")

st.subheader("🔍 SQL QUERIES")
st.subheader("🧠 Medium Level Query")

custom_queries = {
    "1. Total Number of Police Stops": "SELECT COUNT(*) AS total_stops FROM check_post_logs",
    "2. Count of Stops by Violation Type": "SELECT status AS violation_type, COUNT(*) AS count FROM check_post_logs GROUP BY status",
    "3. Number of Arrests vs. Warnings": "SELECT status, COUNT(*) AS count FROM check_post_logs GROUP BY status",
    "4. Average Age of Drivers Stopped": "SELECT AVG(CAST(SUBSTRING_INDEX(driver_id, '_', -1) AS UNSIGNED)) AS avg_age FROM check_post_logs",
    "5. Top 5 Most Frequent Search Types": "SELECT status AS search_type, COUNT(*) AS count FROM check_post_logs GROUP BY status ORDER BY count DESC LIMIT 5",
    "6. Count of Stops by Gender": "SELECT SUBSTRING_INDEX(driver_id, '_', 1) AS gender, COUNT(*) AS count FROM check_post_logs GROUP BY gender",
    "7. Most Common Violation for Arrests": "SELECT status, COUNT(*) AS count FROM check_post_logs WHERE status LIKE '%arrest%' GROUP BY status ORDER BY count DESC LIMIT 1",
    "8. Average Stop Duration for Each Violation": "SELECT status, AVG(TIMESTAMPDIFF(MINUTE, timestamp, NOW())) AS avg_duration FROM check_post_logs GROUP BY status",
    "9. Number of Drug-Related Stops by Year": "SELECT YEAR(timestamp) AS year, COUNT(*) AS count FROM check_post_logs WHERE status LIKE '%drugs%' GROUP BY year",
    "10. Drivers with the Highest Number of Stops": "SELECT driver_id, COUNT(*) AS stop_count FROM check_post_logs GROUP BY driver_id ORDER BY stop_count DESC LIMIT 5",
    "11. Number of Stops Conducted at Night (10 PM - 5 AM)": "SELECT COUNT(*) AS night_stops FROM check_post_logs WHERE HOUR(timestamp) >= 22 OR HOUR(timestamp) <= 5",
    "12. Number of Searches Conducted by Violation Type": "SELECT status, COUNT(*) AS searches FROM check_post_logs WHERE status LIKE '%search%' GROUP BY status",
    "13. Arrest Rate by Driver Gender": """
        SELECT 
            SUBSTRING_INDEX(driver_id, '_', 1) AS gender,
            SUM(CASE WHEN status LIKE '%arrest%' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS arrest_rate_percent
        FROM check_post_logs
        GROUP BY gender
    """,
    "14. Violation Trends Over Time (Monthly)": """
        SELECT DATE_FORMAT(timestamp, '%Y-%m') AS month, COUNT(*) AS count 
        FROM check_post_logs 
        GROUP BY month ORDER BY month
    """,
    "15. Most Common Stop Outcomes for Drug-Related Stops": """
        SELECT status, COUNT(*) AS count 
        FROM check_post_logs 
        WHERE status LIKE '%drugs%' 
        GROUP BY status ORDER BY count DESC LIMIT 3
    """
}

selected_query_name = st.selectbox("Choose a SQL query to run:", list(custom_queries.keys()))

if selected_query_name:
    query = custom_queries[selected_query_name]
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
        st.markdown(f"### 📌 Result: {selected_query_name}")
        st.dataframe(result_df)
    except Exception as e:
        st.error(f"Error running query: {e}")

st.subheader("🧪 Advanced Level Query")

advanced_queries = {
    "1. Yearly Breakdown of Stops and Arrests by Country": """
        SELECT 
            YEAR(timestamp) AS year,
            COUNT(*) AS total_stops,
            SUM(CASE WHEN status LIKE '%arrest%' THEN 1 ELSE 0 END) AS total_arrests
        FROM check_post_logs
        GROUP BY year
        ORDER BY year
    """,

    "2. Driver Violation Trends Based on Age and Gender": """
        SELECT 
            SUBSTRING_INDEX(driver_id, '_', 1) AS gender,
            CAST(SUBSTRING_INDEX(driver_id, '_', -1) AS UNSIGNED) AS age,
            status,
            COUNT(*) AS violation_count
        FROM check_post_logs
        GROUP BY gender, age, status
        ORDER BY violation_count DESC
        LIMIT 100
    """,

    "3. Time Period Analysis of Stops (Morning/Afternoon/Night)": """
        SELECT 
            CASE 
                WHEN HOUR(timestamp) BETWEEN 5 AND 11 THEN 'Morning'
                WHEN HOUR(timestamp) BETWEEN 12 AND 17 THEN 'Afternoon'
                WHEN HOUR(timestamp) BETWEEN 18 AND 21 THEN 'Evening'
                ELSE 'Night'
            END AS time_period,
            COUNT(*) AS total_stops
        FROM check_post_logs
        GROUP BY time_period
    """,

    "4. Correlation Between Age, Violation Type, and Stop Duration": """
        SELECT 
            status,
            CAST(SUBSTRING_INDEX(driver_id, '_', -1) AS UNSIGNED) AS age,
            AVG(TIMESTAMPDIFF(MINUTE, timestamp, NOW())) AS avg_duration_minutes
        FROM check_post_logs
        GROUP BY status, age
        ORDER BY avg_duration_minutes DESC
        LIMIT 50
    """,

    "5. Violations with High Search and Arrest Rates": """
        SELECT 
            status,
            COUNT(*) AS total,
            SUM(CASE WHEN status LIKE '%search%' THEN 1 ELSE 0 END) AS search_count,
            SUM(CASE WHEN status LIKE '%arrest%' THEN 1 ELSE 0 END) AS arrest_count,
            ROUND(SUM(CASE WHEN status LIKE '%search%' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS search_rate,
            ROUND(SUM(CASE WHEN status LIKE '%arrest%' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate
        FROM check_post_logs
        GROUP BY status
        HAVING total > 10
        ORDER BY arrest_rate DESC
    """,

    "6. Driver Demographics by Gender (Age Stats)": """
        SELECT 
            SUBSTRING_INDEX(driver_id, '_', 1) AS gender,
            COUNT(*) AS total_drivers,
            AVG(CAST(SUBSTRING_INDEX(driver_id, '_', -1) AS UNSIGNED)) AS avg_age,
            MIN(CAST(SUBSTRING_INDEX(driver_id, '_', -1) AS UNSIGNED)) AS min_age,
            MAX(CAST(SUBSTRING_INDEX(driver_id, '_', -1) AS UNSIGNED)) AS max_age
        FROM check_post_logs
        GROUP BY gender
    """,

    "7. Top 5 Violations with Highest Arrest Rates": """
        SELECT 
            status,
            COUNT(*) AS total,
            SUM(CASE WHEN status LIKE '%arrest%' THEN 1 ELSE 0 END) AS arrest_count,
            ROUND(SUM(CASE WHEN status LIKE '%arrest%' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate
        FROM check_post_logs
        GROUP BY status
        HAVING total > 10
        ORDER BY arrest_rate DESC
        LIMIT 5
    """
}

selected_adv_query = st.selectbox("Choose an SQL query to run:", list(advanced_queries.keys()))

if selected_adv_query:
    try:
        cursor = conn.cursor()
        cursor.execute(advanced_queries[selected_adv_query])
        adv_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
        st.markdown(f"### 🔎 Result: {selected_adv_query}")
        st.dataframe(adv_df)
    except Exception as e:
        st.error(f"Error executing advanced query: {e}")

cursor.close()
conn.close()