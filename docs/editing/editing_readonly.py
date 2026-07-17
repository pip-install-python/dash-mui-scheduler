import dash_mantine_components as dmc
import dash_mui_scheduler as dms

# Even with readOnly=False, one event is locked via its own `readOnly` key.
events = [
    {
        "id": "standup",
        "title": "Daily standup",
        "start": "2024-01-15T09:00:00",
        "end": "2024-01-15T09:30:00",
        "color": "blue",
    },
    {
        "id": "frozen",
        "title": "Locked: company all-hands (readOnly)",
        "start": "2024-01-16T13:00:00",
        "end": "2024-01-16T14:00:00",
        "color": "red",
        "readOnly": True,
    },
    {
        "id": "demo",
        "title": "Sprint demo",
        "start": "2024-01-18T11:00:00",
        "end": "2024-01-18T12:00:00",
        "color": "green",
    },
]

component = dmc.Stack(
    [
        dmc.Text(
            "Left: a fully read-only calendar (readOnly=True) — no create, move, "
            "resize, or delete. Right: an editable calendar where only the red "
            "all-hands event is locked via its per-event readOnly key.",
            size="sm",
            c="dimmed",
        ),
        dmc.SimpleGrid(
            cols={"base": 1, "md": 2},
            spacing="md",
            children=[
                dms.EventCalendar(
                    id="editing-readonly-cal",
                    events=events,
                    readOnly=True,
                    defaultVisibleDate="2024-01-15",
                    defaultView="week",
                    height=580,
                ),
                dms.EventCalendar(
                    id="editing-perevent-cal",
                    events=events,
                    defaultVisibleDate="2024-01-15",
                    defaultView="week",
                    height=580,
                ),
            ],
        ),
    ],
    gap="sm",
)
