import boto3
from secrets import *
from datetime import datetime
from io import StringIO
import pandas as pd

def connect_to_s3():
    return boto3.resource(
        service_name='s3',
        region_name=AWS_DEFAULT_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

def post_to_s3(df, timestamp):
    year = timestamp.year
    month = timestamp.month
    day = timestamp.day
    s3_client = connect_to_s3()
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    dir = "{}/{}/{}/{}.csv".format(year, month, day, timestamp.time())
    s3_client.Object(AWS_BUCKET, dir).put(Body=csv_buffer.getvalue())