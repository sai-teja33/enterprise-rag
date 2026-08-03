import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';

import { QueryApiService } from '../../core/services/query-api.service';
import { QueryHistoryService } from '../../core/services/query-history.service';
import { QueryResponse } from '../../core/models/query';
import { NotificationService } from '../../core/services/notification.service';

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
    MatIconModule,
    MatDividerModule,
    MatExpansionModule,
    LoadingStateComponent,
    StatusBadgeComponent,
  ],
  templateUrl: './query-playground.component.html',
  styleUrl: './query-playground.component.scss',
})
export class QueryPlaygroundComponent {
  readonly queryApi = inject(QueryApiService);
  readonly queryHistory = inject(QueryHistoryService);
  private readonly notificationService = inject(NotificationService);

  question = '';
  topK = 5;
  isLoading = false;
  response: QueryResponse | null = null;
  showTechnicalDetails = false;

  sampleQuestions = [
    'What is the sick leave policy for employees?',
    'How do I request maternity or paternity leave?',
    'What are the rules for reimbursing travel expenses?',
    'How do I apply for employee medical insurance?',
  ];

  askQuestion(): void {
    if (!this.question.trim()) {
      this.notificationService.error('Please enter a question.');
      return;
    }

    this.isLoading = true;

    this.queryApi
      .askQuestion({
        question: this.question,
        top_k: this.topK,
        debug: true,
      })
      .subscribe({
        next: (result) => {
          this.response = result;
          this.isLoading = false;
          this.queryHistory.addQuery(this.question);
        },

        error: () => {
          this.isLoading = false;
          this.notificationService.error('Unable to query the backend.');
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

  get usedCitations() {
    return this.response?.used_citations ?? [];
  }

  get responseSource() {
    return (
      this.usedCitations[0]?.doc_type ||
      this.usedCitations[0]?.title ||
      this.usedCitations[0]?.file_name ||
      'Unknown'
    );
  }

  get responseMethod() {
    const sources = this.usedCitations.flatMap((citation) => citation.retrieval_sources ?? []);
    const uniqueSources = Array.from(new Set(sources.filter(Boolean)));

    if (!uniqueSources.length) {
      return 'n/a';
    }

    return uniqueSources.length === 1 ? uniqueSources[0] : uniqueSources.join(', ');
  }

  get responseConfidence() {
    const rerankScore = this.response?.retrieval_debug?.top_rerank_score;
    const vectorScore = this.response?.retrieval_debug?.top_vector_score;

    if (rerankScore != null) {
      return rerankScore.toFixed(2);
    }

    if (vectorScore != null) {
      return vectorScore.toFixed(2);
    }

    return 'n/a';
  }

  get answerBadgeVariant() {
    switch (this.response?.answer_mode) {
      case 'not_found':
        return 'not-found';

      case 'partial_answer':
        return 'partial';

      default:
        return 'answer';
    }
  }
}
