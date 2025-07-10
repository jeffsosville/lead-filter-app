import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os

# --- LOAD FROM SECRETS ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TABLE_NAME = "master_contacts"

# --- SAFETY CHECK ---
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Supabase URL or KEY missing in secrets.")
    st.stop()

# --- CONNECT ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- PAGINATED LOADER ---
@st.cache_data(ttl=600)
def load_all_rows(table_name, batch_size=1000):
    all_data = []
    start = 0

    while True:
        end = start + batch_size - 1
        response = supabase.table(table_name).select("*").range(start, end).execute()

        if not response.data:
            break

        all_data.extend(response.data)

        if len(response.data) < batch_size:
            break

        start += batch_size

    df = pd.DataFrame(all_data)
    df.columns = df.columns.str.strip().str.lower()
    return df

# --- LOAD DATA ---
df = load_all_rows(TABLE_NAME)

# --- HANDLE EMPTY ---
if df.empty:
    st.warning("No data found in Supabase table.")
    st.stop()

# --- MAIN UI ---
st.title("🔎 Lead Filter by Location or Keyword")
query = st.text_input("Enter a location or keyword (e.g., 'Dallas', 'Texas')")

if query:
    filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)]
    st.write(f"### Found {len(filtered_df)} matches")
    st.dataframe(filtered_df)
else:
    st.dataframe(df.head(100))  # Show sample if no input
