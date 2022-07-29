'''
This module downloads the daily time series of U.S. effective federal funds
rate and targets from the St. Louis Federal Reserve's FRED system
(https://fred.stlouisfed.org/) or loads it from this directory. It the creates
a time series plot of all the fed funds rate series using the Bokeh plotting
library.

This module defines the following function(s):
    get_fedfunds_data()
    ffrate_plot()
'''
# Import packages
import numpy as np
import pandas as pd
import pandas_datareader as pddr
import datetime as dt
import os
from bokeh.io import output_file
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, Title, Legend, HoverTool
from bokeh.models import DatetimeTickFormatter

'''
Define functions
'''


def get_fedfunds_data(beg_date="earliest", end_date="most_recent",
                      download_from_internet=True):
    '''
    This function either downloads or reads in the daily frequency U.S.
    effective federal funds rate and target data series.

    Args:
        beg_date (str): either "earliest" or "yyyy-mm-dd" format date
        end_date (str): either "most_recent" or "yyyy-mm-dd" format date
        download_from_internet (bool): =True if download data from
            fred.stlouisfed.org, otherwise read data in from local directory

    Other functions and files called by this function:
        ffrates_[yyyy-mm-dd].csv

    Files created by this function:
        ffrates_[yyyy-mm-dd].csv

    Returns:
        ffrates_df (DataFrame): N x 5 DataFrame of date, ffr_effective,
            ffr_targ, ffr_targ_min, ffr_targ_max
        end_date_str2 (str): actual end date of fed funds rate time series in
            'yyyy-mm-dd' format. Can differ from the end_date input to this
            function if the final data for that day have not come out yet
            (usually 2 hours after markets close, 6:30pm EST), or if the
            end_date is one on which markets are closed (e.g. weekends and
            holidays). In this latter case, the pandas_datareader library
            chooses the most recent date for which we have fed funds rate data.
    '''
    if beg_date == "earliest":
        beg_date = dt.datetime.strptime("1954-07-01", '%Y-%m-%d')
    else:
        beg_date = np.maximum(dt.datetime.strptime("1954-07-01", '%Y-%m-%d'),
                              dt.datetime.strptime(beg_date, '%Y-%m-%d'))
    if end_date == "most_recent":
        end_date = dt.datetime.today()
    else:
        end_date = np.minimum(dt.datetime.today(),
                              dt.datetime.strptime(end_date, '%Y-%m-%d'))
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Name the current directory and make sure it has a data folder
    cur_path = os.path.split(os.path.abspath(__file__))[0]
    data_fldr = 'data'
    data_dir = os.path.join(cur_path, data_fldr)
    if not os.access(data_dir, os.F_OK):
        os.makedirs(data_dir)

    filename_str = ('data/ffrates_' + end_date_str + '.csv')

    if download_from_internet:
        # Download the federal funds rates data directly from
        # fred.stlouisfed.org (requires internet connection)
        ffrates_df = pddr.fred.FredReader(
            symbols=['DFF', 'DFEDTAR', 'DFEDTARL', 'DFEDTARU'],
            start=beg_date, end=end_date).read()
        ffrates_df = pd.DataFrame(ffrates_df).sort_index()  # Sort old to new
        ffrates_df = ffrates_df.reset_index(level=['DATE'])
        ffrates_df = ffrates_df.rename(columns={'DATE': 'Date',
                                                'DFF': 'ffr_effective',
                                                'DFEDTAR': 'ffr_targ',
                                                'DFEDTARL': 'ffr_targ_low',
                                                'DFEDTARU': 'ffr_targ_high'})
        end_date_str2 = ffrates_df['Date'].iloc[-1].strftime('%Y-%m-%d')
        end_date = dt.datetime.strptime(end_date_str2, '%Y-%m-%d')
        filename_str = ('data/ffrates_' + end_date_str2 + '.csv')
        ffrates_df.to_csv(filename_str, index=False)
    else:
        # Import the data as pandas DataFrame
        end_date_str2 = end_date_str
        data_file_path = os.path.join(cur_path, filename_str)
        ffrates_df = pd.read_csv(
            data_file_path,
            names=['Date', 'ffr_effective', 'ffr_targ', 'ffr_targ_low',
                   'ffr_targ_high'],
            parse_dates=['Date'], skiprows=1,
            na_values=['.', 'na', 'NaN']
        )
        # usempl_df = usempl_df.dropna()

    print('End date of U.S. federal funds rate series is',
          end_date.strftime('%Y-%m-%d'))

    return ffrates_df, end_date_str2


def ffrate_plot(beg_date="earliest", end_date="most_recent",
                recession_bars=True, download_from_internet=True,
                html_show=True):
    '''
    This function creates the HTML and JavaScript code for the dynamic
    visualization of the time series of the U.S. federal funds effective rate
    and targets.

    Args:
        beg_date (str): either "earliest" or "yyyy-mm-dd" format date
        end_date (str): either "most_recent" or "yyyy-mm-dd" format date
        recession_bars (bool): whether to plot recession bars
        download_from_internet (bool): =True if download data from
            fred.stlouisfed.org, otherwise read data in from local directory
        html_show (bool): =True if open dynamic visualization in browser once
            created

    Other functions and files called by this function:
        get_fedfunds_data()

    Files created by this function:
       images/ffrate_[yyyy-mm-dd].html

    Returns: fig, end_date_str
    '''
    if beg_date == "earliest":
        beg_date = dt.datetime.strptime("1954-07-01", '%Y-%m-%d')
    else:
        beg_date = np.maximum(dt.datetime.strptime("1954-07-01", '%Y-%m-%d'),
                              dt.datetime.strptime(beg_date, '%Y-%m-%d'))
    if end_date == "most_recent":
        end_date = dt.datetime.today()
    else:
        end_date = np.minimum(dt.datetime.today(),
                              dt.datetime.strptime(end_date, '%Y-%m-%d'))
    beg_date_str = beg_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Create directory if images directory does not already exist
    cur_path = os.path.split(os.path.abspath(__file__))[0]
    image_fldr = 'images'
    image_dir = os.path.join(cur_path, image_fldr)
    if not os.access(image_dir, os.F_OK):
        os.makedirs(image_dir)
    data_dir = os.path.join(cur_path, 'data')
    recession_data_path = os.path.join(data_dir, 'recession_data.csv')

    ffrates_df, end_date_str2 = get_fedfunds_data(
        beg_date=beg_date_str, end_date=end_date_str,
        download_from_internet=download_from_internet
    )

    # Create recession data column data source object
    recession_df = pd.read_csv(recession_data_path,
                               parse_dates=['Peak','Trough'])

    ffrates_cds = ColumnDataSource(ffrates_df)
    if end_date_str2 != end_date_str:
        print('Fed funds rate data downloaded on ' + end_date_str + ' has ' +
              'most recent fed funds rate data month of ' + end_date_str2 +
              '.')
    end_date2 = dt.datetime.strptime(end_date_str2, '%Y-%m-%d')

    # Create Bokeh plot of federal funds effective rate and targets
    fig_title = 'U.S. federal funds effective rate and target (daily)'
    filename = ('images/ffrate_' + end_date_str2 + '.html')
    output_file(filename, title=fig_title)

    # Format the tooltip
    tooltips = [('Date', '@Date{%Y-%m-%d}'),
                ('Effective rate', '@ffr_effective{0.00}%'),
                ('Target rate', '@ffr_targ{0.00}%'),
                ('Target min', '@ffr_targ_low{0.00}%'),
                ('Target max', '@ffr_targ_high{0.00}%')]

    # Solve for minimum and maximum PAYEMS/Peak values in monthly main display
    # window in order to set the appropriate xrange and yrange
    min_rate = ffrates_df[[
            'ffr_effective', 'ffr_targ', 'ffr_targ_low', 'ffr_targ_high'
        ]].min().to_numpy().min()
    max_rate = ffrates_df[[
            'ffr_effective', 'ffr_targ', 'ffr_targ_low', 'ffr_targ_high'
        ]].max().to_numpy().max()

    datarange_rates = max_rate - min_rate
    # datarange_dates = int(end_date2 - beg_date)
    fig_rate_buffer_pct = 0.10
    fig_date_buffer_pct = 0.05
    fig = figure(plot_height=500,
                 plot_width=1000,
                 x_axis_label='Date',
                 y_axis_label='federal funds rate',
                 y_range=(min_rate - fig_rate_buffer_pct * datarange_rates,
                          max_rate + fig_rate_buffer_pct * datarange_rates),
                 # x_range=((beg_date - fig_date_buffer_pct * datarange_dates),
                 #          (end_date + fig_date_buffer_pct * datarange_dates)),
                 tools=['save', 'zoom_in', 'zoom_out', 'box_zoom',
                        'pan', 'undo', 'redo', 'reset', 'hover', 'help'],
                 toolbar_location='left')
    fig.title.text_font_size = '18pt'
    fig.toolbar.logo = None
    # Format dates for axis representation and rotate pi/4
    fig.xaxis.formatter=DatetimeTickFormatter(
        days=['%Y-%m-%d'],
        months=['%Y-%m-%d'],
        years=['%Y-%m-%d']
    )
    fig.xaxis.major_label_orientation = np.pi / 4

    ffr_effective = fig.line(
        x='Date', y='ffr_effective', source=ffrates_cds, color='black',
        line_width=2, alpha=0.7, muted_alpha=0.15
    )
    ffr_targ = fig.line(
        x='Date', y='ffr_targ', source=ffrates_cds, color='red', line_width=2,
        alpha=0.7, muted_alpha=0.15
    )
    ffr_range = fig.varea(
        x='Date', y1='ffr_targ_low', y2='ffr_targ_high', source=ffrates_cds,
        color='red', alpha=0.3, muted_alpha=0.15
    )

    if recession_bars:
        # Create recession bars
        recession_data_length = len(recession_df['Peak'])
        for x in range(recession_data_length):
            peak_day = recession_df['Peak'][x]
            trough_day = recession_df['Trough'][x]
            # Recession that started before begin date but end after begin date
            if (peak_day < beg_date and trough_day >= beg_date and
                trough_day <= end_date):
                rec_bar = fig.patch(
                    x=[beg_date, trough_day, trough_day, beg_date],
                    y=[-100, -100, 2 * max_rate, 2 * max_rate],
                    fill_color='gray',
                    fill_alpha=0.3,
                    line_width=0
                )

            # Recesssions completely within begin date and end date
            elif (peak_day >= beg_date and trough_day <= end_date):
                rec_bar = fig.patch(
                    x=[peak_day, trough_day, trough_day, peak_day],
                    y=[-100, -100, 2 * max_rate, 2 * max_rate],
                    fill_color='gray',
                    fill_alpha=0.3,
                    line_width=0
                )

            # Recession that started after begin date but end after end date
            elif (peak_day >= beg_date and peak_day <= end_date and
                trough_day > end_date):
                rec_bar = fig.patch(
                    x=[peak_day, end_date, end_date, peak_day],
                    y=[-100, -100, 2 * max_rate, 2 * max_rate],
                    fill_color='gray',
                    fill_alpha=0.3,
                    line_width=0
                )

        # Add legend
        legend = Legend(items=[("effective rate", [ffr_effective]),
                            ("target rate", [ffr_targ]),
                            ("target range", [ffr_range]),
                            ("Recession", [rec_bar])],
                        location="center")

    else:
        # Add legend
        legend = Legend(items=[("effective rate", [ffr_effective]),
                            ("target rate", [ffr_targ]),
                            ("target range", [ffr_range])],
                        location="center")

    fig.add_layout(legend, 'right')

    # Add title and subtitle to the plot
    fig_title2 = 'U.S. federal funds effective rate and target rate'
    fig.add_layout(Title(text=fig_title2, text_font_style='bold',
                         text_font_size='16pt', align='center'), 'above')

    # Add source text below figure
    updated_date_str = end_date.strftime('%B %-d, %Y')
    fig.add_layout(Title(text='Source: Richard W. Evans (@RickEcon), ' +
                              'historical federal funds rate data from ' +
                              'FRED, updated ' + updated_date_str + '.',
                         align='left',
                         text_font_size='3mm',
                         text_font_style='italic'),
                   'below')
    fig.legend.click_policy = 'mute'

    # Add the HoverTool to the figure
    fig.add_tools(HoverTool(tooltips=tooltips, toggleable=False,
                            formatters={'@Date': 'datetime'}))

    if html_show:
        show(fig)

    return fig, end_date_str


if __name__ == '__main__':
    # execute only if run as a script
    fig, end_date_str = ffrate_plot()
