from bokeh.io import export, output_file
from bokeh.models import (
    ColumnDataSource, HoverTool, LinearColorMapper, Range1d)
from bokeh.palettes import Reds6 as palette
from bokeh.plotting import figure, show
from bokeh.sampledata import us_states
import os
import pandas as pd
from sqlalchemy import create_engine

# connect to database
eng = create_engine(
    "mysql://%s:%s@localhost/va_open"
    % (os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASS")))

# execute query
with open('ptsd_rate_by_state.sql', 'r') as fid:
    ptsd_table = pd.read_sql_query(fid.read(), eng)

# get the state boundaries
state_table = pd.DataFrame(us_states.data).T

# merge tables
ptsd_table = pd.merge(
    state_table, ptsd_table, how='inner', left_index=True, right_on='state')
ptsd_table['ptsd_rate'] = 100 * ptsd_table.total_ptsd / ptsd_table.total_served

# create data source for map
src = ColumnDataSource({
    'lons': ptsd_table['lons'].tolist(),
    'lats': ptsd_table['lats'].tolist(),
    'ptsd_rate': ptsd_table['ptsd_rate'],
    'total_served': ptsd_table['total_served'],
    'total_ptsd': ptsd_table['total_ptsd'],
    'name': ptsd_table['name']
})

# generate color map
palette.reverse()
cmap = LinearColorMapper(palette=palette)

# create output file
output_file("ptsd_by_state.html")

# create figure
us_map = figure(
    width=1200, x_axis_location=None, y_axis_location=None,
    tools="hover", title="Rates of Post Traumatic Stress (2015)")
us_map.grid.grid_line_color = None
us_map.patches(
    'lons', 'lats', source=src, line_color='black',
    fill_color={'field': 'ptsd_rate', 'transform': cmap})
us_map.x_range = Range1d(-130, -60)
us_map.y_range = Range1d(20, 55)

# program hover tool
hover = us_map.select_one(HoverTool)
hover.tooltips = [
    ("State", "@name"),
    ("Total Veterans Enrolled", "@total_served"),
    ("Total PTSD", "@total_ptsd (@ptsd_rate{int}%)")
]

export(us_map)
show(us_map)
