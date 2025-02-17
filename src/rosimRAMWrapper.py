# Required if no admin access to Windows Environmental Varialbes
import os
os.environ['TCL_LIBRARY'] = r'C:\Users\secn17444\pyver\Python313\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\secn17444\pyver\Python313\tcl\tk8.6'

# Inspired by https://stackoverflow.com/questions/6687660/keep-persistent-variables-in-memory-between-runs-of-python-script
from importlib import reload
import sys, os, pathlib, datetime
import pandas as pd
import rosim

import inspect
import re
def dprint(x): # https://stackoverflow.com/questions/32000934/print-a-variables-name-and-value/57225950#57225950
    frame = inspect.currentframe().f_back
    s = inspect.getframeinfo(frame).code_context[0]
    r = re.search(r"\((.*)\)", s).group(1)
    print("{} = {}".format(r,x))

def importRosimFlow(filePathNameRosimFlow):
    #filePathNameRosim = 'c:/Users/Christian/OneDrive/Rosim/SiteVisits/2023-W43/VA SYD/SNB1122_20231024_161222.TXT'
    filePathNameRosimFlow = pathlib.PureWindowsPath(filePathNameRosimFlow)
    filePathNamePickle = os.path.splitext(filePathNameRosimFlow)[0] + '.pkl' #https://bobbyhadz.com/blog/python-remove-extension-from-filename
    filePathNameHDF5 = os.path.splitext(filePathNameRosimFlow)[0] + '.hdf5'
    print('Working directory: ' + os.path.dirname(filePathNameRosimFlow))
    # If import file is not pickled yet, then pickle, else directly import pickled file
    t1 = datetime.datetime.now()
    if not os.path.exists(filePathNamePickle):
        print(t1.strftime('%Y-%m-%d %H:%M:%S') + ': Starting reading csv-file: ' + os.path.basename(filePathNameRosimFlow))
        rosim.importAndPickleRosimFlowDataToDisk(filePathNameRosimFlow,filePathNamePickle)
        t2 = datetime.datetime.now()
        print(t2.strftime('%Y-%m-%d %H:%M:%S') + ': Saving pickled data frame at: ' + os.path.basename(filePathNamePickle))
        duration =t2-t1
        print('Reading csv-file and pickling it to disk took ' + str(duration.total_seconds()) + ' seconds.')
    if not os.path.exists(filePathNameHDF5):
        print(t1.strftime('%Y-%m-%d %H:%M:%S') + ': Starting reading csv-file: ' + os.path.basename(filePathNameHDF5))
        rosim.importAndStoreHDF5RosimFlowDataToDisk(filePathNameRosimFlow,filePathNameHDF5)
        t2 = datetime.datetime.now()
        print(t2.strftime('%Y-%m-%d %H:%M:%S') + ': Saving data to storeHDF5 frame at: ' + os.path.basename(filePathNameHDF5))
        duration =t2-t1
        print('Reading csv-file and pickling it to disk took ' + str(duration.total_seconds()) + ' seconds.')
    t3 = datetime.datetime.now()
    print(t3.strftime('%Y-%m-%d %H:%M:%S') + ': Starting to import data from pickling file: ' + os.path.basename(filePathNamePickle))
    df_flow = rosim.importPickledFileToRAM(filePathNamePickle)
    t4 = datetime.datetime.now()
    print(t4.strftime('%Y-%m-%d %H:%M:%S') + ': Finished importing data from pickling file: ' + os.path.basename(filePathNamePickle))
    return df_flow

def importRosimRain(filePathNameRosimRain):
        #filePathNameRosim = 'c:/Users/Christian/OneDrive/Rosim/SiteVisits/2023-W43/VA SYD/SNB1122_20231024_161222.TXT'
        filePathNameRosimRain = pathlib.PureWindowsPath(filePathNameRosimRain)
        filePathNamePickle = os.path.splitext(filePathNameRosimRain)[0] + '.pkl' #https://bobbyhadz.com/blog/python-remove-extension-from-filename
        filePathNameHDF5 = os.path.splitext(filePathNameRosimRain)[0] + '.hdf5'
        print('Working directory: ' + os.path.dirname(filePathNameRosimRain))
        # If import file is not pickled yet, then pickle, else directly import pickled file
        t1 = datetime.datetime.now()
        if not os.path.exists(filePathNamePickle):
            print(t1.strftime('%Y-%m-%d %H:%M:%S') + ': Starting reading csv-file: ' + os.path.basename(filePathNameRosimRain))
            rosim.importAndPickleRosimRainDataToDisk(filePathNameRosimRain,filePathNamePickle)
            t2 = datetime.datetime.now()
            print(t2.strftime('%Y-%m-%d %H:%M:%S') + ': Saving pickled data frame at: ' + os.path.basename(filePathNamePickle))
            duration =t2-t1
            print('Reading csv-file and pickling it to disk took ' + str(duration.total_seconds()) + ' seconds.')
        if not os.path.exists(filePathNameHDF5):
            print(t1.strftime('%Y-%m-%d %H:%M:%S') + ': Starting reading csv-file: ' + os.path.basename(filePathNameHDF5))
            rosim.importAndStoreHDF5RosimFlowDataToDisk(filePathNameRosimRain,filePathNameHDF5)
            t2 = datetime.datetime.now()
            print(t2.strftime('%Y-%m-%d %H:%M:%S') + ': Saving data to storeHDF5 frame at: ' + os.path.basename(filePathNameHDF5))
            duration =t2-t1
            print('Reading csv-file and pickling it to disk took ' + str(duration.total_seconds()) + ' seconds.')
        t3 = datetime.datetime.now()
        print(t3.strftime('%Y-%m-%d %H:%M:%S') + ': Starting to import data from pickling file: ' + os.path.basename(filePathNamePickle))
        df_rain = rosim.importPickledFileToRAM(filePathNamePickle)
        t4 = datetime.datetime.now()
        print(t4.strftime('%Y-%m-%d %H:%M:%S') + ': Finished importing data from pickling file: ' + os.path.basename(filePathNamePickle))
        return df_rain

def listRainFileNamesInDirectory(sRainsDirPath): #https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    # r=root, d=directories, f = files
    sRainsPathFilenames = []
    for root, directories, filesnames in os.walk(sRainsDirPath):
        for file in filesnames:
            if file.lower().endswith(".txt"):
                dprint(file)
                sRainsPathFilenames.append(os.path.join(root, file))
    return sRainsPathFilenames

df_flow = None
dfs_rains = []

sRainsDirPath = r'c:\Users\secn17444\Documents\RS\Regn'
sRainsPathFilenames = listRainFileNamesInDirectory(sRainsDirPath)
dprint(sRainsDirPath)
sRainsPathFilenames = []
dprint(sRainsPathFilenames)
# sRainsPathFilenames =  [r'c:\Users\Christian\OneDrive\Rosim\SiteVisits\2023-W45\Sth\Regn\Sk_ndal_Centrum_level_c046c.txt',
#                         r'c:\Users\Christian\OneDrive\Rosim\SiteVisits\2023-W45\Sth\Regn\RG-V_ster_ngsv_gen_level_91f87.txt',
#                         r'c:\Users\Christian\OneDrive\Rosim\SiteVisits\2023-W45\Sth\Regn\RG-Spikskogatan_level_da524.txt']

sRainsPathFilenamesJSON =  [r'c:\Users\secn17444\Documents\RS\SMHI\opendata-download-metobs.smhi.se_api_version_1.0_parameter_14_station_52350_period_latest-months_data.json.json']


if __name__ == "__main__":
    while True:
        if not isinstance(df_flow, pd.DataFrame):
            # df_flow = importRosimFlow(r'c:\Users\Christian\OneDrive\Rosim\SiteVisits\2023-W45\Sth\Forsen_20231108_124434.TXT') # Some problem with this data
            df_flow = importRosimFlow(r'c:\Users\secn17444\Documents\RS\FlowData\SNB2432-N_20240313_134006.TXT') # works without flow level cleaning
            # df_flow = importRosimFlow(r'c:\Users\Christian\OneDrive\Rosim\SiteVisits\2023-W45\Sth\KNB-31147_20231107_231932.TXT')
        if not isinstance(dfs_rains, pd.DataFrame):
            del dfs_rains
            dfs_rains =[]
            for sRainPathFilename in sRainsPathFilenames:
                dfs_rains.append(importRosimRain(sRainPathFilename))
        rosim.main(df_flow, dfs_rains)
        print('Press enter to re-run the script, CTRL-C to exit')
        sys.stdin.readline()
        reload(rosim)
