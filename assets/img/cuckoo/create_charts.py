import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import re

measurements = []

with open('assets/img/cuckoo/sizes_bench.txt.benchstat') as f:
    for line in f: 
        match = re.search(r'Filters/size=(\d+)/([A-z]+)/([A-z]+)-4\s+(\d+\.?\d*)(.s)', line)
        if match != None:
            measurements.append(match.groups())

df = pd.DataFrame(data=measurements, columns=['size', 'method', 'filter', 'time', 'unit'])
# Reduce the amount of data, only keeping interesting rows.
df = df.query('(size == "500") or (size == "5000") or (size == "50000")')

fig = px.bar(df, x="size", y="time", color='filter', barmode='group', 
             facet_row="method",
            #  title='Comparing benchmarks of different filters',
             category_orders={'filter': ['Bloomfilter', 'BBloom', 'VedhavyasCuckoo', 'SeiflotfyCuckoo', 'PanmariCuckoo']})
fig.update_xaxes(type='category')
fig.update_yaxes(title_text='Time', ticksuffix=' ns')
# Get's rid of unnecessary method=Insert 
# See https://community.plotly.com/t/changing-label-of-plotly-express-facet-categories/28066/4
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
fig.for_each_trace(lambda t: t.update(name=t.name.split("=")[1]))

pio.write_html(fig, file='_includes/cuckoo_benchmark_figures.html')
