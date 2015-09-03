import json
# import time
import shutil
from pubnub import Pubnub
import boto3
from boto3.s3.transfer import S3Transfer
import os
from botocore.exceptions import ClientError

# from zipfile_infolist import print_info

def bucket_lookup(bucket_name):
    s3 = boto3.resource('s3')
    # bucket = s3.Bucket(bucket_name)
    exists = True
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            exists = False
    return exists


def check_files(file_list, bucket_name):
    s3 = boto3.resource('s3')
    s3_key_list = []
    exists = True
    if bucket_lookup(bucket_name):
        bucket = s3.Bucket(bucket_name)
        # we can continue and verify the files exists
        for k in bucket.objects.all():
            if k.key in file_list:
                print k.key
                s3_key_list.append(k.key)

    if set(file_list) != set(s3_key_list):
        exists = False
    else:
        print 'file list match'

    return exists


def download_files(case_id, file_list, bucket_name, base_name):
    # create a tmp dir > case_id, download files
    # check_files
    save_path = '/tmp'
    save_dir = os.path.join(save_path, 'case_' + case_id)
    download_ok = True
    if not os.path.exists(save_dir):
        os.umask(000)
        os.makedirs(save_dir)

    # s3 = boto3.resource('s3')
    client = boto3.client('s3')
    transfer = S3Transfer(client)
    try:
        if check_files(file_list, bucket_name):
            for item in file_list:
                save_item_name = os.path.join(save_dir, item.replace(base_name, ''))
                transfer.download_file(bucket_name, item, save_item_name)
                # true/false depend operation success/fail
        else:
            print 'check_files fail'
            download_ok = False
    except Exception as error:
        print error
        download_ok = False

    return download_ok


def compress_files(case_id):
    # change to dir, compress files
    save_path = '/tmp'
    base_name = 'case_' + case_id
    prefix = os.path.join(save_path, base_name)
    save_dir = os.path.join(save_path, base_name)
    # /tmp/filename.zip, tmp/case_id/
    zip_file = shutil.make_archive(prefix, 'zip', save_dir)
    # print zip_file
    return zip_file


def upload_zip(case_id, zip_file, bucket_name, prefix):
    save_path = '/tmp'
    base_name = 'case_' + case_id
    save_dir = os.path.join(save_path, base_name)

    zip_key = os.path.join(prefix, os.path.basename(zip_file))
    print 'file to upload: ', zip_key

    client = boto3.client('s3')  # check
    transfer = S3Transfer(client)
    transfer.upload_file(zip_file, bucket_name, zip_key)

    # delete dir
    print 'removing dir: ', save_dir
    shutil.rmtree(save_dir)

    # delete file
    try:
        print 'removing file: ', zip_file
        os.remove(zip_file)
    except OSError:
        print 'fail to delete file: ', zip_file

    return zip_file


def notify(msg):
    pubnub = Pubnub(
        publish_key="pub-c-175764f3-155a-4678-adba-948f6a350717",
        subscribe_key="sub-c-f75f9c02-517c-11e5-85f6-0619f8945a4f",
        pooling=False
    )
    channel = 'service_channel'

    # Synchronous usage
    print pubnub.publish(channel, msg)


def process_data(case_id, file_list, bucket_name, base_name):
    print 'process data called'
    if download_files(case_id, file_list, bucket_name, base_name):
        zip_file_name = compress_files(case_id)
        zip_key = upload_zip(case_id, zip_file_name, bucket_name, base_name)
        # time.sleep(5)
        msg = json.dumps({'case_id': case_id, 'zip_file': zip_key})
        notify(msg)
    else:
        print 'fail to download files'
