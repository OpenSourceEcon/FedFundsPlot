'''
This module downloads the U.S. total nonfarm payrolls seasonally adjusted
(PAYEMS) monthly time series from the St. Louis Federal Reserve's FRED system
(https://fred.stlouisfed.org/series/PAYEMS) or loads it from this directory and
organizes it into 15 series, one for each of the last 15 recessions--from the
current 2020 Coronavirus recession to the Great Depression of 1929. It then
creates a normalized peak plot of the PAYEMS data for each of the last 15
recessions using the Bokeh plotting library.

This module defines the following function(s):
    get_usempl_data()
    usempl_npp()
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
# from bokeh.models import Label
from bokeh.palettes import Category20

'''
Define functions
'''


def get_usempl_data(frwd_mths_max, bkwd_mths_max, end_date_str,
                    download_from_internet=True):
    '''
    This function either downloads or reads in the U.S. total nonfarm payrolls
    seasonally adjusted monthly data series (PAYEMS) and adds variables
    mths_frm_peak and empl_dv_pk for each of the last 15 recessions.

    Args:
        frwd_mths_max (int): maximum number of months forward from the peak
            month to plot
        bckwd_mths_max (int): maximum number of months backward from the peak
            month to plot
        end_date_str (str): end date of PAYEMS time series in 'YYYY-mm-dd'
            format
        download_from_internet (bool): =True if download data from
            fred.stlouisfed.org, otherwise read data in from local directory

    Other functions and files called by this function:
        usempl_[yyyy-mm-dd].csv

    Files created by this function:
        usempl_[yyyy-mm-dd].csv
        usempl_pk_[yyyy-mm-dd].csv

    Returns:
        usempl_pk (DataFrame): N x 46 DataFrame of mths_frm_peak, Date{i},
            Close{i}, and close_dv_pk{i} for each of the 15 recessions for the
            periods specified by bkwd_days_max and frwd_days_max
        end_date_str2 (str): actual end date of DJIA time series in
            'YYYY-mm-dd' format. Can differ from the end_date input to this
            function if the final data for that day have not come out yet
            (usually 2 hours after markets close, 6:30pm EST), or if the
            end_date is one on which markets are closed (e.g. weekends and
            holidays). In this latter case, the pandas_datareader library
            chooses the most recent date for which we have DJIA data.
        peak_vals (list): list of peak DJIA value at the beginning of each of
            the last 15 recessions
        peak_dates (list): list of string date (YYYY-mm-dd) of peak DJIA value
            at the beginning of each of the last 15 recessions
        rec_label_yr_lst (list): list of string start year and end year of each
            of the last 15 recessions
        rec_label_yrmth_lst (list): list of string start year and month and end
            year and month of each of the last 15 recessions
        rec_beg_yrmth_lst (list): list of string start year and month of each
            of the last 15 recessions
        maxdate_rng_lst (list): list of tuples with start string date and end
            string date within which range we define the peak DJIA value at the
            beginning of each of the last 15 recessions
    '''
    end_date = dt.datetime.strptime(end_date_str, '%Y-%m-%d')

    # Name the current directory and make sure it has a data folder
    cur_path = os.path.split(os.path.abspath(__file__))[0]
    data_fldr = 'data'
    data_dir = os.path.join(cur_path, data_fldr)
    if not os.access(data_dir, os.F_OK):
        os.makedirs(data_dir)

    filename_basic = ('data/usempl_' + end_date_str + '.csv')
    filename_full = ('data/usempl_pk_' + end_date_str + '.csv')

    if download_from_internet:
        # Download the employment data directly from fred.stlouisfed.org
        # (requires internet connection)
        start_date = dt.datetime(1939, 1, 1)
        usempl_df = pddr.fred.FredReader(symbols='PAYEMS', start=start_date,
                                         end=end_date).read()
        usempl_df = pd.DataFrame(usempl_df).sort_index()  # Sort old to new
        usempl_df = usempl_df.reset_index(level=['DATE'])
        usempl_df = usempl_df.rename(columns={'DATE': 'Date'})
        end_date_str2 = usempl_df['Date'].iloc[-1].strftime('%Y-%m-%d')
        end_date = dt.datetime.strptime(end_date_str2, '%Y-%m-%d')
        filename_basic = ('data/usempl_' + end_date_str2 + '.csv')
        filename_full = ('data/usempl_pk_' + end_date_str2 + '.csv')
        usempl_df.to_csv(filename_basic, index=False)
        # Merge in U.S. annual average nonfarm payroll employment (not
        # seasonally adjusted) 1919-1938. Date values for annual data are set
        # to July 1 of that year. These data are taken from Table 1 on page 1
        # of "Employment, Hours, and Earnings, United States, 1909-90, Volume
        # I," Bulletin of the United States Bureau of Labor Statistics, No.
        # 2370, March 1991.
        # <https://fraser.stlouisfed.org/title/employment-earnings-united-
        # states-189/employment-hours-earnings-united-states-1909-90-5435/
        # content/pdf/emp_bmark_1909_1990_v1>
        filename_annual = ('data/usempl_anual_1919-1938.csv')
        ann_data_file_path = os.path.join(cur_path, filename_annual)
        usempl_ann_df = pd.read_csv(ann_data_file_path,
                                    names=['Date', 'PAYEMS'],
                                    parse_dates=['Date'], skiprows=1,
                                    na_values=['.', 'na', 'NaN'])
        usempl_df = usempl_df.append(usempl_ann_df, ignore_index=True)
        usempl_df = usempl_df.sort_values(by='Date')
        usempl_df = usempl_df.reset_index(drop=True)
        usempl_df.to_csv(filename_basic, index=False)
        # Add other months to annual data 1919-01-01 to 1938-12-01 and fill in
        # artificial employment data by cubic spline interpolation
        months_df = \
            pd.DataFrame(pd.date_range('1919-01-01', '1938-12-01', freq='MS'),
                         columns=['Date'])
        usempl_df = pd.merge(usempl_df, months_df, left_on='Date',
                             right_on='Date', how='outer')
        usempl_df = usempl_df.sort_values(by='Date')
        usempl_df = usempl_df.reset_index(drop=True)
        usempl_df['PAYEMS'].iloc[:242] = \
            usempl_df['PAYEMS'].iloc[:242].interpolate(method='cubic')
    else:
        # Import the data as pandas DataFrame
        end_date_str2 = end_date_str
        data_file_path = os.path.join(cur_path, filename_basic)
        usempl_df = pd.read_csv(data_file_path, names=['Date', 'PAYEMS'],
                                parse_dates=['Date'], skiprows=1,
                                na_values=['.', 'na', 'NaN'])
        usempl_df = usempl_df.dropna()

    print('End date of U.S. employment series is',
          end_date.strftime('%Y-%m-%d'))

    # Set recession-specific parameters
    rec_label_yr_lst = \
        ['1929-1933',  # (Aug 1929 - Mar 1933) Great Depression
         '1937-1938',  # (May 1937 - Jun 1938)
         '1945',       # (Feb 1945 - Oct 1945)
         '1948-1949',  # (Nov 1948 - Oct 1949)
         '1953-1954',  # (Jul 1953 - May 1954)
         '1957-1958',  # (Aug 1957 - Apr 1958)
         '1960-1961',  # (Apr 1960 - Feb 1961)
         '1969-1970',  # (Dec 1969 - Nov 1970)
         '1973-1975',  # (Nov 1973 - Mar 1975)
         '1980',       # (Jan 1980 - Jul 1980)
         '1981-1982',  # (Jul 1981 - Nov 1982)
         '1990-1991',  # (Jul 1990 - Mar 1991)
         '2001',       # (Mar 2001 - Nov 2001)
         '2007-2009',  # (Dec 2007 - Jun 2009) Great Recession
         '2020-2020']  # (Feb 2020 - Apr 2020) Coronavirus recession

    rec_label_yrmth_lst = ['Aug 1929 - Mar 1933',  # Great Depression
                           'May 1937 - Jun 1938',
                           'Feb 1945 - Oct 1945',
                           'Nov 1948 - Oct 1949',
                           'Jul 1953 - May 1954',
                           'Aug 1957 - Apr 1958',
                           'Apr 1960 - Feb 1961',
                           'Dec 1969 - Nov 1970',
                           'Nov 1973 - Mar 1975',
                           'Jan 1980 - Jul 1980',
                           'Jul 1981 - Nov 1982',
                           'Jul 1990 - Mar 1991',
                           'Mar 2001 - Nov 2001',
                           'Dec 2007 - Jun 2009',  # Great Recession
                           'Feb 2020 - Apr 2020']  # Coronavirus recess'n

    rec_beg_yrmth_lst = ['Aug 1929', 'May 1937', 'Feb 1945', 'Nov 1948',
                         'Jul 1953', 'Aug 1957', 'Apr 1960', 'Dec 1969',
                         'Nov 1973', 'Jan 1980', 'Jul 1981', 'Jul 1990',
                         'Mar 2001', 'Dec 2007', 'Feb 2020']

    maxdate_rng_lst = [('1929-7-1', '1929-10-1'),
                       ('1937-7-1', '1937-7-1'),
                       ('1945-1-1', '1945-3-1'),
                       ('1948-9-1', '1949-1-1'),
                       ('1953-6-1', '1953-8-1'),
                       ('1957-7-1', '1957-9-1'),
                       ('1960-3-1', '1960-5-1'),
                       ('1969-11-1', '1970-3-1'),
                       ('1973-10-1', '1974-7-1'),
                       ('1979-12-1', '1980-3-1'),
                       ('1981-6-1', '1981-8-1'),
                       ('1990-6-1', '1991-8-1'),
                       ('2001-2-1', '2001-4-1'),
                       ('2007-11-1', '2008-1-1'),
                       ('2020-1-1', '2020-3-1')]

    # Create normalized peak series for each recession
    usempl_pk = \
        pd.DataFrame(np.arange(-bkwd_mths_max, frwd_mths_max + 1, dtype=int),
                     columns=['mths_frm_peak'])
    usempl_pk_long = usempl_df.copy()
    peak_vals = []
    peak_dates = []
    for i, maxdate_rng in enumerate(maxdate_rng_lst):
        # Identify peak closing value within two months (with only 2
        # exceptions) of the beginning month of the recession
        peak_val = \
            usempl_df['PAYEMS'][(usempl_df['Date'] >= maxdate_rng[0]) &
                                (usempl_df['Date'] <= maxdate_rng[1])].max()
        peak_vals.append(peak_val)
        usempl_dv_pk_name = 'usempl_dv_pk' + str(i)
        usempl_pk_long[usempl_dv_pk_name] = (usempl_pk_long['PAYEMS'] /
                                             peak_val)
        # Identify date of peak PAYEMS value within two months (with
        # only 2 exceptions) of the beginning month of the recession
        peak_date = \
            usempl_df['Date'][(usempl_df['Date'] >= maxdate_rng[0]) &
                              (usempl_df['Date'] <= maxdate_rng[1]) &
                              (usempl_df['PAYEMS'] == peak_val)].max()
        peak_dates.append(peak_date.strftime('%Y-%m-%d'))
        mths_frm_pk_name = 'mths_frm_pk' + str(i)
        usempl_pk_long[mths_frm_pk_name] = \
            ((usempl_pk_long['Date'].dt.year - peak_date.year) * 12 +
             (usempl_pk_long['Date'].dt.month - peak_date.month))
        # usempl_pk_long[mths_frm_pk_name] = (usempl_pk_long['Date'] -
        #                                     peak_date).dt.years
        print('peak_val ' + str(i) + ' is', peak_val, 'on date',
              peak_date.strftime('%Y-%m-%d'), '(Beg. rec. month:',
              rec_beg_yrmth_lst[i], ')')
        # I need to merge the data into this new usempl_pk DataFrame so that
        # mths_frm_peak variable is shared across the dataframe
        usempl_pk = \
            pd.merge(usempl_pk,
                     usempl_pk_long[[mths_frm_pk_name, 'Date', 'PAYEMS',
                                     usempl_dv_pk_name]],
                     left_on='mths_frm_peak', right_on=mths_frm_pk_name,
                     how='left')
        usempl_pk.drop(columns=[mths_frm_pk_name], inplace=True)
        usempl_pk.rename(
            columns={'Date': f'Date{i}', 'PAYEMS': f'PAYEMS{i}'}, inplace=True)

    usempl_pk.to_csv(filename_full, index=False)

    return (usempl_pk, end_date_str2, peak_vals, peak_dates, rec_label_yr_lst,
            rec_label_yrmth_lst, rec_beg_yrmth_lst, maxdate_rng_lst)


def usempl_npp(frwd_mths_main=35, bkwd_mths_main=4, frwd_mths_max=135,
               bkwd_mths_max=48, usempl_end_date='today',
               download_from_internet=True, html_show=True):
    '''
    This function creates the HTML and JavaScript code for the dynamic
    visualization of the normalized peak plot of the last 15 recessions in the
    United States, from the Great Depression (Aug. 1929 - Mar. 1933) to the
    most recent COVID-19 recession (Feb. 2020 - present).

    Args:
        frwd_mths_main (int): number of months forward from the peak to plot in
            the default main window of the visualization
        bkwd_mths_maim (int): number of months backward from the peak to plot
            in the default main window of the visualization
        frwd_mths_max (int): maximum number of months forward from the peak to
            allow for the plot, to be seen by zooming out
        bkwd_mths_max (int): maximum number of months backward from the peak to
            allow for the plot, to be seen by zooming out
        usempl_end_date (str): either 'today' or the end date of PAYEMS time
            series in 'YYYY-mm-dd' format
        download_from_internet (bool): =True if download data from St. Louis
            Federal Reserve's FRED system
            (https://fred.stlouisfed.org/series/PAYEMS), otherwise read data in
            from local directory
        html_show (bool): =True if open dynamic visualization in browser once
            created

    Other functions and files called by this function:
        get_usempl_data()

    Files created by this function:
       images/usempl_[yyyy-mm-dd].html

    Returns: fig, end_date_str
    '''
    # Create directory if images directory does not already exist
    cur_path = os.path.split(os.path.abspath(__file__))[0]
    image_fldr = 'images'
    image_dir = os.path.join(cur_path, image_fldr)
    if not os.access(image_dir, os.F_OK):
        os.makedirs(image_dir)

    if usempl_end_date == 'today':
        end_date = dt.date.today()  # Go through today
    else:
        end_date = dt.datetime.strptime(usempl_end_date, '%Y-%m-%d')

    end_date_str = end_date.strftime('%Y-%m-%d')

    # Set main window and total data limits for monthly plot
    frwd_mths_main = int(frwd_mths_main)
    bkwd_mths_main = int(bkwd_mths_main)
    frwd_mths_max = int(frwd_mths_max)
    bkwd_mths_max = int(bkwd_mths_max)

    (usempl_pk, end_date_str2, peak_vals, peak_dates, rec_label_yr_lst,
        rec_label_yrmth_lst, rec_beg_yrmth_lst, maxdate_rng_lst) = \
        get_usempl_data(frwd_mths_max, bkwd_mths_max, end_date_str,
                        download_from_internet)
    if end_date_str2 != end_date_str:
        print('PAYEMS data downloaded on ' + end_date_str + ' has most ' +
              'recent PAYEMS data month of ' + end_date_str2 + '.')
    end_date2 = dt.datetime.strptime(end_date_str2, '%Y-%m-%d')

    rec_cds_list = []
    min_main_val_lst = []
    max_main_val_lst = []
    for i in range(15):
        usempl_pk_rec = \
            usempl_pk[['mths_frm_peak', f'Date{i}', f'PAYEMS{i}',
                       f'usempl_dv_pk{i}']].dropna()
        usempl_pk_rec.rename(
            columns={f'Date{i}': 'Date', f'PAYEMS{i}': 'PAYEMS',
                     f'usempl_dv_pk{i}': 'usempl_dv_pk'}, inplace=True)
        rec_cds_list.append(ColumnDataSource(usempl_pk_rec))
        # Find minimum and maximum usempl_dv_pk values as inputs to main plot
        # frame size
        min_main_val_lst.append(
            usempl_pk_rec['usempl_dv_pk'][
                (usempl_pk_rec['mths_frm_peak'] >= -bkwd_mths_main) &
                (usempl_pk_rec['mths_frm_peak'] <= frwd_mths_main)].min())
        max_main_val_lst.append(
            usempl_pk_rec['usempl_dv_pk'][
                (usempl_pk_rec['mths_frm_peak'] >= -bkwd_mths_main) &
                (usempl_pk_rec['mths_frm_peak'] <= frwd_mths_main)].max())

    # Create Bokeh plot of PAYEMS normalized peak plot figure
    fig_title = 'Progression of PAYEMS in last 15 recessions'
    filename = ('images/usempl_npp_' + end_date_str2 + '.html')
    output_file(filename, title=fig_title)

    # Format the tooltip
    tooltips = [('Date', '@Date{%F}'),
                ('Months from peak', '$x{0.}'),
                ('Employment', '@PAYEMS{0,0.},000'),
                ('Fraction of peak', '@usempl_dv_pk{0.0 %}')]

    # Solve for minimum and maximum PAYEMS/Peak values in monthly main display
    # window in order to set the appropriate xrange and yrange
    min_main_val = min(min_main_val_lst)
    max_main_val = max(max_main_val_lst)

    datarange_main_vals = max_main_val - min_main_val
    datarange_main_mths = int(frwd_mths_main + bkwd_mths_main)
    fig_buffer_pct = 0.10
    fig = figure(plot_height=500,
                 plot_width=800,
                 x_axis_label='Months from Peak',
                 y_axis_label='PAYEMS as fraction of Peak',
                 y_range=(min_main_val - fig_buffer_pct * datarange_main_vals,
                          max_main_val + fig_buffer_pct * datarange_main_vals),
                 x_range=((-bkwd_mths_main -
                           fig_buffer_pct * datarange_main_mths),
                          (frwd_mths_main +
                           fig_buffer_pct * datarange_main_mths)),
                 tools=['save', 'zoom_in', 'zoom_out', 'box_zoom',
                        'pan', 'undo', 'redo', 'reset', 'hover', 'help'],
                 toolbar_location='left')
    fig.title.text_font_size = '18pt'
    fig.toolbar.logo = None
    l0 = fig.line(x='mths_frm_peak', y='usempl_dv_pk', source=rec_cds_list[0],
                  color='blue', line_width=5, alpha=0.7, muted_alpha=0.15)
    l1 = fig.line(x='mths_frm_peak', y='usempl_dv_pk', source=rec_cds_list[1],
                  color=Category20[13][0], line_width=2, alpha=0.7,
                  muted_alpha=0.15)
    l2 = fig.line(x='mths_frm_peak', y='usempl_dv_pk', source=rec_cds_list[2],
                  color=Category20[13][1], line_width=2, alpha=0.7,
                  muted_alpha=0.15)
    l3 = fig.line(x='mths_frm_peak', y='usempl_dv_pk', source=rec_cds_list[3],
                  color=Category20[13][2], line_width=2,
                  alpha=0.7, muted_alpha=0.15)
    l4 = fig.line(x='mths_frm_peak', y='usempl_dv_pk', source=rec_cds_list[4],
                  color=Category20[13][3], line_width=2, alpha=0.7,
                  muted_alpha=0.15)
    l5 = fig.line(x='mths_frm_peak', y='usempl_dv_pk', source=rec_cds_list[5],
                  color=Category20[13][4], line_width=2, alpha=0.7,
                  muted_alpha=0.15)
    l6 = fig.line(x='mths_frm_peak', y='usempl_dv_pk', source=rec_cds_list[6],
                  color=Category20[13][5], line_width=2, alpha=0.7,
                  muted_alpha=0.15)
    l7 = fig.line(x='mths_frm_peak', y='usempl_dv_pk', source=rec_cds_list[7],
                  color=Category20[13][6], line_width=2, alpha=0.7,
                  muted_alpha=0.15)
    l8 = fig.line(x='mths_frm_peak', y='usempl_dv_pk', source=rec_cds_list[8],
                  color=Category20[13][7], line_width=2, alpha=0.7,
                  muted_alpha=0.15)
    l9 = fig.line(x='mths_frm_peak', y='usempl_dv_pk', source=rec_cds_list[9],
                  color=Category20[13][8], line_width=2, alpha=0.7,
                  muted_alpha=0.15)
    l10 = fig.line(x='mths_frm_peak', y='usempl_dv_pk',
                   source=rec_cds_list[10], color=Category20[13][9],
                   line_width=2, alpha=0.7, muted_alpha=0.15)
    l11 = fig.line(x='mths_frm_peak', y='usempl_dv_pk',
                   source=rec_cds_list[11], color=Category20[13][10],
                   line_width=2, alpha=0.7, muted_alpha=0.15)
    l12 = fig.line(x='mths_frm_peak', y='usempl_dv_pk',
                   source=rec_cds_list[12], color=Category20[13][11],
                   line_width=2, alpha=0.7, muted_alpha=0.15)
    l13 = fig.line(x='mths_frm_peak', y='usempl_dv_pk',
                   source=rec_cds_list[13], color=Category20[13][12],
                   line_width=2, alpha=0.7, muted_alpha=0.15)
    l14 = fig.line(x='mths_frm_peak', y='usempl_dv_pk',
                   source=rec_cds_list[14], color='black', line_width=5,
                   alpha=0.7, muted_alpha=0.15)

    # Dashed vertical line at the peak PAYEMS value period
    fig.line(x=[0.0, 0.0], y=[-0.5, 2.0], color='black', line_width=2,
             line_dash='dashed', alpha=0.5)

    # Dashed horizontal line at PAYEMS as fraction of peak equals 1
    fig.line(x=[-bkwd_mths_max, frwd_mths_max], y=[1.0, 1.0],
             color='black', line_width=2, line_dash='dashed', alpha=0.5)

    # # Create the tick marks for the x-axis and set x-axis labels
    # major_tick_labels = []
    # major_tick_list = []
    # for i in range(-bkwd_mths_max, frwd_mths_max + 1):
    #     if i % 2 == 0:  # indicates even integer
    #         major_tick_list.append(int(i))
    #         if i < 0:
    #             major_tick_labels.append(str(i) + 'mth')
    #         elif i == 0:
    #             major_tick_labels.append('peak')
    #         elif i > 0:
    #             major_tick_labels.append('+' + str(i) + 'mth')

    # # minor_tick_list = [item for item in range(-bkwd_mths_max,
    # #                                           frwd_mths_max + 1)]
    # major_tick_dict = dict(zip(major_tick_list, major_tick_labels))
    # fig.xaxis.ticker = major_tick_list
    # fig.xaxis.major_label_overrides = major_tick_dict

    # Add legend
    legend = Legend(items=[(rec_label_yrmth_lst[0], [l0]),
                           (rec_label_yrmth_lst[1], [l1]),
                           (rec_label_yrmth_lst[2], [l2]),
                           (rec_label_yrmth_lst[3], [l3]),
                           (rec_label_yrmth_lst[4], [l4]),
                           (rec_label_yrmth_lst[5], [l5]),
                           (rec_label_yrmth_lst[6], [l6]),
                           (rec_label_yrmth_lst[7], [l7]),
                           (rec_label_yrmth_lst[8], [l8]),
                           (rec_label_yrmth_lst[9], [l9]),
                           (rec_label_yrmth_lst[10], [l10]),
                           (rec_label_yrmth_lst[11], [l11]),
                           (rec_label_yrmth_lst[12], [l12]),
                           (rec_label_yrmth_lst[13], [l13]),
                           (rec_label_yrmth_lst[14], [l14])],
                    location='center')
    fig.add_layout(legend, 'right')

    # # Add label to current recession low point
    # fig.text(x=[12, 12, 12, 12], y=[0.63, 0.60, 0.57, 0.54],
    #          text=['2020-03-23', 'DJIA: 18,591.93', '63.3% of peak',
    #                '39 days from peak'],
    #          text_font_size='8pt', angle=0)

    # label_text = ('Recent low \n 2020-03-23 \n DJIA: 18,591.93 \n '
    #               '63\% of peak \n 39 days from peak')
    # fig.add_layout(Label(x=10, y=0.65, x_units='screen', text=label_text,
    #                      render_mode='css', border_line_color='black',
    #                      border_line_alpha=1.0,
    #                      background_fill_color='white',
    #                      background_fill_alpha=1.0))

    # Add title and subtitle to the plot
    fig_title2 = 'Progression of U.S. total nonfarm employment'
    fig_title3 = '(PAYEMS, seasonally adjusted) in last 15 recessions'
    fig.add_layout(Title(text=fig_title3, text_font_style='bold',
                         text_font_size='16pt', align='center'), 'above')
    fig.add_layout(Title(text=fig_title2, text_font_style='bold',
                         text_font_size='16pt', align='center'), 'above')

    # Add source text below figure
    updated_date_str = end_date.strftime('%B %-d, %Y')
    fig.add_layout(Title(text='Source: Richard W. Evans (@RickEcon), ' +
                              'historical PAYEMS data from FRED and BLS, ' +
                              'updated ' + updated_date_str + '.',
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
    fig, end_date_str = usempl_npp()
