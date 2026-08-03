import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatSnackBarModule } from '@angular/material/snack-bar';

import { TenantSelectorComponent } from '../../shared/components/department-selector/tenant-selector.component';
import { TenantStateService } from '../../core/services/department-state.service';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatSidenavModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatListModule,
    MatSnackBarModule,
    TenantSelectorComponent,
  ],
  templateUrl: './app-shell.component.html',
  styleUrl: './app-shell.component.scss',
})
export class AppShellComponent {
  readonly departmentState = inject(TenantStateService);
  readonly isSidenavOpen = signal(true);

  private readonly router = inject(Router);

  readonly navItems = [
    {
      label: 'Dashboard',
      route: '/dashboard',
      icon: 'dashboard',
    },
    {
      label: 'Chat',
      route: '/chat',
      icon: 'chat',
    },
    {
      label: 'Documents',
      route: '/documents',
      icon: 'folder',
    },
  ];

  toggleSidenav(): void {
    this.isSidenavOpen.update((value) => !value);
  }

  get currentPageLabel(): string {
    const current = this.navItems.find((item) => this.router.url.startsWith(item.route));
    return current?.label ?? 'Dashboard';
  }
}
