import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import folium

# 데이터 불러오기
df = pd.read_csv('data/fin_file.csv', encoding='utf-8')

# Dash 애플리케이션 초기화
app = dash.Dash(__name__)

# 애플리케이션 레이아웃 설정
app.layout = html.Div([
    html.H1("여행코스 짜드립니다. 단돈 이찬원..."),
    html.Div([
        dcc.Dropdown(
            id='region-dropdown',
            options=[{'label': region, 'value': region} for region in df['region_nm'].unique()],
            placeholder="지역을 선택해 주십시오.",
            value=None
        ),
        dcc.Dropdown(
            id='age-dropdown',
            options=[{'label': age, 'value': age} for age in df['age'].unique()],
            placeholder="귀하의 연령대를 선택해 주십시오.",
            value=None
        ),
        dcc.Dropdown(
            id='type-dropdown',
            options=[{'label': type, 'value': type} for type in df['type'].unique()],
            placeholder="동행을 선택해 주십시오.",
            value=None
        ),
        dcc.Dropdown(
            id='activity-dropdown',
            options=[{'label': activity, 'value': activity} for activity in df['activity'].unique()],
            placeholder="가장 선호하는 활동을 선택해 주십시오.",
            value=None
        ),
        html.Button('검색', id='search-button', n_clicks=0)
    ], style={'width': '35%', 'display': 'inline-block'}),
    html.Div(id='selected-info', style={'font-size': '20px', 'margin': '10px'}),
    html.Div(id='map-container')
], style={'padding': '20px'})

def create_popup(title, file_name, text, font_size='15px', bold=False):
    # 파일에서 HTML 내용을 읽기
    try:
        with open(f'{file_name}.html', 'r', encoding='utf-8') as file:
            html_content = file.read()
    except FileNotFoundError:
        html_content = "No additional information available."

    # 타이틀 및 텍스트 추가
    title_style = f"font-size: 20px; font-weight: bold; text-align: center;" if bold else f"font-size: {font_size}; text-align: center;"
    text_style = f"font-size: {font_size}; text-align: center;"
    popup_content = f"<div style='width: 200px;'><p style='{title_style}'>{title}</p><p style='{text_style}'>{text}</p></div>"

    # 팝업 내용 결합
    combined_html = popup_content + html_content
    return folium.Popup(combined_html, max_width=300)

@app.callback(
    [Output('map-container', 'children'), Output('selected-info', 'children')],
    [Input('search-button', 'n_clicks')],
    [State('region-dropdown', 'value'),
     State('age-dropdown', 'value'),
     State('type-dropdown', 'value'),
     State('activity-dropdown', 'value')]
)
def update_map(n_clicks, selected_region, selected_age, selected_type, selected_activity):
    if n_clicks == 0:
        return [html.Div(), ""]

    if not selected_region or not selected_age or not selected_type or not selected_activity:
        return ["엥", ""]

    filtered_df = df[
        (df['region_nm'] == selected_region) &
        (df['age'] == selected_age) &
        (df['type'] == selected_type) &
        (df['activity'] == selected_activity)
    ]

    if filtered_df.empty:
        return ["엥", ""]

    map_center = [filtered_df['cent_y'].mean(), filtered_df['cent_x'].mean()]
    map_obj = folium.Map(location=map_center, zoom_start=12)

    related_names = []
    for idx, row in filtered_df.iterrows():
        folium.Marker(
            [row['cent_y'], row['cent_x']],
            popup=create_popup(row['cent_nm'], row['cent_nm'], row['activity'], bold=True),
            tooltip=row['cent_nm'],
            icon=folium.Icon(color='blue')
        ).add_to(map_obj)

        related_names.append(row['related_nm'])
        folium.Marker(
            [row['related_y'], row['related_x']],
            popup=create_popup(row['related_nm'], row['related_nm'], row['text']),
            tooltip=row['related_nm'],
            icon=folium.Icon(color='green')
        ).add_to(map_obj)

    map_obj.save('map.html')
    with open('map.html', 'r', encoding='utf-8') as map_file:  # 파일을 UTF-8 인코딩으로 열기
        map_html = map_file.read()
    selected_info = f"{filtered_df['cent_nm'].iloc[0]}에서는 {', '.join(related_names)}에 가세요"
    return [html.Iframe(srcDoc=map_html, width='100%', height='600'), selected_info]

# 서버 실행
if __name__ == '__main__':
    app.run_server(debug=False)
