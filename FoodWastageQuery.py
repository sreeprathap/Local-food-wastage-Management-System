import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="Basic Query",layout="wide")

def create_connection():
    return mysql.connector.connect(
            host="127.0.0.1",
            user="systemmanage",       
            password="System123",      
            database="food_wastage"    
        )


def run_query(query):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return pd.DataFrame(rows)

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filter Options")

city_filter = st.sidebar.text_input("City (leave blank for all)")
Location_filter = st.sidebar.text_input("Location (leave blank for all)")
provider_filter = st.sidebar.text_input("Name (leave blank for all)")
food_filter = st.sidebar.text_input("Food_Type (leave blank for all)")
meal_filter = st.sidebar.text_input("Meal Type (leave blank for all)")

filters = []
if city_filter:
    filters.append(f"city = '{city_filter}'")
if Location_filter:
    filters.append(f"Location = '{Location_filter}'")
if provider_filter:
    filters.append(f"Name = '{provider_filter}'")
if food_filter:
    filters.append(f"Food_Type = '{food_filter}'")
if meal_filter:
    filters.append(f"Meal_Type = '{meal_filter}'")

where_clause = " AND ".join(filters)
if where_clause:
    where_clause = "WHERE " + where_clause

# ----------------------------
# Example Queries
# ----------------------------
queries = {
#--------------------------------------------------------------------------------------------------------------
    # 1.food proviers data
#--------------------------------------------------------------------------------------------------------------
    "Food Providers": f"SELECT * FROM providers_data {where_clause}",

#--------------------------------------------------------------------------------------------------------------
    # 2.food Receivers data
#--------------------------------------------------------------------------------------------------------------
    "Food Receivers": f"SELECT * FROM receivers_data {where_clause}",

#--------------------------------------------------------------------------------------------------------------
    # 3.How many food providers and receivers are there in each city.
#--------------------------------------------------------------------------------------------------------------
     "Food providers and receivers in each city": f"""SELECT
    City,
    SUM(total_providers) AS total_providers,
    SUM(total_receivers) AS total_receivers
FROM (
    SELECT City, COUNT(DISTINCT Provider_ID) AS total_providers, 0 AS total_receivers
    FROM providers_data
    GROUP BY City

    UNION ALL

    SELECT City, 0 AS total_providers, COUNT(DISTINCT Receiver_ID) AS total_receivers
    FROM receivers_data
    GROUP BY City
) AS combined
{where_clause}
GROUP BY City
ORDER BY City;""",

#--------------------------------------------------------------------------------------------------------------
    # 4.Which type of food provider(restarant,grocery store) contributes the most food.
#--------------------------------------------------------------------------------------------------------------
    "Most valuable food provider":f"""SELECT max(Provider_Type) AS Food_Providers FROM food_listings_data;""",

#--------------------------------------------------------------------------------------------------------------
    # 5.What is the contact information of food providers in a specific city.
#--------------------------------------------------------------------------------------------------------------
    "Contact information of food providers": f"SELECT Name,Address,Contact FROM providers_data {where_clause}",

#--------------------------------------------------------------------------------------------------------------
    # 6. Which receivers have claimed the most food.
#--------------------------------------------------------------------------------------------------------------
    "Most frequnt Food claimer": f"""SELECT Name 
FROM receivers_data
WHERE Receiver_ID IN (
    SELECT max(Receiver_ID)
    FROM claims_data
    WHERE Status = 'Completed'
);""",

#--------------------------------------------------------------------------------------------------------------
    # 7.What is the total quantity of food available form all provides.
#--------------------------------------------------------------------------------------------------------------
    "Total Quantity of food": f"""SELECT sum(Quantity) AS Total_food FROM food_listings_data
                    WHERE Provider_ID IN (SELECT Provider_ID FROM providers_data);""",

#--------------------------------------------------------------------------------------------------------------
    # 8.Which city hast the highest numnber of food listing.
#--------------------------------------------------------------------------------------------------------------
    "Highest Count of City": f"""SELECT Location AS City_Name, COUNT(*) AS Highest_count 
        FROM food_listings_data {where_clause} GROUP BY Location ORDER BY Highest_count DESC""",

#--------------------------------------------------------------------------------------------------------------
    # 9.What are the most commonly available food types.
#--------------------------------------------------------------------------------------------------------------
    "Common Food types": f"""
     SELECT Food_Type AS Type, COUNT(*) AS count
     FROM food_listings_data
     {where_clause} 
     GROUP BY Food_Type
     ORDER BY count DESC""",

#--------------------------------------------------------------------------------------------------------------
    # 10.How Many food claims have been made for each food item.
#--------------------------------------------------------------------------------------------------------------
    "Food Claim Details": f"""
     SELECT Food_Name, COUNT(*) AS count
     FROM food_listings_data
     WHERE Food_ID IN (SELECT Food_ID FROM claims_data) 
     GROUP BY Food_Name
     ORDER BY count DESC""",

#--------------------------------------------------------------------------------------------------------------
    # 11.Which Provider has had the highest number of successful food claims.
#--------------------------------------------------------------------------------------------------------------
    "Highes Food climes": f"""
     SELECT Name, COUNT(Provider_ID) AS provider_count
     FROM providers_data
     WHERE Provider_ID IN (SELECT Provider_ID FROM food_listings_data)
     GROUP BY Name
     ORDER BY provider_count DESC""",

#--------------------------------------------------------------------------------------------------------------
    # 12.What percentage of food claims are completed vs. pending vs canceled
#--------------------------------------------------------------------------------------------------------------
    "Claim Percentage": f"""
    SELECT 
    Status,
    COUNT(*) AS count,
    ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM claims_data), 2) AS percentage
    FROM claims_data
    GROUP BY Status;""",

#--------------------------------------------------------------------------------------------------------------
    # 13.What are the average quantiy of food claimed per receiver
#--------------------------------------------------------------------------------------------------------------
    "Food Claimed per receiver": f"""SELECT 
    r.Receiver_ID,
    r.Name,
    COUNT(c.Claim_ID) AS total_claims
    FROM 
    receivers_data r
    LEFT JOIN 
    claims_data c ON r.Receiver_ID = c.Receiver_ID
    GROUP BY 
    r.Receiver_ID, r.Name
    ;""",

#--------------------------------------------------------------------------------------------------------------
    # 14.Which meal type(brekfast,lunch,dinner,snacks) is claimed the most
#--------------------------------------------------------------------------------------------------------------
    "Meal type claimed": f"""
    SELECT  Meal_type as Meal, count(Meal_Type) as Conts
    FROM food_listings_data
    {where_clause}
    GROUP BY Meal_type
    ORDER BY Conts DESC;""",

#--------------------------------------------------------------------------------------------------------------
    # 15.What is the total quantiy of food donated by each provider.
#--------------------------------------------------------------------------------------------------------------
    "Quantity by Provider": f"""SELECT 
    p.Name,
    SUM(f.Quantity) AS Total_Food_donated
    FROM 
    providers_data p
    JOIN 
    food_listings_data f ON p.Provider_ID = f.Provider_ID
    {where_clause}
    GROUP BY 
    p.Name;""",

}

# ----------------------------
# UI to Select Query
# ----------------------------
st.title("Food Wastage Management Query")

selected_query = st.selectbox("Select a Query", list(queries.keys()))

if st.button("Run Query"):
    df = run_query(queries[selected_query])
    st.dataframe(df)

    # Optional: Download button
    st.download_button("Download CSV", df.to_csv(index=False), "result.csv", "text/csv")
