import pandas
from shiny import App, render, ui, reactive
from pathlib import Path
from matplotlib import pyplot as plt

app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.input_selectize("which_area", "Select Area(s)", choices=["NHS Ayrshire and Arran", "NHS Dumfries and Galloway", "NHS Forth Valley", "NHS Grampian", "NHS Grampian", "NHS Highland", "NHS Lothian", "NHS Orkney", "NHS Shetland", "NHS Western Isles", "NHS Fife", "NHS Tayside", "NHS Greater Glasgow and Clyde", "NHS Lanarkshire", ""], multiple=True, selected=["NHS Lothian"]),
        ui.input_slider("which_year", "Select Year", min=2012, max=2021, value=2012, step=1, sep=""),
        #ui.output_text("some_text", "Deaths in Scotland by Area and Year"),
        ui.output_plot("some_graph"),
                ui.output_table("some_table"),
    ),
)

def server(input, output, session):
    # Loading file
    @reactive.Calc
    def get_data():
        infile = Path(__file__).parent / "deaths_years_places.csv"
        df = pandas.read_csv(infile)
        return df
    
    @output
    @render.plot
    def some_graph():
        # Getting the data
        deaths = pandas.DataFrame( get_data())
        
        # Choosingthe data to be displayed
        areas_to_keep = input.which_area()
        year_to_keep = input.which_year() 
        
        # Filtering the data
        print('Type:', type(areas_to_keep))
        local_deaths = deaths[ (deaths['HBName'].isin(areas_to_keep)) &\
                                (deaths['Year'] == year_to_keep ) ].copy()
        local_deaths.drop(columns=['Year'], inplace = True)
        
        # Grouping and cleaning up
        grouped = local_deaths.groupby(by="InjuryType").sum( numeric_only = True)
        grouped = grouped.sort_values(by="NumberofDeaths", ascending=False)
        
        # Vizualizing
        plt.xticks(rotation='vertical')
        plt.ylim(0, 300)
        bar_colors = ['red' if (cause == 'Poisoning') else 'grey'
                      for cause in grouped.index ]

        plt.title(f"Deaths around {', '.join(areas_to_keep)} in year {year_to_keep}")         
        plt.xlabel("Death Causes") 
        plt.ylabel("Deaths Count") 
        if len(local_deaths) > 0:
          return plt.bar(grouped.index, grouped.NumberofDeaths, color = bar_colors)
        else:
          return None
        
    # Showing a table
    @output
    @render.table
    def some_table():
        deaths = pandas.DataFrame( get_data() )
        
        # Choosingthe data to be displayed
        areas_to_keep = input.which_area()
        year_to_keep = input.which_year() 
        
        # Filtering the data
        local_deaths = deaths[deaths['HBName'].isin(areas_to_keep)].copy()
        return pandas.pivot_table(local_deaths, 
                                  values = ['NumberofDeaths'], 
                                  columns=['Year'],
                                  index=['HBName', 'InjuryType'],
                                 aggfunc=sum).reset_index()

app = App(app_ui, server)
