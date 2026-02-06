import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page config
st.set_page_config(page_title="Olympics History Dashboard", page_icon="🥇", layout="wide")

st.title("🥇 Olympic Games Analysis")
st.markdown("Explore historical data of the Modern Olympic Games.")

# --- Data Loading ---
@st.cache_data
def load_data():
    file_path = "athlete_events.csv"
    
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            st.toast("Loaded 'athlete_events.csv' from local directory!", icon="📂")
            return df
        except Exception as e:
            st.error(f"Error loading local CSV: {e}")
            return None
    else:
        # HARDCODED REAL SAMPLE DATA
        # Source: Historical records of top Olympians
        data = {
            'ID': range(1, 31),
            'Name': [
                'Michael Fred Phelps, II', 'Michael Fred Phelps, II', 'Michael Fred Phelps, II',
                'Larisa Semyonovna Latynina', 'Larisa Semyonovna Latynina',
                'Paavo Johannes Nurmi', 'Paavo Johannes Nurmi',
                'Mark Andrew Spitz', 'Mark Andrew Spitz',
                'Carl Lewis', 'Carl Lewis',
                'Usain St. Leo Bolt', 'Usain St. Leo Bolt', 'Usain St. Leo Bolt',
                'Nadia Elena Comaneci', 'Simone Arianne Biles',
                'Birgit Fischer-Schmidt', 'Edoardo Mangiarotti',
                'Jennifer Elisabeth "Jenny" Thompson', 'Sawao Kato',
                'Jesse Owens', 'Jesse Owens',
                'Florence Griffith Joyner', 'Sergey Bubka',
                'Yelena Isinbayeva', 'Haile Gebrselassie',
                'Rafael Nadal', 'Serena Williams',
                'LeBron James', 'Kevin Durant'
            ],
            'Sex': ['M', 'M', 'M', 'F', 'F', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'F', 'F', 'F', 'M', 'F', 'M', 'M', 'M', 'F', 'M', 'F', 'M', 'M', 'F', 'M', 'M'],
            'Age': [23, 19, 27, 22, 26, 23, 27, 22, 18, 23, 27, 21, 25, 29, 14, 19, 28, 32, 27, 26, 22, 22, 28, 24, 26, 27, 22, 30, 27, 32],
            'Height': [193, 193, 193, 161, 161, 174, 174, 183, 183, 188, 188, 195, 195, 195, 162, 142, 172, 178, 178, 163, 178, 178, 169, 183, 174, 164, 185, 175, 206, 208],
            'Weight': [82, 82, 82, 52, 52, 65, 65, 73, 73, 80, 80, 94, 94, 94, 45, 47, 65, 70, 68, 59, 71, 71, 57, 80, 65, 54, 85, 70, 113, 109],
            'Team': [
                'United States', 'United States', 'United States', 
                'Soviet Union', 'Soviet Union', 
                'Finland', 'Finland', 
                'United States', 'United States', 
                'United States', 'United States', 
                'Jamaica', 'Jamaica', 'Jamaica', 
                'Romania', 'United States', 
                'Germany', 'Italy', 
                'United States', 'Japan', 
                'United States', 'United States',
                'United States', 'Soviet Union',
                'Russia', 'Ethiopia',
                'Spain', 'United States',
                'United States', 'United States'
            ],
            'NOC': ['USA', 'USA', 'USA', 'URS', 'URS', 'FIN', 'FIN', 'USA', 'USA', 'USA', 'USA', 'JAM', 'JAM', 'JAM', 'ROU', 'USA', 'GER', 'ITA', 'USA', 'JPN', 'USA', 'USA', 'USA', 'URS', 'RUS', 'ETH', 'ESP', 'USA', 'USA', 'USA'],
            'Games': [
                '2008 Summer', '2004 Summer', '2012 Summer', 
                '1956 Summer', '1960 Summer', 
                '1920 Summer', '1924 Summer', 
                '1972 Summer', '1968 Summer', 
                '1984 Summer', '1988 Summer', 
                '2008 Summer', '2012 Summer', '2016 Summer', 
                '1976 Summer', '2016 Summer', 
                '1992 Summer', '1952 Summer', 
                '2000 Summer', '1972 Summer',
                '1936 Summer', '1936 Summer',
                '1988 Summer', '1988 Summer',
                '2008 Summer', '2000 Summer',
                '2008 Summer', '2012 Summer',
                '2012 Summer', '2020 Summer'
            ],
            'Year': [
                2008, 2004, 2012, 
                1956, 1960, 
                1920, 1924, 
                1972, 1968, 
                1984, 1988, 
                2008, 2012, 2016, 
                1976, 2016, 
                1992, 1952, 
                2000, 1972,
                1936, 1936,
                1988, 1988,
                2008, 2000,
                2008, 2012,
                2012, 2020
            ],
            'Season': ['Summer'] * 30,
            'City': [
                'Beijing', 'Athina', 'London', 
                'Melbourne', 'Rome', 
                'Antwerpen', 'Paris', 
                'Munich', 'Mexico City', 
                'Los Angeles', 'Seoul', 
                'Beijing', 'London', 'Rio de Janeiro', 
                'Montreal', 'Rio de Janeiro', 
                'Barcelona', 'Helsinki', 
                'Sydney', 'Munich',
                'Berlin', 'Berlin',
                'Seoul', 'Seoul',
                'Beijing', 'Sydney',
                'Beijing', 'London',
                'London', 'Tokyo'
            ],
            'Sport': [
                'Swimming', 'Swimming', 'Swimming', 
                'Gymnastics', 'Gymnastics', 
                'Athletics', 'Athletics', 
                'Swimming', 'Swimming', 
                'Athletics', 'Athletics', 
                'Athletics', 'Athletics', 'Athletics', 
                'Gymnastics', 'Gymnastics', 
                'Canoeing', 'Fencing', 
                'Swimming', 'Gymnastics',
                'Athletics', 'Athletics',
                'Athletics', 'Athletics',
                'Athletics', 'Athletics',
                'Tennis', 'Tennis',
                'Basketball', 'Basketball'
            ],
            'Event': [
                'Swimming Men\'s 100m Butterfly', 'Swimming Men\'s 200m Butterfly', 'Swimming Men\'s 4x100m Medley', 
                'Gymnastics Women\'s Individual All-Around', 'Gymnastics Women\'s Floor', 
                'Athletics Men\'s 10,000 metres', 'Athletics Men\'s 1,500 metres', 
                'Swimming Men\'s 100m Freestyle', 'Swimming Men\'s 4x100m Freestyle', 
                'Athletics Men\'s 100 metres', 'Athletics Men\'s Long Jump', 
                'Athletics Men\'s 100 metres', 'Athletics Men\'s 200 metres', 'Athletics Men\'s 4x100m Relay', 
                'Gymnastics Women\'s Uneven Bars', 'Gymnastics Women\'s Individual All-Around', 
                'Canoeing Women\'s K-1 500 metres', 'Fencing Men\'s Epee, Individual', 
                'Swimming Women\'s 4x100m Freestyle', 'Gymnastics Men\'s Individual All-Around',
                'Athletics Men\'s 100 metres', 'Athletics Men\'s Long Jump',
                'Athletics Women\'s 100 metres', 'Athletics Men\'s Pole Vault',
                'Athletics Women\'s Pole Vault', 'Athletics Men\'s 10,000 metres',
                'Tennis Men\'s Singles', 'Tennis Women\'s Doubles',
                'Basketball Men\'s Basketball', 'Basketball Men\'s Basketball'
            ],
            'Medal': [
                'Gold', 'Gold', 'Gold', 
                'Gold', 'Gold', 
                'Gold', 'Gold', 
                'Gold', 'Gold', 
                'Gold', 'Gold', 
                'Gold', 'Gold', 'Gold', 
                'Gold', 'Gold', 
                'Gold', 'Gold', 
                'Gold', 'Gold',
                'Gold', 'Gold',
                'Gold', 'Gold',
                'Gold', 'Gold',
                'Gold', 'Gold',
                'Gold', 'Gold'
            ]
        }
        
        # Creating multiple entries (rows) to simulate count for aggregating
        # Simply repeating the logic to make the dataset slightly bigger for visual effect
        # For simplicity, we stick to the list above which has ~30 rows of pure Gold winners
        
        df = pd.DataFrame(data)
        st.info("⚠️ Using embedded sample data (Real Historical Champions). Download 'athlete_events.csv' from Kaggle for the full experience.")
        return df

df = load_data()

if df is not None:
    # --- Sidebar ---
    st.sidebar.header("Filter Options")
    
    # Year Filter
    years = sorted(df['Year'].unique())
    selected_year = st.sidebar.multiselect("Select Year", years, default=years)
    
    # Sport Filter
    sports = sorted(df['Sport'].unique())
    selected_sport = st.sidebar.multiselect("Select Sport", sports, default=sports)
    
    # Country Filter
    countries = sorted(df['Team'].unique())
    selected_country = st.sidebar.multiselect("Select Country", countries, default=countries)

    # Filtering Data
    filtered_df = df[
        (df['Year'].isin(selected_year)) & 
        (df['Sport'].isin(selected_sport)) & 
        (df['Team'].isin(selected_country))
    ]

    # --- Metrics ---
    total_athletes = filtered_df['Name'].nunique()
    total_medals = len(filtered_df)
    total_countries = filtered_df['Team'].nunique()

    c1, c2, c3 = st.columns(3)
    c1.metric("🏅 Medals Shown", total_medals)
    c2.metric("🏃 Unique Athletes", total_athletes)
    c3.metric("🌍 Countries", total_countries)

    # --- Visualizations ---
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Medals by Country")
        medal_counts = filtered_df['Team'].value_counts().reset_index()
        medal_counts.columns = ['Country', 'Medals']
        fig_country = px.bar(medal_counts, x='Country', y='Medals', color='Medals', template='plotly_dark')
        st.plotly_chart(fig_country, use_container_width=True)

    with col2:
        st.subheader("📈 Medals over Time")
        if not filtered_df.empty:
            timeline = filtered_df.groupby('Year').size().reset_index(name='Medal Count')
            fig_line = px.line(timeline, x='Year', y='Medal Count', markers=True, template='plotly_dark')
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("No data for current filters.")

    st.subheader("🌟 Top Athletes")
    top_athletes = filtered_df['Name'].value_counts().reset_index().head(10)
    top_athletes.columns = ['Athlete', 'Medal Count']
    
    # Horizontal bar for athletes
    fig_athlete = px.bar(top_athletes, x='Medal Count', y='Athlete', orientation='h', 
                         color='Medal Count', template='plotly_dark', title="Most Decorated Athletes (in selection)")
    fig_athlete.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_athlete, use_container_width=True)

    with st.expander("📄 View Raw Data"):
        st.dataframe(filtered_df)

else:
    st.error("Could not load data.")
