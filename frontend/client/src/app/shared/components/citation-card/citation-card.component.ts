import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { QueryCitation } from '../../../core/models/query';

@Component({
  selector: 'app-citation-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="citation-card">
      <div class="citation-header">
        <strong>Chunk {{ citation().chunk_number ?? '-' }}</strong>
        <span>{{ citation().title ?? 'Untitled' }}</span>
      </div>
      <div class="meta-row">
        <span>{{ citation().doc_type ?? 'Unknown' }}</span>
        <span>{{ citation().file_name ?? 'Unknown file' }}</span>
      </div>
      <div class="meta-row">
        <span>Page {{ citation().page_number ?? '-' }}</span>
        <span>Chunk {{ citation().chunk_index ?? '-' }}</span>
      </div>
      @if (citation().retrieval_sources?.length) {
        <div class="meta-row">
          <span>Sources: {{ citation().retrieval_sources?.join(', ') }}</span>
        </div>
      }
      <div class="scores">
        @if (citation().vector_score != null) {
          <span>Vector: {{ citation().vector_score | number: '1.2-2' }}</span>
        }
        @if (citation().text_score != null) {
          <span>Text: {{ citation().text_score | number: '1.2-2' }}</span>
        }
        @if (citation().rerank_score != null) {
          <span>Rerank: {{ citation().rerank_score | number: '1.2-2' }}</span>
        }
      </div>
    </div>
  `,
  styles: [
    `
      .citation-card {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px 14px;
        background: #f8fafc;
        display: grid;
        gap: 8px;
      }
      .citation-header {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        flex-wrap: wrap;
      }
      .meta-row {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        font-size: 0.9rem;
        color: #475569;
        flex-wrap: wrap;
      }
      .scores {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        font-size: 0.85rem;
        color: #334155;
      }
    `,
  ],
})
export class CitationCardComponent {
  readonly citation = input.required<QueryCitation>();
}
