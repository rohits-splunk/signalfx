#!/usr/bin/env python3
import json
import argparse
import subprocess
import requests
from datetime import datetime as dt
import os
import pandas as pd

import time
from time import strftime
import smtplib
import sys
from email.mime.text import MIMEText

#check for days instead of seconds. Only use -t  , change grace period to int instead of float, use only date for expiration, days for grace period. 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', action='store',dest='realm',help='Splunk IM Realm', type=str, required=True)
    parser.add_argument('-d', action='store',dest='days',help='Number of days to check for Token Rotation', type=int,required=True)
    parser.add_argument('-a', action='store',dest='api_tok',help='API Token to authenticate with Splunk O11y', type=str,required=True)
    parser.add_argument('-t', action='store_true',default=False,dest='boolean_t',help='Switch for Token Rotation to True' )
    parser.add_argument('-f', action='store_false',default=True,dest='boolean_f',help='Switch for Token Rotation to False')
    parser.add_argument('-g', action='store',dest='gp',help='Grace Period in days', type=int, required=True)
    #parser.add_argument('--version', action='version',version='%(prog)s 1.0')
    results = parser.parse_args()
    if str(results.boolean_t) != 'True' and str(results.boolean_f) == 'False':
      sys.exit("User doesnt want to rotate the tokens ")
    realm=str(results.realm)
    api_token=results.api_tok
    grace_period_seconds = int(results.gp*3600*24)
    grace_period = str(abs(results.gp))
    script_run=str(results.boolean_t)
    #print(script_run)
    script_not_run = str(results.boolean_f)
    #print(script_not_run)
    days = results.days
    seconds=days*3600*24
    # import existing Org Tokens from Signal FX using the Session Token :
    url = 'https://api.'+realm+'.signalfx.com/v2/token/' #real, api token need to be parameters, if the url request is invzlid, just exit the program. 
   
    headers = {'X-SF-TOKEN': api_token}

    # payload = open("request.json")
    # res = requests.get(url, headers=headers) . json()
    res = requests.get(url, headers=headers)
    data = res.content
    
    with open('token.json', 'wb') as fp:
        fp.write(data)
        fp.close()
        # print(fp)
    # Opening JSON File
    f = open('token.json',)
    # Returns JSON object as a dictionary
    data = json.load(f)
    entries = data["results"]
    # print(entries)
    df = pd.DataFrame(entries)
    df2 = df[df.columns.difference(['created', 'creator', 'description',
                                   'disabled', 'exceedingLimits', 'limits', 'notifications', 'permissions','id','lastUpdatedBy'])]
    epoch_time = int(time.time())
    df2 = df2.assign(currentTime=epoch_time)
    #df2.loc[:,'currentTime'] = epoch_time
    #df2.reset_index(drop=True, inplace=True)
    #print(df2)
    #t='sprint(df2['expiry'])
    df2 = df2.loc[:,['name','expiry','authScopes','latestRotation','secret','currentTime']]
    df2['expiry'] = df2['expiry'].floordiv(1000)
    df2 = df2.assign(ExpiryDate=pd.to_datetime(df2['expiry'],  unit='s'))
    df['ExpiryDate'] = pd.to_datetime(df2['ExpiryDate']).dt.date
    
    df2 = df2.assign(Remaining=df2['expiry'] - df2['currentTime'])
    current_human_time = str(dt.now())
    
   
    with open('token.log', 'a') as l:
      start_text = '********************************** Script Running at '+current_human_time+' ***********************************'
      l.write(start_text +"\n")
      for index, row in df2.iterrows():
        if row['Remaining'] < seconds: # Number of seconds should be a parameter. 
          #print('True condition is true')
          
          data = 'The following token '+row['name']+' will expire on '+str(row['ExpiryDate']) +' and will be rotated soon with a grace period of '+grace_period+' days'
          print(data)
          l.write(data +"\n")
          tok_rotation(row['name'],realm,row['latestRotation'],str(grace_period_seconds),api_token,data) # 
          #send_mail(row['name'],row['ExpiryDate']) # Uncomment this line if Sendmail Function needs to be called.    
        else:
          data ='The Token '+row['name']+' is not expiring within '+str(days)+' hence need not rotate'
          l.write(data +"\n")
          print(data)
         #Rotate only if the input parameter is set as true/false, If there is nothing to rotate then it should be logged. 
         

        #print('The following Token "'+row['name']+'" will expire on '+str(row['ExpiryDate']))
        #send_mail(row['name'],str(row['ExpiryDate']))
def send_mail(name,ExpiryDate,data):
  body =data
  print(body)
  msg = MIMEText(body)
  msg['Subject'] = 'Splunk O11y Tokens about to expire'
  sender = 'xxxxx@gmail.com' # Replace sender and recepient emails accordingly
  recipient= 'xxxxx@splunk.com'
  s = smtplib.SMTP('smtp.gmail.com', 587)
  s.starttls()
  s.login(sender,'***********') #Add your Google App Authentication token if using GMAIL smtp service 
  msg['From'] = sender
  msg['To'] = recipient
  s.sendmail(sender, recipient, msg.as_string())
  s.quit()
  #print('The following Token "'+name+'" will expire on '+ExpiryDate)
def tok_rotation(name,realm,latestRotation,grace_period,api_token,data):
  ct = dt.now()
  ct_str=str(ct)
  
  #Convert latestRotation epoch time into Human Readable form.
  latestRotation_s=latestRotation/1000 
  latestRotation_datime_obj=dt.utcfromtimestamp(latestRotation_s) 
  datetime_string=latestRotation_datime_obj.strftime( "%d-%m-%Y %H:%M:%S" )
  #First will validate if the Token was rotated within last 7 days. If yes then will exit the function.
  #if latestRotation < days_epoch:
    #print('The following token '+name+' will not be rotated as it was just rotated on'+datetime_string)
  #  return
  #else:
   #url = "https://api."+realm+".signalfx.com/v2/token/"+name+"/rotate?graceful="+grace_period #grace period needs to be in an input, realm, name
  headers = {'X-SF-TOKEN': api_token}
  url = "https://api."+realm+".signalfx.com/v2/token/"+name+"/rotate?graceful="+grace_period
  res = requests.post(url, headers=headers)
  data = res.content  
  with open('token_rotate.log', 'a') as r:
    rdata = 'The token '+name+" was rotated on "+ct_str+" with a grace period of  "+grace_period
    r.write(rdata +"\n")
    

if __name__ == '__main__':
    main()
