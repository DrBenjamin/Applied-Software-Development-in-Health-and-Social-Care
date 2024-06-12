# in this file we will load csv in 4 ways:
# 0. from what user typed in
# 1. from a string
# 2. from a file included in shiny interface
# 3. from url - this one is hardest, since it includes 
# a need for 'waiting' for the result (using async)

import pandas as pd
from io import StringIO
from pathlib import Path
import pyodide.http # this is needed for async url fetching


from shiny import App, render, ui

import pandas as pd
from io import StringIO

app_ui = ui.page_fluid(
    #  this is how you would 'load' a csv from a string, and pre-fill it
    ui.input_text_area("csv_text", "CSV Text - change it to see table change", 
                       value="source,fruit,color\nuser_input,orange,amber\nuser_input,plum,purple"
                       ,rows=5
                      ),
    ui.panel_title("data from user input"),
    ui.output_table("parsed_data_from_user_input"),
    ui.panel_title("data from string"),
    ui.output_table("parsed_data_from_string"),
    ui.panel_title("data from attached file"),
    ui.output_table("parsed_data_from_file"),
    ui.panel_title("data from online file"),
    ui.output_table("parsed_data_from_url"),

)

def server(input, output, session):

    @output
    @render.table
    def parsed_data_from_user_input():
        file_text = StringIO(input.csv_text())
        data = pd.read_csv(file_text)
        return data
    
    @output
    @render.table
    def parsed_data_from_string():

        # we can 'pretend' to have a csv, eg for testing 
        # notice tripple " quote, which is a 'block string' and allows enters
        csv_text = """
        source,fruit,color
        string,apple,green
        string,cherry,maroon
        """
        # if you wanted a non-block normal string you could say
        # csv_text = "source,fruit,color\nstring,apple,green\nstring,cherry,maroon"

        # StringIO pretends the text came from a file, so that pd knows what to do
        file_text = StringIO(csv_text)
        data = pd.read_csv(file_text)
        return data

    @output
    @render.table
    def parsed_data_from_file():
        # actul local file
        infile = Path(__file__).parent / "demo.csv"
        data = pd.read_csv(infile)
        return data
    
    @output
    @render.table
    async  def parsed_data_from_url():
        print("starting")
        # online file
        file_url = "https://raw.githubusercontent.com/drpawelo/data/main/random/fruits_source.csv"
        response = await pyodide.http.pyfetch(file_url)
        data = await response.string()
        loaded_df = pd.read_csv(StringIO(data))
        print(loaded_df)
        # notice await - it means that the function which follows 
        # is 'alowed' to take time (async) and we are fine with (a)waiting for it
        print("done")
        return loaded_df


# This is a shiny.App object. It must be named `app`.
app = App(app_ui, server)
