import os
import sys
import json
from googleapiclient import discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

  
def override_where():
    """ overrides certifi.core.where to return actual location of cacert.pem"""
    # change this to match the location of cacert.pem
    return os.path.abspath("cacert.pem")


# is the program compiled?
if hasattr(sys, "frozen"):
    import certifi.core

    os.environ["REQUESTS_CA_BUNDLE"] = override_where()
    certifi.core.where = override_where

    # delay importing until after where() has been replaced
    import requests.utils
    import requests.adapters
    # replace these variables in case these modules were
    # imported before we replaced certifi.core.where
    requests.utils.DEFAULT_CA_BUNDLE_PATH = override_where()
    requests.adapters.DEFAULT_CA_BUNDLE_PATH = override_where()

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = 'your client_secrets'
# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly', "https://www.googleapis.com/auth/youtube.force-ssl"]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
credentials=None
if os.path.exists('youtube_data_token_brand.pickle'):
    print('Loading Credentials From File...')
    with open('youtube_data_token_brand.pickle', 'rb') as token:
        credentials = pickle.load(token)

# If there are no valid credentials available, then either refresh the token or log in.
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print('Refreshing Access Token...')
        credentials.refresh(Request())
    else:
        print('Fetching New Tokens...')
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',
            scopes=[
                'https://www.googleapis.com/auth/youtube.readonly', "https://www.googleapis.com/auth/youtube.force-ssl"
            ]
        )

        flow.run_local_server(port=8080, prompt='consent',
                              authorization_prompt_message='')
        credentials = flow.credentials

        # Save the credentials for the next run
        with open('youtube_data_token_brand.pickle', 'wb') as f:
            print('Saving Credentials for Future Use...')
            pickle.dump(credentials, f)


# Authorize the request and store authorization credentials.
def get_authenticated_service():



    with open("rest.json", encoding="utf-8") as f:
        service = json.load(f)

    global credentials
    yt = discovery.build_from_document(service,credentials = credentials)

    return yt

# Retrieve a list of broadcasts with the specified status.

def list_broadcasts(youtube = get_authenticated_service(), broadcast_status="all"):
  print ('Broadcasts with status "%s":' % broadcast_status)

  list_broadcasts_request = youtube.liveBroadcasts().list(
    broadcastStatus=broadcast_status,
    part='id,snippet',
    maxResults=50
  )

  while list_broadcasts_request:
    list_broadcasts_response = list_broadcasts_request.execute()
    
    for broadcast in list_broadcasts_response.get('items', []):
      print ('%s (%s)' % (broadcast['snippet']['title'], broadcast['id']))
      try:
        request = youtube.videos().delete(id=broadcast['id'])
      except Exception:
        continue
      request.execute()
      print(f"{broadcast['snippet']['title']} silindi")
    list_broadcasts_request = youtube.liveBroadcasts().list_next(
      list_broadcasts_request, list_broadcasts_response)



try:
    list_broadcasts()
    print("All deleted")
except Exception as e:
    print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
    input()
