import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { DocumentsApiService } from '../../core/services/documents-api.service';
import { NotificationService } from '../../core/services/notification.service';

@Component({
  selector: 'app-upload-document-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatProgressBarModule,
  ],
  template: `
    <h2 mat-dialog-title>Upload document</h2>
    <mat-dialog-content>
      <form [formGroup]="form" class="upload-form">
        <mat-form-field appearance="outline">
          <mat-label>Title</mat-label>
          <input matInput formControlName="title" />
        </mat-form-field>

        <div
          class="dropzone"
          [class.dropzone--active]="isDragging"
          (dragover)="onDragOver($event)"
          (dragleave)="onDragLeave($event)"
          (drop)="onDrop($event)"
          (click)="fileInput.click()"
        >
          <mat-icon>upload_file</mat-icon>
          <div class="dropzone__copy">
            <strong>Drop a PDF or DOCX here</strong>
            <span>or browse from your device</span>
          </div>
          <input
            #fileInput
            type="file"
            accept=".pdf,.docx"
            hidden
            (change)="onFileSelected($event)"
          />
        </div>

        @if (selectedFile) {
          <div class="file-card">
            <div>
              <strong>{{ selectedFile.name }}</strong>
              <div class="file-meta">{{ formatFileSize(selectedFile.size) }}</div>
            </div>
            <button mat-icon-button type="button" (click)="clearSelection()">
              <mat-icon>close</mat-icon>
            </button>
          </div>
        }

        @if (isSubmitting) {
          <div class="progress-block">
            <div class="progress-label">Uploading…</div>
            <mat-progress-bar mode="determinate" [value]="uploadProgress"></mat-progress-bar>
          </div>
        }
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-stroked-button type="button" (click)="cancel()">Cancel</button>
      <button
        mat-flat-button
        color="primary"
        type="button"
        [disabled]="form.invalid || isSubmitting || !selectedFile"
        (click)="submit()"
      >
        {{ isSubmitting ? 'Uploading…' : 'Upload' }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [
    `
      .upload-form {
        display: grid;
        gap: 12px;
        min-width: 320px;
      }
      .dropzone {
        display: grid;
        place-items: center;
        gap: 8px;
        padding: 24px;
        border: 1.5px dashed #cbd5e1;
        border-radius: 14px;
        background: #f8fafc;
        color: #475569;
        cursor: pointer;
      }
      .dropzone--active {
        border-color: #2563eb;
        background: #eff6ff;
      }
      .dropzone__copy {
        display: grid;
        text-align: center;
      }
      .file-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        padding: 10px 12px;
        border-radius: 12px;
        background: #eff6ff;
      }
      .file-meta {
        color: #64748b;
        font-size: 0.85rem;
      }
      .progress-block {
        display: grid;
        gap: 6px;
      }
      .progress-label {
        color: #1d4ed8;
        font-weight: 600;
      }
    `,
  ],
})
export class UploadDocumentDialogComponent {
  private readonly fb = inject(FormBuilder);
  private readonly documentsApi = inject(DocumentsApiService);
  private readonly dialogRef = inject(MatDialogRef<UploadDocumentDialogComponent>);
  private readonly notificationService = inject(NotificationService);

  form: FormGroup;
  isSubmitting = false;
  isDragging = false;
  selectedFile: File | null = null;
  uploadProgress = 0;

  constructor() {
    this.form = this.fb.group({
      title: ['', Validators.required],
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile = input.files?.[0] ?? null;
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = false;
    const file = event.dataTransfer?.files?.[0];
    this.selectedFile = file ?? null;
  }

  clearSelection(): void {
    this.selectedFile = null;
  }

  formatFileSize(size: number): string {
    if (!size) {
      return '0 B';
    }

    const units = ['B', 'KB', 'MB'];
    const exponent = Math.min(Math.floor(Math.log(size) / Math.log(1024)), units.length - 1);
    const value = size / 1024 ** exponent;

    return `${value.toFixed(exponent === 0 ? 0 : 1)} ${units[exponent]}`;
  }

  cancel(): void {
    this.dialogRef.close();
  }

  submit(): void {
    if (this.form.invalid || !this.selectedFile) {
      this.notificationService.error('Please complete all fields and choose a PDF or DOCX file.');
      return;
    }

    this.isSubmitting = true;
    this.uploadProgress = 12;

    const progressTimer = window.setInterval(() => {
      this.uploadProgress = Math.min(this.uploadProgress + 12, 90);
    }, 220);

    const formData = new FormData();
    formData.append('title', this.form.value.title);
    formData.append('file', this.selectedFile);

    this.documentsApi.uploadDocument(formData).subscribe({
      next: () => {
        clearInterval(progressTimer);
        this.uploadProgress = 100;
        this.isSubmitting = false;
        this.notificationService.success('Document uploaded successfully.');
        this.dialogRef.close(true);
      },
      error: (error) => {
        clearInterval(progressTimer);
        this.isSubmitting = false;
        const message = error?.error?.detail ?? 'Upload failed.';
        this.notificationService.error(message);
      },
    });
  }
}
