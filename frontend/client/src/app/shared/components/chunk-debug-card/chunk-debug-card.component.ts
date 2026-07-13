import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RetrievedDebugChunk } from '../../../core/models/query';

@Component({
  selector: 'app-chunk-debug-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="chunk-card">
      <div class="chunk-title">
        <strong>{{ chunk().title ?? 'Untitled chunk' }}</strong>
        <span>{{ chunk().doc_type ?? 'Unknown' }}</span>
      </div>
      <div class="meta-row">
        <span>{{ chunk().file_name ?? 'Unknown file' }}</span>
        <span>Page {{ chunk().page_number ?? '-' }} • Chunk {{ chunk().chunk_index ?? '-' }}</span>
      </div>
      @if (chunk().retrieval_sources?.length) {
        <div class="meta-row">
          <span>Sources: {{ chunk().retrieval_sources?.join(', ') }}</span>
        </div>
      }
      <div class="scores">
        @if (chunk().vector_score != null) {
          <span>Vector: {{ chunk().vector_score | number: '1.2-2' }}</span>
        }
        @if (chunk().text_score != null) {
          <span>Text: {{ chunk().text_score | number: '1.2-2' }}</span>
        }
        @if (chunk().rerank_score != null) {
          <span>Rerank: {{ chunk().rerank_score | number: '1.2-2' }}</span>
        }
      </div>
      <div class="meta-row">
        <span>Vector rank: {{ chunk().vector_rank ?? '-' }}</span>
        <span>Text rank: {{ chunk().text_rank ?? '-' }}</span>
      </div>
      <p>{{ chunk().chunk_preview }}</p>
    </div>
  `,
  styles: [
    `
      .chunk-card {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px 14px;
        background: white;
        display: grid;
        gap: 8px;
      }
      .chunk-title {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        flex-wrap: wrap;
      }
      .meta-row {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        color: #475569;
        font-size: 0.9rem;
        flex-wrap: wrap;
      }
      .scores {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        font-size: 0.85rem;
        color: #334155;
      }
      p {
        margin: 0;
        color: #475569;
        font-size: 0.92rem;
        line-height: 1.5;
      }
    `,
  ],
})
export class ChunkDebugCardComponent {
  readonly chunk = input.required<RetrievedDebugChunk>();
}
