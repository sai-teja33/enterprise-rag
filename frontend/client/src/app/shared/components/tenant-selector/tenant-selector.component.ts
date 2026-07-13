import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { TenantStateService } from '../../../core/services/tenant-state.service';

@Component({
  selector: 'app-tenant-selector',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule],
  templateUrl: './tenant-selector.component.html',
  styleUrl: './tenant-selector.component.scss',
})
export class TenantSelectorComponent {
  readonly tenantState = inject(TenantStateService);
  isOpen = false;

  toggleTenantList(): void {
    this.isOpen = !this.isOpen;
  }

  selectTenant(slug: string): void {
    this.tenantState.setTenant(slug);
    this.isOpen = false;
  }
}
