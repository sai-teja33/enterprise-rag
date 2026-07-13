import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-loading-state',
  standalone: true,
  imports: [CommonModule, MatProgressSpinnerModule],
  template: `
    <div class="loading-state">
      <mat-spinner diameter="36"></mat-spinner>
      <div>{{ message() }}</div>
    </div>
  `,
  styles: [
    `
      .loading-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        padding: 32px 16px;
        color: #475569;
      }
    `,
  ],
})
export class LoadingStateComponent {
  readonly message = input<string>('Loading…');
}
