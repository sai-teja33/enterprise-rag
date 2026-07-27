import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { TenantStateService } from '../../../core/services/department-state.service';

@Component({
  selector: 'app-tenant-selector',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule],
  templateUrl: './tenant-selector.component.html',
  styleUrl: './tenant-selector.component.scss',
})
export class TenantSelectorComponent {
  readonly departmentState = inject(TenantStateService);

  isOpen = false;

  toggleDepartmentList(): void {
    this.isOpen = !this.isOpen;
  }

  selectDepartment(slug: string): void {
    this.departmentState.setDepartment(slug);
    this.isOpen = false;
  }
}
