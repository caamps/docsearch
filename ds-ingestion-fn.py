import json
from urllib.parse import unquote
import boto3
import base64
import urllib3

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket = event["Records"][0]['s3']['bucket']['name']
    key = unquote(event["Records"][0]['s3']['object']['key'].replace('+', ' '), 'utf-8')
    
    s3object = s3.get_object(Bucket=bucket, Key=key)
    s3object_json = json.loads(s3object['Body'].read())
    
    os_auth = 'user:senha'
    
    authb64 = base64.b64encode(os_auth.encode()).decode()
    
    os_url = 'url.com/files/_doc'
    headers = {
        'Content-type': 'application/json',
        'Accept': 'text/plain',
        'Authorization': 'Basic {}'.format(authb64)
    }
    
    http = urllib3.PoolManager()
    request = http.request("POST", os_url, headers=headers, body=json.dumps(s3object_json).encode('utf-8'))
    
    print(request)
    
    return {
        'statusCode': 200,
    }
