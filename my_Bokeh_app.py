from bokeh.plotting import figure, curdoc
from bokeh.layouts import layout, column, row
from bokeh.models import ColumnDataSource, Slider, Select
from bokeh.models.widgets import Div
from bokeh.io import show, output_notebook
from bokeh.models import HoverTool
import numpy as np
import pandas as pd
from scipy import stats
import get_my_data

# Dummy getData and func modules
class getData:
    dataframes = get_my_data.dataframes

    year_to_days = get_my_data.year_to_days

class func:
    @staticmethod
    def ecdf(n_truncated):
        return 1 - (np.arange(1, n_truncated + 1) / n_truncated)
    
    @staticmethod
    def tcdf(volumes_truncated, selected_vmin, n_truncated):
        log_values_theoretical = np.log(volumes_truncated / selected_vmin)
        b_hat = 1 + n_truncated * (np.sum(log_values_theoretical)) ** (-1)
        tcdf = 1 - (volumes_truncated / selected_vmin) ** (1 - b_hat)
        return tcdf, b_hat
    
    @staticmethod
    def power_law(v_max, selected_vmin, n_truncated, number_of_days, b_hat):
        x_values = np.linspace(v_max, selected_vmin, 1000)
        y_annual = (n_truncated / number_of_days) * (x_values / selected_vmin) ** (-b_hat + 1)
        return x_values, y_annual

# Initial setup
selected_year = '2013'
log_selected_vmin = np.log10(0.0001)
df = getData.dataframes[selected_year]
number_of_days = getData.year_to_days[selected_year]
selected_vmin = 10 ** log_selected_vmin
volumes_truncated = df.Volume[df.Volume >= selected_vmin]
n_truncated = len(volumes_truncated)
ecdf = func.ecdf(n_truncated)
tcdf, b_hat = func.tcdf(volumes_truncated, selected_vmin, n_truncated)
v_max = df['Volume'].max()
x_values, y_annual = func.power_law(v_max, selected_vmin, n_truncated, number_of_days, b_hat)

# Create ColumnDataSource
source_data_plot = ColumnDataSource(data=dict(x=df['Volume'], y=df['Normalized Rank']))
source_cdf_plot = ColumnDataSource(data=dict(x=volumes_truncated, ecdf=ecdf, tcdf=tcdf))
source_line = ColumnDataSource(data=dict(x=[selected_vmin, selected_vmin], y=[df['Normalized Rank'].min(), df['Normalized Rank'].max()]))
source_power_law = ColumnDataSource(data=dict(x=x_values, y=y_annual))

# Create plots
data_plot = figure(title="Data Plot", x_axis_type="log", y_axis_type="log", x_axis_label="Volume (m^3)", y_axis_label="Normalized Rank")
data_plot.scatter('x', 'y', source=source_data_plot, legend_label="Data")
data_plot.line('x', 'y', source=source_line, color='red', legend_label="Selected vmin")
data_plot.line('x', 'y', source=source_power_law, color='black', legend_label="Power-law fit")
hover = HoverTool(tooltips=[
    ("Volume", "@x"),
])
data_plot.add_tools(hover)

cdf_plot = figure(title="CDF Plot", x_axis_type="log", y_axis_label="Percent", x_axis_label="Volume (m^3)")
cdf_plot.line('x', 'ecdf', source=source_cdf_plot, color='blue', legend_label="ECDF")
cdf_plot.line('x', 'tcdf', source=source_cdf_plot, color='green', legend_label="TCDF")
cdf_plot.legend.location = "top_left"

# Create widgets
year_selector = Select(title="Select Year", value="2013", options=list(getData.dataframes.keys()))
vmin_slider = Slider(title="vmin", value=log_selected_vmin, start=np.log10(0.0001), end=np.log10(1), step=0.01, width=1150)
result_display = Div(text=f"v_min: {selected_vmin}, D*: {'NA'}, p-value: {'NA'}, b: {b_hat}, Number of events: {n_truncated}")

# Update function to include the logic from the Dash app
def update_plots(attr, old, new):
    selected_year = year_selector.value
    log_selected_vmin = vmin_slider.value
    
    # Get the selected dataframe and associated parameters
    df = getData.dataframes[selected_year]
    number_of_days = getData.year_to_days[selected_year]
    
    # Convert log-selected vmin back to linear scale
    selected_vmin = 10 ** log_selected_vmin
    
    # Update the data for the line indicating selected vmin
    source_line.data = dict(x=[selected_vmin, selected_vmin], y=[df['Normalized Rank'].min(), df['Normalized Rank'].max()])
    
    # Get the volumes greater than the selected minimum and calculate related parameters
    volumes_truncated = df.Volume[df.Volume >= selected_vmin]
    n_truncated = len(volumes_truncated)
    ecdf = func.ecdf(n_truncated)
    tcdf, b_hat = func.tcdf(volumes_truncated, selected_vmin, n_truncated)
    D_star, p_value = stats.ks_2samp(ecdf, tcdf)
    
    # Update the data for the data plot and the CDF plot
    source_data_plot.data = dict(x=df['Volume'], y=df['Normalized Rank'])
    source_cdf_plot.data = dict(x=volumes_truncated, ecdf=ecdf, tcdf=tcdf)
    
    # Calculate power law values
    v_max = df['Volume'].max()
    x_values, y_annual = func.power_law(v_max, selected_vmin, n_truncated, number_of_days, b_hat)
    
    # Update the data for the power law fit in the data plot
    source_power_law.data = dict(x=x_values, y=y_annual)
    
    # Update the result text    
    result_display.text = (f"<strong>v_min</strong>: {selected_vmin:.4f}&nbsp;&nbsp;&nbsp;&nbsp;"
                           f"<strong>Number of events</strong>: {n_truncated}&nbsp;&nbsp;&nbsp;&nbsp;"
                           f"<strong>D*</strong>: {D_star:.3f}&nbsp;&nbsp;&nbsp;&nbsp;"
                           f"<strong>p-value</strong>: {p_value:.4f}&nbsp;&nbsp;&nbsp;&nbsp;"
                           f"<strong>b</strong>: {b_hat:.2f}<br>"
                           )

# Attach callbacks
year_selector.on_change('value', update_plots)
vmin_slider.on_change('value', update_plots)

# Initial call to update_plots to populate the plots and text
update_plots(None, None, None)

# Create a row for the widgets
widget_row = row(year_selector)

# Create a slider row.
slider_row = row(vmin_slider)

# Create a column for the result text
result_row = row(result_display)

# Create a row for the plots
plot_row = row(data_plot, cdf_plot)

# Stack the rows vertically
final_layout = column(widget_row, slider_row, result_row, plot_row)

# Add the final layout to your Bokeh app document
curdoc().add_root(final_layout)
