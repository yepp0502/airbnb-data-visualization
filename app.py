import streamlit as st
import pandas as pd
import altair as alt

df = pd.read_csv('listings (1).csv')

# Clean the 'price' column: remove $ and commas
df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df = df[df['price'].notna()]

# st.write(df.head())

st.title("Airbnb Data Visualization")

st.sidebar.header("Filter Options")
st.sidebar.subheader("Select Price Range & Neighbourhood")
min_price = int(df['price'].min())
max_price = int(df['price'].max())

values = st.sidebar.slider("Select a price range", min_price, max_price, (min_price, max_price))
st.sidebar.write("Selected Price Range:", values)

option = df['neighbourhood_cleansed'].unique().tolist()
option.sort()

selection = st.sidebar.selectbox(
  "Neighbourhood",
  option,
  index=None,
  placeholder="Choose a neighbourhood to explore",
  accept_new_options=True,
)

st.sidebar.write("You selected:", selection)
  
st.subheader("Scatter Plot: Price vs Reviews per Month")

filtered_df = df[(df['price'] >= values[0]) & (df['price'] <= values[1])]
if selection:
  filtered_df = filtered_df[filtered_df['neighbourhood_cleansed'] == selection]

scatter = alt.Chart(filtered_df).mark_point(size=60).encode(
    x="price",
    y="reviews_per_month",
    color="neighbourhood_cleansed",
    tooltip=["name", "price", "reviews_per_month"]
).interactive()

st.altair_chart(scatter, use_container_width=True)


# Sidebar filter: Room Type
st.sidebar.subheader('2. Choose Room Type')
room_types = df['room_type'].dropna().unique().tolist()
selected_room = st.sidebar.selectbox("Room Type", ["All"] + room_types)

st.subheader("Host Acceptance Rate vs Review Scores Rating & Brushing by Neighbourhood")

# Apply Room Type Filter
if selected_room != "All":
    df_filtered = df[df['room_type'] == selected_room]
else:
    df_filtered = df.copy()

# Clean and prepare data on the filtered dataset
df_filtered['host_acceptance_rate'] = df_filtered['host_acceptance_rate'].str.replace('%', '', regex=False)
df_filtered['host_acceptance_rate'] = pd.to_numeric(df_filtered['host_acceptance_rate'], errors='coerce')
df_filtered['review_scores_rating'] = pd.to_numeric(df_filtered['review_scores_rating'], errors='coerce')
df_filtered['review_scores_value'] = pd.to_numeric(df_filtered['review_scores_value'], errors='coerce')

# Drop missing values
df_filtered = df_filtered.dropna(subset=['host_acceptance_rate', 'review_scores_rating', 'review_scores_value', 'neighbourhood_cleansed'])

# Remove outliers
df_filtered = df_filtered[abs(df_filtered['host_acceptance_rate'] - df_filtered['host_acceptance_rate'].mean()) / df_filtered['host_acceptance_rate'].std() <= 3]
df_filtered = df_filtered[abs(df_filtered['review_scores_rating'] - df_filtered['review_scores_rating'].mean()) / df_filtered['review_scores_rating'].std() <= 3]
df_filtered = df_filtered[abs(df_filtered['review_scores_value'] - df_filtered['review_scores_value'].mean()) / df_filtered['review_scores_value'].std() <= 3]

# Create brush selection
brush = alt.selection_interval(encodings=['x'])

# Scatter Plot: Host Acceptance Rate vs Review Scores Rating
scatter = alt.Chart(df_filtered).mark_point(size=60, opacity=0.7).encode(
    x=alt.X('host_acceptance_rate:Q', title='Host Acceptance Rate (%)'),
    y=alt.Y('review_scores_rating:Q', title='Review Scores Rating'),
    tooltip=['host_acceptance_rate', 'review_scores_rating']
).add_selection(
    brush
).properties(
    title='Host Acceptance Rate vs Review Scores',
    width=600,
    height=400
)

# Boxplot: Review Scores Value by Neighbourhood (filtered by brush)
boxplot = alt.Chart(df_filtered).mark_boxplot().encode(
    x=alt.X('neighbourhood_cleansed:N', title='Neighbourhood'),
    y=alt.Y('review_scores_value:Q', title='Review Scores Value'),
    color=alt.Color('neighbourhood_cleansed:N', legend=None)
).transform_filter(
    brush
).properties(
    title='Review Scores Value by Neighbourhood (Filtered by Acceptance Rate)',
    width=600,
    height=400
)

# Display side-by-side charts
st.altair_chart(scatter & boxplot)

# Sidebar filter: Room Type
st.sidebar.subheader('3. Explore Each Id')
id_type = df['id'].dropna().unique().tolist()
selected_id = st.sidebar.selectbox("Id", id_type)

if selected_id:
  df_filtered = df[df['id'] == selected_id]

review_cols = [
    'review_scores_rating',
    'review_scores_accuracy',
    'review_scores_cleanliness',
    'review_scores_checkin',
    'review_scores_communication',
    'review_scores_value'
]

# Melt the data to long format
df_melted = df_filtered.melt(
    value_vars=review_cols,
    var_name='Review Category',
    value_name='Score'
)

# Create the bar chart
st.subheader("Review Categories Based on Id")
st.write("Name: ", df_filtered['name'].iloc[0])
st.write("Id: ", selected_id)

bar = alt.Chart(df_melted).mark_bar().encode(
    x=alt.X('Review Category:N', sort=review_cols),
    y=alt.Y('Score:Q'),
    color=alt.Color('Review Category:N')
).properties(
    width=500,
    height=300
)

st.altair_chart(bar)



