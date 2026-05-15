import streamlit as st
import pandas as pd
import plotly.express as px
import random
import os
import urllib.parse

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="PriceX AI",
    page_icon="🛒",
    layout="wide"
)

# =========================================================
# DATA LOADING & LINK VALIDATOR
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "pricex_phones.csv")

def validate_url(url, model_name, platform):
    """
    Prevents ERR_ADDRESS_UNREACHABLE.
    If the CSV link is broken or invalid, it creates a clean search link.
    """
    url = str(url).strip().lower()
    # Check if the URL is a placeholder or invalid IP-like string
    if url in ["nan", "", "#", "none", "null"] or not ("." in url):
        # Fallback: Search for the product on the platform
        query = urllib.parse.quote(f"{model_name} {platform}")
        return f"https://www.google.com/search?q={query}"
    
    if not url.startswith("http"):
        return "https://" + url
    return url

# Load Data
if not os.path.exists(csv_path):
    df_sample = pd.DataFrame({
        "Model": ["iPhone 17 Pro", "Samsung S25 Ultra", "OnePlus 13"],
        "Brand": ["Apple", "Samsung", "OnePlus"],
        "Series": ["Flagship", "Ultra", "Flagship"],
        "Amazon Link": ["amazon.in", "amazon.in", "amazon.in"], 
        "Flipkart Link": ["flipkart.com", "flipkart.com", "flipkart.com"], 
        "Myntra Link": ["myntra.com", "myntra.com", "myntra.com"]
    })
    df_sample.to_csv(csv_path, index=False)

items = pd.read_csv(csv_path)

# Correct column names
expected_names = ["Model", "Brand", "Series", "Amazon Link", "Flipkart Link", "Myntra Link"]
actual_cols = list(items.columns)
for i, name in enumerate(expected_names):
    if i < len(actual_cols):
        items.rename(columns={actual_cols[i]: name}, inplace=True)

items = items.fillna("N/A")

# Apply the strict validator to prevent the 0.0.x.x error
items["Amazon Link"] = items.apply(lambda x: validate_url(x["Amazon Link"], x["Model"], "Amazon"), axis=1)
items["Flipkart Link"] = items.apply(lambda x: validate_url(x["Flipkart Link"], x["Model"], "Flipkart"), axis=1)
items["Myntra Link"] = items.apply(lambda x: validate_url(x["Myntra Link"], x["Model"], "Myntra"), axis=1)

if "Price" not in items.columns:
    items["Price"] = [random.randint(25000, 120000) for _ in range(len(items))]
if "Rating" not in items.columns:
    items["Rating"] = [round(random.uniform(3.8, 4.9), 1) for _ in range(len(items))]

# =========================================================
# SESSION STATE
# =========================================================
if "wishlist_data" not in st.session_state:
    st.session_state.wishlist_data = []

# =========================================================
# HEADER & CREDITS
# =========================================================
st.markdown("<h1 style='text-align: center; color: #2563eb; font-size: 60px; margin-bottom: 0px;'>PriceX</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; color: #64748b; margin-top: 0px;'>By: Sachingouda, Ramachandra, Sumit, Amruta and Vaishnavi</p>", unsafe_allow_html=True)
st.markdown("---")

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🤖 PriceX AI Filters")
search = st.sidebar.text_input("🔍 Search Models", placeholder="e.g. iPhone 11")
budget = st.sidebar.slider("💰 Max Budget (₹)", 10000, 200000, 150000)

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Product List")
st.sidebar.info("\n".join([f"• {m}" for m in sorted(items["Model"].unique())]))

# =========================================================
# UI STYLING
# =========================================================
st.markdown(f"""
<style>
    .product-card {{
        background: white; padding: 25px; border-radius: 18px;
        border: 1px solid #e2e8f0; margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }}
    .brand-label {{ color: #1e293b; font-size: 32px; font-weight: 800; margin-bottom: 5px; }}
    .model-label {{ color: #475569; font-size: 18px; margin-bottom: 15px; }}
    .price-tag {{ color: #10b981; font-size: 28px; font-weight: bold; margin: 15px 0; }}
    .shop-links {{ display: flex; gap: 10px; margin-top: 20px; }}
    .shop-btn {{
        display: inline-block; padding: 12px 18px; border-radius: 10px;
        text-decoration: none !important; font-size: 14px; font-weight: bold;
        color: white !important; text-align: center;
    }}
    .amz {{ background: #ff9900; }}
    .flk {{ background: #2874f0; }}
    .myn {{ background: #ff3f6c; }}
    .ai-box {{
        background: #f0fdf4; border: 2px solid #22c55e; 
        padding: 15px; border-radius: 12px; margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)

def render_product_card(row, key_suffix):
    st.markdown(f"""
    <div class="product-card">
        <div class="brand-label">{row['Brand']}</div>
        <div class="model-label">{row['Model']} | {row['Series']}</div>
        <div class="price-tag">₹{row['Price']:,}</div>
        <p style="color: #f59e0b; font-size: 18px;">⭐ {row['Rating']}</p>
        <div class="shop-links">
            <a href="{row['Amazon Link']}" target="_blank" class="shop-btn amz">Amazon</a>
            <a href="{row['Flipkart Link']}" target="_blank" class="shop-btn flk">Flipkart</a>
            <a href="{row['Myntra Link']}" target="_blank" class="shop-btn myn">Myntra</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"❤️ Save to Wishlist", key=f"btn_{key_suffix}"):
        if row['Model'] not in [x['Model'] for x in st.session_state.wishlist_data]:
            st.session_state.wishlist_data.append(row.to_dict())
            st.toast(f"Saved {row['Model']}!")

# =========================================================
# APP TABS
# =========================================================
tab1, tab2, tab3 = st.tabs(["🛍️ Browse", "📊 AI Comparison", "❤️ Wishlist"])

filtered = items[(items["Price"] <= budget)]
if search:
    filtered = filtered[filtered["Model"].str.contains(search, case=False)]

with tab1:
    if not filtered.empty:
        cols = st.columns(3)
        for i, (idx, row) in enumerate(filtered.iterrows()):
            with cols[i % 3]:
                render_product_card(row, f"br_{idx}")
    else:
        st.warning("No products match your filters.")

with tab2:
    st.header("📊 Comparison")
    selection = st.multiselect("Select products:", items["Model"].unique())
    if len(selection) >= 2:
        cdf = items[items["Model"].isin(selection)].copy()
        cdf['Value'] = (cdf['Rating'] * 100000) / cdf['Price']
        best = cdf.loc[cdf['Value'].idxmax()]
        st.markdown(f"<div class='ai-box'>🤖 AI suggests <b>{best['Model']}</b> for best value.</div>", unsafe_allow_html=True)
        st.dataframe(cdf[["Model", "Brand", "Price", "Rating"]], use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(cdf, x="Model", y="Price", color="Model"), use_container_width=True)

with tab3:
    if st.session_state.wishlist_data:
        if st.button("Clear All"):
            st.session_state.wishlist_data = []
            st.rerun()
        w_cols = st.columns(3)
        for i, row_dict in enumerate(st.session_state.wishlist_data):
            with w_cols[i % 3]:
                render_product_card(pd.Series(row_dict), f"ws_{i}")
    else:
        st.info("Wishlist is empty.")
