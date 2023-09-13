import os
import dash
from dash import Dash, dcc, html, Input, Output
from dash import dash_table
import plotly.express as px
import pandas as pd
from turtledata import TurtleData
import csv

turtles = TurtleData()
heliuskey = os.getenv('HELIUS_API')
url = "https://rpc.helius.xyz/?api-key=" + str(heliuskey)

mintlist = []
with open("assets/turtlesNFT_mintlist.csv") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        mintlist.append(row[-1]) # Assuming the account is in the first column


# Get the dealtokens from turtles class
dealtokens = turtles.get_dealtokens(url, mintlist)
dealtokens.append("AFCJxSQggZxKC6QMJZg34EyEDFhafiw8GgQM6pE81KyC")

# create the dataframe
df = pd.DataFrame()
for mint in dealtokens:
    df_concat = turtles.create_dataframe(url, mint)
    print("Created dataframe for " + mint )
    df = pd.concat([df, df_concat])
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df = df.query('Quantity != 0')

# Create a base url for the solscan.io website
base_url = "https://solscan.io/token/"
df["WalletURL"] = base_url + df["Wallet"]
df["Wallet"] = "[" + df["Wallet"] + "](" + df["WalletURL"] + ")"
df["TokenAddressURL"] = base_url + df["TokenAddress"]
df["TokenAddress"] = "[" + df["TokenAddress"] + "](" + df["TokenAddressURL"] + ")"
df = df.drop(['TokenAddressURL'], axis=1)

# create the dropdown to select the deal tokens
dealtoken_dropdown = dcc.Dropdown(
    options=[{"label": token, "value": token} for token in df['DealToken'].unique()] + [{"label": "All", "value": "ALL"}], # append a select all option to the options list
    value="ALL", # make the select all option the default value
    id="dealtoken-dropdown"
)

# Create pie chart for distribution
color_discrete_sequence = ['limegreen', 'mediumseagreen', 'forestgreen', 'darkgreen', 'olivedrab', 'seagreen']
df_pivot = pd.pivot_table(df.query('Quantity != 0'), index='DealToken', values='Wallet', aggfunc='nunique').reset_index()
fig = px.pie(df_pivot, names='DealToken', values='Wallet', title='Unique Wallets per DealToken', hole=0.45, color_discrete_sequence=color_discrete_sequence)
fig.update_traces(textposition='inside', textinfo='percent+label')


# Create the datatable with the supply
df_pivot2 = pd.pivot_table(df.query('Quantity != 0'), index='DealToken', values='Supply', aggfunc='max').reset_index()
df_pivot2 = df_pivot2.merge(df[['DealToken', 'Quantity']], on='DealToken', how='left')
df_pivot2 = df_pivot2.groupby('DealToken').agg({'Supply': 'max', 'Quantity': 'median'}).reset_index()
df_pivot2 = df_pivot2.rename(columns={'Quantity': 'QtyMedianOwned'})
df_pivot2["Supply"] = df_pivot2.Supply.apply(lambda x : "{:,}".format(x))
table2 = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in df_pivot2.columns],
    data=df_pivot2.to_dict('records'),
    sort_action='native',
    filter_action='native', 
    style_cell={'textAlign': 'center'} 
)

df["Quantity"] = df.Quantity.apply(lambda x : "{:,}".format(x))
df["Supply"] = df.Supply.apply(lambda x : "{:,}".format(x))
# Create table with all records
table = dash_table.DataTable(
    columns=[{"name": i, "id": i, "presentation": "markdown"} for i in df.columns if i != "WalletURL"],
    data=df.to_dict('records'),
    page_size = 10,
    filter_action='native', 
    sort_action='native',
    export_format='csv', 
    style_cell={'textAlign': 'center'}, 
    style_header={
        'backgroundColor': 'limegreen', 
        'font': {'size': 14, 'weight': 'bold', 'color': 'white'} 
    },
    id="table" 
)

# create the header
header = html.H1(
    children="Turtle Deal Token Distribution",
    style={
        'backgroundColor': 'black', 
        'color': 'white', 
        'fontWeight': 'bold'
    }
)


# Define the application
app = dash.Dash(__name__)
app.title = 'Turtlenomics'
application = app.server

# The layouy of the app
app.layout = html.Div(children=[
    html.Img(src="assets/vcbanner.png", style={"width": "100%", "height": "30%","border": "1px solid black"}),
    header,
    dealtoken_dropdown,
    html.Div([
        dcc.Graph(id="token-distro-graph"),
        dcc.Graph(figure=fig, style={'width': '50%'}),
    ], style={'display': 'flex', 'flex-direction': 'row'}),
    html.Div([
        table,
        table2
    ], style={'width': '100%', 'margin': 'auto'}) 
])

# Create a callback function with two outputs: one for the pie chart and one for the table
@app.callback(
    [
        Output(component_id="token-distro-graph", component_property="figure"),
        Output(component_id="table", component_property="data")
    ],
    Input(component_id="dealtoken-dropdown", component_property="value")
)

def update_graph_and_table(selected_dealtoken):
    if selected_dealtoken == "ALL":
        filtered_dealtoken = df
    else:
        filtered_dealtoken = df[df["DealToken"] == selected_dealtoken]
    
    # Create a pie chart using plotly express
    grouped_dealtoken = filtered_dealtoken.groupby("DealToken").agg({"Wallet": "nunique"})
    grouped_dealtoken = grouped_dealtoken.reset_index()
    bar_fig = px.bar(
        grouped_dealtoken,
        x="DealToken", y="Wallet",
        color="DealToken",
        title=f"Unique {selected_dealtoken} holders",
        color_discrete_sequence=['limegreen']
    )
    
    # Return the pie chart figure and the filtered DataFrame as a dictionary of records
    return bar_fig, filtered_dealtoken.to_dict('records')

if __name__=='__main__':
    application.run(debug=False,port=8080)
