import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import streamlit as st

from frontend.client import create_restaurant, delete_restaurant, list_restaurants, update_restaurant

st.set_page_config(page_title="FoodieLog", page_icon="🍽️", layout="wide")
st.title("🍽️ FoodieLog")
st.caption(
    "Track restaurants you want to visit and ones you've already tried. "
    "Use the sidebar to filter your list, then use the sections below to add, update, or remove entries."
)

# ── Data loading ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def _load() -> list[dict]:
    return list_restaurants()


def refresh() -> None:
    _load.clear()
    st.rerun()


# ── Fetch + guard ─────────────────────────────────────────────────────────────

try:
    restaurants = _load()
except Exception as exc:
    st.error(
        "**Cannot reach the API.** Make sure the backend is running:\n\n"
        "```\nuv run uvicorn app.main:app --reload\n```\n\n"
        f"Error detail: `{exc}`"
    )
    st.stop()

df = pd.DataFrame(restaurants) if restaurants else pd.DataFrame(
    columns=["id", "name", "cuisine", "city", "rating", "status"]
)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Filters")
    st.caption("Narrow down the list below. All sections respect the active filters.")

    status_filter = st.multiselect(
        "Status",
        options=["Want to Go", "Visited"],
        default=["Want to Go", "Visited"],
        help="'Want to Go' = wishlist. 'Visited' = places you've already been to.",
    )

    if not df.empty and "cuisine" in df.columns:
        cuisines = sorted(df["cuisine"].unique())
        cuisine_filter = st.multiselect(
            "Cuisine",
            options=cuisines,
            default=cuisines,
            help="Select one or more cuisine types to show.",
        )
    else:
        cuisine_filter = []

    min_rating, max_rating = st.slider(
        "Minimum – Maximum rating",
        min_value=1, max_value=5, value=(1, 5),
        help="1 = poor, 5 = excellent. Drag both handles to set a range.",
    )

    st.divider()
    if st.button("🔄 Refresh data", help="Force-reload the restaurant list from the API."):
        refresh()

# ── Apply filters ─────────────────────────────────────────────────────────────

if not df.empty:
    mask = (
        df["status"].isin(status_filter)
        & df["rating"].between(min_rating, max_rating)
    )
    if cuisine_filter:
        mask &= df["cuisine"].isin(cuisine_filter)
    filtered = df[mask].reset_index(drop=True)
else:
    filtered = df

# ── Summary metrics ───────────────────────────────────────────────────────────

total   = len(df)
visited = int((df["status"] == "Visited").sum()) if not df.empty else 0
want    = total - visited
avg_rating = round(df["rating"].mean(), 1) if not df.empty and total > 0 else "—"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total restaurants", total,      help="All entries in the database.")
col2.metric("Visited",           visited,    help="Places you've already been to.")
col3.metric("Want to Go",        want,       help="Restaurants still on your wishlist.")
col4.metric("Avg rating",        avg_rating, help="Mean star rating across all entries (1–5).")

st.divider()

# ── Restaurant list ───────────────────────────────────────────────────────────

st.subheader(f"Restaurants ({len(filtered)} shown)")

if filtered.empty:
    if total == 0:
        st.info("No restaurants saved yet. Use **Add a restaurant** below to get started.")
    else:
        st.info("No restaurants match the current filters. Try adjusting the sidebar.")
else:
    display = filtered.copy()
    display["rating"] = display["rating"].apply(lambda r: "⭐" * int(r))
    st.dataframe(
        display[["id", "name", "cuisine", "city", "rating", "status"]],
        width="stretch",
        hide_index=True,
        column_config={
            "id":      st.column_config.NumberColumn("ID",      width="small"),
            "name":    st.column_config.TextColumn("Name",      width="medium"),
            "cuisine": st.column_config.TextColumn("Cuisine",   width="small"),
            "city":    st.column_config.TextColumn("City",      width="small"),
            "rating":  st.column_config.TextColumn("Rating",    width="small"),
            "status":  st.column_config.TextColumn("Status",    width="medium"),
        },
    )

st.divider()

# ── Add restaurant ────────────────────────────────────────────────────────────

with st.expander("➕  Add a restaurant", expanded=total == 0):
    st.caption("Fill in the details below and click **Save** to add a new entry to your list.")
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name    = c1.text_input(
            "Name *",
            placeholder="e.g. Pasta Roma",
            help="The restaurant's display name. Words are automatically title-cased.",
        )
        cuisine = c2.text_input(
            "Cuisine *",
            placeholder="e.g. Italian",
            help="The type of food served — Italian, Japanese, Mexican, etc.",
        )
        c3, c4, c5 = st.columns(3)
        city   = c3.text_input(
            "City *",
            placeholder="e.g. Tel Aviv",
            help="The city where this restaurant is located.",
        )
        rating = c4.slider(
            "Your rating",
            min_value=1, max_value=5, value=3,
            help="1 = poor  ·  3 = decent  ·  5 = excellent",
        )
        status = c5.selectbox(
            "Status",
            ["Want to Go", "Visited"],
            help="'Want to Go' adds it to your wishlist. 'Visited' marks it as done.",
        )
        submitted = st.form_submit_button("💾 Save restaurant", use_container_width=True)

    if submitted:
        missing = [f for f, v in [("Name", name), ("Cuisine", cuisine), ("City", city)] if not v.strip()]
        if missing:
            st.warning(f"Please fill in: **{', '.join(missing)}**.")
        else:
            try:
                created = create_restaurant(
                    name=name, cuisine=cuisine, city=city, rating=rating, status=status,
                )
                st.success(
                    f"**{created['name']}** added to your list! "
                    f"{'Check it off once you visit.' if status == 'Want to Go' else 'Enjoy the memory.'}"
                )
                refresh()
            except Exception as exc:
                st.error(f"Could not save the restaurant. The API returned: `{exc}`")

# ── Mark as Visited ───────────────────────────────────────────────────────────

with st.expander("✅  Mark as Visited"):
    st.caption("Move a restaurant from your wishlist to your visited list with one click.")
    want_rows = filtered[filtered["status"] == "Want to Go"] if not filtered.empty else pd.DataFrame()

    if want_rows.empty:
        st.info(
            "No 'Want to Go' restaurants in the current view. "
            "Either all are already Visited, or adjust the sidebar filters."
        )
    else:
        options = {f"{r['name']}  —  {r['cuisine']}, {r['city']}": r for _, r in want_rows.iterrows()}
        chosen_label = st.selectbox(
            "Select a restaurant to mark as Visited",
            list(options.keys()),
            help="Only restaurants with 'Want to Go' status are shown here.",
        )
        if st.button("✅ Mark as Visited", key="mark_visited_btn"):
            r = options[chosen_label]
            try:
                update_restaurant(
                    int(r["id"]),
                    name=r["name"], cuisine=r["cuisine"], city=r["city"],
                    rating=int(r["rating"]), status="Visited",
                )
                st.success(f"**{r['name']}** marked as Visited. Hope it was great!")
                refresh()
            except Exception as exc:
                st.error(f"Update failed: `{exc}`")

# ── Delete ────────────────────────────────────────────────────────────────────

with st.expander("🗑️  Delete a restaurant"):
    st.caption("Permanently remove an entry. This cannot be undone.")
    if filtered.empty:
        st.info("No restaurants to delete with the current filters.")
    else:
        del_options = {
            f"{r['name']}  —  {r['cuisine']}, {r['city']}": int(r["id"])
            for _, r in filtered.iterrows()
        }
        chosen = st.selectbox("Select a restaurant to delete", list(del_options.keys()), key="del_select")
        st.warning(f"You are about to permanently delete **{chosen.split('  —  ')[0]}**. This cannot be undone.")
        if st.button("🗑️ Confirm delete", type="primary", key="confirm_delete_btn"):
            try:
                delete_restaurant(del_options[chosen])
                st.success("Restaurant deleted.")
                refresh()
            except Exception as exc:
                st.error(f"Delete failed: `{exc}`")

# ── Export ────────────────────────────────────────────────────────────────────

st.divider()
st.subheader("Export")
st.caption("Download the currently filtered list as a CSV file you can open in Excel or Google Sheets.")

if not filtered.empty:
    csv_bytes = filtered.to_csv(index=False).encode()
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv_bytes,
        file_name="foodielog_export.csv",
        mime="text/csv",
        help=f"Exports {len(filtered)} restaurant(s) matching the current filters.",
    )
else:
    st.caption("Apply different filters to get exportable results.")
