import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-stat-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="stat-card">
      <div class="stat-label">{{ label() }}</div>
      <div class="stat-value">{{ value() }}</div>
      @if (hint(); as hintText) {
        <div class="stat-hint">{{ hintText }}</div>
      }
    </div>
  `,
  styles: [
    `
      .stat-card {
        background: linear-gradient(135deg, #0f172a 0%, #1f3a5f 100%);
        color: white;
        border-radius: 16px;
        padding: 18px 20px;
        min-height: 116px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
      }
      .stat-label {
        font-size: 0.85rem;
        opacity: 0.8;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }
      .stat-value {
        font-size: 1.7rem;
        font-weight: 700;
      }
      .stat-hint {
        margin-top: 10px;
        font-size: 0.9rem;
        opacity: 0.8;
      }
    `,
  ],
})
export class StatCardComponent {
  readonly label = input.required<string>();
  readonly value = input.required<string | number>();
  readonly hint = input<string>();
}
