import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os
import gdown


st.set_page_config(page_title="🏏 ipl", layout="wide")
# -------------------------------------------------------------------------------
#         Functional Logic
# -----------------------------------------------------------------------------

def match_type_wise(type):
    matches['Wining Margin'] = matches['result_margin'].astype(str) + ' ' + matches['result']
    match_type_df = matches[matches['match_type'] == type][['season','winner','Wining Margin','opponent','player_of_match']].sort_values('season', ascending=False).reset_index(drop=True)
    match_type_df = match_type_df.rename(columns={'season':'Season','winner':'Winner','opponent':'Opponent','player_of_match':'Player of Match'})
    match_type_df.index = range(1 , len(match_type_df) +1)
    return match_type_df

# Performance of teams
def success_ratio_func_season(team_name):                  # Find the success rate of any team
    total_match_played = matches_season[matches_season['team1']== team_name].shape[0] + matches_season[matches_season['team2']==team_name].shape[0]
    total_win = matches_season[matches_season['winner'] == team_name].shape[0]
    success_ratio = round((total_win/total_match_played) * 100,2)
    return success_ratio

def success_ratio_graph_season(matches_season):            # Success Ratio Graph plot
    all_teams = pd.unique(matches_season[['team1', 'team2']].values.ravel())  # Combine both columns and get unique values
    success_rate_all_teams = []    # Making list of all teams success rate
    for i in (all_teams):
        rate = success_ratio_func_season(i)
        success_rate_all_teams.append(rate)
    
    
    df_success_rate_all_teams = pd.DataFrame({             # Dataframe of success_rate_all_teams 
        'team_name': all_teams,
        'success_rate': success_rate_all_teams
    }) 
    # Arange alphabetical order
    df_success_rate_all_teams = df_success_rate_all_teams.sort_values('team_name').reset_index(drop=True)
    
    # Bar chart
    fig_m = plt.figure(figsize=(10,5))
    bars = plt.bar(df_success_rate_all_teams['team_name'],df_success_rate_all_teams['success_rate'], color='skyblue')
    
    for bar in bars:                                       # Add value labels on top of each bar
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.2f}%', 
             ha='center', va='bottom', fontsize=9)
    
    plt.xticks(rotation=45, ha='right')
    plt.title(f'Success Rate of IPL Teams {season_selected}')
    plt.xlabel('Team Name')
    plt.ylabel('Success Rate (%)')
    plt.grid(axis='y')
    plt.tight_layout()
    st.pyplot(fig_m)

def batter_high_score(name):
    batter_df = deliveries[deliveries['batter'] == name]
    high_score = batter_df.groupby('match_id')['batsman_runs'].sum().sort_values(ascending=False).values[0]
    return high_score

def batter_total_runs(name):
    total_runs = deliveries[deliveries['batter'] == name]['batsman_runs'].sum()
    return total_runs

def strike_rate_batter(name):
    total_ball_played = deliveries[(deliveries['batter'] == name) & (deliveries['extras_type'] != 'wides') & (deliveries['extras_type'] != 'noballs')].shape[0]
    total_run = deliveries[deliveries['batter'] == name]['batsman_runs'].sum()
    s_rate= round((total_run/total_ball_played)*100,2)
    return s_rate

def batter_hundreds(name):
    season_match_batter_run = deliveries.groupby(['season','match_id', 'batter'])['batsman_runs'].sum().reset_index(name='run')
    num_hundreds = season_match_batter_run[(season_match_batter_run['run'] >= 100) & (season_match_batter_run['batter'] == name)].shape[0]
    return num_hundreds

def batter_fifties(name):
    
    season_match_batter_run = deliveries.groupby(['season','match_id', 'batter'])['batsman_runs'].sum().reset_index(name='run')
    num_fifties= season_match_batter_run[(season_match_batter_run['run'] >= 50) & (season_match_batter_run['run'] < 100) & (season_match_batter_run['batter'] == name)].shape[0]
    return num_fifties

def not_out(name):
    num_of_dismissed = deliveries[deliveries['player_dismissed'] == name].shape[0]
    num_of_matches = deliveries[deliveries['batter'] == name]['match_id'].nunique()
    not_dismissed = num_of_matches - num_of_dismissed
    return not_dismissed

def season_wise_run_graph(name):
    player_df = deliveries[deliveries['batter'] == name]
    season_wise_run = player_df.groupby('season')['batsman_runs'].sum().reset_index(name='total_run')
        
    # Bar chart
    fig_season = plt.figure(figsize=(10,5))
    bars = plt.bar(season_wise_run['season'], season_wise_run['total_run'], color='skyblue')
    
    for bar in bars:                                       # Add value labels on top of each bar
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height, f'{height}', 
             ha='center', va='bottom', fontsize=9)
    
    plt.xticks(ticks=season_wise_run['season'].unique(), labels=season_wise_run['season'].unique(), rotation=45, ha='right') # Force x-axis to use only integer ticks
    plt.title(f'Season-wise Score of {name}')
    plt.xlabel('Seasons')
    plt.ylabel('Total Score')
    plt.grid(axis='y')
    plt.tight_layout()
    st.pyplot(fig_season)

def dismissal_kind_batter(name):             # Bar Chart ----> Dismissal Kind
    fig_bar = plt.figure(figsize=(8,3))
    dismissal_kind_df = deliveries[deliveries['batter'] == name]['dismissal_kind'].value_counts().reset_index(name='count')
    plt.barh(dismissal_kind_df['dismissal_kind'], dismissal_kind_df['count'])
    plt.title(f"Dismissal Type: {name}")
    plt.xlabel('Number of Dismissals')
    plt.ylabel('Dismissal Kind')
    plt.grid(axis='x')
    plt.tight_layout()
    st.pyplot(fig_bar)

def top_n_batsman(num):
    top_batsmans = (deliveries.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(num).reset_index())
    top_batsmans.index = range(1, len(top_batsmans) + 1)
    top_batsmans = top_batsmans.rename(columns = {'batter':'Batsman Name','batsman_runs':'Batsman Runs',})
    return top_batsmans

def top_n_bowler(num):
    valid_dismissals = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled']
    filtered_df = deliveries[deliveries['dismissal_kind'].isin(valid_dismissals)]
    wicket_counts = filtered_df.groupby('bowler').size().reset_index(name='Wickets')
    top_bowlers = wicket_counts.sort_values(by='Wickets', ascending=False).head(num).reset_index(drop=True)
    top_bowlers.index = range(1, len(top_bowlers) + 1)
    top_bowlers = top_bowlers.rename(columns = {'bowler': 'Bowler Name', 'Wickets': 'Wickets'})
    return top_bowlers

# --------->  Bowler Performance -----------> all
@st.cache_data
def bowler_performance_all():
    # 1. Total Wicket Taken 
    valid_dismissals = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled']
    bowler_wickets = bowler_ball_wise_df[bowler_ball_wise_df['dismissal_kind'].isin(valid_dismissals)].shape[0]
    
    # 2. Bowling Average
    batsman_runs_conceded = bowler_ball_wise_df['batsman_runs'].sum()
    extra_runs_conceded = bowler_ball_wise_df[bowler_ball_wise_df['extras_type'].isin(['wides','noballs'])]['extra_runs'].sum()
    total_runs_conceded = batsman_runs_conceded + extra_runs_conceded
    if bowler_wickets > 0:
        bowling_average = round(total_runs_conceded/bowler_wickets, 2)
    else:
        bowling_average = 0
    
    # 3. Economy Rate
    legal_balls_over = bowler_ball_wise_df[bowler_ball_wise_df['ball'] <= 6].shape[0]
    over_bowled = legal_balls_over/6
    if over_bowled> 0:
        economy_rate = round(total_runs_conceded/over_bowled,2)
    else:
        economy_rate = 0
    
    # 4. Strike Rate
    if bowler_wickets > 0:
        strike_rate = round(total_runs_conceded/bowler_wickets, 2)
    else:
        strike_rate = 0
    
    # 5. Dot Ball Percentage
    dot_balls = (bowler_ball_wise_df['total_runs'] == 0).sum()
    total_legal_deliveries = bowler_ball_wise_df[~bowler_ball_wise_df['extras_type'].isin(['wides','noballs'])].shape[0]
    if total_legal_deliveries > 0:
        dot_ball_percentage = round((dot_balls/total_legal_deliveries) * 100, 2)
    else:
        dot_ball_percentage = 0
    
    # 6. Boundary Percentage
    boundaries = (bowler_ball_wise_df['batsman_runs'].isin([4 , 6])).sum()
    if boundaries > 0:
        boundary_percentage = round((boundaries/total_legal_deliveries)*100)
    else:
        boundary_percentage = 0
    
    # 7. Runs per Over
    if over_bowled > 0:
        runs_per_over = round(total_runs_conceded/over_bowled, 2)
    else:
        runs_per_over = 0
    
    # 8. Batting Contribution
    batting_contribution = batting_contribution_df['batsman_runs'].sum()
    
    bowler_performance_df = pd.DataFrame({
        'Wicket Taken': [bowler_wickets],
        'Bowling Average':[bowling_average],
        'Economy Rate': [economy_rate],
        'Strike Rate': [strike_rate],
        'Dot Ball %' : [dot_ball_percentage],
        'Boundary %' : [boundary_percentage],
        'Runs per Over': [runs_per_over],
        'Batting Contribution': [batting_contribution],
        'Overs Bowled': [round(over_bowled, 2)]
    })
    return bowler_performance_df

def batter_vs_bowler(batter_name, bowler_name):
    batter_bowler_df = deliveries[(deliveries['batter'] == batter_name) & (deliveries['bowler'] == bowler_name)]
    total_bowled = batter_bowler_df.shape[0]
    total_run = batter_bowler_df['batsman_runs'].sum()
    six_count = (batter_bowler_df['batsman_runs'] == 6).sum()
    four_count = (batter_bowler_df['batsman_runs'] == 4).sum()
    dot_balls = (batter_bowler_df['batsman_runs'] == 0).sum()

    if total_bowled > 0:                                                # Strike rate for batter
        strike_rate_batter = round(total_run / total_bowled * 100,2)
    else:
        strike_rate_batter = 0

    wicket = batter_bowler_df['player_dismissed'].notna().sum()     # Wickets and strike rate for bowler
    
    if wicket > 0:
        strike_rate_bowler = round(total_bowled / wicket, 2)
        
    else:
        strike_rate_bowler = 0
    
    data = [{               # Create a DataFrame
        "Balls": total_bowled,
        "Runs": total_run,
        "S/R (Batsman)": strike_rate_batter,
        "6's": six_count,
        "4's": four_count,
        "Dot's": dot_balls,
        "Wickets": wicket,
        "S/R (Bowler)": strike_rate_bowler
    }]
    df = pd.DataFrame(data)
    return df

# --------------------------------------------------------------------------------------
#          Streamlit App
# -------------------------------------------------------------------------------------

st.header(' 🏏 IPL Performance Analyzer')

# Import datasets
matches = pd.read_csv('data/matches_clean_data.csv')

##########################
# deliveries = pd.read_csv('data/deliveries_clean_data.csv')
############
@st.cache_data
def load_deliveries():
    file_path = 'data/deliveries_clean_data.csv'
    if not os.path.exists(file_path):
        # st.info("Downloading similarity matrix from Google Drive...")
        file_id = "1uhm9ib9-X8PhxFKciaNm5y0isVVqeGlZ"   # https://drive.google.com/file/d/1uhm9ib9-X8PhxFKciaNm5y0isVVqeGlZ/view?usp=sharing
        url = f"https://drive.google.com/uc?id={file_id}"
        os.makedirs('data', exist_ok=True)
        gdown.download(url, file_path, quiet=False)
    return pd.read_csv(file_path)
deliveries = load_deliveries()
###############

batter_list = sorted(deliveries['batter'].unique())
bowler_list = sorted(deliveries['bowler'].unique())
#--------------------------------------------------------------------------------------
#           Sidebar
#--------------------------------------------------------------------------------------
sidebar_radio = st.sidebar.radio('Select to Explore',options=['About IPL','🏆 Winners List','📈 Team Performance','🏅 Top Players',"🏏 Batsman's Performance","🏃‍♂️ Bowler's Performance",'⚔️ Batsman vs Bowler'])
# --------------------------------------
#           About IPL
#---------------------------------------
if sidebar_radio == 'About IPL':
    st.subheader('About the Indian Premier League (IPL)')
    st.markdown("""
    <p style='text-align: justify;'>
    The Indian Premier League (IPL) is a professional Twenty20 cricket league founded by the Board of Control for Cricket in India 
    (BCCI) in 2008. It has grown into one of the most popular and financially successful cricket tournaments in the world.
    Played annually during the Indian summer (March to May), the IPL features top international and domestic players competing 
    in a fast-paced, highly entertaining format.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='text-align: justify;'>
    The league began with eight franchise teams representing major Indian cities, and it has since expanded and evolved, both in 
    terms of viewership and cricketing innovation. The inaugural champions were the Rajasthan Royals, while Mumbai Indians and 
    Chennai Super Kings have become two of the most successful teams in IPL history.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='text-align: justify;'>
    With a mix of explosive batting, strategic bowling, cutting-edge technology, and passionate fan support, the IPL has transformed 
    cricket into a global spectacle. It serves as a platform for emerging talents and is known for its high energy, thrilling 
    finishes, and cricketing excellence.
    </p>
    """, unsafe_allow_html=True)
# --------------------------------------
#           Winners List
#---------------------------------------
elif sidebar_radio == '🏆 Winners List':
    st.subheader("Match Winners List")
    match_type_list = ['Final','Qualifier 1','Qualifier 2','Eliminator','Semi Final','Elimination Final', "3rd Place Play-Off"]
    match_selected = st.selectbox("Select Match Type:", options= match_type_list)
    st.table(match_type_wise(match_selected))

# --------------------------------------
#           Performance of Teams
#---------------------------------------
elif sidebar_radio == '📈 Team Performance':         # Success rate of each team --> season-wise
    with st.container(border=True):
        st.subheader("Success Rate of Each Team")
        season_list = ["All"] + sorted(matches['season'].unique(), reverse=True)

        season_selected = st.selectbox("Select Season:", options= season_list)
        if season_selected == 'All':
            matches_season = matches
            success_ratio_graph_season(matches)
        else:
            matches_season = matches[matches['season']==season_selected]
            success_ratio_graph_season(matches_season)
    with st.container(border=True):
        df_pie = match_type_wise('Final').groupby('Winner')['Winner'].value_counts().reset_index()
        fig_pie = plt.figure()
        plt.pie(df_pie['count'], labels = df_pie['Winner'], autopct='%1.0f%%')
        plt.title("Champion Percentage")
        st.pyplot(fig_pie)
# --------------------------------------
#           Top Players
#---------------------------------------
elif sidebar_radio == '🏅 Top Players':        # Top nth Batsmans & Bowlers
    tab1, tab2 = st.tabs(['🏏 Batsman', '🏃‍♂️ Bowler'])
    with tab1:
        with st.container(border=True):          
            st.subheader('Top Batsmen in IPL History')
            no_of_players = st.radio("Select the number of Players:", options=[10,15,20,25,30], horizontal=True, key=1)
            
            if no_of_players == no_of_players:
                col1, col2 = st.columns([1,2])
                with col1.container(border=True):
                    st.subheader('Top Batsmen')
                    st.table(top_n_batsman(no_of_players))
                with col2.container(border=True):
                    st.subheader("Top 10 Batsmen in IPL History")
                    top_batsmen = top_n_batsman(no_of_players).sort_values('Batsman Runs')
                    fig3, ax3 = plt.subplots(figsize=(10, no_of_players*.77))
                    ax3.barh(top_batsmen['Batsman Name'], top_batsmen['Batsman Runs'], color="skyblue")
                    ax3.set_xlabel("Total Runs")
                    # ax3.set_ylabel("Batsman")
                    ax3.set_title("Top 10 Batsmen in IPL History")
                    st.pyplot(fig3)
    with tab2:
        with st.container(border=True):          
            st.subheader('Top Bowlers in IPL History')
            no_of_players = st.radio("Select the number of Players:", options=[10,15,20,25,30], horizontal=True, key=2)
            
            if no_of_players == no_of_players:
                col1, col2 = st.columns([1,2])
                with col1.container(border=True):
                    st.subheader('Top Bowlers')
                    st.table(top_n_bowler(no_of_players))
                with col2.container(border=True):
                    st.subheader("Top 10 Bowlers in IPL History")
                    top_batsmen = top_n_bowler(no_of_players).sort_values('Wickets')
                    fig3, ax3 = plt.subplots(figsize=(10, no_of_players*.7))
                    ax3.barh(top_batsmen['Bowler Name'], top_batsmen['Wickets'], color="skyblue")
                    ax3.set_xlabel("Total Wickets")
                    # ax3.set_ylabel("Bowler")
                    ax3.set_title("Top 10 Bowlers in IPL History")
                    st.pyplot(fig3)
    
# --------------------------------------
#          Batsman's Performance
#---------------------------------------
elif sidebar_radio == "🏏 Batsman's Performance":                    # Display score of batsman
    st.subheader('Batsman Insights: IPL Career Summary')
    
    with st.container(border=True):
        batter_list.insert(0,"None")
        selected_batter = st.selectbox("Select a batsman for scores in IPL:",options= batter_list)
        if selected_batter != "None":
            with st.container(border=True):
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("High Score", batter_high_score(selected_batter))
                col2.metric("Total Score", batter_total_runs(selected_batter))
                col3.metric("Strike Rate", strike_rate_batter(selected_batter))
                col4.metric("Match Played", deliveries[deliveries['batter'] == selected_batter]['match_id'].nunique())
                col1.metric("Ducks", (deliveries[deliveries['batter']== selected_batter].groupby('match_id')['batsman_runs'].sum() == 0).sum())
                col2.metric("Hundreds", batter_hundreds(selected_batter))
                col3.metric("Fifties", batter_fifties(selected_batter))
                col4.metric("Not Out", not_out(selected_batter))    

            with st.container(border=True):
                season_wise_run_graph(selected_batter)
            with st.container(border=True):
                dismissal_kind_batter(selected_batter)
        else:
            pass
# --------------------------------------
#           Bowler's Performance
#---------------------------------------
elif sidebar_radio == "🏃‍♂️ Bowler's Performance":
    st.subheader('Bowler Insights: IPL Career Summary')
    
    with st.container(border=True):
        bowler_list.insert(0, "None")
        selected_bowler = st.selectbox("Select a bowler for scores in IPL:",options= bowler_list)

        if selected_bowler != "None":
            with st.container(border=True):
                bowler_ball_wise_df = deliveries[deliveries['bowler'] == selected_bowler].reset_index(drop=True)
                batting_contribution_df = deliveries[deliveries['batter'] == selected_bowler].reset_index(drop=True)
                df = bowler_performance_all()
                st.subheader("All Season's Performance")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Wicket Taken", df['Wicket Taken'].values[0])
                col2.metric('Bowling Average',df['Bowling Average'].values[0])
                col3.metric('Economy Rate', df['Economy Rate'].values[0])
                col4.metric('Strike Rate', df['Strike Rate'].values[0])
                col1.metric('Dot Ball %', df['Dot Ball %'].values[0])
                col2.metric('Boundary %	', df['Boundary %'].values[0])
                col3.metric('Runs per Over', df['Runs per Over'].values[0])
                col4.metric('Batting Contribution', df['Batting Contribution'].values[0])
                col1.metric("Over Bowled", df['Overs Bowled'].values[0])
                st.cache_data.clear()

            season_list = ["Please Select Season"] + sorted(bowler_ball_wise_df['season'].unique())
            selected_season = st.selectbox("Select Season:", options=season_list)
            if selected_season != "Please Select Season":
                with st.container(border=True):
                    bowler_ball_wise_df = bowler_ball_wise_df[bowler_ball_wise_df['season'] == selected_season]
                    batting_contribution_df = batting_contribution_df[batting_contribution_df['season'] == selected_season]
                    df_name_season = bowler_performance_all()
                    st.subheader('Season wise Bowler Performance')
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Wicket Taken", df_name_season['Wicket Taken'].values[0])
                    col2.metric('Bowling Average',df_name_season['Bowling Average'].values[0])
                    col3.metric('Economy Rate', df_name_season['Economy Rate'].values[0])
                    col4.metric('Strike Rate', df_name_season['Strike Rate'].values[0])
                    col1.metric('Dot Ball %', df_name_season['Dot Ball %'].values[0])
                    col2.metric('Boundary %	', df_name_season['Boundary %'].values[0])
                    col3.metric('Runs per Over', df_name_season['Runs per Over'].values[0])
                    col4.metric('Batting Contribution', df_name_season['Batting Contribution'].values[0])
                    col1.metric("Over Bowled", df_name_season['Overs Bowled'].values[0])
                    st.cache_data.clear()
            else:
                pass

        else:
            pass
# --------------------------------------
#         Batsman Vs Bowler
#---------------------------------------
elif sidebar_radio == '⚔️ Batsman vs Bowler':
    with st.container(border=True):          # Batsman vs Bowler performence
        batter_list.insert(0,"None")
        st.subheader("Batsman Vs Bowler in IPL History")
        col1, col2 =st.columns(2)
        
        selected_batter_comparison = col1.selectbox("Batsman to compare: ", options= batter_list)
        bowler_list_batter = ["None"] + sorted(deliveries[deliveries['batter'] == selected_batter_comparison]['bowler'].unique())
        selected_bowler_comparison = col2.selectbox("Bowler to compare: ", options= bowler_list_batter)

        if ((selected_batter_comparison != "None") & (selected_bowler_comparison != "None")):
            df = batter_vs_bowler(selected_batter_comparison, selected_bowler_comparison)
            st.write("---")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Balls", df['Balls'])
            col2.metric("Total Runs", df['Runs'])
            col3.metric("S/R (Batsman)", df['S/R (Batsman)'])
            col4.metric("Dot Balls", df["Dot's"])

            col1.metric("Six's", df["6's"])
            col2.metric("Four's", df["4's"])
            col3.metric("Wickets", df["Wickets"])
            col4.metric("S/R (Bowler)", (df["S/R (Bowler)"]))

#---------------------------------------------------------
# Footer
#----------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<hr style="margin-top: 30px;">
<div style="text-align: center; font-size: 0.9em; color: gray;">
    Created by <b>Partho Sarothi Das</b><br>
    <i>Aspiring Data Scientist | Passionate about ML & Visualization</i><br>
    Email: <a href="mailto:partho52@gmail.com">partho52@gmail.com</a>
</div>
""", unsafe_allow_html=True)
