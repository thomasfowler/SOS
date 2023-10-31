from bokeh.document import Document
from bokeh.models import ColumnDataSource, FactorRange, HoverTool
from bokeh.plotting import figure


def bar_chart_handler(doc: Document) -> None:
    fruits = ['Actual', 'Forecast', 'Budget']
    counts = [5, 8, 3]

    source = ColumnDataSource(data=dict(fruits=fruits, counts=counts))
    p = figure(x_range=fruits, plot_height=350, title="Actual vs. Forecast vs. Budget", toolbar_location=None, tools="")
    p.vbar(x='fruits', top='counts', width=0.9, source=source)
    p.add_tools(HoverTool())
    doc.add_root(p)
