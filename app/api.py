import logging
import os

from django.shortcuts import render
import djqscsv

import cloudstorage as gcs
from google.appengine.api import app_identity
from . import models

def download(request):
    qs = models.Elements.objects.all()
    filename = djqscsv.generate_filename(qs, append_datestamp=True)
    return djqscsv.render_to_csv_response(qs, filename)

def upload(request):
    qs = models.Elements.objects.all()
    filename = djqscsv.generate_filename(qs, append_datestamp=True)

    my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)
    gcs.set_default_retry_params(my_default_retry_params)
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name
    file_obj = djqscsv.render_to_csv_response(qs, filename)

    try:
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open(bucket+'/'+filename,
                            'w', 
                            content_type='text/csv',
                            options={'x-goog-meta-foo': 'foo',
                                     'x-goog-meta-bar': 'bar'},
                            retry_params=write_retry_params)
        gcs_file.write(file_obj.content)
        gcs_file.close()

    except Exception, e:  # pylint: disable=broad-except
        logging.exception(e)
    return render(request, 'app/index.html')
