import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { DocumentChunksResponse } from '../../core/models/documents';

@Component({
  selector: 'app-chunks-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule],
  template: `
    <h2 mat-dialog-title>Document Chunks</h2>
    <mat-dialog-content>
      <div class="summary">Total chunks: {{ data.total_chunks }}</div>
      <div class="chunk-list">
        @for (chunk of data.chunks; track chunk.id) {
          <div class="chunk-item">
            <div class="chunk-header">
              <strong>Chunk {{ chunk.chunk_index ?? '-' }}</strong>
              <span>Page {{ chunk.page_number ?? '-' }} • Size {{ chunk.chunk_size ?? '-' }}</span>
            </div>
            <p>{{ chunk.chunk_preview }}</p>
          </div>
        }
      </div>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-flat-button color="primary" mat-dialog-close>Close</button>
    </mat-dialog-actions>
  `,
  styles: [
    `
      .summary {
        margin-bottom: 12px;
        color: #334155;
        font-weight: 600;
      }
      .chunk-list {
        display: grid;
        gap: 10px;
        max-height: 420px;
        overflow: auto;
      }
      .chunk-item {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px;
        background: #f8fafc;
      }
      .chunk-header {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 8px;
        flex-wrap: wrap;
      }
      p {
        margin: 0;
        color: #475569;
        line-height: 1.5;
      }
    `,
  ],
})
export class ChunksDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public readonly data: DocumentChunksResponse) {}
}
