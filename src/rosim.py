import os, sys
import pathlib, datetime
import pandas as pd #pip install pandas
from IPython.display import display
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import MO, WeekdayLocator
import numpy as np
import pprint
import json

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget

# from pandasgui import show

# TODO Keep variables in RAM between different sessions
# https://stackoverflow.com/questions/3047412/in-memory-database-in-python
# https://stackoverflow.com/questions/6687660/keep-persistent-variables-in-memory-between-runs-of-python-script

def get_file_extension(file_path):
    _, extension = os.path.splitext(file_path)
    return extension.lower()  # Convert to lowercase for case-insensitive comparison

def importAndPickleRosimFlowDataToDisk(filePathNameRosimFlow, filePathNamePickle):
    print('#######################################################################')   
    print('Working directy:' + os.getcwd())
    print('Working with this import file:'+ filePathNameRosimFlow.as_posix())   
    #https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
    #df = pd.read_csv(filePathName, encoding = 'ANSI', delimiter = '\t', header = None, skiprows=8, nrows = 100, on_bad_lines='skip')
    #t1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t1 + ': Starting reading csv-file: ' + filePathNamePickle)
    df = pd.read_csv(filePathNameRosimFlow, encoding = 'ANSI', delimiter = '\t', header = 'infer', skiprows=8, on_bad_lines='warn', decimal=".")   
    #https://docs.python.org/3/library/pickle.html (Is not required, use df.to_pickle() and pd.read_pickle() instead)
    #https://stackoverflow.com/questions/62160051/storing-pandas-dataframe-in-working-memory
    #t2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t2 + ': Starting to pickle imported csv-data frame: ' + filePathNamePickle)
    df.attrs = {'filePathNameRosimFlow': filePathNameRosimFlow}
    df.to_pickle(filePathNamePickle) #Saves the imported textfile to disk in a new name as a binary file
    #t3 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t3 + ': Saving pickled data frame: ' + filePathNamePickle)

def importAndStoreHDF5RosimFlowDataToDisk(filePathNameRosimFlow, filePathNameHDF5):
    print('#######################################################################')   
    print('Working directy:' + os.getcwd())
    print('Working with this import file:'+ filePathNameRosimFlow.as_posix())   
    #https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
    #df = pd.read_csv(filePathName, encoding = 'ANSI', delimiter = '\t', header = None, skiprows=8, nrows = 100, on_bad_lines='skip')
    #t1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t1 + ': Starting reading csv-file: ' + filePathNamePickle)
    df = pd.read_csv(filePathNameRosimFlow, encoding = 'ANSI', delimiter = '\t', header = 'infer', skiprows=8, on_bad_lines='warn', decimal=".")   
    #https://docs.python.org/3/library/pickle.html (Is not required, use df.to_pickle() and pd.read_pickle() instead)
    #https://stackoverflow.com/questions/62160051/storing-pandas-dataframe-in-working-memory
    #t2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t2 + ': Starting to pickle imported csv-data frame: ' + filePathNamePickle)
    df.attrs = {'filePathNameRosimFlow': filePathNameRosimFlow}
    store = pd.HDFStore(filePathNameHDF5) #Saves the imported textfile to disk in a new name as a binary file
    store.put("df", df)
    store.get_storer("df").attrs.my_attribute = df.attrs
    # print(str(store.get_storer("df").attrs.my_attribute))
    store.close()
    #t3 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t3 + ': Saving pickled data frame: ' + filePathNamePickle)

def importAndPickleRosimRainDataToDisk(filePathNameRosimRain, filePathNamePickle):
    print('#######################################################################')   
    print('Working directy:' + os.getcwd())
    print('Working with this import file:'+ filePathNameRosimRain.as_posix())   
    #https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
    #df = pd.read_csv(filePathName, encoding = 'ANSI', delimiter = '\t', header = None, skiprows=8, nrows = 100, on_bad_lines='skip')
    #t1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t1 + ': Starting reading csv-file: ' + filePathNamePickle)
    if get_file_extension(filePathNameRosimRain) == ".txt":
        df = pd.read_csv(filePathNameRosimRain, encoding = 'UTF-8', delimiter = '\t', header = 'infer', skiprows=1, on_bad_lines='warn', decimal=".")
    if get_file_extension(filePathNameRosimRain) == ".json":
        with open(filePathNameRosimRain) as file:
            rainJSON = json.loads(file)
            df = pd.json_normalize(rainJSON) #TODO 2024-03-19_Not finished
    display(df)
    #https://docs.python.org/3/library/pickle.html (Is not required, use df.to_pickle() and pd.read_pickle() instead)
    #https://stackoverflow.com/questions/62160051/storing-pandas-dataframe-in-working-memory
    #t2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t2 + ': Starting to pickle imported csv-data frame: ' + filePathNamePickle)
    df.attrs = {'filePathNameRosimRain': filePathNameRosimRain}
    df.to_pickle(filePathNamePickle) #Saves the imported textfile to disk in a new name as a binary file
    #t3 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t3 + ': Saving pickled data frame: ' + filePathNamePickle)

def importAndStoreHDF5RosimRainDataToDisk(filePathNameRosimRain, filePathNameHDF5):
    print('#######################################################################')   
    print('Working directy:' + os.getcwd())
    print('Working with this import file:'+ filePathNameRosimRain.as_posix())   
    #https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
    #df = pd.read_csv(filePathName, encoding = 'ANSI', delimiter = '\t', header = None, skiprows=8, nrows = 100, on_bad_lines='skip')
    #t1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t1 + ': Starting reading csv-file: ' + filePathNamePickle)
    df = pd.read_csv(filePathNameRosimRain, encoding = 'UTF-8', delimiter = '\t', header = 'infer', skiprows=1, on_bad_lines='warn', decimal=".")   
    #https://docs.python.org/3/library/pickle.html (Is not required, use df.to_pickle() and pd.read_pickle() instead)
    #https://stackoverflow.com/questions/62160051/storing-pandas-dataframe-in-working-memory
    #t2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t2 + ': Starting to pickle imported csv-data frame: ' + filePathNamePickle)
    df.attrs = {'filePathNameRosimRain': filePathNameRosimRain}
    # pprint.pprint(df.attrs)
    store = pd.HDFStore(filePathNameHDF5) #Saves the imported textfile to disk in a new name as a binary file
    store.put("df", df)
    store.get_storer("df").attrs.my_attribute = df.attrs
    # print(str(store.get_storer("df").attrs.my_attribute))
    store.close()
    #t3 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t3 + ': Saving pickled data frame: ' + filePathNamePickle)

def importPickledFileToRAM(filePathNamePickle):
    #t1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t1 + ': Starting to import data from pickle file: ' + filePathNamePickle)
    df = pd.read_pickle(filePathNamePickle)
    df.attrs = {'filePathNamePickle': filePathNamePickle}
    #t2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t2 + ': Finished importing data from pickle file: ' + filePathNamePickle)
    return df

def importHDF5FileToRAM(filePathNameHDF5):
    #t1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t1 + ': Starting to import data from pickle file: ' + filePathNamePickle)
    df = pd.read_pickle(filePathNameHDF5)
    df.attrs = {'filePathNameHDF5': filePathNameHDF5}
    #t2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print(t2 + ': Finished importing data from pickle file: ' + filePathNamePickle)
    return df

import inspect
import re
def dprint(x): # https://stackoverflow.com/questions/32000934/print-a-variables-name-and-value/57225950#57225950
    frame = inspect.currentframe().f_back
    s = inspect.getframeinfo(frame).code_context[0]
    r = re.search(r"\((.*)\)", s).group(1)
    print("{} = {}".format(r,x))

def findFileNameWithTwoDirectorysBelow(sPathFileName):
    res = None
    count = 0
    for i in range(0, len(sPathFileName)):
        if sPathFileName[::-1][i] == '\\':
            count = count + 1
            if count == 3:
                res = i
                break
    return sPathFileName[len(sPathFileName)-res-1:]

def findStartDateOfDataframe(df):
    iRow = 0
    dprint(len(df['datetime']))
    for iRow in range(0, len(df['datetime'])):
        dprint(iRow)
        dprint(df['datetime'].iloc[iRow])
        if df['datetime'].iloc[iRow] > pd.Timestamp(datetime.date(2000,1,1)):
            return df['datetime'].iloc[iRow]

def exportDfToExcel(df):
    #Export to excel
    # display(df_flow)
    sPathFileNameExcel = df.attrs['filePathNamePickle'].replace('.pkl','_pd.xlsx')
    sPathFileNameExcel = sPathFileNameExcel.replace('\\','/')

    # Not finished: df_flow.drop(df_flow[df_flow[yHead].str.isnumeric())].index, inplace = True))
    print('Exporting cleaned dataframe to excel. This can take several minutes and there is no progress bar.')
    t1 = datetime.datetime.now()
    print(t1.strftime('%Y-%m-%d %H:%M:%S') + ': Starting export at: ' + os.path.basename(sPathFileNameExcel))
    df.to_excel(sPathFileNameExcel) #Works, but takes very long time
    t2 = datetime.datetime.now()
    print(t2.strftime('%Y-%m-%d %H:%M:%S') + ': Finished export at: ' + os.path.basename(sPathFileNameExcel))
    duration =t2-t1
    print('Dataframe export to excel is finished.')
    print('Duration of export ' + str(duration.total_seconds()) + ' seconds.')


def scatterPlotDfToDateTime(df_flow, yHead, df_rains):
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    # print('plt.style.available:')

    dprint(plt.style.available)
    plt.style.use('default')
    df_flow['datetime'] = pd.to_datetime(df_flow['date'] + ' ' + df_flow['time'], format = r'%d.%m.%Y %H:%M:%S')
    # show(df_flow) # pandasgui
    dprint(len(df_flow))
    # df_flow.drop(df_flow[np.logical_not(df_flow[yHead].str.isnumeric())].index, inplace = True) # 20231127 TODO Causes som problem with some import csv files
    dprint(len(df_flow))
    #https://stackoverflow.com/questions/64195782/how-to-obtain-the-datatypes-of-objects-in-a-mixed-datatype-column
    # m = df_flow['datetime'].apply(lambda v: isinstance(v, datetime))
    # df_flow['dateTimeClean'] = pd.to_datetime(np.where(m, df_flow['datetime'], np.NaN))

    # exportDfToExcel(df_flow)

    dateTimeFlowStart = findStartDateOfDataframe(df_flow)
    dprint(dateTimeFlowStart)
    # display('df_flow.head():' + str(df_flow.head()))
    # print('Header of data series to be plotted:'+ df_flow[yHead].name)
    # plot Level #https://matplotlib.org/stable/plot_types/basic/scatter_plot.html#sphx-glr-plot-types-basic-scatter-plot-py
    print('Last row: ' + str(df_flow['datetime'].iloc[-1]))
    print('Highest level [m]: ' + str(df_flow[yHead].max()))
    plt.style.use('_mpl-gallery')
    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    # plt.subplots(figsize=(600*px, 200*px))    

    # fig, ax1 = plt.subplots(figsize=(1920*px, 900*px)) # External monitor
    fig, ax1 = plt.subplots(figsize=(1600*px, 800*px)) # figsize=(1920*px, 1080*px)
    ax1.set_title(label='Level [m] ('+ findFileNameWithTwoDirectorysBelow(df_flow.attrs['filePathNamePickle']) +')')
    #ax.scatter(x, y, s=sizes, c=colors, vmin=0, vmax=100)
    # print('From ' + str(df_flow['datetime'].iloc[0]) + ' to ' + str(df_flow['datetime'].iloc[-1]))
    
    ax1.plot(df_flow['datetime'], df_flow[yHead], c='blue', label=str(df_flow[yHead].name), zorder=0)
    xDateFormat = mdates.DateFormatter(r'%Y-%m-%d')
    #xDateFormatWeekNum = mdates.DateFormatter(r'%Y-W%U')
    xDateFormatWeekNum = mdates.DateFormatter(r'W%U-%m-%d')
    ax1.format_xdata = xDateFormat
    ax1.xaxis.set_major_formatter(xDateFormat)
    ax1.xaxis.set_minor_formatter(xDateFormatWeekNum)
    ax1.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1,interval=1))
    ax1.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=MO))
    ax1.grid(visible=True, which='major', axis='both', color='grey')
    ax1.grid(visible=True, which='minor', axis='both', color='lightgrey')
    ax1.tick_params(which='minor', labelcolor='lightgrey')
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles, labels, loc='upper left', bbox_to_anchor=(0, -0.12), fancybox=True,)

    ax1.set(xlim=(df_flow['datetime'].iloc[0], df_flow['datetime'].iloc[-1]),
           ylim=(0, df_flow[yHead].max()))
    # ax1.set(xlim=(df_flow['datetime'].iloc[0], df_flow['datetime'].iloc[-1]),
    #        ylim=(0, 0.5))   
    plt.ylabel('Level [m]', c='blue')
    plt.xticks(rotation=90, minor=False)
    plt.xticks(rotation=90, minor=True)

    #ax.secondary_yaxis()
    ax2 = ax1.twinx()
    dprint(len(df_rains))
    dprint(dateTimeFlowStart)
    for df_rain in df_rains:
        df_rain['datetime'] = pd.to_datetime(df_rain['Time'], format = r'%Y-%m-%d %H:%M:%S')
        dprint(df_rain.attrs['filePathNamePickle'])
        dprint(df_rain.iloc[0]['datetime'])
        dprint(len(df_rain))
        #https://sparkbyexamples.com/pandas/pandas-drop-rows-with-condition/
        df_rain.drop(df_rain[df_rain['datetime'] < dateTimeFlowStart].index, inplace = True)
        # df_rain = df_rain[df_rain['datetime'] >= dateTimeFlowStart]  #Didn't work, although it is according to the example above 
        dprint(len(df_rain))
        dprint(df_rain.iloc[0]['datetime'])        
        # dprint(df_rain)
        # df_flow['dateTimeClean'] = pd.to_datetime(np.where(m, df_rain['datetime'], np.NaN))        
        sRainName = str(df_rain.columns[1]).strip("\'")
        sRainNameNew = 'Rain @' + sRainName + ', cumsum [mm]'
        # dprint(sRainName)
        df_rain[sRainNameNew] = df_rain.iloc[:,[1]].cumsum()
        # dprint(df_rain)
        # display('df_rain.head():' + str(df_rain.head()))

        ax2.plot(df_rain['datetime'], df_rain[sRainNameNew], marker='none', linestyle='solid', label= sRainNameNew)
        # ax2.plot(df_rain['datetime'], df_rain.iloc[:,[2]], marker='none', linestyle='solid', label= str(df_rain.columns[2]))
        # ax.secondary_yaxis()
        # ax.scatter(secondary_y=True, color='black', ax=ax)
        handles, labels = ax2.get_legend_handles_labels()
        ax2.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.16, -0.12), ncol= 4, fancybox=True,)

        plt.ylabel('Cumulative sum of rainfall [mm]')

    plt.subplots_adjust(bottom=0.2,left=0.05, top=0.95, right=0.95)
    plt.show()

    # Create a Tkinter window
    import tkinter as tk
    from tkinter import messagebox
    winTk = tk.Tk()
    winTk.title('Matplotlib Scatter Plot')

    # Export figure as image
    sPathFileName = df_flow.attrs['filePathNamePickle'].replace('.pkl', '_' + yHead + '.pdf')
    sPathFileName = sPathFileName.replace('\\','/')
    plt.savefig(sPathFileName)

    # Embed Matplotlib figure in Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=winTk)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()

    # Set the position of the figure window (upper left corner)
    winTk.geometry("+0+0")

    # Function to close the Tkinter window and exit the Tkinter event loop
    # def on_closing(2):
    def on_closing(*args): # Don't understand why *args are required for w.bind('<Escape>', on_closing) to work https://www.askpython.com/python/examples/fixed-takes-0-positional-arguments-but-1-was-given
        winTk.destroy()
        winTk.quit()
        # if messagebox.askokcancel("Quit", "Do you want to quit?"):
        #     root.destroy()
        #     root.quit()

    # Close button
    #close_button = tk.Button(root, text="Close", command=on_closing)
    #close_button.pack()
    
    # Bind the ESC key with the callback function https://www.tutorialspoint.com/how-to-bind-the-escape-key-to-close-a-window-in-tkinter
    winTk.bind('<Escape>', on_closing)
    #w.bind('<Escape>', lambda e: on_closing(e)) # Not yet sure what the callback function e can be used for?!     

    # Run the Tkinter event loop
    winTk.protocol("WM_DELETE_WINDOW", on_closing)
    print('Plotting:' + str(yHead))
    winTk.mainloop()
    print('Plot closed.')

def main(df_flow, df_rains):
    t6 = datetime.datetime.now()
    print(t6.strftime('%Y-%m-%d %H:%M:%S') + ': Starting to print dataframe')
    print('Number of rows in data:' + str(df_flow.index[-1]))

    scatterPlotDfToDateTime(df_flow, 'level    [m]', df_rains)
    # scatterPlotDfToDateTime(df, 'velocity [m/s]')
    # scatterPlotDfToDateTime(df_flow, 'flowrate [l/s]', df_rains)
    # scatterPlotDfToDateTime(df, 'velocity(1) [m/s]')
    # scatterPlotDfToDateTime(df, 'water-us NIVUS [m]')
    # scatterPlotDfToDateTime(df, 'pressure int. [m]')
    # scatterPlotDfToDateTime(df, 'air-us NIVUS [m]')

    t7 = datetime.datetime.now()
    print(t7.strftime('%Y-%m-%d %H:%M:%S') + ': Finnished printing dataframe')
    duration =t7-t6
    print('Printing of the data frame took ' + str(duration.total_seconds()) + ' seconds.')

    #datetime_object = datetime.strptime(datetime_str, r'%d/%m/%y %H:%M:%S')

    # t6 = datetime.datetime.now()
    # print(t6.strftime('%Y-%m-%d %H:%M:%S') + ': Starting to print dataframe')
    # display(df.to_string())
    # t7 = datetime.datetime.now()
    # print(t7.strftime('%Y-%m-%d %H:%M:%S') + ': Finnished printing dataframe')
    # duration =t7-t6
    # print('Printing of the data frame took ' + str(duration.total_seconds()) + ' seconds.')





#filePathNamePickle = Path(filePathNameRosim).root + Path(filePathNameRosim).stem +  '.pkl' #Good, but does not include file directory