import io
import logging

from fastapi import File, HTTPException, UploadFile
from googleapiclient.http import MediaIoBaseUpload
from sqlalchemy.orm import Session

from app.config.database import commit, create
from app.config.settings import Settings
from app.models.document import Document
from app.utils.google_drive import authenticate_google_drive

logger = logging.getLogger(__name__)


def get_or_create_folder(drive_service, folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = (
        drive_service.files()
        .list(q=query, spaces='drive', fields='files(id, name)')
        .execute()
    )
    folders = results.get('files', [])

    if folders:
        logger.info(f'Folder {folder_name} found with id {folders[0]["id"]}')
        print(f'Folder {folder_name} found with id {folders[0]["id"]}')
        return folders[0]['id']

    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    folder = (
        drive_service.files()
        .create(body=folder_metadata, fields='id')
        .execute()
    )

    permission = {
        'type': 'domain',
        'domain': Settings().GOOGLE_DOMAIN,
        'role': 'reader',
        'allowFileDiscovery': True,
    }
    drive_service.permissions().create(
        fileId=folder.get('id'), body=permission
    ).execute()

    print(f'Folder {folder_name} created with id {folder.get("id")}')
    logger.info(f'Folder {folder_name} created with id {folder.get("id")}')
    return folder.get('id')


class CreateDocumentUseCase:
    @staticmethod
    @commit
    def execute(db: Session, file: UploadFile = File(...)):
        try:
            contents = file.file.read()
            file_stream = io.BytesIO(contents)

            drive_service = authenticate_google_drive()

            folder = get_or_create_folder(
                drive_service, Settings().GOOGLE_FOLDER_NAME
            )

            file_metadata = {
                'name': file.filename,
                'parents': [folder],
            }

            media = MediaIoBaseUpload(
                file_stream, mimetype=file.content_type, resumable=True
            )
            uploaded_file = (
                drive_service.files()
                .create(body=file_metadata, media_body=media, fields='id')
                .execute()
            )

            file_id = uploaded_file['id']

            permission = {
                'type': 'domain',
                'role': 'reader',
                'domain': Settings().GOOGLE_DOMAIN,
                'allowFileDiscovery': True,
            }

            drive_service.permissions().create(
                fileId=file_id,
                body=permission,
            ).execute()

            drive_service.files().get(
                fileId=file_id, fields='webViewLink'
            ).execute()

            share_link = (
                drive_service.files()
                .get(fileId=file_id, fields='webViewLink')
                .execute()
            )
            logger.info(
                f'File {file.filename} uploaded with id {file_id}, link {share_link["webViewLink"]}'
            )

        except Exception as e:
            logger.error(f'Erro ao criar documento no Google Drive: {str(e)}')
            raise HTTPException(status_code=500, detail=str(e))

        # TODO: Adicionar o ID do usuário que fez o upload
        document = Document(
            name=file.filename,
            shared_link=share_link['webViewLink'],
            g_file_id=file_id,
            g_folder_id=folder,
            user_id=13,
        )
        document_db, error = create(db, document)

        if error:
            return None, error

        return document_db, None
