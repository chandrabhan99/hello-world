import os
import datetime
import uuid
from azure.storage.blob import generate_container_sas, BlobSasPermissions
from azure.storage.blob import BlobServiceClient

endpoint_suffix = "core.windows.net"
account_name = os.environ["storage-accountname"]
container_name = os.environ["storage-containername"]
account_key = os.environ["accountkey"]
connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};accountkey={account_key};EndpointSuffix={endpoint_suffix};"

def get_new_sas():
    start_time = datetime.datetime.now(datetime.timezone.utc)
    expiry_time = start_time + datetime.timedelta(minutes=2)
    
    sas_token = generate_container_sas(
        account_name=account_name,
        container_name=container_name,
        account_key=account_key,
        permission=BlobSasPermissions(create=True),
        expiry=expiry_time,
        start=start_time
    )

    return {
        "cv_key": str(uuid.uuid1()), 
        "sas_url": f"https://{account_name}.blob.core.windows.net/{container_name}?{sas_token}" 
    }

def get_blob(container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_content = blob_client.download_blob().readall()
    return blob_content