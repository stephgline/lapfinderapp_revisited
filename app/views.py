
from app import app
from flask import render_template, request, send_file
import geocoder
import pandas as pd
import numpy as np

#from app import lapfinder
#import pdb
import pickle
import os, time
from geopy.distance import vincenty
from time import sleep


#this function scrapes the rec center websites for up to date lap hours
def get_schedule():
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pools = pickle.load(open("poolsdf.p", "rb"))
    urls = pools['website_source'].tolist()
    pool_names = pools['swimming_pool'].tolist()
    pooldfs = []

    for i, pool in enumerate(pool_names):
        url = urllib.request.urlopen(urls[i])
        s = url.read()
        soup = BeautifulSoup(s, "lxml")
        other = ["program", "center-hrs"]
        letters = soup.find_all(["p", "div"], other ) 
        swimposting = []
        otherposting = []
        for i in letters:
            if max(str(i).find('Lap Swim'), str(i).find('Adult Swim'), str(i).find('Adult Lap Swim'), 
                   str(i).find('Adult and Senior Swim'), str(i).find('Adult -Senior Lap/Swim')) > 0:
                swimposting.append(str(i))
            if str(i).find('Building Hours') > 0:
                swimposting.append(str(i))
            else:
                otherposting.append(str(i))

        #make a loop that saves lap swim programs and substitutes the days of the week for the building hours which separate them
        poolraw = swimposting[7:] #sometimes more building hours after swim schedule
        #make a loop that saves lap swim programs and substitutes the days of the week for the building hours which separate them
        pool_sched = {}
        count = 0
        #tony dapolitio specifically has senior lap swims. for now do not handle these specially
        for i in poolraw:
            try:
                if str(i).find('Building Hours') > 0:
                    pool_sched[days_of_week[count]] = []
                    count = count + 1
                if max(str(i).find('Lap Swim'), str(i).find('Adult Swim'), str(i).find('Adult Lap Swim'), 
                       str(i).find('Adult and Senior Swim'), str(i).find('Adult -Senior Lap/Swim')) > 0:
                    pool_sched[days_of_week[count-1]].append(re.findall('[0-9]*:[0-9]*\s[a-z]\s-\s[0-9]*:[0-9]*\s[a-z]'  ,str(i)))
            except:
                continue
        pooldf = pd.DataFrame.from_dict(pool_sched, orient='index')
        pooldf = pooldf.transpose()
        pooldf['pool'] = pool
        #remove list
        f = lambda x: 'None' if x==None else x[0]
        pooldf['Monday'] = pooldf['Monday'].map(f)
        pooldf['Tuesday'] = pooldf['Tuesday'].map(f)
        pooldf['Wednesday'] = pooldf['Wednesday'].map(f)
        pooldf['Thursday'] = pooldf['Thursday'].map(f)
        pooldf['Friday'] = pooldf['Friday'].map(f)
        pooldf['Saturday'] = pooldf['Saturday'].map(f)
        pooldf['Sunday'] = pooldf['Sunday'].map(f)
        pooldfs.append(pooldf)
        allpools = pd.concat(pooldfs)
        pickle.dump( allpools, open("poolscheduledf.p", "wb" ) )
    return allpools
        
#a function to retrieve the lat and lon of a pool that handles weird query limit errors
#todo fix to handle incorrect addresses so doesn't enter infinite loop
# def get_coord(startaddress, counter):
#     NoneType = type(None)
#     sleep(1)
#     g = geocoder.google(startaddress)

#     g = g.latlng

#     if type(g) == NoneType:
#         print(counter)
#         if counter < 5:
#             counter += 1
#             get_coord(startaddress, counter)
def get_coord(startaddress):
    NoneType = type(None)
    sleep(1)
    g = geocoder.google(startaddress)

    g = g.latlng

    if type(g) == NoneType:
        get_coord(startaddress)
    else:     
        return g 

def get_laphours(laphours):
    if laphours == '':
    	return 'There are no lap hours today.'
    else:
    	return laphours   

def addresscoord(startaddress):
    poolsched = pickle.load( open("app/static/poolscheduledf.p", "rb" ) )
    poolsdf = pickle.load(open("app/static/poolsdf.p", "rb"))
    
    #five tries
    coord = get_coord(startaddress)

    
    localmin = 0
    mindict = {}
    pool_list = list(poolsdf['swimming_pool'])
    for i, j in enumerate(poolsdf['latlon']):
        dist = vincenty(coord, j).miles

        if localmin == 0:
            localmin = dist
        if dist < localmin:
            localmin = dist
            mindict[localmin] = (pool_list[i],j)
        else:
            continue
    closepool = mindict[localmin]
    closepool = closepool[0]
    day = time.strftime("%A")
    
    
    pooladdress =  list(poolsdf[poolsdf['swimming_pool']==closepool]['address'])[0]
    

    laphours = ", ".join(list(poolsched[(poolsched['pool']==closepool) & (poolsched[day]!= 'None')][day]))
    laphours = get_laphours(laphours)
    
    today = time.strftime("%A %D")
    website = list(poolsdf[poolsdf['swimming_pool']==closepool]['website_source'])[0]

    hours = poolsched[poolsched['pool'] == closepool][['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
   
    #get dimensions for pool
    indoordim = pickle.load(open("app/static/poolsdimensions.p", "rb"))
    dimensions = list(indoordim[indoordim['pool']==closepool]['dimensions'])[0]
    return  closepool, pooladdress, laphours , today, website,  dimensions, hours





def directpool(poolchoice):
    closepool = poolchoice
    today = time.strftime("%A %D")
    day = time.strftime("%A")
    poolsched = pickle.load( open("app/static/poolscheduledf.p", "rb" ) )
    poolsdf = pickle.load(open("app/static/poolsdf.p", "rb"))
    pooladdress =  list(poolsdf[poolsdf['swimming_pool']==closepool]['address'])[0]
    laphours = ", ".join(list(poolsched[(poolsched['pool']==closepool) & (poolsched[day]!= 'None')][day]))

    website = list(poolsdf[poolsdf['swimming_pool']==closepool]['website_source'])[0]
    hours = poolsched[poolsched['pool'] == closepool][['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
   
    #get dimensions for pool
    indoordim = pickle.load(open("app/static/poolsdimensions.p", "rb"))
    dimensions = list(indoordim[indoordim['pool']==closepool]['dimensions'])[0]
    if laphours == '':
        laphours = 'There are no laphours today.'
    return closepool, pooladdress, laphours, today, website, hours, dimensions


@app.route('/about')
def about():
	return render_template("about.html")

#@app.route('/lapfinder')
@app.route('/')
def lapfinder():
	return render_template("lapfinderindex.html")



@app.route('/lapfinderoutput')
def lapfinderoutput():
    startaddress = request.args.get('LFID')
    if len(startaddress)>0:
        closepool, pooladdress, laphours, today, website,  dimensions, hours = addresscoord(startaddress)
        return render_template("lapfinderoutput.html", closepool=closepool, pooladdress=pooladdress, laphours =laphours, today=today, website=website,  dimensions=dimensions, tables=[hours.to_html()])

    else:
        poolchoice = request.args.get('pool')
        if poolchoice == 'None':
            return render_template("lapfinderindexnone.html")
        else:
            closepool, pooladdress, laphours, today, website, hours, dimensions = directpool(poolchoice)
            return render_template("lapfinderdirectoutput.html", closepool=closepool, pooladdress=pooladdress, laphours =laphours, today=today, website=website, tables=[hours.to_html()], dimensions=dimensions)




















