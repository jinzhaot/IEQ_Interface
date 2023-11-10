import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, Point
import matplotlib as mpl
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os, time

os.environ["TZ"] = "UTC"
time.tzset()
st.set_page_config(layout='wide')

@st.cache_data
def read_shpe(select_parm):
    # Read the Temperature and Humidity Data
    if select_parm == 'Temperature' or 'RH':
        temp = pd.read_csv(select_parm + '.csv', parse_dates=['Time Point'])

        s = gpd.read_file('shp-line.shp')
        geo_list = [Polygon(x.coords) for x in reversed(s['geometry'])]
        geo_list.append(Point((53.5, 42.5)))
        geo_dict = {
            'Sensor': ['hollow1', 'hollow2', 'outline', 'VC21411021', 'VC21410706', 'VC21411024',
                       'VC21410705', 'VC21410733', 'DC21410602', 'KC20710690', 'VC21410989',
                       'VC21410650', 'VC21410682', 'KC20710673', 'VC21410995', 'VC21410701',
                       'VC21411018', 'VC21411016', 'VC21410591', 'VC21410979', 'VC21410889',
                       'VC21410644', 'VC21410651', 'VC21410972', 'VC21410978', 'VC21410570',
                       'VC21410975', 'VC21410977', 'outdoor'],

            'geometry': geo_list
        }
        geo = pd.DataFrame.from_dict(geo_dict)
        temp_geo = pd.merge(temp, geo, on="Sensor", how='left')
        gdf = gpd.GeoDataFrame(temp_geo, geometry='geometry')
        bound = gpd.GeoSeries(Polygon(s['geometry'][25].coords))
        hollow = gpd.GeoSeries([Polygon(s['geometry'][26].coords), Polygon(s['geometry'][27].coords)])

        del s
        del temp_geo
        del geo
        return gdf, bound, hollow

    # Read the other Data
    else:
        tvoc = pd.read_csv(select_parm + '.csv', parse_dates=['Time Point'])
        s = gpd.read_file('shp-line.shp')
        geo_list = [Polygon(x.coords) for x in reversed(s['geometry'])]
        geo_dict = {
            'Sensor': ['hollow1', 'hollow2', 'outline', 'VC21411021', 'VC21410706', 'VC21411024',
                       'VC21410705', 'VC21410733', 'DC21410602', 'KC20710690', 'VC21410989',
                       'VC21410650', 'VC21410682', 'KC20710673', 'VC21410995', 'VC21410701',
                       'VC21411018', 'VC21411016', 'VC21410591', 'VC21410979', 'VC21410889',
                       'VC21410644', 'VC21410651', 'VC21410972', 'VC21410978', 'VC21410570',
                       'VC21410975', 'VC21410977'],

            'geometry': geo_list
        }
        geo = pd.DataFrame.from_dict(geo_dict)
        tvoc_geo = pd.merge(tvoc, geo, on="Sensor", how='left')
        gdf = gpd.GeoDataFrame(tvoc_geo, geometry='geometry')
        bound = gpd.GeoSeries(Polygon(s['geometry'][25].coords))
        hollow = gpd.GeoSeries([Polygon(s['geometry'][26].coords), Polygon(s['geometry'][27].coords)])
        del s
        del tvoc
        del geo
        return gdf, bound, hollow


# @st.cache(suppress_st_warning=True, allow_output_mutation=True)
@st.cache_data
def read_cm(select_parm):

    # Create the Colormap for Temperature
    if select_parm == 'Temperature':
        colorArr = [mpl.cm.coolwarm.__call__(i) for i in range(0, 300, 20)]
        cmap = mpl.colors.ListedColormap(colorArr)
        bounds = [i for i in range(16, 31, 1)]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
        return cmap, norm

    # Create the Colormap for RH
    if select_parm == 'RH':
        colorArr = ['#DC3939', '#F96468', '#FCB1B2', '#FCB1B2', '#C1E9FF', '#C1E9FF', '#BAD5FE', '#9CB2FE', '#7F90FD',
                    '#616DFD', '#444AFC']
        cmap = mpl.colors.ListedColormap(colorArr)
        bounds = [i for i in range(0, 110, 10)]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
        return cmap, norm

    # Create the Colormap for CO2
    if select_parm == 'CO2':
        colorArr = [mpl.cm.coolwarm.__call__(i) for i in range(30, 300, 10)]
        cmap = mpl.colors.ListedColormap(colorArr)
        bounds = [i for i in range(400, 1500, 100)]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
        return cmap, norm

    # Create the Colormap for PM25
    if select_parm == 'PM25':
        cmap = mpl.cm.coolwarm
        bounds = [i for i in range(15, 50, 5)]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
        return cmap, norm

    # Create the Colormap for PM10
    if select_parm == 'PM10':
        cmap = mpl.cm.coolwarm
        bounds = [i for i in range(50, 300, 50)]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
        return cmap, norm

    # Create the Colormap for TVOC
    if select_parm == 'TVOC':
        colorArr = [mpl.cm.coolwarm.__call__(i) for i in range(60, 300, 24)]
        cmap = mpl.colors.ListedColormap(colorArr)
        bounds = [i for i in range(100, 400, 30)]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
        return cmap, norm



params = ["Temperature (C)", "RH (%)", "CO2 (ppm)", "TVOC (ppb)", "PM10 (µg/m3)", "PM2.5 (µg/m3)"]

# plot boundary for closed offices
closedSpaces = ['VC21411024', 'VC21410682', 'VC21410644', 'VC21410972',
                'VC21410978',
                'VC21410733', 'VC21410989', 'VC21410701',
                'VC21410651']

if "select_parm" not in st.session_state:
    st.session_state.select_parm, st.session_state.unit = params[0].split(" ")

select_parm, unit = st.session_state.select_parm, st.session_state.unit
st.sidebar.title("Parameters:")
for p in params:
    if st.sidebar.button(p):
        select_parm, unit = p.split(" ")
        if p == "PM2.5 (µg/m3)":
            select_parm = 'PM25'
        st.session_state.select_parm, st.session_state.unit = select_parm, unit


st.sidebar.title("Animations:")
animations = ['RH', 'RH_occupied', 'RH_unoccupied', 'Temperature', 'Temperature_occupied', 'Temperature_unoccupied', 'CO2']

rh = st.sidebar.button('RH')
rh_occ = st.sidebar.button('RH occupied')
rh_unocc = st.sidebar.button('RH unoccupied')
temp = st.sidebar.button('Temperature')
temp_occ = st.sidebar.button('Temperature occupied')
temp_unocc = st.sidebar.button('Temperature unoccupied')
co2 = st.sidebar.button('CO2')
co2_occ = st.sidebar.button('CO2 occupied')
co2_unocc = st.sidebar.button('CO2 unoccupied')

if rh:
    with st.container():
        video_file = open('animations/RH.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
        chart_placeholder = st.empty()
        slider_placeholder = st.empty()

elif rh_occ:
    with st.container():
        video_file = open('animations/RH_occupied.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
        chart_placeholder = st.empty()
        slider_placeholder = st.empty()

elif rh_unocc:
    with st.container():
        video_file = open('animations/RH_unoccupied.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
        chart_placeholder = st.empty()
        slider_placeholder = st.empty()


elif temp:
    with st.container():
        video_file = open('animations/Temperature.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
        chart_placeholder = st.empty()
        slider_placeholder = st.empty()


elif temp_occ:
    with st.container():
        video_file = open('animations/Temperature_occupied.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
        chart_placeholder = st.empty()
        slider_placeholder = st.empty()

elif temp_unocc:
    with st.container():
        video_file = open('animations/Temperature_unoccupied.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
        chart_placeholder = st.empty()
        slider_placeholder = st.empty()

elif co2:
    with st.container():
        video_file = open('animations/CO2.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
        chart_placeholder = st.empty()
        slider_placeholder = st.empty()

elif co2_occ:
    with st.container():
        video_file = open('animations/CO2_occupied.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
        chart_placeholder = st.empty()
        slider_placeholder = st.empty()

elif co2_unocc:
    with st.container():
        video_file = open('animations/CO2_unoccupied.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
        chart_placeholder = st.empty()
        slider_placeholder = st.empty()

else:
    with st.container():
        if select_parm == "PM25":
            st.title("PM2.5" + " " + unit)
        else:
            st.title(select_parm + " " + unit)

        if 'appStarted' not in st.session_state:
            st.session_state.appStarted = True
            chart_placeholder = st.empty()
            slider_placeholder = st.empty()
        else:
            chart_placeholder = st.session_state.chart_placeholder
            slider_placeholder = st.session_state.slider_placeholder





    gdf, bound, hollow = read_shpe(select_parm)

    cmap, norm = read_cm(select_parm)


    t = slider_placeholder.slider(
        label='Time',
        min_value=datetime(2022, 1, 1, 5, 0),
        max_value=datetime(2022, 5, 2, 12, 0),
        step=timedelta(hours=1),
        format="YYYY/M/D - H:mm")

    mask = (gdf['Time Point'] == t)

    if t.hour < 6 or t.hour > 18:
        bg_color = '#D1D1D1'
    else:
        bg_color = 'white'

    fig, ax = plt.subplots(figsize=(16, 9), facecolor=bg_color)

    bound.plot(ax=ax, color='white', edgecolor="black", linewidth=1.5)
    data = gdf[mask]


    # Plot the Temperature
    if select_parm in ['Temperature', 'RH']:
        if select_parm == 'Temperature':
            legend_bound = (18, 24)
            paramUnit = 'C'
        if select_parm == 'RH':
            legend_bound = (20, 70)
            paramUnit = '%'


        # plot regions
        data.plot('value', cmap=cmap, norm=norm, ax=ax, markersize=1000)
        data[data.Sensor.isin(closedSpaces)].geometry.boundary.plot(ax=ax, color='black', linewidth=1)
        hollow.plot(ax=ax, color=bg_color, edgecolor="black", linewidth=1.5)

        # plot sensors
        ax.scatter(x=[45.25562564, 45.87822688, 47.58810628, 47.58810628, 48.72626014,
                       48.93883318, 50.33400285, 51.54711857, 51.73944658, 52.64372536,
                       54.46744857, 53.33035165, 54.4407126 , 53.42508597, 52.3609246 ,
                       51.8413017 , 52.21920929, 50.12105118, 48.65854635, 47.99720815,
                       46.88035633, 45.75461772, 45.86259135, 53.48374047, 54.35374989],
                   y=[42.76445303, 42.11688836, 42.11613632, 43.19213747, 42.76034206,
                       42.11609056, 42.12610571, 43.06377877, 42.09908809, 42.48361516,
                       44.75605302, 45.0461348 , 46.78218787, 46.88675225, 47.21058944,
                       46.29649442, 45.79391079, 44.27298384, 43.82742594, 44.38397824,
                       43.70599634, 44.12428293, 44.51218304, 43.69329852, 43.01358077],
                   c='orange', edgecolors='red', linewidths=0.5, s=40)

        ax.set_facecolor(bg_color)

        ax.set_axis_off()
        ax.add_artist(ax.patch)
        ax.patch.set_zorder(-1)

        ax.annotate(str(round(data[data['Sensor'] == 'outdoor']['value'].values[0], 1)) + paramUnit, (53.5-0.15, 42.5), color='white', weight='bold', fontsize=8)
        ax.annotate('outdoor', (53.5 - 0.3, 42.5 - 0.4), color='black', fontsize=13, weight='bold')

        temp_mask = ((data[data['Sensor'] != 'outdoor']['value'] <= legend_bound[0]) | (data[data['Sensor'] != 'outdoor']['value'] >= legend_bound[1]))

        if temp_mask.sum() != 0:
            coord = data[data['Sensor'] != 'outdoor'][temp_mask]['geometry'].to_list()
            coord_temp = data[data['Sensor'] != 'outdoor'][temp_mask]['value'].to_list()
            for i in range(len(coord)):
                x, y = coord[i].centroid.x, coord[i].centroid.y
                ax.annotate(str(round(coord_temp[i], 1)) + paramUnit, (x-0.15, y), color='white', weight='bold')


        # edit the colorbar
        cbar = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        cax = plt.axes([0.88, 0.1, 0.03, 0.8])  # [xcoord, ycoord, width, long]
        cbar = fig.colorbar(cbar, cax=cax)


        if select_parm == 'RH':
            cbar.set_ticks([i for i in range(0, 110, 10)])
            cbar.ax.set_yticklabels(['0',
                                     '10%',
                                     r"$\bf{20}$%" + ' ' + r"$\bf{Acceptable}$",
                                     '30%',
                                     r"$\bf{40}$%" + ' ' + r"$\bf{High}$" + ' ' + r"$\bf{Perf}$",
                                     '50%',
                                     r"$\bf{60}$%" + ' ' + r"$\bf{High}$" + ' ' + r"$\bf{Perf}$",
                                     r"$\bf{70}$%" + ' ' + r"$\bf{Acceptable}$",
                                     '80%',
                                     '90%',
                                     '100%'])
        elif select_parm == 'Temperature':
            cbar.set_ticks([i for i in range(16, 30, 2)])
            cbar.ax.set_yticklabels(['16C(60.8F)',
                                     r"$\bf{" + '18C(64.4F) lower bound' + "}$",
                                     '20C(68.0F)',
                                     '22C(71.6F)',
                                     r"$\bf{" + '24C(75.2F) upper bound' + "}$",
                                     '26C(78.8F)',
                                     '28C(82.4F)',
                                     '30C(86.0F)'])



    # Plot the others
    else:
        data.plot('value', cmap=cmap, norm=norm, ax=ax, markersize=1000)
        data[data.Sensor.isin(closedSpaces)].geometry.boundary.plot(ax=ax, color='black', linewidth=1)
        hollow.plot(ax=ax, color=bg_color, edgecolor="black", linewidth=1.5)

        # plot sensors
        ax.scatter(x=[45.25562564, 45.87822688, 47.58810628, 47.58810628, 48.72626014,
                      48.93883318, 50.33400285, 51.54711857, 51.73944658, 52.64372536,
                      54.46744857, 53.33035165, 54.4407126, 53.42508597, 52.3609246,
                      51.8413017, 52.21920929, 50.12105118, 48.65854635, 47.99720815,
                      46.88035633, 45.75461772, 45.86259135, 53.48374047, 54.35374989],
                   y=[42.76445303, 42.11688836, 42.11613632, 43.19213747, 42.76034206,
                      42.11609056, 42.12610571, 43.06377877, 42.09908809, 42.48361516,
                      44.75605302, 45.0461348, 46.78218787, 46.88675225, 47.21058944,
                      46.29649442, 45.79391079, 44.27298384, 43.82742594, 44.38397824,
                      43.70599634, 44.12428293, 44.51218304, 43.69329852, 43.01358077],
                   c='orange', edgecolors='red', linewidths=0.5, s=40)


        ax.set_facecolor(bg_color)

        ax.set_axis_off()
        ax.add_artist(ax.patch)
        ax.patch.set_zorder(-1)
        if select_parm == 'TVOC':
            mask = (data['value'] >= 220)
        if select_parm == 'CO2':
            mask = (data['value'] >= 1000)
        if select_parm == 'PM25':
            mask = (data['value'] >= 35)
        if select_parm == 'PM10':
            mask = (data['value'] >= 150)
        if mask.sum() != 0:
            coord = data[mask]['geometry'].to_list()
            coord_tvoc = data[mask]['value'].to_list()
            for i in range(len(coord)):
                x, y = coord[i].centroid.x, coord[i].centroid.y
                ax.annotate(str(round(coord_tvoc[i], 1)), (x - 0.15, y), color='white')

        # edit the colorbar
        cbar = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        cax = plt.axes([0.88, 0.1, 0.03, 0.8])  # [xcoord, ycoord, width, long]
        cbar = fig.colorbar(cbar, cax=cax)

        if select_parm == "TVOC":
            cbar.set_ticks([100, 130, 160, 176, 190, 220, 250, 280, 310, 340, 370])
            cbar.ax.set_yticklabels(['<100ppb',
                                     '130ppb',
                                     '160ppb',
                                     r"$\bf{176ppb}$" + ' ' + r"$\bf{High}$" + ' ' + r"$\bf{Perf}$",
                                     '190ppb',
                                     r"$\bf{220ppb}$" + ' ' + r"$\bf{Acceptable}$",
                                     '250ppb',
                                     '280ppb',
                                     '310ppb',
                                     '340ppb',
                                     '>370ppb'])

        elif select_parm == "CO2":
            cbar.set_ticks([400, 600, 800 ,1000, 1200, 1400])
            cbar.ax.set_yticklabels(['400ppm',
                                     r"$\bf{600ppm}$" + ' ' + r"$\bf{High}$" + ' ' + r"$\bf{Perf}$",
                                     '800ppm',
                                     r"$\bf{1000ppm}$" + ' ' + r"$\bf{Acceptable}$",
                                     '1200ppm',
                                     '>1400ppm'])

        elif select_parm == 'PM10':
            cbar.set_ticks([50, 100, 150, 200, 250])
            cbar.ax.set_yticklabels(['50µg/m3',
                                     '100µg/m3',
                                     '150µg/m3',
                                     '200µg/m3',
                                     '250µg/m3'])

        elif select_parm == 'PM25':
            cbar.set_ticks([15, 20, 25, 30, 35, 40, 45])
            cbar.ax.set_yticklabels(['15µg/m3',
                                     '20µg/m3',
                                     '25µg/m3',
                                     '30µg/m3',
                                     '35µg/m3',
                                     '40µg/m3',
                                     '45µg/m3'])


    chart_placeholder.pyplot(fig, clear_figure=True)

    # caching
    st.session_state.chart_placeholder = chart_placeholder
    st.session_state.slider_placeholder = slider_placeholder
