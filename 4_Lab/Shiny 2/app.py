from shiny import App, render, ui, reactive
import pandas as pd
import pyodide.http
from io import StringIO
import matplotlib.pyplot as plt

# Some notes:
# async - this means a function we're defining might take a while to run
# await - this means that we do really want to wait for this function call
# nonlocal - this means the variable we're using is not in a local scope 
#           (it is global / shared between functions)

app_ui = ui.page_fluid(
    ui.tags.p("Number of Deaths in that year"),
    ui.input_slider("select_years", "Range slider", value=(2012, 2022), min=2012, max=2022, sep=""),
        ui.output_table("deaths_table"),
        ui.output_plot("deaths_graph")
)

def server(input, output, session):
    # start with empty data
    deaths_df = None 

    # only if data is not there yet, get it from the web
    async def refresh_data():
        nonlocal deaths_df 
        if (deaths_df is None): 
            print("Load online Data")
            url = "https://raw.githubusercontent.com/drpawelo/data/main/health/ui_deaths_2022.csv"
            response = await pyodide.http.pyfetch(url)
            data = await response.string()
            deaths_df = pd.read_csv(StringIO(data)) # and save in a global variable

    @reactive.Calc
    async def just_selected_data():
        nonlocal deaths_df
        await refresh_data()
        if (deaths_df is None): # if data not there, return an empty 
            return pd.DataFrame({'Year':[], 'NumberofDeaths':[] })
        else:
            year_start, year_end = input.select_years()
            ca_scotland = "S92000003"
            just_accumulated = deaths_df[(deaths_df.AgeGroup == "All") & \
                (deaths_df.InjuryLocation == "All") & (deaths_df.CA == ca_scotland) & \
                (deaths_df.Sex == "All") & (deaths_df.InjuryType == "All")] \
                [ ['Year', 'NumberofDeaths'] ]
            just_some_years = just_accumulated[(just_accumulated.Year >= year_start) & \
                    (just_accumulated.Year <= year_end)]
            return just_some_years
    
    @output
    @render.table
    async def deaths_table():
        deaths_data = await just_selected_data()
        return deaths_data


    @output
    @render.plot()
    async def deaths_graph():
        deaths_data = await just_selected_data()
        return plt.bar(deaths_data.Year, deaths_data.NumberofDeaths)

app = App(app_ui, server)
