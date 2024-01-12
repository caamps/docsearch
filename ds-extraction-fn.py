import json
import boto3
from urllib.parse import unquote
import re

client = boto3.client('textract')
s3 = boto3.client('s3')

def sns_handler(event):
    message = json.loads(event["Records"][0]['Sns']['Message'])
    JobId = message["JobId"]
    response = client.get_document_text_detection(JobId=JobId)
    bucket = message['DocumentLocation']['S3Bucket']
    key = unquote(message['DocumentLocation']['S3ObjectName'].replace('+', ' '), 'utf-8')
    return {'response': response, 'bucket': bucket, 'key': key}

def s3_handler(event):
    bucket = event["Records"][0]['s3']['bucket']['name']
    key = unquote(event["Records"][0]['s3']['object']['key'].replace('+', ' '), 'utf-8')
    file_extension = key.split('.')[-1].lower()
    
    response = 'requesting'
    if file_extension == 'pdf':
        request = client.start_document_text_detection(
                DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': key}},
                NotificationChannel={'RoleArn': 'arn_da_role', 'SNSTopicArn': 'arn_do_sns'})
    else:
        image = {'S3Object': {'Bucket': bucket, 'Name': key}}
        response = client.detect_document_text(Document=image)
    return {'response': response, 'bucket': bucket, 'key': key}

def upload(data):
    text = ''
    textract_response = data['response']
    bucket = data['bucket']
    key = data['key']
    print(textract_response['Blocks'])
    for obj in textract_response['Blocks']:
        if 'Text' in obj:
            if (obj['BlockType'] == 'WORD'):
                text += obj['Text'] + ' '
    file_name = re.sub(r'[^\w]', '', (key.rsplit('.', 1)[0]).lower()) + '.json'
    data = {
        'file': key,
        'text': text
    }
        
    json_data = json.dumps(data, indent = 2, ensure_ascii=False)
        
    s3.put_object(Body=json_data, Bucket='ds-output-bucket', Key=file_name)
    
    

def lambda_handler(event, context):
    # TODO implement
    
    textract_response = ''
    data = {}
    
    if('EventSource' in event['Records'][0]):
        data = sns_handler(event)
        textract_response = data['response']
    else:
        data = s3_handler(event)
        textract_response = data['response']
    
    if textract_response != 'requesting':
        upload(data)
        
    
    return {
        'statusCode': 200,
    }
