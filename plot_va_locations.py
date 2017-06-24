from bokeh.io import output_file
from bokeh.models import ColumnDataSource, Range1d
from bokeh.plotting import figure, show
from bokeh.sampledata import us_states
import os
import pandas as pd
from sqlalchemy import create_engine


# get the state boundaries
state_table = pd.DataFrame(us_states.data).T
state_src = ColumnDataSource({
    'lons': state_table['lons'].tolist(),
    'lats': state_table['lats'].tolist()
})

# connect to database
eng = create_engine(
    "mysql://%s:%s@localhost/va_open"
    % (os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASS")))

# read the va location table
va_locs = pd.read_sql_table('va_location', eng)
va_src = ColumnDataSource(va_locs)

# create output file
output_file("va_locations.html")

# create figure
us_map = figure(width=1200, x_axis_location=None, y_axis_location=None)
us_map.background_fill_color = 'black'
us_map.grid.grid_line_color = None
us_map.patches(
    'lons', 'lats', source=state_src, line_color='white', fill_color='black')
us_map.x_range = Range1d(-130, -60)
us_map.y_range = Range1d(20, 55)

us_map.circle(
    'longitude', 'latitude', source=va_src, fill_color='green',
    line_color='white', alpha=0.5)
show(us_map)
