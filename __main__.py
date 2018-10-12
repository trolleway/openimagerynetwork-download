
import argparse, os
import untangle
import cPickle as pickle
import urllib
from progress.bar import Bar
import time

def GetCapabilities():

    bucket_contents = list()
    
    from urllib import urlopen

    
    #get list of files
    step=0
    last_key = ''
    
    while True:
        step = step + 1
        url='http://oin-hotosm.s3.amazonaws.com/?list-type=2'
        print step
        if step > 1:
            url = url + '&start-after='+last_key
            
        print url    
        response = urlopen(url).read()
        response_dict = untangle.parse(urlopen(url))    
        print response_dict.ListBucketResult.Name.cdata
        for element in response_dict.ListBucketResult.Contents:
            new_element = dict()
            new_element['Key'] = element.Key.cdata
            bucket_contents.append(new_element)
            last_key = element.Key.cdata
            
        IsTruncated = response_dict.ListBucketResult.IsTruncated.cdata
        if IsTruncated == 'false':
            break
    
    print len(bucket_contents)
    
    with open("bucket_contents.file", "wb") as f:
        pickle.dump(bucket_contents, f, pickle.HIGHEST_PROTOCOL)

def GetFootprints():
    
    base_url = 'http://oin-hotosm.s3.amazonaws.com/'
    temp_dir = 'files'
    counter = 0
    
    with open("bucket_contents.file", "rb") as f:
        bucket_contents = pickle.load(f)
        
        
        #calculate count of footprints for progressbar
        
        keys_count = 0
        for element in bucket_contents:
            if element['Key'].endswith('_footprint.json'):
                keys_count = keys_count + 1

        bar = Bar('Processing', max=keys_count, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds')
        for element in bucket_contents:
            #rint key
            if element['Key'].endswith('_footprint.json'):
                footprint_url = base_url+element['Key']
                footprint_filepath = os.path.join(temp_dir,element['Key'])
                footprint_filepath = footprint_filepath.replace('/', os.sep)

                #print footprint_url
                #print footprint_filepath
                directory = os.path.dirname(footprint_filepath)
                
                if not os.path.exists(directory):
                    os.makedirs(directory)
                if not os.path.isfile(footprint_filepath): 
                    counter = counter + 1
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
    counter = 0
    temp_dir = 'files'

    footprints_filename = 'footprints.gpkg'
    if os.path.exists(footprints_filename):
      os.remove(footprints_filename)

  
    
    with open("bucket_contents.file", "rb") as f:
        bucket_contents = pickle.load(f)
        
        
        #calculate count of footprints for progressbar
        
        keys_count = 0

        for element in bucket_contents:
            if element['Key'].endswith('_footprint.json'):
                keys_count = keys_count + 1

        bar = Bar('Merging OAM footprints', max=keys_count, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds')
        for element in bucket_contents:
            #rint key
            if element['Key'].endswith('_footprint.json'):
                if counter == 0:
                    cmd = 'ogr2ogr -overwrite {output_filename} {source_filename}'.format(output_filename=footprints_filename, source_filename=os.path.join(temp_dir,element['Key']))
                    os.system(cmd)
                    
                cmd = 'ogrmerge.py -o {footprints_filename} {source_filename} -single -update -append -src_layer_field_name key'.format(footprints_filename=footprints_filename, source_filename=os.path.join(temp_dir,element['Key']))
                cmd = cmd + ' -src_layer_field_content  {AUTO_NAME}'
                #print cmd
                counter = counter + 1
                bar.next()
                os.system(cmd)
        bar.finish()

if __name__ == '__main__':
    #GetCapabilities()
    #GetFootprints()
    MergeFoorprints()
