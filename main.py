from flask import Flask, request, jsonify, redirect, session, url_for
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import google.auth

app = Flask(__name__)
app.secret_key = 'AIzaSyCRBfdXfpkBwiTAvJlrVcCBNEa0wAJYMhI'  # Set a secret key for session management

# Google OAuth 2.0 Client Configuration
# Replace with your client_id.json file path
CLIENT_SECRETS_FILE = "client_id.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

@app.route('/')
def index():
    # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow steps
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    # Store the state in session for later use
    session['state'] = state

    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can be verified in the authorization server response
    state = session['state']

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session
    # Credentials are available in flow.credentials
    session['credentials'] = {
        'token': flow.credentials.token,
        'refresh_token': flow.credentials.refresh_token,
        'token_uri': flow.credentials.token_uri,
        'client_id': flow.credentials.client_id,
        'client_secret': flow.credentials.client_secret,
        'scopes': flow.credentials.scopes
    }

    return redirect(url_for('test_api'))

@app.route('/files/<fileId>', methods=['GET'])
def get_file(fileId):
    if 'credentials' not in session:
        return redirect('authorize')

    # Load credentials from the session
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])

    try:
        # Build the Google Drive service
        service = build('drive', 'v3', credentials=credentials)

        # Call the Drive API
        file = service.files().get(fileId=fileId).execute()

        return jsonify(file)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
