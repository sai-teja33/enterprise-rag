import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatToolbarModule } from '@angular/material/toolbar';

import { DocumentsApiService } from '../../core/services/documents-api.service';
import { TenantStateService } from '../../core/services/department-state.service';

import { DepartmentDocumentStatusResponse, DocumentStatusItem } from '../../core/models/documents';

import { UploadDocumentDialogComponent } from './upload-document-dialog.component';
import { PreviewDocumentDialogComponent } from './preview-document-dialog.component';
import { ChunksDialogComponent } from './chunks-dialog.component';

import { LoadingStateComponent } from '../../shared/components/loading-state/loading-state.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';

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
    MatSnackBarModule,
    MatTableModule,
    MatToolbarModule,
    MatProgressSpinnerModule,
    LoadingStateComponent,
    EmptyStateComponent,
    StatusBadgeComponent,
  ],
  templateUrl: './documents.component.html',
  styleUrl: './documents.component.scss',
})
export class DocumentsComponent implements OnInit {
  readonly documentsApi = inject(DocumentsApiService);
  readonly departmentState = inject(TenantStateService);

  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

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
    'actions',
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

        this.snackBar.open('Unable to load documents.', 'Dismiss', {
          duration: 4000,
        });
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
          width: '720px',
          data: response,
        });
      },
      error: () => {
        this.snackBar.open('Unable to preview document.', 'Dismiss', {
          duration: 4000,
        });
      },
    });
  }

  openChunks(document: DocumentStatusItem): void {
    this.documentsApi.getDocumentChunks(document.document_id).subscribe({
      next: (response) => {
        this.dialog.open(ChunksDialogComponent, {
          width: '780px',
          data: response,
        });
      },
      error: () => {
        this.snackBar.open('Unable to load document chunks.', 'Dismiss', {
          duration: 4000,
        });
      },
    });
  }

  reprocess(document: DocumentStatusItem): void {
    this.isLoading = true;

    this.documentsApi.reprocessDocument(document.document_id).subscribe({
      next: () => {
        this.snackBar.open('Document reprocessed successfully.', 'Dismiss', {
          duration: 4000,
        });

        this.loadStatus();
      },
      error: () => {
        this.isLoading = false;

        this.snackBar.open('Document reprocessing failed.', 'Dismiss', {
          duration: 4000,
        });
      },
    });
  }
}
