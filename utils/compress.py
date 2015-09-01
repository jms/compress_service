__author__ = 'jms'
import boto3
import zipfile

# queue settings
from rq import Queue
from redis import Redis

def check_files(file_list, bucket_name):
    s3 = boto3.resource('s3')
    s3_key_list = []
    exists = True
    for b in s3.buckets.all():
        if b.name == bucket_name:
            # we can continue and verify the files exists
            for k in b.objects.all():
                if k.key in file_list:
                    s3_key_list.append(k.key)
        else:
            exists = False

    if set(file_list) != set(s3_key_list):
        exists = False

    return exists


def download_files(case_id, file_list):
    # create a tmp dir > case_id, download files
    pass


def compress_files(case_id, file_list):
    # change to dir, compress files
    pass


def upload_zip(zip_file):
    # upload to s3, return key
    pass
