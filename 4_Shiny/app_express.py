from shiny import reactive
from shiny.express import render, ui 
from datetime import datetime

ui.h1("Title")

@reactive.calc
def time():
    reactive.invalidate_later(1)
    return datetime.now()

@render.code
def greeting():
    return f"Hello, world!\nIt's currently {time()}."