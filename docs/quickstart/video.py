from dash import html

# A responsive 16:9 YouTube embed. The outer box caps the width and the
# padding-bottom trick keeps the iframe at a 16:9 ratio on any screen.
component = html.Div(
    html.Div(
        html.Iframe(
            # youtube-nocookie, matching the landing-page embed (pages/home.py):
            # no tracking cookies are set until the reader presses play.
            src="https://www.youtube-nocookie.com/embed/i-CZH7W5ZsA",
            title="dash-mui-scheduler walkthrough",
            style={
                "position": "absolute",
                "top": 0,
                "left": 0,
                "width": "100%",
                "height": "100%",
                "border": 0,
                "borderRadius": "8px",
            },
            allow=(
                "accelerometer; autoplay; clipboard-write; encrypted-media; "
                "gyroscope; picture-in-picture; web-share; fullscreen"
            ),
        ),
        style={
            "position": "relative",
            "paddingBottom": "56.25%",  # 16:9
            "height": 0,
            "overflow": "hidden",
        },
    ),
    style={"maxWidth": 720, "margin": "0 auto"},
)
