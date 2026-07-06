# Status colors -- shared across anything that needs to render a monument's
# status as a colored box: bounds2pdf.py's per-monument headline today, and
# the planned overview map (order-number markers reusing these same colors)
# later. Text color (knockout white vs. black) is derived from each
# background's relative luminance rather than hand-picked per status, so a
# future color swap can't accidentally leave unreadable low-contrast text.
STATUS_COLORS = {
    'Painted':         '#2E7D32',   # green -- done
    'Found':           '#1565C0',   # blue -- located, partial success
    "Couldn't paint":  '#EF6C00',   # orange -- found but an issue
    'Not Found':       '#C62828',   # red -- problem
    'Documented':      '#BDBDBD',   # light gray -- no field visit
}

DEFAULT_STATUS_COLOR = '#BDBDBD'


def knockout_text_color(hex_color):
    """Return '#ffffff' or '#000000', whichever contrasts better with hex_color."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return '#000000' if luminance > 0.5 else '#ffffff'
