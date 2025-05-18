import asyncio
import uuid
from abc import ABC, abstractmethod
from io import BytesIO
from typing import List

import PyPDF2
from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.database import get_chroma_collection
from app.config.settings import Settings


class DocumentProccessStrategy(ABC):
    def __init__(self) -> None:
        self.processing_jobs = {}

    def get_job_status(self, job_id: str):
        if job_id not in self.processing_jobs:
            return {'status': 'Not Found'}
        return self.processing_jobs[job_id]

    @abstractmethod
    async def execute(self, file: UploadFile) -> dict: ...


class DocumentProccessFactory:
    @staticmethod
    def get_strategy(file: UploadFile) -> DocumentProccessStrategy:
        assert file.filename
        if file.filename.lower().endswith('.pdf'):
            return PDFStrategy(file)
        else:
            raise ValueError('Usupported Document Type')


class PDFStrategy(DocumentProccessStrategy):
    def __init__(self, file: UploadFile):
        self.file = file

    async def execute(self, file: UploadFile) -> dict:
        chunk_size = Settings().RAG_CHUNK_SIZE
        chunk_overlap = Settings().RAG_CHUNK_OVERLAP

        job_id = str(uuid.uuid4())
        self.processing_jobs[job_id] = {
            'status': 'processing',
            'progress': 0,
            'file': file.filename,
        }

        try:
            text = self._extract_text_from_pdf(file)
            self.processing_jobs[job_id]['progress'] = 30

            chunks = self._split_text(text, chunk_size, chunk_overlap)
            self.processing_jobs[job_id]['progress'] = 60

            metadata = []
            ids = []

            for i, chunk in enumerate(chunks):
                chunk_id = uuid.uuid4()
                ids.append(chunk_id)
                metadata.append({
                    'source': file.filename(),  # type: ignore
                    'chunk': i,
                    'chunk_size': len(chunk),
                })

            batch_size = Settings().BATCH_SIZE
            for i in range(0, len(chunks), batch_size):
                end_idx = min(i + batch_size, len(chunks))

                collection = get_chroma_collection()
                collection.add(
                    documents=chunks[i:end_idx],
                    ids=ids[i:end_idx],
                    metadatas=metadata[i:end_idx],
                )

                progress = 60 + int((end_idx / len(chunks)) * 40)
                self.processing_jobs[job_id]['progress'] = min(progress, 99)
                await asyncio.sleep(0.1)

            self.processing_jobs[job_id]['status'] = 'completed'
            self.processing_jobs[job_id]['progress'] = 100

            return {
                'job_id': job_id,
                'status': 'completed',
                'collection_name': Settings().CHROMA_COLLECTION,
                'chunks_count': len(chunks),
            }

        except Exception as e:
            self.processing_jobs[job_id]['status'] = 'failed'
            self.processing_jobs[job_id]['error'] = str(e)
            raise

    def _extract_text_from_pdf(self, file: UploadFile):
        file_content = file.file.read()
        text = ''
        with BytesIO(file_content) as file_obj:
            reader = PyPDF2.PdfReader(file_obj)
            for page in reader.pages:
                text += page.extractText() + '\n'

        file.file.seek(0)

        return text

    def _split_text(
        self, text: str, chunk_size: int, chunk_overlap: int
    ) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

        return splitter.split_text(text)
