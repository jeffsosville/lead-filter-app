import streamlit as st
import pandas as pd
from supabase import create_client, Client
from streamlit_authenticator import Authenticate
import copy

# --- CONFIG ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]
TABLE_NAME = "master_contacts"

# --- AUTH ---
users = copy.deepcopy(st.secrets["credentials"])

authenticator = Authenticate(
    users,
    "lead_filter_cookie",
    "some_random_signature_key",
    cookie_expiry_days=1
)

name, auth_status, username = authenticator.login("Login", "main")

# --- MAIN ---
if auth_status:
    st.sidebar.success(f"Welcome, {name}!")
    authenticator.logout("Logout", "sidebar")

    @st.cache_data(show_spinner="Loading leads...")
    def load_data():
        client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        all_rows = []
        offset = 0
        while True:
            res = client.table(TABLE_NAME).select("*").range(offset, offset + 999).execute()
            if not res.data:
                break
            all_rows.extend(res.data)
            offset += 1000
        return pd.DataFrame(all_rows)

    st.title("🔍 Lead Filter by Location or Keyword")
    query = st.text_input("Search keyword or location").strip().lower()
    df = load_data()

    if query:
        filtered = df[
            df['location'].astype(str).str.lower().str.contains(query, na=False) |
            df['route_inquired'].astype(str).str.lower().str.contains(query, na=False) |
            df['tags'].astype(str).str.lower().str.contains(query, na=False) |
            df['state'].astype(str).str.lower().str.contains(query, na=False) |
            df['state1'].astype(str).str.lower().str.contains(query, na=False) |
            df['state2'].astype(str).str.lower().str.contains(query, na=False)
        ]
        st.write(f"✅ {len(filtered)} results")
        st.dataframe(filtered)
        st.download_button("📥 Download CSV", data=filtered.to_csv(index=False), file_name="filtered_leads.csv", mime="text/csv")
    else:
        st.info("Start typing to filter the lead database.")

elif auth_status is False:
    st.error("Login failed. Please check your username and password.")

elif auth_status is None:
    st.warning("Please enter your credentials.")
