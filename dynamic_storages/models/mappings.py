from storages.backends import apache_libcloud, azure_storage, dropbox, ftp, gcloud, s3boto3, sftpstorage

LAST_STATUS_CHOICES = [["v", "Valid"], ["e", "Error"], ["u", "Unknown"]]
STORAGE_PROVIDER_MAP = {
    "libcloud": {"class": apache_libcloud.LibCloudStorage, "name": "Apache LibCloud"},
    "azure": {"class": azure_storage.AzureStorage, "name": "Azure Blob Storage"},
    "dropbox": {"class": dropbox.DropBoxStorage, "name": "Dropbox"},
    "ftp": {"class": ftp.FTPStorage, "name": "FTP"},
    "gcloud": {"class": gcloud.GoogleCloudStorage, "name": "Google Cloud Storage"},
    "s3boto3": {"class": s3boto3.S3Boto3Storage, "name": "S3/Boto3"},
    "do": {"class": s3boto3.S3Boto3Storage, "name": "Digital Ocean (boto3)"},
    "sftp": {"class": sftpstorage.SFTPStorage, "name": "SFTP"},
    "default": {},
}
