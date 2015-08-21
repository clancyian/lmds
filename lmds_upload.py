# File to S3
# Inspired by http://fromacoder.blogspot.ie/2012/06/recursive-s3-uploading-from-python.html
import sys
import os
import re
import boto
from boto.s3.key import Key
import boto.s3.connection
from config import *
import boto.dynamodb2
from boto.dynamodb2.table import Table

failed = open('failed.txt','w') 

def uploadFilesToS3(root,folder): 

    source_folder = root + '/' + folder

    conn = boto.s3.connect_to_region(region,
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        is_secure=True,               # uncomment if you are not using ssl
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
    )

    bucket = conn.get_bucket(bucket_name)

    conndyn = boto.dynamodb2.connect_to_region(region,
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
    )

    link = Table(
        'imagemetdata',
        connection=conndyn
    )

    k = Key(bucket) 
    for path,dir,files in os.walk(source_folder): 
        for file in files: 

	    if file.endswith("bmp"):


                # find the work number in the file name
	        worknumber = re.match( r'(.*)_.*', file, re.M|re.I)
 	        print "worknumber : ", worknumber.group(1)

                relpath = os.path.relpath(os.path.join(path,file)) 
	        fullpath = path + '/' + file
	        print fullpath 
	        # If we remove the root from the fullpath
                keypath = fullpath.replace(root, '')
	        print keypath 

	        keyname = keypath.replace (" ", "_")

	        # open the processhistory.log
                phlog = open(path + '/' + "ProcessHistory.log", "r")
	        print phlog.name

		foundwn = False 

		for line in phlog:
		    if worknumber.group(1) in line:
		        print line
			foundwn = True
			# go until cctserialnumber found
		    if (foundwn):
			#print "Now searching for cctserialnumber"
	                cctserialnumber = re.match( r'CAMERA ID:\s*(\w*)', line, re.M|re.I)
			if cctserialnumber:
 	           	    print "cctserialnumber : ", cctserialnumber.group(1)
			    # Write to dynamo
			    link.put_item(data={
 				'fqfilepath': keyname,
    				'cctserialnumber': cctserialnumber.group(1),
			    })

			    break 
			   
		
	        phlog.close

                if not bucket.get_key(keyname):
                    print 'sending...',keyname
                    k.key = keyname 
                    k.set_contents_from_filename(fullpath)
                #try:
                #    k.set_acl('public-read')
                #except:
                #    failed.write(relpath+', ')  
    failed.close()


uploadFilesToS3(sys.argv[1],sys.argv[2]) 
