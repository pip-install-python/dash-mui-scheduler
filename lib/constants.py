PAGE_TITLE_PREFIX = "dash-mui-scheduler | "
# App accent: a blue palette ("brand") anchored on rgb(51,153,255) = #3399ff,
# defined in components/appshell.py theme.colors. Set back to "teal" to revert.
PRIMARY_COLOR = "brand"
APP_VERSION = "0.1.0"

# Populated by pages/markdown.py when loading documentation files (raw markdown
# keyed by page name) — used by the "copy for LLM" button directive.
NAME_CONTENT_MAP = {}

# Mantine style props that pollute auto-generated kwargs tables. Kept for
# parity with the documentation boilerplate; harmless for scheduler components.
PROPS_TO_EXCLUDE = [
    "unstyled", "m", "my", "mx", "mt", "mb", "ms", "me", "ml", "mr",
    "p", "py", "px", "pt", "pb", "ps", "pe", "pl", "pr",
    "bg", "c", "opacity", "ff", "fz", "fw", "lts", "ta", "lh", "fs", "tt",
    "td", "w", "miw", "maw", "h", "mih", "mah", "bgsz", "bgp", "bgr", "bga",
    "pos", "top", "left", "bottom", "right", "inset", "display", "flex",
]
