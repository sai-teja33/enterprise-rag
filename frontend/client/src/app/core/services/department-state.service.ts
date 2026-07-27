import { Injectable, signal } from '@angular/core';
import { DepartmentOption } from '../models/tenant';

@Injectable({
  providedIn: 'root',
})
export class TenantStateService {
  private readonly storageKey = 'enterprise-rag:selected-department';

  readonly departments: DepartmentOption[] = [
    {
      label: 'Human Resources',
      slug: 'hr',
    },
    {
      label: 'Information Technology',
      slug: 'it',
    },
  ];

  readonly selectedDepartment = signal<DepartmentOption>(this.getInitialDepartment());

  constructor() {
    this.selectedDepartment.set(this.getInitialDepartment());
  }

  setDepartment(slug: string): void {
    const department = this.departments.find((item) => item.slug === slug) ?? this.departments[0];

    this.selectedDepartment.set(department);
    localStorage.setItem(this.storageKey, department.slug);
  }

  getSelectedDepartmentSlug(): string {
    return this.selectedDepartment().slug;
  }

  private getInitialDepartment(): DepartmentOption {
    if (typeof window === 'undefined') {
      return this.departments[0];
    }

    const stored = localStorage.getItem(this.storageKey);

    return this.departments.find((department) => department.slug === stored) ?? this.departments[0];
  }
}
