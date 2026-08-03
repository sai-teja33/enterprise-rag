import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ICellRendererAngularComp } from 'ag-grid-angular';
import { ICellRendererParams } from 'ag-grid-community';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { DocumentStatusItem } from '../../core/models/documents';

@Component({
  selector: 'app-document-actions-cell-renderer',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule],
  template: `
    <div class="action-buttons">
      <button mat-stroked-button class="table-action" (click)="onPreview()">
        <mat-icon>visibility</mat-icon>
        Preview
      </button>
      <button mat-flat-button color="primary" class="table-action" (click)="onReprocess()">
        <mat-icon>sync</mat-icon>
        Reprocess
      </button>
    </div>
  `,
  styles: [
    `
      .action-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
      .table-action {
        min-height: 34px;
        border-radius: 999px;
        padding: 0 12px;
      }
      .table-action mat-icon {
        margin-right: 6px;
        font-size: 16px;
        width: 16px;
        height: 16px;
      }
    `,
  ],
})
export class DocumentActionsCellRendererComponent implements ICellRendererAngularComp {
  private params!: ICellRendererParams & {
    context?: {
      onPreview?: (document: DocumentStatusItem) => void;
      onReprocess?: (document: DocumentStatusItem) => void;
    };
  };

  agInit(params: ICellRendererParams): void {
    this.params = params as typeof this.params;
  }

  refresh(): boolean {
    return true;
  }

  onPreview(): void {
    const document = this.params.data as DocumentStatusItem;
    this.params.context?.onPreview?.(document);
  }

  onReprocess(): void {
    const document = this.params.data as DocumentStatusItem;
    this.params.context?.onReprocess?.(document);
  }
}
