from dash import html, Input, Output, State, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

# Dates are ISO strings (wall time, no Z). The component writes the full
# `events` array back to Dash on every create / move / resize / delete.
events = [
    {"id": "1", "title": "Sprint planning", "start": "2024-01-15T09:00:00", "end": "2024-01-15T10:30:00", "color": "blue"},
    {"id": "2", "title": "Design review", "start": "2024-01-16T13:00:00", "end": "2024-01-16T14:00:00", "color": "purple"},
    {"id": "3", "title": "1:1", "start": "2024-01-17T11:00:00", "end": "2024-01-17T11:30:00", "color": "green"},
]

ALL_VIEWS = ["day", "week", "month", "agenda"]

# `views` controls which view buttons the calendar offers. The CheckboxGroup
# below drives it live — uncheck a view and its button disappears from the
# calendar's toolbar. `view` (controlled) is kept on a value that still exists.
component = html.Div(
    [
        dmc.CheckboxGroup(
            id="views-restrict-group",
            label="View buttons to offer",
            description="Toggle which views appear in the calendar's toolbar.",
            value=ALL_VIEWS,
            mb="md",
            children=dmc.Group(
                [dmc.Checkbox(label=v.capitalize(), value=v) for v in ALL_VIEWS],
                mt="xs",
            ),
        ),
        dms.EventCalendar(
            id="views-restrict-cal",
            events=events,
            views=ALL_VIEWS,
            view="week",
            defaultVisibleDate="2024-01-15",
            height=560,
        ),
    ]
)


@callback(
    Output("views-restrict-cal", "views"),
    Output("views-restrict-cal", "view"),
    Input("views-restrict-group", "value"),
    State("views-restrict-cal", "view"),
    prevent_initial_call=True,
)
def restrict_views(selected, current_view):
    # Keep the canonical order; always leave at least one view available.
    views = [v for v in ALL_VIEWS if v in selected] or ["week"]
    # If the active view was just removed, fall back to the first remaining one.
    view = current_view if current_view in views else views[0]
    return views, view
