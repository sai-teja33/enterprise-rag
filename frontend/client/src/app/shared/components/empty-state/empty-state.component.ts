import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="empty-state">
      <h3>{{ title() }}</h3>
      <p>{{ description() }}</p>
    </div>
  `,
  styles: [
    `
      .empty-state {
        border: 1px dashed #cbd5e1;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        color: #475569;
        background: #f8fafc;
      }
      h3 {
        margin: 0 0 8px;
        color: #0f172a;
      }
      p {
        margin: 0;
      }
    `,
  ],
})
export class EmptyStateComponent {
  readonly title = input.required<string>();
  readonly description = input.required<string>();
}
