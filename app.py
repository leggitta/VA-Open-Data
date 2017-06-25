import flask
from bokeh.embed import components
from bokeh.models import (
    ColumnDataSource, HoverTool, LinearColorMapper, Range1d)
from bokeh.palettes import Reds8 as palette
from bokeh.plotting import figure
from bokeh.sampledata import us_states
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
import os
import pandas as pd
from sqlalchemy import create_engine

app = flask.Flask(__name__)
palette.reverse()


def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]


@app.route("/")
def map_ptsd():
    # Grab the inputs arguments from the URL
    args = flask.request.args

    # Get all the form arguments in the url with defaults
    metric = getitem(args, 'metric', 'PTSD Rate')
    year = getitem(args, 'year', '2014')

    # connect to database
    eng = create_engine(
        "mysql://%s:%s@localhost/va_open"
        % (os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASS")))

    # execute query
    with open('ptsd_rate_by_state.sql', 'r') as fid:
        ptsd_table = pd.read_sql_query(fid.read(), eng)

    # separate years
    p14 = ptsd_table.query('year == 2014').reset_index(drop=True)
    p15 = ptsd_table.query('year == 2015').reset_index(drop=True)

    col_add = ['total_served', 'total_ptsd']
    if year == '2014':
        ptsd_table = p14
    elif year == '2015':
        ptsd_table = p15
    elif year == '2015+2014':
        ptsd_table = p15
        ptsd_table[col_add] += p14[col_add]

    # get the state boundaries
    state_table = pd.DataFrame(us_states.data).T

    # merge tables
    ptsd_table = pd.merge(
        state_table, ptsd_table, how='inner',
        left_index=True, right_on='state')
    ptsd_table['ptsd_rate'] = (
        100 * ptsd_table.total_ptsd / ptsd_table.total_served)

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
    cmap = LinearColorMapper(palette=palette)

    # create figure
    us_map = figure(
        width=1200, x_axis_location=None, y_axis_location=None,
        tools="hover", title="Rates of Post Traumatic Stress (2015)")
    us_map.grid.grid_line_color = None
    us_map.patches(
        'lons', 'lats', source=src, line_color='black',
        fill_color={'field': metric, 'transform': cmap})
    us_map.x_range = Range1d(-130, -60)
    us_map.y_range = Range1d(20, 55)

    # program hover tool
    hover = us_map.select_one(HoverTool)
    hover.tooltips = [
        ("State", "@name"),
        ("Total Veterans Enrolled", "@total_served"),
        ("Total PTSD", "@total_ptsd (@ptsd_rate{int}%)")
    ]

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    script, div = components(us_map)
    html = flask.render_template(
        'embed.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
        metric=metric,
        year=year
    )
    return encode_utf8(html)


if __name__ == "__main__":
    app.run(debug=True)
