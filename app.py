import streamlit as st
import pandas as pd

@st.cache_data
def load_data(path="data/Project_Tracking.csv"):
    """Load project tracking data from CSV."""
    # Load CSV, parsing numbers with commas (e.g., "987,311") correctly
    df = pd.read_csv(path, thousands=',')
    # Ensure 'Initial Estimated Savings' is numeric
    df['Initial Estimated Savings'] = pd.to_numeric(df['Initial Estimated Savings'], errors='coerce')
    return df

def main():
    st.set_page_config(page_title="Project Tracker", layout="wide")
    st.title("Project Tracker Dashboard")

    # Load data
    df = load_data()

    # Sidebar filters
    st.sidebar.header("Search and Select")

    # Additional sidebar filters
    area_options = df["Area"].dropna().unique().tolist()
    selected_areas = st.sidebar.multiselect("Filter by Area", options=area_options, default=area_options)
    status_options = df["Project Status"].dropna().unique().tolist()
    selected_status = st.sidebar.multiselect("Filter by Project Status", options=status_options, default=status_options)
    # Savings slider
    min_sav = int(df["Initial Estimated Savings"].min())
    max_sav = int(df["Initial Estimated Savings"].max())
    selected_savings = st.sidebar.slider(
        "Filter by Initial Estimated Savings",
        min_value=min_sav,
        max_value=max_sav,
        value=(min_sav, max_sav)
    )
    # General Area
    gen_area_options = df["General Area"].dropna().unique().tolist()
    selected_gen_areas = st.sidebar.multiselect(
        "Filter by General Area",
        options=gen_area_options,
        default=gen_area_options
    )

    search_query = st.sidebar.text_input("Search by ID or Title", "")
    # Filter as user types and apply additional filters
    mask = pd.Series([True] * len(df))
    # Search filter
    if search_query:
        mask &= (
            df["ID"].astype(str).str.contains(search_query, case=False, na=False)
            | df["Title"].str.contains(search_query, case=False, na=False)
        )
    # Conditional filters: only apply if the user selection is narrower than full options
    if len(selected_areas) < len(area_options):
        mask &= df["Area"].isin(selected_areas)
    if len(selected_status) < len(status_options):
        mask &= df["Project Status"].isin(selected_status)
    # Savings range filter (always applied)
    mask &= df["Initial Estimated Savings"].between(selected_savings[0], selected_savings[1])
    # Other multi-filters
    if len(selected_gen_areas) < len(gen_area_options):
        mask &= df["General Area"].isin(selected_gen_areas)
    filtered_df = df[mask]

    st.sidebar.write(f"Found {len(filtered_df)} projects")

    # Sorting
    sort_columns = ["ID", "Title", "Initial Estimated Savings", "Project Status"]
    sort_by = st.sidebar.selectbox("Sort by", options=sort_columns, index=2)
    ascending = st.sidebar.checkbox("Ascending order", value=False)
    filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)

    # Show filtered projects with "View Details" button for each
    st.subheader("Filtered Projects")
    if filtered_df.empty:
        st.write("No matching projects found.")
    else:
        # Initialize selection state
        if "selected_proj" not in st.session_state:
            st.session_state.selected_proj = None

        # List projects with buttons
        filtered_display = filtered_df.reset_index(drop=True)
        for idx, row in filtered_display.iterrows():
            cols = st.columns([1, 4, 1])
            cols[0].write(row["ID"])
            cols[1].write(row["Title"])
            if cols[2].button("View Details", key=f"view_{idx}"):
                st.session_state.selected_proj = row["ID"]

        # Show details for the selected project
        if st.session_state.selected_proj:
            # Safely retrieve the selected project
            matching = df[df["ID"] == st.session_state.selected_proj]
            if matching.empty:
                st.warning("Selected project not found. Please adjust filters or re-select a project.")
            else:
                project = matching.iloc[0]
                st.header(f"{project['ID']} - {project['Title']}")
                st.subheader("Project Details")
                for col in df.columns:
                    value = project.get(col, "")
                    st.markdown(f"**{col}:** {value}")

if __name__ == "__main__":
    main()
