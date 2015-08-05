# File to S3
# Inspired by http://fromacoder.blogspot.ie/2012/06/recursive-s3-uploading-from-python.html
import sys
import boto
from boto.s3.key import Key
import boto.s3.connection
from config import *

failed = open('failed.txt','w') 

def uploadFilesToS3(source_folder): 

    conn = boto.s3.connect_to_region(region,
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        is_secure=True,               # uncomment if you are not using ssl
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
    )

    bucket = conn.get_bucket(bucket_name)


    k = Key(bucket) 
    for path,dir,files in os.walk(source_folder): 
        for file in files: 
            relpath = os.path.relpath(os.path.join(path,file)) 
            if not bucket.get_key(relpath):
                print 'sending...',relpath
                k.key = relpath
                k.set_contents_from_filename(relpath)
                #try:
                #    k.set_acl('public-read')
                #except:
                #    failed.write(relpath+', ')  
    #failed.close()


uploadFilesToS3(sys.argv[1]) 
