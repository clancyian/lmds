import web
from web import form
import boto
from boto.s3.key import Key
import boto.s3.connection
from config import *
import boto.dynamodb2
from boto.dynamodb2.table import Table


render = web.template.render('templates/')

urls = (
    '/', 'index'
)

myform = form.Form(
    form.Textbox('image',
        form.notnull))

conndyn = boto.dynamodb2.connect_to_region(region,
    aws_access_key_id = access_key,
    aws_secret_access_key = secret_key,
)

link = Table(
   'imagemetdata',
    connection=conndyn
)


class index:
    def GET(self):
        form = myform()
        return render.formhome(form)

    def POST(self):
	imageList = []
        form = myform()
        if not form.validates():
            return render.formhome(form)
        else:

            conn = boto.s3.connect_to_region(region,
                aws_access_key_id = access_key,
                aws_secret_access_key = secret_key,
                is_secure=True,               # uncomment if you are not using ssl
                calling_format = boto.s3.connection.OrdinaryCallingFormat(),
            )

            bucket = conn.get_bucket(bucket_name)

	    print 'querying for '  + form.d.image
	    rs = link.query_2(index='cctserialnumber-index',
                              cctserialnumber__eq=form.d.image)
			      
            #rs = bucket.list(prefix=form.d.image)

            for key in rs:
		print key['fqfilepath']
		#if key.name.endswith('bmp'):

                url = conn.generate_url(
                    60,
                    'GET',
                    bucket_name,
                    key['fqfilepath'],
                    )

		print url
	        imageList.append(url)

            return render.formresult(imageList)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

