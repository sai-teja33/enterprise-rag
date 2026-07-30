import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class QueryHistoryService {
  private readonly storageKey = 'enterprise-rag:recent-queries';

  readonly recentQueries = signal<string[]>(this.loadHistory());

  addQuery(question: string): void {
    const trimmed = question.trim();
    if (!trimmed) {
      return;
    }

    const existing = this.recentQueries();
    const next = [trimmed, ...existing.filter((item) => item !== trimmed)].slice(0, 8);
    this.recentQueries.set(next);

    if (typeof window !== 'undefined') {
      localStorage.setItem(this.storageKey, JSON.stringify(next));
    }
  }

  private loadHistory(): string[] {
    if (typeof window === 'undefined') {
      return [];
    }

    try {
      const stored = localStorage.getItem(this.storageKey);
      return stored ? (JSON.parse(stored) as string[]) : [];
    } catch {
      return [];
    }
  }
}
