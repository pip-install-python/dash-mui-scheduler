"""Minimal standalone smoke test for dash_mui_scheduler.

Run after `npm run build`:

    python usage.py

Then open http://127.0.0.1:8051 and confirm the calendar renders and that
adding / moving an event prints a `lastAction` to the console.
"""
import dash
from dash import Dash, html, dcc, Input, Output, callback
import dash_mui_scheduler as dms

app = Dash(__name__)

INITIAL_EVENTS = [
    {"id": 1, "title": "Team Meeting", "start": "2024-01-15T10:00:00", "end": "2024-01-15T11:00:00"},
    {"id": 2, "title": "Project Review", "start": "2024-01-16T14:00:00", "end": "2024-01-16T15:30:00"},
    {"id": 3, "title": "Client Call", "start": "2024-01-17T09:00:00", "end": "2024-01-17T10:00:00"},
]

app.layout = html.Div(
    [
        html.H3("dash-mui-scheduler · EventCalendar smoke test"),
        dms.EventCalendar(
            id="cal",
            events=INITIAL_EVENTS,
            defaultVisibleDate="2024-01-15",
            height=600,
        ),
        html.Pre(id="readout", style={"background": "#f5f5f5", "padding": "1rem"}),
    ],
    style={"maxWidth": 1000, "margin": "2rem auto"},
)


@callback(
    Output("readout", "children"),
    Input("cal", "events"),
    Input("cal", "lastAction"),
)
def show(events, last_action):
    return f"lastAction: {last_action}\n\n{len(events or [])} events:\n" + "\n".join(
        f"  {e['id']}: {e['title']}  {e['start']} -> {e['end']}" for e in (events or [])
    )


if __name__ == "__main__":
    app.run(debug=True, port=8051)
