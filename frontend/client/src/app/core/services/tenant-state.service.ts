import { Injectable, signal } from '@angular/core';
import { TenantOption } from '../models/tenant';

@Injectable({ providedIn: 'root' })
export class TenantStateService {
  private readonly storageKey = 'enterprise-rag:selected-tenant';

  readonly tenants: TenantOption[] = [
    { label: 'Acme Tech', slug: 'acme-tech' },
    { label: 'Nova Finance', slug: 'nova-finance' },
    { label: 'Zenith Retail', slug: 'zenith-retail' },
  ];

  readonly selectedTenant = signal<TenantOption>(this.getInitialTenant());

  constructor() {
    this.selectedTenant.set(this.getInitialTenant());
  }

  setTenant(slug: string): void {
    const tenant = this.tenants.find((item) => item.slug === slug) ?? this.tenants[0];
    this.selectedTenant.set(tenant);
    localStorage.setItem(this.storageKey, tenant.slug);
  }

  getSelectedTenantSlug(): string {
    return this.selectedTenant().slug;
  }

  private getInitialTenant(): TenantOption {
    if (typeof window === 'undefined') {
      return this.tenants[0];
    }

    const stored = localStorage.getItem(this.storageKey);
    return this.tenants.find((tenant) => tenant.slug === stored) ?? this.tenants[0];
  }
}
