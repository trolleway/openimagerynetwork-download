
import os
import untangle
import cPickle as pickle
import urllib
from progress.bar import Bar
import time


import argparse

temp_dir = 'files'
def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 45

    parser = argparse.ArgumentParser(description='''Download foorptints and metadata of OpenImageryNetwork scenes from Amazon s3 ''',
            formatter_class=PrettyFormatter)
    parser.add_argument('--storage', help = 'Path to storage location. Used like www folder in webserver. ')
    parser.add_argument('--last', default=0,help = 'process only this most recent number of scenes')

    parser.epilog = \
        '''Samples: 

time python %(prog)s --last 15
''' \
        % {'prog': parser.prog}
    return parser

    
def GetCapabilities(storage=''):
    
    

    bucket_contents = list()
    
    from urllib import urlopen

    
    #get list of files
    step=0
    last_key = ''
    bar = Bar('Get list of S3 bucket content', max_value=progressbar.UnknownLength, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds')
    
    while True:
        step = step + 1
        bar.next()
        url='http://oin-hotosm.s3.amazonaws.com/?list-type=2'
        print step
        if step > 1:
            url = url + '&start-after='+last_key
            
        #print url    
        response = urlopen(url).read()
        response_dict = untangle.parse(urlopen(url))    
        #print response_dict.ListBucketResult.Name.cdata
        for element in response_dict.ListBucketResult.Contents:
            new_element = dict()
            new_element['Key'] = element.Key.cdata
            bucket_contents.append(new_element)
            last_key = element.Key.cdata
            
        IsTruncated = response_dict.ListBucketResult.IsTruncated.cdata
        if IsTruncated == 'false':
            break
    bar.finish()
    print 'Files in bucket: ' + str(len(bucket_contents))
    
    with open(os.path.join(storage,"bucket_contents.file"), "wb") as f:
        pickle.dump(bucket_contents, f, pickle.HIGHEST_PROTOCOL)

def DebugCapabilities():
    
    base_url = 'http://oin-hotosm.s3.amazonaws.com/'
    temp_dir = 'files'
    counter = 0
    
    with open(os.path.join(storage,"bucket_contents.file"), "rb") as f:
        bucket_contents = pickle.load(f)
        
        
        #calculate count of footprints 
        
        keys_count = 0
        for element in bucket_contents:
            if element['Key'].endswith('meta.json'):
                keys_count = keys_count + 1
                print base_url + element['Key']
        print keys_count

                
def GetFiles(endswith='_meta.json', last=0, storage=''):
    
    base_url = 'http://oin-hotosm.s3.amazonaws.com/'
    temp_dir = 'files'
    counter = 0
    
    with open(os.path.join(storage,"bucket_contents.file"), "rb") as f:
        bucket_contents = pickle.load(f)
        
        
        #calculate count of footprints for progressbar
        
        keys_count = 0
        for element in bucket_contents:
            if element['Key'].endswith(endswith):
                keys_count = keys_count + 1
                
        print 'Found {keys_count} files to download. If they exist in local cache, download will skipped'.format(keys_count=keys_count)
        bar = Bar('Download OAM footprints', max=keys_count, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds')
        for element in bucket_contents:
            #rint key
            if element['Key'].endswith(endswith):
                footprint_url = base_url+element['Key']
                footprint_filepath = os.path.join(storage,element['Key'])
                footprint_filepath = footprint_filepath.replace('/', os.sep) #slash symbols become from S3 key

                #print footprint_url
                #print footprint_filepath
                directory = os.path.dirname(footprint_filepath)
                
                if not os.path.exists(directory):
                    os.makedirs(directory)
                if not os.path.isfile(footprint_filepath): 
                    counter = counter + 1
                    if (last <> 0): 
                        if (int(counter) < (int(keys_count) - int(last))):
                            bar.next()
                            continue
                    while True:
                        try:
                            urllib.urlretrieve(footprint_url, footprint_filepath)
                            time.sleep(0.4)
                            bar.next()
                            break
                        except:
                            print 'cooldown 20 seconds...'
                            time.sleep(30)
                            
                    #if counter % 20 == 0:
                    #    time.sleep(40)
                #bar.next()
        bar.finish()   
def MergeFoorprints():
    #deprecated function for merging footprint.json files - they provided for not all scenes
    counter = 0
    temp_dir = 'files'
    import json
    
    base_url = 'http://oin-hotosm.s3.amazonaws.com/'
    geojsonHeader='''    
{
"type": "FeatureCollection",
"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
                                                                                
"features": [
'''
    geojsonFooter='''
]
}
'''

    footprints_filename = 'footprints.geojson'
    if os.path.exists(footprints_filename):
      os.remove(footprints_filename)

  
    
    with open("bucket_contents.file", "rb") as f:
        bucket_contents = pickle.load(f)
        
        #calculate count of footprints for progressbar
        
        keys_count = 0

        for element in bucket_contents:
            if element['Key'].endswith('_footprint.json'):
                keys_count = keys_count + 1
                
        fs = open(footprints_filename,'w')
        fs.write(geojsonHeader+"\n")
        fs.close()
        fs = open(footprints_filename,'a')    

        start_record = 1
        #start_record = 2731
        end_record = float('Inf')

        bar = Bar('Merging OAM footprints', max=keys_count, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds')
        for element in bucket_contents:

            #rint key
            if element['Key'].endswith('_footprint.json'):
                with open(os.path.join(temp_dir,element['Key'])) as jsonfile:
                    counter = counter + 1
                    if counter < start_record:
                       bar.next()
                       continue
                    data = json.load(jsonfile)
                    try:
                        geometry = data['features'][0]['geometry']
                    except:
                        print 'geometry read error at ' + element['Key'] + ' skipped'
                        bar.next()
                        continue
                        
                    #if 1==1: 
                    if data['features'][0]['geometry']['coordinates'][0][0][0] == float('Inf'):
                        print "\n signal"
                        print str(data['features'][0]['geometry']['coordinates'][0][0][0]).isdigit
                        
                        bar.next()
                        #quit()
                        continue
                    geojsonString='{ "type": "Feature", "properties": { "key": "%(key)s", "url_geotiff": "%(url_geotiff)s" }, "geometry":  %(geometry)s }, '
                    exportString = geojsonString % {"key" : element['Key'],'url_geotiff' : base_url + element['Key'] ,"geometry" : json.dumps(geometry)}
                    fs.write(exportString+"\n")
                    print ' '+str(counter)


                if counter == end_record:
                    bar.next()
                    break
                bar.next()
                #os.system(cmd)
        bar.finish()

        fs.write(geojsonFooter+"\n")
        fs.close()
        
        
        
def MergeMeta(storage=''):
    #merge files "meta" into csv with polygon
    counter = 0
    temp_dir = os.path.join(storage,'files')
    import json
    
    base_url = 'http://oin-hotosm.s3.amazonaws.com/'


    footprints_filename = os.path.join(storage,'footprints.geojson')
    if os.path.exists(footprints_filename):
      os.remove(footprints_filename)

  
    
    with open(os.path.join(storage,"bucket_contents.file"), "rb") as f:
        bucket_contents = pickle.load(f)
        #calculate count of meta files for progressbar
        keys_count = 0

        for element in bucket_contents:
            if element['Key'].endswith('_meta.json'):
                keys_count = keys_count + 1
                


        start_record = 1
        #start_record = 2731
        end_record = float('Inf')
        
        import unicodecsv as csv
        csvfile = open(os.path.join(storage,'footprints.csv'), "wb")

        spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL,encoding='utf-8')
        spamwriter.writerow(['counter',
        'uuid',
        'title',
        'footprint',
        'gsd',
        'file_size',
        'acquisition_start',
        'acquisition_end',
        'platform',
        'provider',
        'contact',
        'properties.sensor',
        'properties.thumbnail',
        'properties.tms',
        'properties.wmts',
        'uploaded_at',
        
        
        
        ])

        bar = Bar('Merging OAM footprints', max=keys_count, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds')
        for element in bucket_contents:
            if element['Key'].endswith('_meta.json'):
                if os.path.isfile(os.path.join(storage,element['Key'])) == False:
                    bar.next()
                    continue
                with open(os.path.join(storage,element['Key'])) as jsonfile:
                    counter = counter + 1
                    if counter < start_record:
                       bar.next()
                       continue
                    data = json.load(jsonfile)
                    try:
                        footprint = data['footprint']
                    except:
                        print 'geometry read error at ' + element['Key'] + ' skipped'
                        bar.next()
                        continue
                        
                    #if 1==1: 
                    if data['footprint'] == float('Inf'):
                        print str(data['features'][0]['geometry']['coordinates'][0][0][0]).isdigit
                        
                        bar.next()
                        continue


                    spamwriter.writerow([counter,data['uuid'],data['title'],
                    str(footprint),
                    data['gsd'],
                    data['file_size'],data['acquisition_start'],data['acquisition_end'],
                    data['platform'],data['provider'],data['contact'],
                    data['properties'].get('sensor'),
                    data['properties'].get('thumbnail'),
                    data['properties'].get('tms'),
                    data['properties'].get('wmts'),
                    str(data.get('uploaded_at'))
                    ]
                    )


                if counter == end_record:
                    bar.next()
                    break
                bar.next()
                #os.system(cmd)
        bar.finish()

        csvfile.close()

if __name__ == '__main__':
    parser = argparser_prepare()
    args = parser.parse_args()
    
    GetCapabilities(storage=args.storage)
    #DebugCapabilities()
    GetFiles('_meta.json',last=args.last,storage=args.storage)
    MergeMeta(storage=args.storage)
