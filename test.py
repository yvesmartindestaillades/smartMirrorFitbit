import dash
import dash_core_components as dcc
import datetime as dt

app = dash.Dash(__name__)

app.layout = dcc.DatePickerSingle(
    id='my-date-picker-single',
    date=dt.date.today(),
    style={
        'backgroundColor': 'lightblue',
        'border': '1px solid black',
        'color': 'black',
        'fontFamily': 'Arial',
        'fontSize': 18,
        'fontWeight': 'bold',
        'height': 50,
        'lineHeight': '50px',
        'textAlign': 'center',
        'width': 200,
    }
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
