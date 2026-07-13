import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { QueryApiService } from '../../core/services/query-api.service';
import { TenantStateService } from '../../core/services/tenant-state.service';
import { QueryResponse } from '../../core/models/query';
import { CitationCardComponent } from '../../shared/components/citation-card/citation-card.component';
import { ChunkDebugCardComponent } from '../../shared/components/chunk-debug-card/chunk-debug-card.component';
import { LoadingStateComponent } from '../../shared/components/loading-state/loading-state.component';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';

@Component({
  selector: 'app-query-playground',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatExpansionModule,
    MatSnackBarModule,
    CitationCardComponent,
    ChunkDebugCardComponent,
    LoadingStateComponent,
    StatusBadgeComponent,
  ],
  templateUrl: './query-playground.component.html',
  styleUrl: './query-playground.component.scss',
})
export class QueryPlaygroundComponent implements OnInit {
  readonly queryApi = inject(QueryApiService);
  readonly tenantState = inject(TenantStateService);
  private readonly snackBar = inject(MatSnackBar);

  question = '';
  topK = 5;
  isLoading = false;
  response: QueryResponse | null = null;
  sampleQuestions = [
    'Summarize the key policy updates for this tenant.',
    'What are the most important documents to review?',
    'Explain the latest onboarding guidance.',
  ];

  ngOnInit(): void {}

  askQuestion(): void {
    if (!this.question.trim()) {
      this.snackBar.open('Please enter a question before submitting.', 'Dismiss', {
        duration: 4000,
      });
      return;
    }

    this.isLoading = true;
    this.queryApi
      .askQuestion({
        tenant_id: this.tenantState.getSelectedTenantSlug(),
        question: this.question,
        top_k: this.topK,
        debug: true,
      })
      .subscribe({
        next: (result) => {
          this.response = result;
          this.isLoading = false;
        },
        error: () => {
          this.isLoading = false;
          this.snackBar.open(
            'The query request failed. Please verify the backend is running.',
            'Dismiss',
            { duration: 4000 },
          );
        },
      });
  }

  selectSample(question: string): void {
    this.question = question;
  }

  get retrievalDebug() {
    return this.response?.retrieval_debug;
  }

  get lexicalOverlap() {
    return this.retrievalDebug?.lexical_overlap;
  }

  get debugInfo() {
    return this.response?.debug_info;
  }

  get retrievedChunks() {
    return this.debugInfo?.retrieval?.retrieved_chunks ?? [];
  }

  get answerBadgeVariant(): string {
    if (this.response?.answer_mode === 'not_found') {
      return 'not-found';
    }
    if (this.response?.answer_mode === 'partial_answer') {
      return 'partial';
    }
    return 'answer';
  }

  get rescueBadgeVariant(): string {
    return this.debugInfo?.rescue_used ? 'answer' : 'not-found';
  }
}
