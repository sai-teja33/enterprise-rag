import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

import { QueryApiService } from '../../core/services/query-api.service';
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
export class QueryPlaygroundComponent {
  readonly queryApi = inject(QueryApiService);
  private readonly snackBar = inject(MatSnackBar);

  question = '';

  topK = 5;

  isLoading = false;

  response: QueryResponse | null = null;

  sampleQuestions = [
    'How many sick leaves are allowed?',
    'Who is covered under medical insurance?',
    'How do I reset my VPN password?',
    'How do I install approved software?',
  ];

  askQuestion(): void {
    if (!this.question.trim()) {
      this.snackBar.open('Please enter a question.', 'Dismiss', {
        duration: 3000,
      });
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
        },

        error: () => {
          this.isLoading = false;

          this.snackBar.open('Unable to query the backend.', 'Dismiss', {
            duration: 4000,
          });
        },
      });
  }

  selectSample(question: string) {
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

  get rescueBadgeVariant() {
    return this.debugInfo?.rescue_used ? 'answer' : 'not-found';
  }
}
