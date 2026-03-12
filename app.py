from ipyleaflet import (
    Marker,
    DivIcon,
    Map,
    basemaps,
    leaflet,
    Popup,
    Choropleth,
    LayersControl,
    GeoJSON,
    GeoData,
    Popup,
    DivIcon,
    Marker,
)
from shiny import App, reactive, ui, render
from shinywidgets import output_widget, render_widget
from ipywidgets import widgets
from shapely.geometry import shape
import pandas as pd
import shiny.experimental as x
import plotly.express as px
import plotly.graph_objects as go
from plotly_streaming import render_plotly_streaming
from pathlib import Path
from branca.colormap import linear
import json
import copy
import faicons
from shared import region_party_summary, df_final, party_gender_summary, council_summary, district_summary, region_summary

with open("data/mw.json", "r") as f:
    districts_geojson = json.load(f)

category_colors = {
    "Serverless": 0,
    "Containers": 1,
    "Cloud Operations": 2,
    "Security & Identity": 3,
    "Dev Tools": 4,
    "Machine Learning & GenAI": 5,
    "Data": 6,
    "Networking & Content Delivery": 7,
    "Front-End Web & Mobile": 8,
    "Storage": 9,
    "Game Tech": 10,
}
bill_rng = (
    min(district_summary.Female_percentage),
    max(district_summary.Female_percentage),
)

# reactive data source
def df_final_data():
    return df_final

def get_color_theme(theme, list_categories=None):

    if theme == "Custom":
        list_colors = [
            "#F6AA54",
            "#2A5D78",
            "#9FDEF1",
            "#B9E52F",
            "#E436BB",
            "#6197E2",
            "#863CFF",
            "#30CB71",
            "#ED90C7",
            "#DE3B00",
            "#25F1AA",
            "#C2C4E3",
            "#33AEB1",
            "#8B5011",
            "#A8577B",
        ]
    elif theme == "RdBu":
        list_colors = px.colors.sequential.RdBu.copy()
        del list_colors[5]  # Remove color position 5
    elif theme == "GnBu":
        list_colors = px.colors.sequential.GnBu
    elif theme == "RdPu":
        list_colors = px.colors.sequential.RdPu
    elif theme == "Oranges":
        list_colors = px.colors.sequential.Oranges
    elif theme == "Blues":
        list_colors = px.colors.sequential.Blues
    elif theme == "Reds":
        list_colors = px.colors.sequential.Reds
    elif theme == "Hot":
        list_colors = px.colors.sequential.Hot
    elif theme == "Jet":
        list_colors = px.colors.sequential.Jet
    elif theme == "Rainbow":
        list_colors = px.colors.sequential.Rainbow

    if list_categories is not None:
        final_list_colors = [
            list_colors[category_colors[category] % len(list_colors)]
            for category in list_categories
        ]
    else:
        final_list_colors = list_colors

    return final_list_colors

def get_color_template(mode):
    if mode == "light":
        return "plotly_white"
    else:
        return "plotly_dark"

def get_background_color_plotly(mode):
    if mode == "light":
        return "white"
    else:
        return "rgb(29, 32, 33)"

def get_map_theme(mode):
    print(mode)
    if mode == "light":
        return basemaps.CartoDB.Positron
    else:
        return basemaps.CartoDB.DarkMatter

def create_custom_icon(count):

    size_circle = 45 + (count / 10)

    # Define the HTML code for the icon
    html_code = f"""
    <div style=".leaflet-div-icon.background:transparent !important;
        position:relative; width: {size_circle}px; height: {size_circle}px;">
        <svg width="{size_circle}" height="{size_circle}" viewBox="0 0 42 42"
            class="donut" aria-labelledby="donut-title donut-desc" role="img">
            <circle class="donut-hole" cx="21" cy="21" r="15.91549430918954"
                fill="white" role="presentation"></circle>
            <circle class="donut-ring" cx="21" cy="21" r="15.91549430918954"
                fill="transparent" stroke="color(display-p3 0.9451 0.6196 0.2196)"
                stroke-width="3" role="presentation"></circle>
            <text x="50%" y="60%" text-anchor="middle" font-size="13"
                font-weight="bold" fill="#000">{count}</text>
        </svg> Malawi
    </div>
    """

    # Create a custom DivIcon
    return DivIcon(
        icon_size=(50, 50), icon_anchor=(25, 25), html=html_code, class_name="dummy"
    )


def create_custom_popup(country, total, dark_mode, color_theme):

    # Group by 'region' and count occurrences of each region
    df = district_summary

    # Create a pie chart using plotly.graph_objects
    data = [
        go.Pie(
            labels="Region",
            values="%",
            hole=0.3,
            textinfo="percent+label",
            marker=dict(colors=get_color_theme(color_theme, "Region")),
        )
    ]

    # Set title and template
    layout = go.Layout(
        title=f"{total} Community Builders in {country}",
        template=get_color_template(dark_mode),
        paper_bgcolor=get_background_color_plotly(dark_mode),
        title_x=0.5,
        titlefont=dict(size=20),
        showlegend=False,
    )

    figure = go.Figure(data=data, layout=layout)
    figure.update_traces(
        textposition="outside", textinfo="percent+label", textfont=dict(size=15)
    )
    figure.layout.width = 600
    figure.layout.height = 400

    popup = Popup(child=go.FigureWidget(figure), max_width=600, max_height=400)

    return popup


app_ui = ui.page_fillable(
    ui.page_navbar(
        ui.nav_spacer(),
        ui.nav_panel(
            "Dashboard",
            ui.row(
                ui.layout_columns(
                    ui.output_ui("total_registered_box"),
                    ui.output_ui("total_voted_box"),
                    ui.output_ui("voter_empathy_box"),                    
                    ui.output_ui("turn_out_box"),
                    col_widths=(3, 3, 3, 3),
                ),
            ),
            ui.row(
                ui.layout_columns(
                    x.ui.card(
                        ui.row(
                            ui.layout_columns(
                                x.ui.card(output_widget("plot_0")),
                                x.ui.card(output_widget("plot_1")),
                                col_widths=(6, 6),
                            ),
                        ),
                        ui.row(
                            ui.layout_columns(
                                x.ui.card(output_widget("plot_3")),
                                col_widths=(12),
                            ),
                        ),
                    ),
                    x.ui.card(output_widget("plot_5")),
                    col_widths=(8, 4),
                ),
            ),
        ),
        # ui.nav_panel(
        #     "Map",
        # ),
        title=ui.div(
            ui.img(
                src="images/logo.png", style="max-height: 40px; vertical-align: middle;"
            ),
            ui.span(
                "Gender Representation in Parliament",
                style="font-size: 22px; font-weight: 600; margin-left: 8px; vertical-align: middle;",
            ),
            style="display: flex; align-items: center;",
        ),
        id="page",
        sidebar=ui.sidebar(
            ui.div(
                ui.input_slider(
                    "Total",
                    "Female Representation (%)",
                    min=bill_rng[0],
                    max=bill_rng[1],
                    value=bill_rng,
                    pre="",
                ),   
            ),
            ui.div(
                ui.input_checkbox_group(
                    "Region",
                    "Region",
                    ["Southern", "Central", "Northern"],
                    selected=["Southern", "Central", "Northern"],
                    inline=False,
                ),                
                ui.input_action_button(
                    "select_all_regions", "Select All", class_="btn-sm me-1"
                ),
                ui.input_action_button(
                    "clear_all_regions", "Clear All", class_="btn-sm"
                ),
                style="max-height: 550px; overflow-y: auto; font-size: 11px; style:none;",
            ),
            ui.div(
                ui.input_checkbox_group(
                    "District",
                    "District",
                    sorted(df_final_data()["District"].unique().tolist()),
                    selected=(df_final_data()["District"].unique().tolist()),
                    inline=False
                ),
                ui.input_action_button(
                    "select_all_districts", "Select All", class_="btn-sm"
                ),
                ui.input_action_button(
                    "clear_all_districts", "Clear All", class_="btn-sm"
                ),
                style="max-height: 550px; overflow-y: auto; font-size: 11px; style:none;",
            ),
            ui.input_action_button("reset", "Reset filter"),
            ui.input_dark_mode(id="dark_mode", mode="light"),
            open="closed",
            # style="width: 100%; --bs-accent: #FD9902; color: #FD9902; height: 8px;",
        ),
        footer=ui.h6(
            ui.row(
                "www.francis.chidziwisano.github.io © 2024",
                style="color: white !important; text-align: center;",
            )
        ),
        window_title="Malawi 2020 General General Elections Turn Out",
    ),
    ui.tags.style(
        """
        .leaflet-popup-content {
            width: 600px !important;
        }
        .navbar-nav {
            margin-left: auto !important;
        }
        .leaflet-div-icon {
            background: transparent !important;
            border: transparent !important;
        }
        .collapse-toggle {
            color: #OOO !important;
            background-color: white !important;
        }
        .main {
            /* Background image */
            background-image: url("images/background_dark.png");
            height: 100%;
            background-position: center;
            background-repeat: no-repeat;
            background-size: cover;
        }        
        div#map_full.html-fill-container {
            height: -webkit-fill-available !important;
            min-height: 850px !important;
            max-height: 2000px !important;
        }
        div#main_panel.html-fill-container {
            height: -webkit-fill-available !important;
        }
        .input_checkbox_group:checked{
            color: #000;
            accent-color: FD9902;
        }
        .nav_panel {
                margin-right: 800px;
                background: #FD9902;
        }
        """
    ),
    icon="images/favicon.ico",
)


def server(input, output, session):

    @reactive.effect
    @reactive.event(input.select_all_districts)
    def _():
        d = df_final_data()
        ui.update_checkbox_group(
            "District",
            choices=sorted(d["District"].unique().tolist()),
            selected=sorted(d["District"].unique().tolist()),
        )

    @reactive.effect
    @reactive.event(input.select_all_regions)
    def _():
        ui.update_checkbox_group(
            "Region",
            choices=sorted(region_summary["Region"].unique().tolist()),
            selected=sorted(region_summary["Region"].unique().tolist()),
        )
    
    @reactive.effect
    @reactive.event(input.clear_all_districts)
    def _():
        ui.update_checkbox_group("District", selected=[])

    @reactive.effect
    @reactive.event(input.clear_all_regions)
    def _():
        ui.update_checkbox_group("Region", selected=[])


    @reactive.calc
    def tips_data():
        bill = input.Total()
        idx1 = district_summary.Female_percentage.between(bill[0] - 1, bill[1] + 1)
        idx2 = district_summary.Region.isin(input.Region())
        idx3 = district_summary.District.isin(input.District())
        return district_summary[idx1 & idx2 & idx3]

    @reactive.calc
    def regional_data():
        rdx1 = region_summary.Region.isin(input.Region())
        return region_summary[rdx1]
    
    @reactive.calc
    def df_final_data():
        bill = input.Total()
        df_final_idx1 = df_final.Region.isin(input.Region())
        df_final_idx2 = df_final.District.isin(input.District())
        df_final_idx3 = district_summary.Female_percentage.between(bill[0] - 1, bill[1] + 1)
        return df_final[df_final_idx1 & df_final_idx2 & df_final_idx3]

    @output
    @render.ui
    def total_registered_box():
        d = tips_data()
        return ui.value_box(
            title=ui.span("# of Constituencies", style="font-size:16px; color:#6B7280;"),
            showcase=faicons.icon_svg(
                "location-dot", width="50px", fill="#A5A5A5 !important"
            ),
            value=ui.span(f"{int(d.Total.sum()):,}", style="font-size:40px; font-weight:700; color:#1F2937;"),
        )

    @output
    @render.ui
    def total_voted_box():
        d = tips_data()
        with_male = round(
            (
                (d.Total.sum()) - (d.Pending.sum())
            )
        )
        return ui.value_box(
            title=ui.span("Members of Parliament", style="font-size:16px; color:#6B7280;"),
            showcase=faicons.icon_svg(
                "users", width="50px", fill="#B3E5FC !important"
            ),
            value=ui.span(f"{int((with_male)):,}", style="font-size:40px; font-weight:700; color:#1F2937;"),
        )

    @output
    @render.ui
    def voter_empathy_box():
        d = tips_data()
        voter_empathy = round(
            (
                d.Male.sum() / d.Total.sum()
            )
            * 100,
        )
        with_male = round(
            (
                (d.Male != 0).sum()
            )
        )
        return ui.value_box(
            title=ui.span("Male", style="font-size:16px; color:#6B7280;"),
            showcase=faicons.icon_svg(
                "person", width="50px", fill="#4C9AFF !important"
            ),
            value=ui.markdown(
                f"<span style='font-size:40px; font-weight:700; color:#1F2937;'> {int(d.Male.sum()):,} </span>"
                f"<span style='font-size:14px; color: grey; vertical-align: super;'><i> ({voter_empathy}%) | {with_male} Districts</i></span>"
            ),
        )
    
    @output
    @render.ui
    def turn_out_box():
        d = tips_data()
        total_registered = round(
            (d.Female.sum() / d.Total.sum()) * 100
        )
        no_female = round(
            (
                (d.Female != 0).sum()
            )
        )
        return ui.value_box(
            title=ui.span("Female", style="font-size:16px; color:#6B7280;"),
            showcase=faicons.icon_svg(
                "person-dress", width="50px", fill="#FF6FB1 !important"
            ),
            value=ui.markdown(
                f"<span style='font-size:40px; font-weight:700; color:#1F2937;'> {int(d.Female.sum()):,} </span>"
                f"<span style='font-size:14px; color: grey; vertical-align: super;'><i> ({total_registered}%) | {no_female}  Districts</i></span>"
            ),
            theme="",
        )

    @reactive.Calc
    @output
    @render_widget
    @reactive.event(input.dark_mode)
    def map_full():
        map = Map(
            basemap=get_map_theme(input.dark_mode()),
            center=(-13.254308, 34.301525),
            zoom=7,
            scroll_wheel_zoom=True,
        )

        with ui.Progress(min=0, max=len(district_summary)) as progress:
            progress.set(
                message="Calculation in progress", detail="This may take a while..."
            )

            for index, row in district_summary.iterrows():
                lat = float(row["Latitude"])
                lon = float(row["Longtude"])
                country = row["District"]
                count = row["Total"]

                # Add a marker with the custom icon to the map
                custom_icon = create_custom_icon(count)

                marker = Marker(
                    location=(lat, lon),
                    icon=custom_icon,
                    draggable=False,
                    # popup=custom_popup,
                )

                map.add_layer(marker)

                progress.set(index, message=f"Calculating country {country}")

            map.add_control(leaflet.ScaleControl(position="bottomleft"))

            progress.set(index, message="Rendering the map...")

        return map

    @reactive.Calc
    @output
    @render_plotly_streaming()
    def plot_0():
        d = df_final_data()

        custom_colors = {
        'Female': "#FF6FB1",  # purple  
        'Male': "#4C9AFF",    # teal
        'Pending': "#A5A5A5"     # teal
        }

        fig1 = px.pie(
            d,
            names="Gender",
            hole=0.5,
            title="Gender Representation | National",
            template=get_color_template(input.dark_mode()),
            color="Gender",
            color_discrete_map=custom_colors,
        )

        fig1.update_layout(
            paper_bgcolor=get_background_color_plotly(input.dark_mode()), title_x=0.5
        )
        fig1.update_traces(
            textposition="outside",
            texttemplate="<b>%{label}<br>%{value} </b><i><span style='font-size:14px; color: grey;>(%{percent:.0%})</span></i>",
            hovertemplate="<b>%{label}</b><br>Voter Turnout: %{percent}<extra></extra>",
            textfont=dict(size=15),
            showlegend=False,
        )
        fig1.update_layout(
            title={
                'text': "<b> National </b> | <span style='font-size:16px; color: grey; vertical-align: super;'> <i> Gender Distribution </i></span> ",
                'x': 0,             # 0 = left, 0.5 = center, 1 = right
                'xanchor': 'left'
            })

        return fig1
    
    @reactive.Calc
    @output
    @render_plotly_streaming()
    def plot_1():
        # Melt dataframe for plotly
            df = regional_data().copy()

            # Create a single bar chart with both count and percentage annotations
            df_melted = pd.melt(
                df, 
                id_vars=['Region', 'Total'], 
                value_vars=['Male', 'Female',  'Pending'],
                var_name='Gender', 
                value_name='Count')

            # Calculate percentages for plotting bars
            df_melted['Percentage'] = df_melted.apply(
                lambda row: (row['Count'] / row['Total'])*100 if row['Total'] > 0 else 0,
                axis=1
            ) 

            fig2 = px.bar(
                        df_melted, 
                        x='Region', 
                        y='Percentage',
                        category_orders={
                            "Region": ["Central", "Northern", "Southern"]
                        },
                        color='Gender',
                        title='Gender Distribution by Region with Percentages',
                        labels={'Count': 'Number of People', 'Region': 'Region'},
                        barmode='group',
                        color_discrete_map={'Male': '#4C9AFF', 'Female': '#FF6FB1', 'Pending': '#A5A5A5'})

            # Add both count and percentage annotations
            for i, row in df_melted.iterrows():
                region = row['Region']
                gender = row['Gender']
                count = row['Count']
                total = row['Total']
                
                # Get percentage for this gender in this region
                if gender in ['Female', 'Male']:
                    # Calculate percentage
                    # total = df.loc[df['Region'] == region, 'Total'].values[0]
                    percentage = (count / total) * 100 if total > 0 else 0
                    
                    # Add annotation with both count and percentage
                    fig2.add_annotation(
                        x=region,
                        y=percentage,
                        text=f"<b>{percentage:.0f}%<br><span style='font-size:14px; color: grey;'><i>({count})</i></span></b>",
                        showarrow=False,
                        font=dict(size=15),
                        yshift=22 if percentage > 0 else 0,
                        xshift= {'Male': -45, 'Female': 0, 'Pending': 40}[gender]
                    )
                else:
                    # For Pending, just show count
                    percentage = (count / total) * 100 if total > 0 else 0
                    fig2.add_annotation(
                        x=region,
                        y=count,
                        text=f"<b style='font-size:14px;'>{percentage:.0f}%</b>",
                        showarrow=False,
                        font=dict(size=10),
                        yshift=18 if count > -1 else 0,
                        xshift= {'Male': -40, 'Female': 0, 'Pending': 40}[gender]
                    )

            fig2.update_layout(
                title={'x': 0.5, 'xanchor': 'center'},
                xaxis_title="",
                yaxis_title="<i>Number of Mp's</i>",
                hovermode='x unified',
                legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.2,      # position below chart
                xanchor='right',
                x=0.4,
                title_text=None,
                font=dict(size=14, weight='bold'),
                title=dict(text="Gender", font=dict(size=14, weight='bold'))
                ),
                xaxis=dict(
                            tickfont=dict(size=15, color="black",  # optional font settings
                                        weight="bold")),  # bold labels
                 # Remove background color
                plot_bgcolor='#FFF',   # transparent plot area
                paper_bgcolor='#FFF'   # transparent surrounding area
            )
            fig2.update_layout(
            title={
                'text': "<b> Regional </b> | <span style='font-size:16px; color: grey; vertical-align: super;'><i> Gender Distribution </i></span>",
                'x': 0,             # 0 = left, 0.5 = center, 1 = right
                'xanchor': 'left'
            })
            # fig2.show()
            return(fig2)     

    @reactive.Calc
    @output
    @render_widget
    def plot_5():
        d = tips_data()  # Your reactive filtered dataframe

        fig5 = Map(center=(-13.254308, 34.301525), zoom=7)

        # Safe copy of geojson and filter districts
        geojson_fixed = copy.deepcopy(districts_geojson)
        district_names = d["District"].str.strip().tolist()
        geojson_fixed["features"] = [
            f
            for f in geojson_fixed["features"]
            if f["properties"]["name"].strip() in district_names
        ]

        # Assign ID for Choropleth
        for f in geojson_fixed["features"]:
            f["id"] = f["properties"]["name"].strip()

        # Colormap
        values = list(d["Female_percentage"])
        colormap = linear.PuRd_03.scale(min(values), max(values))
        colormap.caption = "Voter Empathy (Female_percentage)"

        # Choropleth layer
        choro = Choropleth(
            geo_data=geojson_fixed,
            choro_data={
                k.strip(): v for k, v in zip(d["District"], d["Female_percentage"])
            },
            key_on="id",
            colormap=colormap,
            hover_style={"fillOpacity": 0.9, "color": "red"},
            border_color="black",
            style={"fillOpacity": 0.8, "dashArray": "5, 5"},
        )
        fig5.add_layer(choro)

        # ---- STATIC DISTRICT NAME LABELS ----
        for feature in geojson_fixed["features"]:
            geom = shape(feature["geometry"])
            centroid = geom.centroid
            name = feature["properties"]["name"].strip()

            label = Marker(
                location=(centroid.y, centroid.x),
                icon=DivIcon(
                    html=f"""
                        <div style="
                            font-size:8pt;
                            # font-weight:bold;
                            color:#000;
                            padding:0px 4px;
                            white-space:nowrap;
                        ">
                            {name}
                        </div>
                    """
                ),
            )

            fig5.add_layer(label)

        # Label marker holder
        label_marker = []

        # Hover callback
        def on_hover(event, feature, **kwargs):
            nonlocal label_marker
            if label_marker:
                fig5.remove_layer(label_marker[0])
                label_marker = []
            if event == "mouseover":
                geom = shape(feature["geometry"])
                centroid = geom.centroid
                name = feature["properties"]["name"].strip()
                voter_empathy = d.loc[
                    d["District"].str.strip() == name, "Female_percentage"
                ].values[0]

                marker = Marker(
                    location=(centroid.y, centroid.x),
                    icon=DivIcon(
                        html=f"""
                            <div style="
                                display:inline-block;
                                text-align:center;
                                white-space:nowrap;
                                font-size:12pt;
                                color:black;
                                background:white;
                                padding:2px 6px;
                                border-radius:4px;
                                border:1px solid gray;
                            ">
                                <div style="font-size:12pt; color:darkgreen;">{round(voter_empathy)}%</div>
                            </div>
                            """
                    ),
                )
                fig5.add_layer(marker)
                label_marker = [marker]

        # Invisible GeoJSON layer for hover detection
        geo = GeoJSON(
            data=geojson_fixed,
            style={"color": "transparent", "fillOpacity": 0},
            hover_style={"fillOpacity": 0.1},
        )
        geo.on_hover(on_hover)
        fig5.add_layer(geo)

        # Controls
        fig5.add_control(LayersControl())
        fig5.add_control(colormap)

        return fig5

    @reactive.Calc
    @output
    @render_plotly_streaming()
    def plot_3():
        d = tips_data()
        # Create the bar plot
        fig3 = px.bar(
            d,
            x="District",
            y="Female_percentage",
            color="Female_percentage",
            color_continuous_scale="PuRd",  # Or "Blues", "Plasma", etc.
            text="Female_percentage",
            text_auto=True,
            labels={
                "district": "District",
                "count": "Female_percentage",
                "region": "Region",
                "location": "Latitude",
            },
            title="Female Representation by District",
            template=get_color_template(input.dark_mode()),
        )
        fig3.update_traces(texttemplate='%{text}%')

        fig3.update_layout(
            xaxis=dict(
                tickfont=dict(size=14, color="black"),  # X-axis tick labels
                showgrid=False,  # Hide x-axis gridlines
            ),
            yaxis=dict(
                tickfont=dict(size=15, color="black"),  # Y-axis tick labels
                gridcolor="lightgray",  # Y-axis gridline color
                range=[0, 70],  # Set y-axis range
            ),
        )
        fig3.update_layout(
            title={
                'text': "<b>District</b> | <span style='font-size:16px; color: grey; vertical-align: super;'> <i>Percentage of Female Members of Parliament </i></span>",
                'x': 0,             # 0 = left, 0.5 = center, 1 = right
                'xanchor': 'left'
            })
        return fig3


static_dir = Path(__file__).parent / "static"
app = App(app_ui, server, static_assets=static_dir)
