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
  private readonly baseUrl = `${environment.apiBaseUrl}/departments`;

  constructor(private readonly http: HttpClient) {}

  getDocumentStatus(departmentSlug: string): Observable<DepartmentDocumentStatusResponse> {
    return this.http.get<DepartmentDocumentStatusResponse>(
      `${this.baseUrl}/${departmentSlug}/documents/status`,
    );
  }

  uploadDocument(departmentSlug: string, payload: FormData): Observable<UploadDocumentResponse> {
    return this.http.post<UploadDocumentResponse>(
      `${this.baseUrl}/${departmentSlug}/documents/upload`,
      payload,
    );
  }

  previewDocument(departmentSlug: string, documentId: string): Observable<PreviewDocumentResponse> {
    return this.http.get<PreviewDocumentResponse>(
      `${this.baseUrl}/${departmentSlug}/documents/${documentId}/preview`,
    );
  }

  getDocumentChunks(
    departmentSlug: string,
    documentId: string,
  ): Observable<DocumentChunksResponse> {
    return this.http.get<DocumentChunksResponse>(
      `${this.baseUrl}/${departmentSlug}/documents/${documentId}/chunks`,
    );
  }

  reprocessDocument(
    departmentSlug: string,
    documentId: string,
  ): Observable<ReprocessDocumentResponse> {
    return this.http.post<ReprocessDocumentResponse>(
      `${this.baseUrl}/${departmentSlug}/documents/${documentId}/reprocess`,
      {},
    );
  }
}
