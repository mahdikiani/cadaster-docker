import io
import logging
import os

import boto3
import dotenv
import requests
from botocore.exceptions import ClientError
from singleton import Singleton


class S3(metaclass=Singleton):
    def __init__(self) -> None:
        dotenv.load_dotenv()

        host = os.getenv("S3_HOST")
        access_key = os.getenv("S3_ACCESS_KEY")
        secret_key = os.getenv("S3_SECRET_KEY")
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.client = boto3.client(
            "s3",
            endpoint_url=host,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def list_files_and_dirs(self):
        files = []
        dirs = []
        continuation_token = None

        while True:
            if continuation_token:
                response = self.client.list_objects_v2(
                    Bucket=self.bucket_name, ContinuationToken=continuation_token
                )
            else:
                response = self.client.list_objects_v2(Bucket=self.bucket_name)

            if "Contents" in response:
                files.extend([obj["Key"] for obj in response["Contents"]])

            if "CommonPrefixes" in response:
                dirs.extend([prefix["Prefix"] for prefix in response["CommonPrefixes"]])

            if not response.get("IsTruncated"):
                break

            continuation_token = response.get("NextContinuationToken")

        return files, dirs

    def create_directory(self, directory_path):
        """Create a directory in the S3 bucket.

        :param client: S3 Client
        :param bucket: Bucket to create the directory in
        :param directory_path: Directory path in S3 bucket
        """
        self.client.put_object(Bucket=self.bucket_name, Key=f"{directory_path}/")

    def upload_url(self, url, object_name=None, proxies=None):
        """Upload a file to an S3 bucket

        :param client: S3 Client
        :param url: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        response = requests.get(url, proxies=proxies, timeout=60, verify=False)
        response.raise_for_status()

        if object_name is None:
            object_name = url.split("/")[-1]  # Extract the file name from the URL
        # check if object_name has a directory path
        if "/" in object_name:
            directory_path = "/".join(object_name.split("/")[:-1])
            self.create_directory(directory_path)

        try:
            file_obj = io.BytesIO(response.content)
            res = self.client.upload_fileobj(file_obj, self.bucket_name, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True


def main():
    try:
        s3 = S3()
        url = "https://smid.bot.inbeet.tech/ffc738de-9511-4397-b9a2-dc40c08ee41c.png"
        directory_path = "z/key"
        object_key = f"{directory_path}/img.png"

        s3.upload(url, object_key)
    except Exception as exc:
        logging.info(exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
