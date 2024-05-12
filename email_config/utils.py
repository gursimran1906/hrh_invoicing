import asyncio
import configparser
import datetime
import asyncio

from datetime import datetime, timezone, timedelta
import json
from pprint import pprint
import re
import math
import sys
import os
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
from configparser import SectionProxy
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
import httpx
from datetime import datetime, timedelta
import json
import logging
import base64


logging.basicConfig(filename='email_config/email_job.log', level=logging.ERROR)


def send_email(body, to_email, subject,pdf_content):
    setup_instance = Setup()
    print(body, to_email, subject)
    asyncio.run(setup_instance.send_email(body, to_email, subject,pdf_content))
    
    logging.info(f"Email sent to {to_email} with subject: {subject}")


def remove_log_file():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, "email_job.log")
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"{file_path} has been successfully removed on {datetime.now()}.")
    else:
        logging.warning(f"The file {file_path} does not exist.")


class Graph:
    settings: SectionProxy
    client_credential: ClientSecretCredential
    app_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        client_secret = self.settings['clientSecret']
        self.from_email = os.getenv('FROM_EMAIL')

        self.client_credential = ClientSecretCredential(
            tenant_id, client_id, client_secret)
        self.app_client = GraphServiceClient(self.client_credential)

    async def get_app_only_token(self):
        graph_scope = 'https://graph.microsoft.com/.default'
        access_token = await self.client_credential.get_token(graph_scope)
        return access_token.token

    async def send_email(self, body, to_email, subject, pdf_content):

        to_email = to_email
        

        send_mail_endpoint = f"https://graph.microsoft.com/v1.0/users/{
            self.from_email}/sendMail/"

        email_payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": to_email
                        }
                    }
                ],
                "from": {
                    "emailAddress": {
                        "address": f"{self.from_email}"
                    }
                }
            },
            "saveToSentItems": "false"
        }
        if pdf_content:
            email_payload["message"]["attachments"] = [{
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": "invoice.pdf",
                "contentBytes": base64.b64encode(pdf_content).decode("utf-8")
            }]
        headers = {
            'Authorization': f'Bearer {await self.get_app_only_token()}',
            'Content-Type': 'application/json'
        }

        # Send the request to send the email
        async with httpx.AsyncClient() as client:
            response = await client.post(send_mail_endpoint, data=json.dumps(email_payload), headers=headers)

            if response.status_code == 202:
                print(f"Email sent successfully to {to_email}")
                logging.info(f"Email sent successfully to {to_email}")
            else:
                print()
                logging.error(f"Error sending email to {to_email}: {response.status_code}, {response.text}")



class Setup:

    def __init__(self):

        load_dotenv()

        azure_client_id = os.getenv('AZURE_CLIENT_ID')
        azure_client_secret = os.getenv('AZURE_CLIENT_SECRET')
        azure_tenant_id = os.getenv('AZURE_TENANT_ID')
        azure_settings = {'clientId': azure_client_id,
                          'clientSecret': azure_client_secret, 'tenantId': azure_tenant_id}

        # Use self.graph consistently
        self.graph = Graph(azure_settings)

    async def display_access_token(self):
        # Use self.graph consistently
        token = await self.graph.get_app_only_token()
        print('App-only token:', token, '\n')

    async def send_email(self, body, to_email, subject, pdf_content):
        await self.graph.send_email(body, to_email, subject,pdf_content)



