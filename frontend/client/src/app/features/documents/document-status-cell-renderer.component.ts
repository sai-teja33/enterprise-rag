import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ICellRendererAngularComp } from 'ag-grid-angular';
import { ICellRendererParams } from 'ag-grid-community';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';

@Component({
  selector: 'app-document-status-cell-renderer',
  standalone: true,
  imports: [CommonModule, StatusBadgeComponent],
  template: `
    @if (value) {
      <app-status-badge label="Ready" variant="ready"></app-status-badge>
    } @else if (totalChunks > 0) {
      <app-status-badge label="Pending" variant="pending"></app-status-badge>
    } @else {
      <app-status-badge label="Not Processed" variant="not-processed"></app-status-badge>
    }
  `,
})
export class DocumentStatusCellRendererComponent implements ICellRendererAngularComp {
  value = false;
  totalChunks = 0;

  agInit(params: ICellRendererParams): void {
    this.value = Boolean(params.value);
    this.totalChunks = Number((params.data as { total_chunks?: number })?.total_chunks ?? 0);
  }

  refresh(): boolean {
    return true;
  }
}
