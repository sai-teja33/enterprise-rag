import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { QueryRequest, QueryResponse } from '../models/query';

@Injectable({
  providedIn: 'root',
})
export class QueryApiService {
  private readonly baseUrl = `${environment.apiBaseUrl}/query`;

  constructor(private readonly http: HttpClient) {}

  askQuestion(payload: QueryRequest): Observable<QueryResponse> {
    return this.http.post<QueryResponse>(`${this.baseUrl}/ask`, payload);
  }
}
