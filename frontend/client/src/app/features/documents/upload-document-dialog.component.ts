import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { DocumentsApiService } from '../../core/services/documents-api.service';
import { TenantStateService } from '../../core/services/tenant-state.service';

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
    MatSnackBarModule,
  ],
  template: `
    <h2 mat-dialog-title>Upload Document</h2>
    <mat-dialog-content>
      <form [formGroup]="form" class="upload-form">
        <mat-form-field appearance="outline">
          <mat-label>Title</mat-label>
          <input matInput formControlName="title" />
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Document Type</mat-label>
          <input matInput formControlName="docType" />
        </mat-form-field>

        <input type="file" accept=".pdf,.docx" (change)="onFileSelected($event)" />
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-stroked-button (click)="cancel()">Cancel</button>
      <button
        mat-flat-button
        color="primary"
        [disabled]="form.invalid || isSubmitting"
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
      input[type='file'] {
        margin-top: 8px;
      }
    `,
  ],
})
export class UploadDocumentDialogComponent {
  private readonly fb = inject(FormBuilder);
  private readonly documentsApi = inject(DocumentsApiService);
  private readonly tenantState = inject(TenantStateService);
  private readonly dialogRef = inject(MatDialogRef<UploadDocumentDialogComponent>);
  private readonly snackBar = inject(MatSnackBar);

  form: FormGroup;
  isSubmitting = false;
  selectedFile: File | null = null;

  constructor() {
    this.form = this.fb.group({
      title: ['', Validators.required],
      docType: ['', Validators.required],
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile = input.files?.[0] ?? null;
  }

  cancel(): void {
    this.dialogRef.close();
  }

  submit(): void {
    if (this.form.invalid || !this.selectedFile) {
      this.snackBar.open('Please complete all fields and choose a PDF/DOCX file.', 'Dismiss', {
        duration: 4000,
      });
      return;
    }

    this.isSubmitting = true;
    const formData = new FormData();
    formData.append('title', this.form.value.title);
    formData.append('doc_type', this.form.value.docType);
    formData.append('file', this.selectedFile);

    this.documentsApi.uploadDocument(this.tenantState.getSelectedTenantSlug(), formData).subscribe({
      next: () => {
        this.isSubmitting = false;
        this.snackBar.open('Document uploaded successfully.', 'Dismiss', { duration: 4000 });
        this.dialogRef.close(true);
      },
      error: (error) => {
        this.isSubmitting = false;
        const message = error?.error?.detail ?? 'Upload failed.';
        this.snackBar.open(message, 'Dismiss', { duration: 5000 });
      },
    });
  }
}
