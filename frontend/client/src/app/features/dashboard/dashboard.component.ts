import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { RouterLink } from '@angular/router';

import { DocumentsApiService } from '../../core/services/documents-api.service';
import { TenantStateService } from '../../core/services/department-state.service';

import { DepartmentDocumentStatusResponse } from '../../core/models/documents';

import { StatCardComponent } from '../../shared/components/stat-card/stat-card.component';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';
import { LoadingStateComponent } from '../../shared/components/loading-state/loading-state.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    RouterLink,
    StatCardComponent,
    StatusBadgeComponent,
    LoadingStateComponent,
    EmptyStateComponent,
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
  readonly documentsApi = inject(DocumentsApiService);
  readonly departmentState = inject(TenantStateService);

  isLoading = false;

  statusResponse: DepartmentDocumentStatusResponse | null = null;

  displayedColumns = [
    'title',
    'doc_type',
    'file_name',
    'uploaded_at',
    'total_chunks',
    'embedded_chunks',
    'ready',
  ];

  ngOnInit(): void {
    this.loadStatus();
  }

  loadStatus(): void {
    this.isLoading = true;

    this.documentsApi.getDocumentStatus().subscribe({
      next: (response) => {
        this.statusResponse = response;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      },
    });
  }

  get readyDocumentsCount(): number {
    return this.statusResponse?.documents.filter((doc) => doc.ready_for_query).length ?? 0;
  }

  get totalChunks(): number {
    return this.statusResponse?.documents.reduce((sum, doc) => sum + doc.total_chunks, 0) ?? 0;
  }

  get embeddedChunks(): number {
    return this.statusResponse?.documents.reduce((sum, doc) => sum + doc.embedded_chunks, 0) ?? 0;
  }

  get statusBadgeVariant(): string {
    return 'ready';
  }
}
