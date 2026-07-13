import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-status-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="status-badge" [ngClass]="variant()">
      {{ label() }}
    </span>
  `,
  styles: [
    `
      .status-badge {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 4px 10px;
        font-size: 0.8rem;
        font-weight: 600;
      }
      .ready {
        background: #dcfce7;
        color: #166534;
      }
      .pending {
        background: #fef3c7;
        color: #92400e;
      }
      .not-processed {
        background: #e2e8f0;
        color: #334155;
      }
      .answer {
        background: #dbeafe;
        color: #1d4ed8;
      }
      .not-found {
        background: #fee2e2;
        color: #b91c1c;
      }
      .partial {
        background: #fef3c7;
        color: #92400e;
      }
      .direct {
        background: #dcfce7;
        color: #166534;
      }
      .scoped {
        background: #ede9fe;
        color: #6d28d9;
      }
    `,
  ],
})
export class StatusBadgeComponent {
  readonly label = input.required<string>();
  readonly variant = input<string>('default');
}
