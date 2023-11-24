from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from google_auth_oauthlib.flow import InstalledAppFlowid
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os

app = FastAPI()

# 这是您的OAuth 2.0客户端配置文件路径
CLIENT_SECRETS_FILE = 'client_id.json'

# 定义所需的API权限范围
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# 请求模型
class FolderContentRequest(BaseModel):
    folder_id: str

def get_google_drive_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build('drive', 'v3', credentials=credentials)

@app.post("/get-folder-content/")
def get_folder_content(request: FolderContentRequest, service=Depends(get_google_drive_service)):
    try:
        # 在这里使用service对象调用Google Drive API
        folder_id = request.folder_id
        # 示例: 列出文件夹中的文件
        response = service.files().list(q=f"'{folder_id}' in parents").execute()
        return response.get('files', [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

