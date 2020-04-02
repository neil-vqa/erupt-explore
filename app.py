import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as do
import pandas as pd
import numpy as np
import json
import os


app = dash.Dash(__name__,
			external_stylesheets=[dbc.themes.SANDSTONE])
app.title='Eruption Explorer'
server = app.server

map_token = os.environ.get('MAP_TOKEN')
map_style = os.environ.get('MAP_STYLE')

data = pd.read_excel('Volcano Eruptions (mod).xlsx')
vulcan_list = list(data['Activity Evidence'].unique())
vulcan_opts = [{'label':k, 'value':k} for k in vulcan_list]


content = dbc.Container(
	[
		dbc.Row(
			dbc.Col(
				dbc.Row(
					[
						dcc.Graph(id='map',config={'displayModeBar': False}, style={'width':'100%', 'height':'100vh'}),
						html.Div(
							[
								dbc.Card(
									[
										html.H4('Volcano Eruption Explorer'),
										html.Hr(),
										dcc.Dropdown(
											id='activity-select',
											placeholder='Select activity evidence',
											clearable=False,
											options=vulcan_opts
										),
										dbc.Button('Explore',id='explore-button',color='secondary',
												block=True, className='mt-4'),
										html.Hr(),
										html.P(id='count-display'),
										html.Hr(className='mt-0'),
										dcc.Markdown(id='info-display',className='py-0')
									],
									body=True,
									style={'color':'#000000','backgroundColor':'#ffffff'},
									className='opacity-0h5 shadow-lg pb-0'
				                   )
							],
							id='over_map',
							style={"width": "18rem"}
						),
						html.Div(
							[
								dbc.Card(
									[
										html.H5('Interaction Guide'),
										html.Hr(className='mt-0'),
										dcc.Markdown(['''
													Start by applying the filter located at the upper left corner. 
										
													You may click on a point to view the volcano details. 
										
													Deselect the volcano by clicking the point once again. 
										
													You can zoom and pan over the terrain map using the mouse.
													
													This app is best viewed using widescreen devices.
													'''])
										
									],
									body=True,
									style={'color':'#000000','backgroundColor':'#ffffff'},
									className='opacity-0h5 shadow-lg'
				                   )
							],
							id='over_map2',
							style={"width": "18rem"}
						),
						html.Div(id='dummy', style={'display':'none'})
					],
					id='wrapper'
					
				)
			)
		)
	],
	fluid=True,
	style={'height':'100vh'}
)

def serve_layout():
	return content

app.layout = serve_layout


@app.callback(
	[Output('map','figure'),
	Output('count-display','children'),],
	[Input('dummy','children'),
	Input('explore-button','n_clicks')],
	[State('activity-select','value')]
)
def update_map(children,n_clicks,value):
	if value is None:
		notice = do.Figure(do.Indicator(
			mode= 'number',
			value= None,
			title = {"text": "Welcome!<br><span style='font-size:0.5em'>Hover over the lower right corner to view the interaction guide.</span><br><span style='font-size:0.5em'>Hover over the upper left corner to view the filter & info menu.</span><br><span style='font-size:0.3em;color:#ffffff'>Data Source: Global Volcanism Program | Developer: Neil A. (nvqa.business@gmail.com)</span>",
					'font':{'family':'Roboto','color':'#ffffff','size':50}},
			number={'font':{'color':'#8e8c84'}}))
		notice.update_layout(margin= do.layout.Margin(t=150,b=0), plot_bgcolor='#8e8c84', paper_bgcolor='#8e8c84')
		
		count_text = 'No info yet.'
		
		return notice,count_text
		
	else:
		df = data.loc[data['Activity Evidence']==value]
		midpoint = (np.average(data['latitude']), np.average(data['longitude']))
		
		vulcan_lat = list(df['latitude'])
		vulcan_lon = list(df['longitude'])
		vulcan_name = list(df['Volcano Name'])
		vulcan_type = list(df['Primary Volcano Type'])
		vulcan_country = list(df['Country'])
		vulcan_erup = list(df['Last Known Eruption'])
		
		hover_text = ['Name: ' + "<span style='color:#ffffff'>{}</span>".format(x) + '<br>Type: ' + "<span style='color:#ffffff'>{}</span>".format(y) + '<br>Country: ' + "<span style='color:#ffffff'>{}</span>".format(z) + '<br>Last Eruption: ' + "<span style='color:#ffffff'>{}</span>".format(v) for x,y,z,v in zip(vulcan_name,vulcan_type,vulcan_country,vulcan_erup)]

		map1 = do.Figure()
		map1.add_trace(
			do.Scattermapbox(
				lat=vulcan_lat,
				lon=vulcan_lon,
				mode='markers',
				marker=do.scattermapbox.Marker(
					size=10,
					color='#8e8c84',
					opacity=0.8
					),
				text= hover_text,
				hoverinfo='text',
				showlegend= False
			)
		)
		map1.update_layout(
			mapbox= do.layout.Mapbox(
				accesstoken= map_token,
				center= do.layout.mapbox.Center(
					lat=midpoint[0],
					lon= midpoint[1]
				),
				pitch=45,
				zoom= 2,
				style= map_style
			),
			margin= do.layout.Margin(
				l=0,
				r=0,
				t=0,
				b=0
			),
			clickmode='event+select'
		)
		
		count_text = 'Found {} volcanoes.'.format(len(vulcan_name))
	
		return map1,count_text

@app.callback(
	Output('info-display','children'),
	[Input('map','clickData')]
)
def display_info(clickData):
	if clickData is None:
		text = 'No info yet.'
		return text
	else:	
		raw = json.dumps(clickData)
		info = json.loads(raw)
		query = data.loc[(data['longitude']==info['points'][0]['lon']) & (data['latitude']==info['points'][0]['lat'])]
		name = str(query['Volcano Name'].values[0])
		type_of = str(query['Primary Volcano Type'].values[0])
		country = str(query['Country'].values[0])
		last_date = str(query['Last Known Eruption'].values[0])
		region = str(query['Region'].values[0])
		elev = str(query['Elevation'].values[0])
		rock = str(query['Dominant Rock Type'].values[0])
		tectonic = str(query['Tectonic Setting'].values[0])
		
		text = '''
			**{}**
			
			*Type:* {}
			
			*Country:* {}
			
			*Last Eruption:* {}
			
			*Region:* {}
			
			*Elevation:* {} meters
			
			*Dominant Rock Type:* {}
			
			*Tectonic Setting:* {}
			'''.format(name,type_of,country,last_date,region,elev,rock,tectonic)
		
		return text


if __name__ == '__main__':
	app.run_server(debug=False)

