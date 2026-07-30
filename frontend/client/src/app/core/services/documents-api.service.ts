import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  DepartmentDocumentStatusResponse,
  DocumentChunksResponse,
  PreviewDocumentResponse,
  ReprocessDocumentResponse,
  UploadDocumentResponse,
} from '../models/documents';

@Injectable({
  providedIn: 'root',
})
export class DocumentsApiService {
  private readonly baseUrl = `${environment.apiBaseUrl}/documents`;

  constructor(private readonly http: HttpClient) {}

  getDocumentStatus(): Observable<DepartmentDocumentStatusResponse> {
    return this.http.get<DepartmentDocumentStatusResponse>(`${this.baseUrl}/status`);
  }

  uploadDocument(payload: FormData): Observable<UploadDocumentResponse> {
    return this.http.post<UploadDocumentResponse>(`${this.baseUrl}/upload`, payload);
  }

  previewDocument(documentId: string): Observable<PreviewDocumentResponse> {
    return this.http.get<PreviewDocumentResponse>(`${this.baseUrl}/${documentId}/preview`);
  }

  getDocumentChunks(documentId: string): Observable<DocumentChunksResponse> {
    return this.http.get<DocumentChunksResponse>(`${this.baseUrl}/${documentId}/chunks`);
  }

  reprocessDocument(documentId: string): Observable<ReprocessDocumentResponse> {
    return this.http.post<ReprocessDocumentResponse>(`${this.baseUrl}/${documentId}/reprocess`, {});
  }
}
