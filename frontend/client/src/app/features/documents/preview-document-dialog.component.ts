import { Component, Inject, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { PreviewDocumentResponse } from '../../core/models/documents';

@Component({
  selector: 'app-preview-document-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule],
  template: `
    <h2 mat-dialog-title>Document Preview</h2>
    <mat-dialog-content>
      <div class="meta-grid">
        <div><strong>Title:</strong> {{ data.title }}</div>
        <div><strong>Doc Type:</strong> {{ data.doc_type }}</div>
        <div><strong>File:</strong> {{ data.file_name }}</div>
        <div><strong>LangChain Docs:</strong> {{ data.num_langchain_docs }}</div>
        <div><strong>Text Length:</strong> {{ data.text_length }}</div>
      </div>
      <pre>{{ data.text_preview }}</pre>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-flat-button color="primary" mat-dialog-close>Close</button>
    </mat-dialog-actions>
  `,
  styles: [
    `
      .meta-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px;
        margin-bottom: 16px;
      }
      pre {
        white-space: pre-wrap;
        font-size: 0.9rem;
        line-height: 1.5;
        max-height: 360px;
        overflow: auto;
        background: #f8fafc;
        padding: 12px;
        border-radius: 8px;
      }
      @media (max-width: 700px) {
        .meta-grid {
          grid-template-columns: 1fr;
        }
      }
    `,
  ],
})
export class PreviewDocumentDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public readonly data: PreviewDocumentResponse) {}
}
