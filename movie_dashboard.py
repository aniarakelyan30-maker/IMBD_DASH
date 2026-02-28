"""
IMDB Top 1000 Movies Interactive Dashboard
==========================================
A comprehensive Dash application for exploring and analyzing IMDB's top 1000 movies.



This dashboard allows users to:
- Filter movies by year range, genres, and rating thresholds
- Explore relationships between ratings, votes, and financial performance
- Identify trends in cinema over multiple decades
- Analyze director and genre performance metrics
"""

# ============================================================================
# IMPORTS
# ============================================================================
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# DATA LOADING AND PREPROCESSING
# ============================================================================

def load_and_preprocess_data():
    """
    Load the IMDB dataset and perform necessary data cleaning and preprocessing.
    
    Processing steps:
    1. Load CSV file
    2. Handle missing values
    3. Parse runtime (remove ' min' suffix and convert to numeric)
    4. Clean Gross revenue (remove commas)
    5. Create additional feature columns
    6. Extract genre list for filtering
    
    Returns:
        DataFrame: Cleaned and preprocessed movie data
    """
    
    df = pd.read_csv('imdb_top_1000.csv')
    # pd.to_numeric - սա պանդասի ֆունկցիա է, որն օգտագործվում է տվյալ սյունը թվային փոխակերպելու համար։

    # Convert Released_Year to numeric, fill NaN with the median year
    # errors='coerce' նշանակում է՝ եթե տվյալը չի կարող փոխակերպվել թվային արժեքի, ապա այն կվերածվի NaN:
    df['Released_Year'] = pd.to_numeric(df['Released_Year'], errors='coerce')
    df['Released_Year'].fillna(df['Released_Year'].median(), inplace=True)
    df['Released_Year'] = df['Released_Year'].astype(int) 
    # այստեղ փոխում ենք ամբողջ թվի
    
    # Parse runtime: remove ' min' and convert to integer
    df['Runtime_Minutes'] = df['Runtime'].str.replace(' min', '').astype(int)
    # այստեղ ֆիլմի րոպեները ևս թվային արժեքի ենք վերափոխում , որպեսզի հետագայում վիզուալիզացիայում օգտագործենք։
    
    # Clean Gross revenue: remove commas and convert to numeric
    df['Gross'] = pd.to_numeric(df['Gross'].str.replace(',', ''), errors='coerce')
    
    # Create a numerical decade column for analysis
    df['Decade'] = (df['Released_Year'] // 10 * 10).astype(int)
    
    # Split genres into lists (comma-separated in original data)
    df['Genre_List'] = df['Genre'].str.split(', ')
    # այստեղ ժանրերը պատճենում ենք որպես ցուցակ, որպեսզի հետագայում ֆիլտրելիս օգտագործենք։
    
    # Ensure Meta_score is numeric (handle missing values)
    df['Meta_score'] = pd.to_numeric(df['Meta_score'], errors='coerce')
    # մետա սկորը դա ֆիլմի որակի լրացուցիչ գնահատական է։ այստեղ այն նույնպես թվային արժեքի ենք վերափոխում։
    # մետա սկորը ցույց է տալիս թե ֆիլմը որքանով է համապատասխանում քննադատների կարծիքներին հաշված IMDB գնահատականից։
    
    # Create rating categories (4 bins = 3 labels)
    df['Rating_Category'] = pd.cut(df['IMDB_Rating'], 
                                    bins=[0, 7, 8, 9, 10.1], 
                                    labels=['Low (<7)', 'Good (7-8)', 'Very Good (8-9)', 
                                           'Excellent (9+)'])
    # այստեղ ստեղծում ենք ֆիլմերի գնահատականների կատեգորիաներ՝ ըստ IMDB գնահատականի։
    
    # Calculate revenue per vote (proxy for financial impact)
    df['Revenue_Per_Vote'] = df['Gross'] / df['No_of_Votes']
    df['Revenue_Per_Vote'] = df['Revenue_Per_Vote'].fillna(0)
    # այստեղ ստեղծում ենք նոր սյուն՝ որը ցույց է տալիս յուրաքանչյուր քվեի դիմաց եկամուտը։
    # այսինքն՝ որքան գումար է բերել ֆիլմը յուրաքանչյուր քվեի դիմաց։
    # քանի որ ֆիլմերի եկամուտը կարող է բացակայել,
    # այդ դեպքում այն լցնում ենք 0-ով։ սա պարզապես, որպեսզի հասկաանանք կապը քվեի և եկամուտի միջև։
    
    # Handle missing values
    df['Gross'].fillna(0, inplace=True)
    df['Meta_score'].fillna(df['Meta_score'].mean(), inplace=True)
    # այստեղ լրացնում ենք բաց թողնված արժեքները՝ եկամուտը 0-ով, իսկ մետա սկորը՝ միջին արժեքով։
    
    return df

# Load the data
df = load_and_preprocess_data()

# Get unique genres for dropdown filter
all_genres = sorted(list(set([genre for genres in df['Genre_List'] for genre in genres])))
# այստեղ ստեղծում ենք ժանրերի ամբողջական ցուցակը՝ ֆիլտրի համար։
# դա անում ենք այսպես՝ վերցնում ենք յուրաքանչյուր ֆիլմի ժանրերի ցուցակը,
# այնուհետև բոլոր ժանրերը դնում ենք մեկ ընդհանուր ցուցակի մեջ և վերցնում
#  միայն եզակի արժեքները՝ օգտագործելով set()։

# ============================================================================
# INITIALIZE DASH APP
# ============================================================================

app = dash.Dash(__name__)
app.title = "IMDB Movies Dashboard - Interactive Analytics"

# Define color scheme
COLOR_PRIMARY = '#1f77b4'
COLOR_SECONDARY = '#ff7f0e'
COLOR_SUCCESS = '#2ca02c'
COLOR_DANGER = '#d62728'
COLOR_WARNING = '#ff9800'

# այստեղ սահմանում ենք գույների պալիտրա՝ վիզուալիզացիաների համար։

# ============================================================================
# DEFINE APP LAYOUT
# ============================================================================

# սա իրենից ներկայացնում է Dash հավելվածի գլխավոր կառուցվածքը՝
# որը բաղկացած է տարբեր բաժիններից՝ հեդեր, ֆիլտրեր, մետրիկներ, վիզուալիզացիաներ և ֆուտեր։

# հեդերը պարունակում է հավելվածի վերնագիրը և նկարագրությունը, դա այն հատվածն է,
# որը տեսնում է օգտատերը առաջինը։ օրինակ՝ վերնագիրը "IMDB Top 1000 Movies Dashboard" և նկարագրությունը
# "Interactive analytics and visualization of IMDB's highest-rated films"- սա ցույց է տալիս, թե ինչ է անում հավելվածը։
# 

# կոդի կառուցվածքը հետևյալն է՝ app.layout = html.Div([ - այստեղ սկսվում է գլխավոր բաժինը։
#  սա html.Div է, որը պարունակում է բոլոր ենթաբաժինները։
# html.Div([]) - սա ենթաբաժին է, որը կարող է պարունակել այլ HTML տարրեր կամ Dash կոմպոնենտներ։
#  օրինակ՝ հեդերը, ֆիլտրերը, մետրիկները և այլն։ այսինքն html.Div-ը օգտագործվում է տարբեր բաժիններ ստեղծելու համար։
# լեյաութը էջի սկելետն է, որը սահմանում է, թե ինչպես են տարրերը դասավորված և ինչպես են դրանք փոխազդում իրար հետ, 
# իսկ տարրեր ասելով՝ նկատի ունենք տարբեր վիզուալ կոմպոնենտներ, ինչպիսիք են գրաֆիկները, սլայդերները, կոճակները և այլն։

app.layout = html.Div([
    # սա հիմնական բաժինն է, որը պարունակում է բոլոր ենթաբաժինները։
    # Header Section
    html.Div([
    # սա այն հատվածն է, որը տեսնում է օգտատերը առաջինը։
        html.Div([
            # սա այն հատվածն է, որը պարունակում է հավելվածի վերնագիրը և նկարագրությունը։
            html.H1("🎬 IMDB Top 1000 Movies Dashboard", 
                   style={'margin': '0', 'color': 'white', 'fontSize': '2.5em'}),
            html.P("Interactive analytics and visualization of IMDB's highest-rated films",
                  style={'margin': '10px 0 0 0', 'color': 'rgba(255,255,255,0.8)', 'fontSize': '1.1em'})
        ], style={'padding': '30px'})
    ], style={
        'backgroundColor': '#1a1a2e',
        'marginBottom': '30px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    }),
    # այսեղ մենք ինչ արեցինք - ստեղծեցինք html.Div, որը պարունակում է հեդերի բաժինը։
    # Main Container
    html.Div([
        # ====================================================================
        # FILTER SECTION
        # ====================================================================
        html.Div([
            html.H2("📊 Filter Options", style={'marginBottom': '20px', 'color': '#1a1a2e'}),
        #  ստեղ մենք ստեղծեցինք ֆիլտրերի բաժինը՝ որը թույլ է տալիս օգտատերերին ֆիլտրել տվյալները ըստ տարբեր չափանիշների։

            html.Div([
                # Year Range Slider
                html.Div([
                    html.Label("Year Range:", style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='year-slider',
                        min=df['Released_Year'].min(),
                        max=df['Released_Year'].max(),
                        step=1,
                        value=[df['Released_Year'].min(), df['Released_Year'].max()],
                        marks={str(year): str(year) for year in range(
                            df['Released_Year'].min(), 
                            df['Released_Year'].max() + 1, 
                            10)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                ], style={'marginBottom': '25px'}),
                
                # Genre Dropdown
                html.Div([
                    html.Label("Select Genre (Optional):", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='genre-dropdown',
                        options=[{'label': 'All Genres', 'value': 'all'}] + 
                                [{'label': genre, 'value': genre} for genre in all_genres],
                        value='all'
                    ),
                ], style={'marginBottom': '25px'}),
                
                # Rating Threshold Slider
                html.Div([
                    html.Label("Minimum IMDB Rating:", style={'fontWeight': 'bold'}),
                    dcc.Slider(
                        id='rating-slider',
                        min=5,
                        max=10,
                        step=0.1,
                        value=5,
                        marks={i: f'{i}.0' for i in range(5, 11)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                ], style={'marginBottom': '25px'}),
                
                # Reset Filters Button
                html.Button(
                    '🔄 Reset Filters',
                    id='reset-button',
                    n_clicks=0,
                    #   - սա կոճակ է, որը օգտագործվում է ֆիլտրերը վերականգնելու համար։  0-ն նշանակում է, որ սկզբում կոճակը չի սեղմված։
                    style={
                        'padding': '12px 24px',
                        'backgroundColor': COLOR_PRIMARY,
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'fontSize': '1em',
                        'marginTop': '10px'
                    }
                ),
            ], style={
                'backgroundColor': '#f5f5f5',
                'padding': '20px',
                'borderRadius': '8px',
                'marginBottom': '25px'
            }),
        ], style={
            'backgroundColor': 'white',
            'padding': '25px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
            'marginBottom': '30px'
        }),
        
        # ====================================================================
        # SUMMARY METRICS SECTION
        # ====================================================================
# այս հատվածը ցույց է տալիս հիմնական մետրիկները՝ որոնք թարմացվում են ֆիլտրերի հիման վրա։սա գտնվում է 
# ֆիլտրերի տակ քանի որ այն կարևոր տեղեկատվություն է տալիս օգտատիրոջը։
# սրանք դեշբորդի ամենաարագ տեսանելի մետրիկներն են, որոնք օգնում են օգտատիրոջը արագ հասկանալ տվյալների
#  հիմնական միտումները։


        html.Div([
            html.Div([
                html.Div([
                    html.H3("Total Movies", style={'color': '#666', 'fontSize': '0.9em', 'margin': '0'}),
                    html.H2(id='metric-count', children='0', style={'margin': '10px 0 0 0', 'color': COLOR_PRIMARY})
                ], style={'backgroundColor': '#f9f9f9', 'padding': '20px', 'borderRadius': '8px', 'textAlign': 'center'}),
                
                html.Div([
                    html.H3("Average Rating", style={'color': '#666', 'fontSize': '0.9em', 'margin': '0'}),
                    html.H2(id='metric-avg-rating', children='0.0', style={'margin': '10px 0 0 0', 'color': COLOR_SUCCESS})
                ], style={'backgroundColor': '#f9f9f9', 'padding': '20px', 'borderRadius': '8px', 'textAlign': 'center'}),
                
                html.Div([
                    html.H3("Total Votes", style={'color': '#666', 'fontSize': '0.9em', 'margin': '0'}),
                    html.H2(id='metric-total-votes', children='0', style={'margin': '10px 0 0 0', 'color': COLOR_SECONDARY})
                ], style={'backgroundColor': '#f9f9f9', 'padding': '20px', 'borderRadius': '8px', 'textAlign': 'center'}),
                
                html.Div([
                    html.H3("Total Gross Revenue", style={'color': '#666', 'fontSize': '0.9em', 'margin': '0'}),
                    html.H2(id='metric-gross', children='$0', style={'margin': '10px 0 0 0', 'color': COLOR_WARNING})
                ], style={'backgroundColor': '#f9f9f9', 'padding': '20px', 'borderRadius': '8px', 'textAlign': 'center'}),
            ], style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
                'gap': '15px',
                'marginBottom': '30px'
            }),
        ]),
        
        # ====================================================================
        # VISUALIZATIONS SECTION
        # ====================================================================
        html.Div([
            # Row 1: Two main visualizations
            html.Div([
                # Visualization 1: Rating vs Votes Scatter Plot
                html.Div([
                    dcc.Graph(
                        id='scatter-rating-votes',
                        style={'height': '400px'}
                    )
                ], style={
                    'width': '48%',
                    'display': 'inline-block',
                    'marginRight': '2%',
                    'backgroundColor': 'white',
                    'padding': '15px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
                }),
                
                # Visualization 2: Rating Distribution Histogram
                html.Div([
                    dcc.Graph(
                        id='histogram-ratings',
                        style={'height': '400px'}
                    )
                ], style={
                    'width': '48%',
                    'display': 'inline-block',
                    'backgroundColor': 'white',
                    'padding': '15px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
                }),
            ], style={'marginBottom': '30px', 'display': 'flex', 'gap': '15px'}),
            
            # Row 2: Time series and genre analysis
            html.Div([
                # Visualization 3: Average Rating Over Years (Time Series)
                html.Div([
                    dcc.Graph(
                        id='line-rating-trend',
                        style={'height': '400px'}
                    )
                ], style={
                    'width': '48%',
                    'display': 'inline-block',
                    'marginRight': '2%',
                    'backgroundColor': 'white',
                    'padding': '15px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
                }),
                
                # Visualization 4: Top Genres Bar Chart
                html.Div([
                    dcc.Graph(
                        id='bar-top-genres',
                        style={'height': '400px'}
                    )
                ], style={
                    'width': '48%',
                    'display': 'inline-block',
                    'backgroundColor': 'white',
                    'padding': '15px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
                }),
            ], style={'marginBottom': '30px', 'display': 'flex', 'gap': '15px'}),
            
            # Row 3: Top directors and revenue analysis
            html.Div([
                # Visualization 5: Top Directors by Average Rating
                html.Div([
                    dcc.Graph(
                        id='bar-top-directors',
                        style={'height': '400px'}
                    )
                ], style={
                    'width': '48%',
                    'display': 'inline-block',
                    'marginRight': '2%',
                    'backgroundColor': 'white',
                    'padding': '15px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
                }),
                
                # Visualization 6: Rating vs Revenue Scatter
                html.Div([
                    dcc.Graph(
                        id='scatter-rating-revenue',
                        style={'height': '400px'}
                    )
                ], style={
                    'width': '48%',
                    'display': 'inline-block',
                    'backgroundColor': 'white',
                    'padding': '15px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
                }),
            ], style={'marginBottom': '30px', 'display': 'flex', 'gap': '15px'}),
            
            # Row 4: Top 30 Popular Films
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='bar-top-30-films',
                        style={'height': '600px'}
                    )
                ], style={
                    'width': '100%',
                    'backgroundColor': 'white',
                    'padding': '15px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
                }),
            ], style={'marginBottom': '30px'}),
        ], style={
            'padding': '0'
        }),
        
    ], style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '0 20px'}),
    
    # Footer
    html.Div([
        html.P("Data Source: IMDB Top 1000 Movies | Last Updated: February 2026 | "
               "Dashboard built with Dash, Plotly, and Pandas",
              style={'margin': '0', 'color': 'rgba(255,255,255,0.7)', 'fontSize': '0.9em'})
    ], style={
        'backgroundColor': '#1a1a2e',
        'padding': '20px',
        'textAlign': 'center',
        'marginTop': '40px',
        'color': 'white'
    })
], style={'backgroundColor': '#f0f2f5', 'minHeight': '100vh'})

# ============================================================================
# CALLBACKS - INTERACTIVE UPDATES
# ============================================================================

@app.callback(
        # սա callback ֆունկցիա է, որը թարմացնում է վիզուալիզացիաները և մետրիկները՝ այսինքն ,
        #   երբ օգտատերը փոխում է ֆիլտրերը, այս ֆունկցիան կանչվում 
        # է և թարմացնում է բոլոր գրաֆիկները և մետրիկները՝ ըստ նոր ֆիլտրերի։
        # ֆիլտրերը են՝ տարիների սլայդերը, ժանրերի դրոփդաունը, գնահատականի սլայդերը և վերականգման կոճակը։
    # OUTPUTS: All visualizations and metrics
    [Output('scatter-rating-votes', 'figure'),
     Output('histogram-ratings', 'figure'),
     Output('line-rating-trend', 'figure'),
     Output('bar-top-genres', 'figure'),
     Output('bar-top-directors', 'figure'),
     Output('scatter-rating-revenue', 'figure'),
     Output('bar-top-30-films', 'figure'),
     Output('metric-count', 'children'),
     Output('metric-avg-rating', 'children'),
     Output('metric-total-votes', 'children'),
     Output('metric-gross', 'children'),

    #  այստեղ մենք ասում ենք ՝ որ այս ֆունկցիան պետք է թարմացնի բոլոր վիզուալիզացիաները և մետրիկները։
     # Store for reset button
     Output('year-slider', 'value'),
     Output('genre-dropdown', 'value'),
     Output('rating-slider', 'value')],
    #  այստեղ ասում ենք նաև, որ վերականգման կոճակի սեղմման դեպքում պետք է վերականգնել ֆիլտրերի արժեքները։
    
    # INPUTS: All filter controls
    [Input('year-slider', 'value'),
     Input('genre-dropdown', 'value'),
     Input('rating-slider', 'value'),
     Input('reset-button', 'n_clicks')],
    #  այստեղ ասում ենք, որ այս ֆունկցիան պետք է արձագանքի այս ֆիլտրերի փոփոխություններին։
    
    # PREVENT_INITIAL_CALL: Don't run on page load
    prevent_initial_call=False
    # այստեղ մենք ասում ենք, որ այս ֆունկցիան պետք է աշխատի նաև էջի առաջին բեռնումի ժամանակ։
)
def update_dashboard(year_range, selected_genre, min_rating, reset_clicks):
    """
    Main callback function that updates all dashboard visualizations and metrics.
    
    This function is triggered whenever any filter is changed:
    1. Year range slider
    2. Genre dropdown
    3. Rating threshold slider
    4. Reset button
    
    It filters the data based on user inputs and creates all 6 visualizations,
    along with updated summary metrics.
    
    Args:
        year_range (list): Min and max years selected [min_year, max_year]
        selected_genre (str): Selected genre or 'all' for no filtering
        min_rating (float): Minimum rating threshold
        reset_clicks (int): Number of times reset button was clicked
    
    Returns:
        tuple: Contains all updated figures and metrics
    """
    
    # Check if reset button was clicked (using callback context)
    from dash import callback_context
    if callback_context.triggered and callback_context.triggered[0]['prop_id'] == 'reset-button.n_clicks':
        # Reset all filters to default values
        year_range = [df['Released_Year'].min(), df['Released_Year'].max()]
        selected_genre = 'all'
        min_rating = 5
    
    # ====================================================================
    # DATA FILTERING
    # ====================================================================
    
    # Filter by year range
    filtered_df = df[(df['Released_Year'] >= year_range[0]) & 
                     (df['Released_Year'] <= year_range[1])]
    
    # Filter by genre (if not 'all')
    if selected_genre != 'all':
        filtered_df = filtered_df[filtered_df['Genre_List'].apply(lambda x: selected_genre in x)]
    
    # Filter by minimum rating
    filtered_df = filtered_df[filtered_df['IMDB_Rating'] >= min_rating]
    
    # ====================================================================
    # VISUALIZATION 1: SCATTER PLOT - Rating vs Number of Votes
    # ====================================================================
    # Purpose: Shows the relationship between movie quality (rating) and popularity (votes)
    # Insight: High-rated movies tend to receive more votes, showing correlation between quality and interest
    
    fig_scatter_votes = px.scatter(
        filtered_df,
        x='No_of_Votes',
        y='IMDB_Rating',
        hover_data=['Series_Title', 'Released_Year', 'Director'],
        color='Released_Year',
        size='Runtime_Minutes',
        labels={'No_of_Votes': 'Number of Votes', 'IMDB_Rating': 'Rating'},
        title='Rating vs Popularity (Votes)',
        color_continuous_scale='Viridis'
    )
    fig_scatter_votes.update_layout(
        hovermode='closest',
        font=dict(size=10),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # ====================================================================
    # VISUALIZATION 2: HISTOGRAM - Rating Distribution
    # ====================================================================
    # Purpose: Shows the distribution of movie ratings across the dataset
    # Insight: Helps understand if ratings are skewed towards higher values (quality bias in top 1000)
    
    fig_histogram = go.Figure()
    fig_histogram.add_trace(go.Histogram(
        x=filtered_df['IMDB_Rating'],
        nbinsx=20,
        name='Movies',
        marker=dict(color=COLOR_PRIMARY, line=dict(color='white', width=1))
    ))
    fig_histogram.update_layout(
        title='Distribution of IMDB Ratings',
        xaxis_title='IMDB Rating',
        yaxis_title='Number of Movies',
        showlegend=False,
        font=dict(size=10),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # ====================================================================
    # VISUALIZATION 3: LINE CHART - Rating Trend Over Time
    # ====================================================================
    # Purpose: Shows how average movie ratings have changed over decades
    # Insight: Identifies whether movie quality has improved or declined over time
    
    yearly_avg = filtered_df.groupby('Released_Year').agg({
        'IMDB_Rating': 'mean',
        'Series_Title': 'count'
    }).reset_index()
    # groupby-ից հետո Released_Year-ը դառնում է index։ reset_index-ը դարձնում է սովորական սյունակ։
    yearly_avg.columns = ['Year', 'Average_Rating', 'Movie_Count']
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=yearly_avg['Year'],
        y=yearly_avg['Average_Rating'],
        mode='lines+markers',
        name='Average Rating',
        line=dict(color=COLOR_SUCCESS, width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(44, 160, 44, 0.2)'
    ))
    fig_line.update_layout(
        title='Average Movie Rating Over Time',
        xaxis_title='Year',
        yaxis_title='Average Rating',
        font=dict(size=10),
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified'
    )
    
    # ====================================================================
    # VISUALIZATION 4: BAR CHART - Top Genres
    # ====================================================================
    # Purpose: Shows which genres are most common in the top-rated movies
    # Insight: Identifies dominant genres that define high-quality cinema
    
    genre_counts = {}
    for genres in filtered_df['Genre_List']:
        for genre in genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    genre_df = pd.DataFrame(
        list(genre_counts.items()),
        columns=['Genre', 'Count']
    ).sort_values('Count', ascending=False).head(10)
    
    fig_genres = px.bar(
        genre_df,
        x='Count',
        y='Genre',
        orientation='h',
        title='Top 10 Genres in Top-Rated Movies',
        labels={'Count': 'Number of Movies', 'Genre': 'Genre'},
        color='Count',
        color_continuous_scale='Blues'
    )
    fig_genres.update_layout(
        font=dict(size=10),
        margin=dict(l=150, r=50, t=50, b=50),
        showlegend=False
    )
    
    # ====================================================================
    # VISUALIZATION 5: BAR CHART - Top Directors by Average Rating
    # ====================================================================
    # Purpose: Shows which directors consistently produce high-rated films
    # Insight: Identifies master filmmakers with best track records
    
    director_stats = filtered_df.groupby('Director').agg({
        'IMDB_Rating': 'mean',
        'Series_Title': 'count'
    }).reset_index()
    director_stats.columns = ['Director', 'Avg_Rating', 'Movie_Count']
    
    # Only show directors with at least 2 movies in filtered set
    director_stats = director_stats[director_stats['Movie_Count'] >= 2]
    director_stats = director_stats.sort_values('Avg_Rating', ascending=False).head(10)
    
    fig_directors = px.bar(
        director_stats,
        x='Avg_Rating',
        y='Director',
        orientation='h',
        title='Top Directors by Average Rating (Min 2 Films)',
        labels={'Avg_Rating': 'Average Rating', 'Director': 'Director'},
        color='Avg_Rating',
        color_continuous_scale='Greens'
    )
    fig_directors.update_layout(
        font=dict(size=10),
        margin=dict(l=150, r=50, t=50, b=50),
        showlegend=False
    )
    
    # ====================================================================
    # VISUALIZATION 6: SCATTER PLOT - Rating vs Box Office Revenue
    # ====================================================================
    # Purpose: Shows whether critical acclaim (rating) correlates with financial success
    # Insight: Explores the relationship between critical ratings and commercial performance
    
    # Filter out movies with zero gross revenue for cleaner visualization
    revenue_df = filtered_df[filtered_df['Gross'] > 0]
    
    fig_revenue = px.scatter(
        revenue_df,
        x='IMDB_Rating',
        y='Gross',
        hover_data=['Series_Title', 'Released_Year'],
        color='Released_Year',
        size='No_of_Votes',
        title='Rating vs Box Office Revenue',
        labels={'IMDB_Rating': 'IMDB Rating', 'Gross': 'Box Office Revenue ($)'},
        color_continuous_scale='Plasma'
    )
    fig_revenue.update_yaxes(type='log')
    fig_revenue.update_layout(
        hovermode='closest',
        font=dict(size=10),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # ====================================================================
    # VISUALIZATION 7: HORIZONTAL BAR CHART - Top 30 Most Popular Films
    # ====================================================================
    # Purpose: Shows the most popular films by number of votes
    # Insight: Identifies which films have captured audience interest the most
    
    top_30_films = filtered_df.nlargest(30, 'No_of_Votes')[['Series_Title', 'No_of_Votes', 'IMDB_Rating']]
    top_30_films = top_30_films.sort_values('No_of_Votes', ascending=True)
    
    fig_top_30 = go.Figure()
    fig_top_30.add_trace(go.Bar(
        y=top_30_films['Series_Title'],
        x=top_30_films['No_of_Votes'],
        orientation='h',
        marker=dict(
            color=top_30_films['IMDB_Rating'],
            colorscale='Viridis',
            colorbar=dict(title="Rating"),
            line=dict(color='white', width=1)
        ),
        text=top_30_films['No_of_Votes'].apply(lambda x: f'{int(x):,}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Votes: %{x:,}<extra></extra>'
    ))
    
    fig_top_30.update_layout(
        title='Top 30 Most Popular Films (by Number of Votes)',
        xaxis_title='Number of Votes',
        yaxis_title='Film Title',
        height=600,
        margin=dict(l=300, r=100, t=60, b=50),
        font=dict(size=10),
        showlegend=False,
        hovermode='closest'
    )
    
    # ====================================================================
    # SUMMARY METRICS
    # ====================================================================
    
    metric_count = len(filtered_df)  
    # սա ֆիլտրերից հետև մնացած ֆիլմերի քանակն է, որը ցույց է տալիս, թե քանի ֆիլմ է համապատասխանում ընտրված ֆիլտրերին։
    metric_avg_rating = f"{filtered_df['IMDB_Rating'].mean():.2f}"
    metric_total_votes = f"{int(filtered_df['No_of_Votes'].sum()):,}"
    metric_gross = f"${filtered_df['Gross'].sum()/1e9:.2f}B" if filtered_df['Gross'].sum() > 0 else "$0"
    
    return (
        fig_scatter_votes,
        fig_histogram,
        fig_line,
        fig_genres,
        fig_directors,
        fig_revenue,
        fig_top_30,
        metric_count,
        metric_avg_rating,
        metric_total_votes,
        metric_gross,
        year_range,
        selected_genre,
        min_rating
    )

# ============================================================================
# RUN THE APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("IMDB MOVIES DASHBOARD - Starting Application")
    print("=" * 70)
    print("\n📊 Dashboard is running...")
    print("🌐 Open your browser and navigate to: http://127.0.0.1:8050/")
    print("\n✨ Features:")
    print("   • Interactive filtering by year, genre, and rating")
    print("   • 6 professional visualizations")
    print("   • Real-time metric updates")
    print("   • Responsive design")
    print("\n" + "=" * 70 + "\n")
    
    app.run(debug=True)
