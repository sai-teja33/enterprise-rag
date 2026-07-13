import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  DocumentChunksResponse,
  PreviewDocumentResponse,
  ReprocessDocumentResponse,
  TenantDocumentStatusResponse,
  UploadDocumentResponse,
} from '../models/documents';

@Injectable({ providedIn: 'root' })
export class DocumentsApiService {
  private readonly baseUrl = `${environment.apiBaseUrl}/tenants`;

  constructor(private readonly http: HttpClient) {}

  getDocumentStatus(tenantSlug: string): Observable<TenantDocumentStatusResponse> {
    return this.http.get<TenantDocumentStatusResponse>(
      `${this.baseUrl}/${tenantSlug}/documents/status`,
    );
  }

  uploadDocument(tenantSlug: string, payload: FormData): Observable<UploadDocumentResponse> {
    return this.http.post<UploadDocumentResponse>(
      `${this.baseUrl}/${tenantSlug}/documents/upload`,
      payload,
    );
  }

  previewDocument(tenantSlug: string, documentId: string): Observable<PreviewDocumentResponse> {
    return this.http.get<PreviewDocumentResponse>(
      `${this.baseUrl}/${tenantSlug}/documents/${documentId}/preview`,
    );
  }

  getDocumentChunks(tenantSlug: string, documentId: string): Observable<DocumentChunksResponse> {
    return this.http.get<DocumentChunksResponse>(
      `${this.baseUrl}/${tenantSlug}/documents/${documentId}/chunks`,
    );
  }

  reprocessDocument(tenantSlug: string, documentId: string): Observable<ReprocessDocumentResponse> {
    return this.http.post<ReprocessDocumentResponse>(
      `${this.baseUrl}/${tenantSlug}/documents/${documentId}/reprocess`,
      {},
    );
  }
}
