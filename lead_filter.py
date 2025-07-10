import os
import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIG ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "master_contacts"

st.set_page_config(page_title="🔎 Lead Filter", layout="wide")
st.title("🔎 Lead Filter by Location or Keyword")

# --- CONNECT TO SUPABASE ---
@st.cache_data(ttl=600)
def load_data():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table(TABLE_NAME).select("*").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        df.columns = df.columns.str.strip().str.lower()  # Normalize column names
        return df
    else:
        return pd.DataFrame()

df = load_data()

# --- SEARCH ---
search_term = st.text_input("Enter a location, state, or keyword (e.g., 'Dallas', 'Texas')").lower()

if df.empty:
    st.warning("No data found in Supabase.")
else:
    if search_term:
        match_cols = ['location', 'state', 'tags', 'message', 'source_url']
        filters = []

        for col in match_cols:
            if col in df.columns:
                filters.append(df[col].astype(str).str.lower().str.contains(search_term, na=False))

        if filters:
            combined_filter = filters[0]
            for f in filters[1:]:
                combined_filter |= f

            filtered = df[combined_filter]
            st.success(f"✅ Found {len(filtered)} matching leads.")
            st.dataframe(filtered.sort_values(by="date", ascending=False), use_container_width=True)
        else:
            st.error(f"❌ None of the target columns ({', '.join(match_cols)}) were found.")
            st.write("Available columns:", df.columns.tolist())
    else:
        st.info("Please enter a search term to filter leads.")
        st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True)
