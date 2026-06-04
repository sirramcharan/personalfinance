"""Chart utilities using Plotly for the finance dashboard."""

import plotly.graph_objects as go
import plotly.express as px


THEME = {
    "bg": "rgba(16, 20, 30, 0.95)",
    "card": "rgba(25, 30, 45, 0.8)",
    "accent1": "#00d4ff",
    "accent2": "#7b61ff",
    "accent3": "#00ff9d",
    "accent4": "#ff6b6b",
    "accent5": "#ffd93d",
    "text": "#e0e6ed",
    "subtext": "#8892a6",
    "grid": "rgba(255, 255, 255, 0.08)",
}


def get_base_layout(title: str = "", height: int = 320) -> dict:
    """Return base Plotly layout config."""
    return dict(
        title=dict(text=title, font=dict(color=THEME["text"], size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=THEME["text"]),
        height=height,
        xaxis=dict(
            gridcolor=THEME["grid"],
            zerolinecolor=THEME["grid"],
            tickfont=dict(color=THEME["subtext"], size=11),
        ),
        yaxis=dict(
            gridcolor=THEME["grid"],
            zerolinecolor=THEME["grid"],
            tickfont=dict(color=THEME["subtext"], size=11),
        ),
        legend=dict(font=dict(color=THEME["subtext"], size=11)),
        margin=dict(l=40, r=20, t=40, b=20),
    )


def make_donut_chart(labels: list, values: list, title: str = "") -> go.Figure:
    """Create a donut chart for expense/income breakdown."""
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(
                    colors=[
                        THEME["accent1"],
                        THEME["accent2"],
                        THEME["accent3"],
                        THEME["accent4"],
                        THEME["accent5"],
                    ]
                ),
                textinfo="label+percent",
                textfont=dict(color=THEME["text"]),
            )
        ]
    )
    fig.update_layout(
        **get_base_layout(title),
        showlegend=True,
        legend=dict(font=dict(color=THEME["subtext"])),
    )
    fig.update_traces(hoverinfo="label+percent+value", hoverlabel_font_color=THEME["text"])
    return fig


def make_bar_chart(
    x: list, y: list, title: str = "", color: str = None, y_title: str = ""
) -> go.Figure:
    """Create a bar chart."""
    fig = go.Figure(
        data=[
            go.Bar(
                x=x,
                y=y,
                marker_color=color or THEME["accent1"],
                marker=dict(
                    line=dict(color="rgba(0,0,0,0.2)", width=0.5),
                    opacity=0.85,
                ),
            )
        ]
    )
    fig.update_layout(
        **get_base_layout(title),
        yaxis=dict(title=y_title, **get_base_layout()["yaxis"]),
    )
    fig.update_traces(hovertemplate="%{y:.2f}<extra></extra>")
    return fig


def make_line_chart(
    x: list,
    y: list,
    title: str = "",
    line_color: str = None,
    y_title: str = "",
    fill_to_zero: bool = False,
) -> go.Figure:
    """Create a line chart for trends."""
    fig = go.Figure(
        data=[
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                line=dict(color=line_color or THEME["accent1"], width=3),
                fill="tozeroy" if fill_to_zero else None,
                fillcolor=f"rgba(0, 212, 255, 0.15)",
                marker=dict(size=6, color=line_color or THEME["accent1"]),
            )
        ]
    )
    fig.update_layout(
        **get_base_layout(title),
        yaxis=dict(title=y_title, **get_base_layout()["yaxis"]),
    )
    fig.update_traces(hovertemplate="%{y:.2f}<extra></extra>")
    return fig


def make_multi_line_chart(
    data: dict, title: str = "", y_title: str = ""
) -> go.Figure:
    """Create multi-line chart from dict of {label: [values]}."""
    colors = [
        THEME["accent1"],
        THEME["accent2"],
        THEME["accent3"],
        THEME["accent4"],
        THEME["accent5"],
    ]
    fig = go.Figure()
    for i, (label, values) in enumerate(data.items()):
        fig.add_trace(
            go.Scatter(
                y=values,
                name=label,
                mode="lines+markers",
                line=dict(color=colors[i % len(colors)], width=2.5),
                marker=dict(size=5),
            )
        )
    fig.update_layout(
        **get_base_layout(title),
        yaxis=dict(title=y_title, **get_base_layout()["yaxis"]),
    )
    return fig


def make_indicator(value: float, title: str = "", prefix: str = "Rs ") -> go.Figure:
    """Create a single KPI indicator gauge."""
    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=value,
            title=dict(text=title, font=dict(size=16, color=THEME["text"])),
            number=dict(
                font=dict(size=36, color=THEME["accent1"]),
                prefix=prefix,
                valueformat=".0f",
            ),
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        height=150,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def make_kpi_card(label: str = "", value: float = 0, prefix: str = "Rs ", color: str = None) -> go.Figure:
    """Create a KPI card gauge indicator."""
    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=value,                                                                                
            title=dict(text=label, font=dict(size=16, color=THEME["text"])),
            number=dict(
                font=dict(size=36, color=color or THEME["accent1"]),
                prefix=prefix,
                valueformat=".0f",
            ),
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        height=150,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig
