import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MAT_SNACK_BAR_DATA, MatSnackBarRef } from '@angular/material/snack-bar';

export interface NotificationSnackbarData {
  message: string;
  variant: 'success' | 'error' | 'info';
}

@Component({
  selector: 'app-notification-snackbar',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule],
  template: `
    <div class="snackbar" [ngClass]="variantClass">
      <mat-icon class="snackbar__icon">{{ iconName }}</mat-icon>
      <span class="snackbar__message">{{ data.message }}</span>
      <button mat-button class="snackbar__action" (click)="dismiss()">Dismiss</button>
    </div>
  `,
  styleUrl: './notification-snackbar.component.scss',
})
export class NotificationSnackbarComponent {
  private readonly snackBarRef = inject(MatSnackBarRef<NotificationSnackbarComponent>);
  readonly data = inject<NotificationSnackbarData>(MAT_SNACK_BAR_DATA);

  get iconName(): string {
    switch (this.data.variant) {
      case 'error':
        return 'error';
      case 'info':
        return 'info';
      default:
        return 'check_circle';
    }
  }

  get variantClass(): string {
    return `snackbar--${this.data.variant}`;
  }

  dismiss(): void {
    this.snackBarRef.dismiss();
  }
}
