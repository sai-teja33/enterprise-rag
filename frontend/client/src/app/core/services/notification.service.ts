import { Injectable, inject } from '@angular/core';
import { MatSnackBar, MatSnackBarConfig } from '@angular/material/snack-bar';
import { NotificationSnackbarComponent } from '../../shared/components/notification-snackbar/notification-snackbar.component';

@Injectable({
  providedIn: 'root',
})
export class NotificationService {
  private readonly snackBar = inject(MatSnackBar);

  private readonly config: MatSnackBarConfig = {
    duration: 4000,
    horizontalPosition: 'center',
    verticalPosition: 'bottom',
    panelClass: ['app-snackbar'],
  };

  success(message: string): void {
    this.open(message, 'success');
  }

  error(message: string): void {
    this.open(message, 'error');
  }

  info(message: string): void {
    this.open(message, 'info');
  }

  private open(message: string, variant: 'success' | 'error' | 'info'): void {
    this.snackBar.openFromComponent(NotificationSnackbarComponent, {
      ...this.config,
      data: { message, variant },
      panelClass: ['app-snackbar', `app-snackbar--${variant}`],
    });
  }
}
