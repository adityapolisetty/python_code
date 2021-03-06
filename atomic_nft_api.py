# Importing necessary packages 
import pandas as pd
import requests
import datetime
import time
import os
import sys 
import numpy as np
import ast
import regex as re
from datetime import datetime

# API request function - extracts daily NFT data 
def API_request_Atomic(limit, time_data, time_start, lines_to_save_data, data_folder):
    counter = 0
    df = pd.DataFrame({}, dtype=str)
    url = "https://wax.api.atomicassets.io/atomicmarket/v1/sales/"
    col_list = ["asset_id","listing_symbol","listing_price","collection_name","created_at_time"]
    
    state = {'sold':'3'}
    page=1
    time_start = int(time_start.timestamp()*10**3)
    time_data = int(time_data.timestamp()*10**3)
    supp = pd.to_datetime(time_start, unit='ms')

    with open(data_folder+str(supp.month)+"_"+str(supp.year)+'.txt', 'w') as f:
    
        while(time_data>time_start):
            # time_dup = datetime.fromtimestamp(time_data)
            # print(time_dup)
            querystring = {"state":state["sold"],
                "before":time_data,
                "page":str(page),
                "limit":str(limit)}
            
            response = requests.request("GET", url, params=querystring)
            #print(response.status_code)

            if response.status_code==200:
                df_supp = pd.DataFrame(response.json()['data'], dtype=str)
                if len(df_supp)==0: break
                df = df.append(df_supp, ignore_index=True)
                
                time_data_supp = int(df_supp.created_at_time.min())
                
                if page>1:
                    if (pd.to_datetime(time_data, unit='ms') -  pd.to_datetime(time_data_supp, unit='ms'))>pd.Timedelta('3 hours'): 
                        page=1
                        time_data=time_data_supp
                    else: page+=1
                else:
                    if time_data == time_data_supp: page+=1
                    else: time_data = time_data_supp
                
                counter +=limit
                if counter%lines_to_save_data==0:
                    print(len(df_supp), len(df), pd.to_datetime(time_data, unit='ms'), pd.to_datetime(time_data_supp, unit='ms'), page)
                    supp = pd.to_datetime(time_start, unit='ms')  
                    for j in (0,len(df)-1):
                        d = df['assets'].iloc[j]
                        d =  re.search("'asset_id': '(.*)', 'owner'", d) 
                        df['asset_id'] = d.group(1)
                    df[col_list].to_csv(data_folder+'NFT_Atomic_'+str(supp.month)+'_'+str(supp.year)+'.csv.gz', index=False)

                f.write( "\n"+ str(len(df_supp))+","+str( len(df))+","+ str(pd.to_datetime(time_data, unit='ms'))+"," +str(pd.to_datetime(time_data_supp, unit='ms'))+","+str( page))
            time.sleep(1)
        
    
    if len(df)>0:
        print(len(df_supp), len(df), pd.to_datetime(time_data, unit='ms'), pd.to_datetime(time_data_supp, unit='ms'), page)
        df2 = []
        for j in range(len(df)):
            d = df['assets'].iloc[j] 
            d =  re.search("'asset_id': '(.*)', 'owner'", d) 
            df2.append(d.group(1))

        df['asset_id'] = df2
        print(df[col_list])
        df[col_list].to_csv(data_folder+'NFT_Atomic_'+str(supp.month)+'_'+str(supp.year)+'.csv.gz', index=False)
            
    else:
        print('No data in this month')
        
try:
    dt_start_time = pd.to_datetime(sys.argv[1])
    dt_end_time = pd.to_datetime(sys.argv[2])
except:
    sys.exit('Wrong time format')
    
dt_time = [dt_start_time, dt_end_time]
print('From: ', dt_time[0])
print('To: ', dt_time[1])

lines_to_save_data = 5000
limit = 100
data_folder = ".\\Data_Atomic\\"

for i in range(len(dt_time)-1):
    
    data_folder = ".\\Data_Atomic\\"
    os.system(r'mkdir '+data_folder) 
    data_folder += str(dt_time[-2-i].month)+'_'+str(dt_time[-2-i].year)+'\\'
    os.system('mkdir '+data_folder)
    API_request_Atomic(limit, dt_time[-1-i], dt_time[-2-i], lines_to_save_data, data_folder)