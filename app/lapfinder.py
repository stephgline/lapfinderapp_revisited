import geocoder
import pandas as pd
import numpy as np
import pickle
import os, time
from geopy.distance import vincenty
from time import sleep


#this function scrapes the rec center websites for up to date lap hours
#should be run ~once a week (1xday?) to ensure correct schedules
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
def get_coord(startaddress):
    sleep(1)
    g = geocoder.google(startaddress)

    g = g.latlng

    if len(g) == 0:
        get_coord(startaddress)
    else:     
        return g   
#TODO: add in pool dimensions
#TODO: add in direct pool
def addresscoord(startaddress):
    poolsched = pickle.load( open("app/static/poolscheduledf.p", "rb" ) )
    poolsdf = pickle.load(open("app/static/poolsdf.p", "rb"))
    
    #coord = get_coord(startaddress)
    coord = [40.6487392, -73.97446289999999]
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
    # day = time.strftime("%A")
    
    
    # pooladdress =  list(poolsdf[poolsdf['swimming_pool']==closepool[0]]['address'])[0]
    

    # laphours = ", ".join(list(poolsched[(poolsched['pool']==closepool[0]) & (poolsched[day]!= 'None')][day]))
    
    # today = time.strftime("%A %D")
    # website = list(poolsdf[poolsdf['swimming_pool']==closepool[0]]['website_source'])[0]

    # cur = con.cursor()
    #TODO add in static dimensions dataframe pickle
    # cur.execute('SELECT Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday FROM  lap_schedule_table5 WHERE Pool = "%s";' %(closepool))
    # query_results = cur.fetchall()
    # hours = []
    # for result in query_results:
    #     hours.append(dict(Monday=result[0], Tuesday=result[1], Wednesday=result[2], Thursday=result[3], Friday=result[4],Saturday=result[5], Sunday=result[6]))
    
    # indoordimdict = pickle.load(open("app/static/indoordimdict.p", "rb"))
    #dimensions = indoordimdict[closepool]

    #cur = con.cursor()
    #cur.execute('SELECT Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday FROM  lap_schedule_table5 WHERE Pool = "%s";' %(closepool))
    #query_results = cur.fetchall()
    #hours = []
    #for result in query_results:
    #hours.append(dict(Monday=result[0], Tuesday=result[1], Wednesday=result[2], Thursday=result[3], Friday=result[4],Saturday=result[5], Sunday=result[6]))
    

    # hours = allpools[allpools['pool'] == closepool[0]][['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
    # hours = hours.to_html()
    # #get dimensions for pool
    # indoordim = pickle.load(open("app/static/poolsdimensions.p", "rb"))
    # dimensions = indoordim[indoordim['pool'] == closepool]['dimensions'][0]
    return  closepool[0]




#TODO: fix to handle entering a pool directly
# def directpool(poolchoice):
#     closepool = poolchoice
#     os.environ['TZ'] = 'EST+05EDT,M4.1.0,M10.5.0'
#     time.tzset()
#     now = time.strftime("%A")
#     con = mdb.connect('localhost', 'root', '', 'lap_schedule')
#     poolhoursplace = pd.read_sql('SELECT p.Pool, a.address, p.%s FROM lap_schedule_table5 AS p JOIN pool_table6 AS a ON p.Pool = a.swimming_pool WHERE Pool = "%s"' %(now, closepool) , con)
#     pooladdress = poolhoursplace['address'].iloc[0]
#     laplist = poolhoursplace.ix[:, 2:].values.tolist()
#     laphours = []
#     for i in laplist:
#         if i[0] == 'None':
#             continue
#         else:
#             laphours.append(i[0])
            
#     if laphours == []:
#         laphours.append('There are no lap hours today')

#     laphours = ", ".join(laphours)


#     today = time.strftime("%A %D")
#     poolswebsdict = pickle.load(open("app/static/poolsandwebsites.p", "rb"))
#     website = poolswebsdict[closepool]

#     cur = con.cursor()
#     cur.execute('SELECT Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday FROM  lap_schedule_table5 WHERE Pool = "%s";' %(closepool))
#     query_results = cur.fetchall()
#     hours = []
#     for result in query_results:
#         hours.append(dict(Monday=result[0], Tuesday=result[1], Wednesday=result[2], Thursday=result[3], Friday=result[4],Saturday=result[5], Sunday=result[6]))

#     indoordimdict = pickle.load(open("app/static/indoordimdict.p", "rb"))
#     dimensions = indoordimdict[closepool]
#     return closepool, pooladdress, laphours, today, website, hours, dimensions

