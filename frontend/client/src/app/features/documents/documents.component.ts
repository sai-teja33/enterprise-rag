import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { AgGridAngular } from 'ag-grid-angular';
import {
  AllCommunityModule,
  ColDef,
  GridOptions,
  ModuleRegistry,
  themeQuartz,
} from 'ag-grid-community';

import { DocumentsApiService } from '../../core/services/documents-api.service';
import { TenantStateService } from '../../core/services/department-state.service';
import { NotificationService } from '../../core/services/notification.service';

import { DepartmentDocumentStatusResponse, DocumentStatusItem } from '../../core/models/documents';

import { UploadDocumentDialogComponent } from './upload-document-dialog.component';
import { PreviewDocumentDialogComponent } from './preview-document-dialog.component';

import { LoadingStateComponent } from '../../shared/components/loading-state/loading-state.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { DocumentActionsCellRendererComponent } from './document-actions-cell-renderer.component';
import { DocumentStatusCellRendererComponent } from './document-status-cell-renderer.component';

ModuleRegistry.registerModules([AllCommunityModule]);

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatDialogModule,
    MatProgressSpinnerModule,
    AgGridAngular,
    LoadingStateComponent,
    EmptyStateComponent,
  ],
  templateUrl: './documents.component.html',
  styleUrl: './documents.component.scss',
})
export class DocumentsComponent implements OnInit {
  readonly documentsApi = inject(DocumentsApiService);
  readonly departmentState = inject(TenantStateService);
  private readonly notificationService = inject(NotificationService);
  private readonly dialog = inject(MatDialog);

  isLoading = false;
  statusResponse: DepartmentDocumentStatusResponse | null = null;
  documents: DocumentStatusItem[] = [];

  readonly theme = themeQuartz;

  readonly defaultColDef: ColDef = {
    sortable: true,
    filter: true,
    resizable: true,
    flex: 1,
  };

  readonly gridOptions: GridOptions = {
    pagination: true,
    paginationPageSize: 12,
    domLayout: 'autoHeight',
    suppressClickEdit: true,
    context: {
      onPreview: (document: DocumentStatusItem) => this.openPreview(document),
      onReprocess: (document: DocumentStatusItem) => this.reprocess(document),
    },
  };

  readonly columnDefs: ColDef[] = [
    { headerName: 'Title', field: 'title', minWidth: 200, flex: 1.2 },
    { headerName: 'Document Type', field: 'doc_type', minWidth: 140 },
    { headerName: 'File Name', field: 'file_name', minWidth: 180 },
    {
      headerName: 'Uploaded',
      field: 'uploaded_at',
      minWidth: 160,
      valueFormatter: (params) => (params.value ? new Date(params.value).toLocaleString() : '-'),
    },
    { headerName: 'Chunks', field: 'total_chunks', maxWidth: 100 },
    { headerName: 'Embedded', field: 'embedded_chunks', maxWidth: 100 },
    {
      headerName: 'Status',
      field: 'ready_for_query',
      minWidth: 120,
      maxWidth: 140,
      cellRenderer: DocumentStatusCellRendererComponent,
      cellRendererParams: {
        variantMap: {
          ready: 'ready',
          pending: 'pending',
          notProcessed: 'not-processed',
        },
      },
    },
    {
      headerName: 'Actions',
      minWidth: 200,
      maxWidth: 220,
      cellRenderer: DocumentActionsCellRendererComponent,
    },
  ];

  ngOnInit(): void {
    this.loadStatus();
  }

  loadStatus(): void {
    this.isLoading = true;

    this.documentsApi.getDocumentStatus().subscribe({
      next: (response) => {
        this.statusResponse = response;
        this.documents = response.documents;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.notificationService.error('Unable to load documents.');
      },
    });
  }

  openUploadDialog(): void {
    const dialogRef = this.dialog.open(UploadDocumentDialogComponent, {
      width: '560px',
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadStatus();
      }
    });
  }

  openPreview(document: DocumentStatusItem): void {
    this.documentsApi.previewDocument(document.document_id).subscribe({
      next: (response) => {
        this.dialog.open(PreviewDocumentDialogComponent, {
          width: '760px',
          maxWidth: '94vw',
          data: response,
        });
      },
      error: () => {
        this.notificationService.error('Unable to preview document.');
      },
    });
  }

  reprocess(document: DocumentStatusItem): void {
    this.isLoading = true;

    this.documentsApi.reprocessDocument(document.document_id).subscribe({
      next: () => {
        this.notificationService.success('Document reprocessed successfully.');
        this.loadStatus();
      },
      error: () => {
        this.isLoading = false;
        this.notificationService.error('Document reprocessing failed.');
      },
    });
  }
}
