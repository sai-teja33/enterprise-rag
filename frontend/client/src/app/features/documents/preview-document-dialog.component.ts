import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { PreviewDocumentResponse } from '../../core/models/documents';

@Component({
  selector: 'app-preview-document-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule, MatIconModule],
  template: `
    <div class="dialog-header" mat-dialog-title>
      <div>
        <h2>Document preview</h2>
        <p>{{ data.file_name }}</p>
      </div>
      <button mat-icon-button mat-dialog-close aria-label="Close preview">
        <mat-icon>close</mat-icon>
      </button>
    </div>

    <mat-dialog-content class="dialog-content">
      <div class="meta-grid">
        <div>
          <span class="meta-label">Title</span><strong>{{ data.title }}</strong>
        </div>
        <div>
          <span class="meta-label">Document type</span><strong>{{ data.doc_type }}</strong>
        </div>
        <div>
          <span class="meta-label">File name</span><strong>{{ data.file_name }}</strong>
        </div>
        <div>
          <span class="meta-label">LangChain docs</span
          ><strong>{{ data.num_langchain_docs }}</strong>
        </div>
        <div>
          <span class="meta-label">Text length</span><strong>{{ data.text_length }}</strong>
        </div>
      </div>
      <div class="preview-body">
        <pre>{{ data.text_preview }}</pre>
      </div>
    </mat-dialog-content>
  `,
  styles: [
    `
      .dialog-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
        padding-bottom: 8px;
      }
      .dialog-header h2 {
        margin: 0;
        font-size: 1.1rem;
      }
      .dialog-header p {
        margin: 2px 0 0;
        color: #64748b;
      }
      .dialog-content {
        display: grid;
        gap: 12px;
        padding-top: 4px;
      }
      .meta-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
      }
      .meta-grid > div {
        display: grid;
        gap: 2px;
        padding: 10px 12px;
        border-radius: 12px;
        background: #f8fafc;
      }
      .meta-label {
        color: #64748b;
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
      }
      .preview-body {
        max-height: min(60vh, 560px);
        overflow: auto;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        background: #f8fafc;
        padding: 14px;
      }
      pre {
        margin: 0;
        white-space: pre-wrap;
        font-size: 0.92rem;
        line-height: 1.6;
        color: #334155;
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
