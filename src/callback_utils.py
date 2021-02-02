""" Dash Callback Collection

Callbacks that are triggered at 60 second (with the exception of the 1s for the countdown) for refreshing the
plots of the dashboard with newly written data from the Redis database

"""
import dash
import frontend_utils
import dash_html_components as html
from dash.dependencies import Input, Output, State


def init_callbacks(app, elements):
    """
    a way to bring required elements, aside from the app, into this separate doc for performing the updates

    :param app:
    :param elements:
    :return:
    """
    spinner = elements['spinner']
    ts = elements['timestamp']
    slider_config = elements['slider-config']
    n = elements['n']
    slider = elements['slider']
    scatter = elements['scatter']
    db = elements['db']
    stations = elements['station']
    speedbar = elements['speedbar']
    countbar = elements['countbar']
    gapbar = elements['gapbar']
    table = elements['table']
    countdown_duration = elements['countdown-duration']
    cam_ids = elements['cam-ids']
    cam_link = elements['cam-link']
    streets = elements['streets']

    @app.callback(Output("pie-graph", "figure"),
                  Input("second-interval", "n_intervals"))
    def update_countdown(n):
        """
        animates the countdown spinner
        :param n:
        :return:
        """
        time_elapsed = n % countdown_duration
        time_remaining = countdown_duration - time_elapsed
        spinner.increment(time_elapsed, time_remaining)
        return spinner.fig


    @app.callback(
        [Output('speed-live-graph', "figure"),
         Output('count-live-graph', "figure"),
         Output("gap-live-graph", "figure"),
         Output("table-div", "children")
         ],
        Input("minute-interval", "n_intervals")
    )
    def update_barplots_and_table(_):
        new_speed_values = db.latest_readings("vehicle-speed")
        new_count_values = db.latest_readings("vehicle-count")
        new_gap_values = db.latest_readings("vehicle-gap-time")

        speedbar.set_data(new_speed_values, stations, "kmh")
        countbar.set_data(new_count_values, stations, "cars")
        gapbar.set_data(new_gap_values, stations, "s")

        table.df["speed (kmh)"] = new_speed_values
        table.df["count (cars)"] = new_count_values
        table.df["gap time (s)"] = new_gap_values

        table.refresh()

        return speedbar.fig, countbar.fig, gapbar.fig, table.table

    @app.callback(
        Output("timestamp-text", "children"),
        Input("minute-interval", "n_intervals")
    )
    def update_timestamp(_):
        new_timestamp = db.latest_readings("time")[0]
        ts.update_time(new_timestamp)
        return ts.stamp

    @app.callback(
        Output("hist-plot", "figure"),
        [Input("minute-interval", "n_intervals"),
         Input("drop-0","value"),
         Input("drop-1","value"),
         Input("drop-2","value"),
         Input("cust-slider","value")
         ]
    )
    def update_scatter(n_intervals,datatype_selection, station_a, station_b,slider_values):
        """
        main update logic for all the plots. Triggered either by the 60second interval, or a selection of different
        detectors and/or reading_type in the historic scatter plot
        :param slider_values:
        :param _:
        :param selection_1:
        :param selection_2:
        :param selection_0:
        :return:
        """
        ctx = dash.callback_context
        trigger = ctx.triggered[0]["prop_id"]

        [idx_left, idx_right] = slider_values

        if datatype_selection == "speed":
            datatype = "vehicle-speed"
            unit = "kmh"
        elif datatype_selection == "count":
            datatype = "vehicle-count"
            unit = "cars"
        else:
            datatype = "vehicle-gap-time"
            unit = "seconds"

        new_times_utc = db.n_latest_readings("time", n)[0]
        new_data = db.n_latest_readings(datatype, n)
        new_hist_dict = {s: l for s, l in zip(stations, new_data)}

        new_primary_values = new_hist_dict[station_a]
        new_secondary_values = new_hist_dict[station_b]

        scatter.set_unit(unit)
        scatter.set_labels(new_times_utc)

        scatter.update_primary_fig(new_primary_values)
        scatter.update_secondary_fig(new_secondary_values)

        scatter.zoom_in(idx_left,idx_right)

        return scatter.base_fig

    @app.callback(
        [Output("left-marker", "style"),
         Output("left-marker", "children"),
         Output("right-marker", "style"),
         Output("right-marker", "children")],
        [Input('cust-slider', 'value'),
         Input("minute-interval","n_intervals")
         ]
    )
    def update_slider(slider_values,_):
        """
        animates the handles and handle values of the slider
        :param slider_values:
        :param n_intervals:
        :return:
        """
        new_times_utc = db.n_latest_readings("time", n)[0]
        slider.set_labels(new_times_utc)

        [idx_left, idx_right] = slider_values
        offset_left = int(100 * (idx_left / n))
        offset_right = int(100 * (idx_right / n))-5

        style_left = {"marginLeft": "{}%".format(offset_left), "marginTop": "0px"}
        style_left.update(slider_config)

        style_right = {"marginLeft": "{}%".format(offset_right), "marginTop": "27px"}
        style_right.update(slider_config)

        text_left = slider.labels[idx_left]
        text_right = slider.labels[idx_right]

        text_left = frontend_utils.date_convert(text_left)
        text_right = frontend_utils.date_convert(text_right)

        text_left = text_left.strftime("%H:%M:%S")
        text_right = text_right.strftime("%H:%M:%S")

        return style_left, text_left, style_right,text_right

    @app.callback(
        [Output("camera-modal", "is_open"),
         Output("modal-body", "children"),
         Output("modal-header", "children"),
         Output("station-camera-dropdown", "value")
         ],
        [Input("open-modal", "n_clicks"),
         Input("close-modal", "n_clicks"),
         Input("prev-camera", "n_clicks"),
         Input("next-camera", "n_clicks")],
        [
            State("station-camera-dropdown", "value"),
            State("camera-modal", "is_open")
        ]
    )
    def view_traffic_cam(open_btn, close_btn, go_prev, go_next, selection, is_open):
        """
        callbacks to open a modal element for viewing the traffic cam of the selected detector, and then handles
        the carousel behavior within the modal element
        :param open_btn:
        :param close_btn:
        :param go_prev:
        :param go_next:
        :param selection:
        :param is_open:
        :return:
        """
        ctx = dash.callback_context
        trigger = ctx.triggered[0]["prop_id"]

        if "open" in trigger:
            camera_id = cam_ids[selection]
            url = cam_link.format(camera_id)
            img = html.Img(srcSet=url, style={"maxWidth": "300px"})
            title = selection + ":  Notre-Dame/{}".format(streets[selection])

            return [(not is_open), img, title, selection]

        if "close" in trigger:
            return [False, None, None, selection]

        if "next" in trigger:
            new_selection_num = int(selection.split(" ")[-1]) + 1
            if new_selection_num > 9:
                new_selection_num = 1

            new_selection = "station " + str(new_selection_num)
            camera_id = cam_ids[new_selection]
            url = cam_link.format(camera_id)
            img = html.Img(srcSet=url, style={"maxWidth": "300px"})
            title = new_selection + ":  Notre-Dame/{}".format(streets[new_selection])

            return [True, img, title, new_selection]

        if "prev" in trigger:

            new_selection_num = int(selection.split(" ")[-1]) - 1
            if new_selection_num < 1:
                new_selection_num = 9

            new_selection = "station " + str(new_selection_num)
            camera_id = cam_ids[new_selection]
            url = cam_link.format(camera_id)
            img = html.Img(srcSet=url, style={"maxWidth": "300px"})
            title = new_selection + ":  Notre-Dame/{}".format(streets[new_selection])

            return [True, img, title, new_selection]

        return [False, None, None, selection]
