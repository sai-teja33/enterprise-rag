import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterOutlet } from '@angular/router';

import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatCardModule } from '@angular/material/card';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';

import { TenantSelectorComponent } from '../../shared/components/department-selector/tenant-selector.component';
import { TenantStateService } from '../../core/services/department-state.service';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    MatSidenavModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatListModule,
    MatCardModule,
    MatSnackBarModule,
    TenantSelectorComponent,
  ],
  templateUrl: './app-shell.component.html',
  styleUrl: './app-shell.component.scss',
})
export class AppShellComponent {
  readonly departmentState = inject(TenantStateService);

  private readonly router = inject(Router);

  readonly snackBar = inject(MatSnackBar);

  navItems = [
    {
      label: 'Dashboard',
      route: '/dashboard',
      icon: 'dashboard',
    },
    {
      label: 'Knowledge Base',
      route: '/documents',
      icon: 'folder',
    },
    {
      label: 'AI Assistant',
      route: '/query',
      icon: 'smart_toy',
    },
    {
      label: 'Evaluation',
      route: '/evaluation',
      icon: 'analytics',
    },
  ];

  navigate(route: string): void {
    this.router.navigateByUrl(route);
  }
}
