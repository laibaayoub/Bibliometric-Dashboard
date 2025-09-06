import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
from dash import Dash, dcc, html

df = pd.read_excel('savedrecs.xlsx')
df.columns = df.columns.str.strip()

def extract_country(address):
    if pd.isna(address):
        return None
    parts = str(address).split(';')[-1].split(',')
    return parts[-1].strip()
df['Country'] = df['C1'].apply(extract_country)

# 1. Publications Over Time (green line)
pub_trend = df['PY'].value_counts().sort_index()
fig_pub = px.line(x=pub_trend.index, y=pub_trend.values,
                  labels={'x':'Year','y':'Number of Publications'},
                  title="Publications Over Time")
fig_pub.update_traces(line_color='green')

# 2. Top Sources (horizontal bar)

top_sources = df['SO'].value_counts().head(10).reset_index()
top_sources.columns = ['Source', 'Count']  

# Create horizontal bar chart
fig_sources = px.bar(top_sources, x='Count', y='Source', orientation='h',
                     color='Source', color_discrete_sequence=px.colors.qualitative.Set3,
                     title="Top 10 Journals/Conferences")
fig_sources.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False,xaxis_title="Number of Publications"  )


# 3. Top Authors (horizontal bar)
authors = df['AF'].dropna().str.split('; ')
authors_flat = [a.strip() for sublist in authors for a in sublist]
authors_series = pd.Series(authors_flat).value_counts().head(10).reset_index()
authors_series.columns = ['Author','Count']
fig_authors = px.bar(authors_series, x='Count', y='Author', orientation='h',
                     color='Author', color_discrete_sequence=px.colors.qualitative.Set2,
                     title="Top 10 Authors")
fig_authors.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False,xaxis_title="Number of Publications" )

# 4. Languages (pie chart)

langs = df['LA'].value_counts()
labels = langs.index.tolist()
values = langs.values.tolist()

custom_text = []
for i, label in enumerate(labels):
    if label.lower() == "english":
        custom_text.append(f"{values[i]} ({values[i]/sum(values)*100:.1f}%)")
    else:
        custom_text.append("")
fig_langs = go.Figure(data=[go.Pie(
    labels=labels,
    values=values,
    textinfo='text',          
    hole=0.1,
    marker=dict(colors=px.colors.qualitative.Set3),
    pull=[0.05]*len(labels)   
)])

fig_langs.update_layout(title_text="Languages of Publications")

# 5. Keywords (top 20)
keywords = df['DE'].dropna().str.split('; ')
keywords_flat = [k.strip().lower() for sublist in keywords for k in sublist]
keywords_series = pd.Series(keywords_flat).value_counts().head(20).reset_index()
keywords_series.columns = ['Keyword','Frequency']
fig_keywords = px.bar(keywords_series, x='Keyword', y='Frequency', title="Top 20 Keywords")
fig_keywords.update_layout(xaxis_tickangle=-45)

# 6. Countries (pie chart)
country_counts = df['Country'].value_counts().head(10).reset_index()
country_counts.columns = ['Country','Count']
fig_countries = px.pie(country_counts, values='Count', names='Country',
                       title="Top 10 Countries by Publications", hole=0.1)

# --- Dash App ---
app = Dash(__name__)

app.layout = html.Div([
    html.H1("BIBLIOMETRIC DASHBOARD", style={'textAlign':'center','color':"#142EBE",'font-size':40}),
    
    html.Div([
        html.Div(dcc.Graph(figure=fig_pub), style={'width':'40%','display':'inline-block'}),
        html.Div(dcc.Graph(figure=fig_sources), style={'width':'60%','display':'inline-block'}),
    ]),
    html.Div([
        html.Div(dcc.Graph(figure=fig_authors), style={'width':'60%','display':'inline-block'}),
        html.Div(dcc.Graph(figure=fig_langs), style={'width':'40%','display':'inline-block'}),
    ]),
    html.Div([
        html.Div(dcc.Graph(figure=fig_keywords), style={'width':'48%','display':'inline-block'}),
        html.Div(dcc.Graph(figure=fig_countries), style={'width':'52%','display':'inline-block'}),
    ]),
])
server = app.server
if __name__ == "__main__":
    app.run(debug=True,port=8052) 