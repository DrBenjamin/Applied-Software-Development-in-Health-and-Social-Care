from pathlib import Path

import pandas
from shiny import App, render, ui, reactive
from matplotlib import pyplot as plt

app_ui = ui.page_fluid(
    ui.input_slider("which_year", "Select Year", min= 2012, max=2021,value=2012, step=1, sep=""),
    ui.output_plot("some_graph"),
    ui.output_table("some_table"),
)


def server(input, output, session):
    # helper function where we load the file
    @reactive.Calc
    def get_data():
        infile = Path(__file__).parent / "deaths_years_places.csv"
        df = pandas.read_csv(infile)
        return df

    
    @output
    @render.plot
    def some_graph():
        # get data
        deaths = pandas.DataFrame( get_data())
        # which to keep? this could come from an input. dropdown? selector? see year slider
        areas_to_keep = ["NHS Lothian","NHS Fife"]
        year_to_keep = input.which_year() 
        # filter some data
        # this could be single items (use ==) or lists of allowed items (use .isin())
        local_deaths = deaths[ (deaths['HBName'].isin(areas_to_keep)) &\
                                (deaths['Year'] == year_to_keep ) ].copy()
        local_deaths.drop(columns=['Year'], inplace = True)
        # group and cleanup
        grouped = local_deaths.groupby(by="InjuryType").sum( numeric_only = True)
        grouped = grouped.sort_values(by="NumberofDeaths", ascending=False)
        # graph time!
        plt.xticks(rotation='vertical')
        plt.ylim(0, 300)
        bar_colors = ['red' if (cause == 'Poisoning') else 'grey'
                      for cause in grouped.index ]

        plt.title(f"Deaths around {', '.join(areas_to_keep)} in year {year_to_keep}")         
        plt.xlabel("Death Causes") 
        plt.ylabel("Deaths Count") 
        return plt.bar(grouped.index, grouped.NumberofDeaths, color = bar_colors)



    # a bit random example of a table
    @output
    @render.table
    def some_table():
        deaths = pandas.DataFrame( get_data() )
        return pandas.pivot_table(deaths, 
                                  values = ['NumberofDeaths'], 
                                  columns=['Year'],
                                  index=['HBName', 'InjuryType'],
                                 aggfunc=sum).reset_index()


app = App(app_ui, server)
