#SecureCheck-A-Police-Stop-Log-System

Introduction
 
SecureCheck is a digital dashboard system designed to help police departments log, manage, and analyze data from vehicle stops at check posts. Built using Python, MySQL, and Streamlit, it provides an interactive interface for storing and exploring traffic stop data efficiently.

Step 1: Database Setup
I connected to a MySQL database called 'violations' and created a table called 'check_post_logs' like 
1.vehicle number
2.driver ID (gender + age)
3.officer ID
4.timestamp
5.status of each stop

Step 2: Loading and Cleaning Data
I loaded data from a CSV file like fill missing values, generate unique vehicle and officer IDs and created a combined timestamp column and then i stored this data in the MySQL database.

Step 3: Streamlit Dashboard Features
I built an interactive web dashboard using Streamlit with these key features like View all police stop logs in a live data table.- Run 15 medium-level SQL queries like total stops, arrest vs warning, gender-wise stats, and violation trends and 7 advanced SQL queries to discover deeper patterns, like arrest rates, stop times, and age correlations and Search a specific vehicle number to check its history and  Display quick stats like total stops, top officers, and most active hours and Predict stop outcome and violation type using simple logic based on time, age, and gender.

Conclusion
SecureCheck helps law enforcement agencies digitize and monitor their traffic stops in real-time and it combines data processing, SQL analytics, and a simple UI to improve transparency, reporting, and operational efficiency.
                                                          
