import hashlib, hmac, datetime, requests, json, os
from dotenv import load_dotenv

load_dotenv()

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def get_signature_key(key, date_stamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

def signed_request(method, url, payload):
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION')
    service = 'bedrock'
    host = url.split('//')[1].split('/')[0]

    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')

    canonical_uri = '/' + url.split('//')[1].split('/', 1)[1]
    payload_hash = hashlib.sha256(json.dumps(payload).encode('utf-8')).hexdigest()
    canonical_headers = f'content-type:application/json\nhost:{host}\nx-amz-date:{amz_date}\n'
    signed_headers = 'content-type;host;x-amz-date'
    canonical_request = f'{method}\n{canonical_uri}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}'

    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f'{datestamp}/{region}/{service}/aws4_request'
    string_to_sign = f'{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()}'

    signing_key = get_signature_key(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    headers = {
        'Content-Type': 'application/json',
        'X-Amz-Date': amz_date,
        'Authorization': f'{algorithm} Credential={access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}'
    }
    return requests.post(url, json=payload, headers=headers)