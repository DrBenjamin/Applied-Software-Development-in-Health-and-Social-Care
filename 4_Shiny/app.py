import pandas
from shiny import App, render, ui, reactive
from shiny.types import ImgData
from pathlib import Path
from matplotlib import pyplot as plt
from PIL import Image
from pathlib import Path
here = Path(__file__).parent
nhs_areas = ["NHS Ayreshire and Arran", "NHS Borders", "NHS Dumfries and Galloway", "NHS Fife", "NHS Forth Valley", "NHS Grampian", "NHS Greater Glasgow and Clyde", "NHS Highland", "NHS Lanarkshire", "NHS Lothian", "NHS Orkney", "NHS Shetland", "NHS Tayside", "NHS Western Isles"]

app_ui = ui.page_fluid(
    ui.h1("Deaths in Scotland"),
    ui.input_selectize("which_area", "Select Area(s)", choices=nhs_areas, multiple=True),
    ui.output_image("show_image", height="100%"),
    ui.input_slider("which_year", "Select Year", min=2012, max=2021, value=2012, step=1, sep="", width="100%"),
    ui.output_plot("show_graph", width="100%"),
    ui.output_table("show_table", width="100%"),
)

def server(input, output, session):
    @reactive.Calc
    def get_data():
        # Loading the file
        infile = Path(__file__).parent / "deaths_years_places.csv"
        df = pandas.read_csv(infile)
        return df

    @output
    @render.plot
    def show_graph():
        # Getting the data
        deaths = pandas.DataFrame( get_data())
        
        # Choosing the data to be displayed
        areas_to_keep = input.which_area()
        year_to_keep = input.which_year() 
        
        # Filtering the data
        local_deaths = deaths[ (deaths['HBName'].isin(areas_to_keep)) &\
                                (deaths['Year'] == year_to_keep ) ].copy()
        local_deaths.drop(columns=['Year'], inplace=True)
        
        # Grouping and cleaning up
        grouped = local_deaths.groupby(by="InjuryType").sum(numeric_only=True)
        grouped = grouped.sort_values(by="NumberofDeaths", ascending=False)
        
        # Visualizing
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
        
    # Visualizing the areas
    @render.image(delete_file=False)
    def show_image():
        # Creating the map
        areas_list = input.which_area()
        image = 'Maps/Map.png'
        file = here / image
        img = Image.open(file)
        map = Image.new("RGB", img.size, (255, 255, 255))
        map.paste(img, box=(0, 0), mask=img.split()[3]) # 3 is the alpha channel
        for area in areas_list:
            image = 'Maps/' + nhs_areas[nhs_areas.index(area)].replace(" ", "_") + '.png'
            file = here / image
            img_overlay = Image.open(file)
            map.paste(img_overlay, box=(0, 0), mask=img_overlay.split()[3]) # 3 is the alpha channel
        image = "Maps/Map_.png"
        file = here / image
        map.save(file)
        img: ImgData = {"src": str(file), "width": "100%"}
        return img
        
    # Showing a table
    @output
    @render.table
    def show_table():
        deaths = pandas.DataFrame(get_data())
        
        # Choosing the data to be displayed
        areas_to_keep = input.which_area()
        
        # Filtering the data
        local_deaths = deaths[deaths['HBName'].isin(areas_to_keep)].copy()
        return pandas.pivot_table(local_deaths, 
                                  values = ['NumberofDeaths'], 
                                  columns=['Year'],
                                  index=['HBName', 'InjuryType'],
                                  aggfunc=sum).reset_index()

app = App(app_ui, server)
