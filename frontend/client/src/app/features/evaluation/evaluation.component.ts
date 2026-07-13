import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { EvaluationService } from '../../core/services/evaluation.service';
import { StatCardComponent } from '../../shared/components/stat-card/stat-card.component';

@Component({
  selector: 'app-evaluation',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTableModule, StatCardComponent],
  templateUrl: './evaluation.component.html',
  styleUrl: './evaluation.component.scss',
})
export class EvaluationComponent implements OnInit {
  private readonly evaluationService = inject(EvaluationService);

  summary: any;
  displayedColumns = ['tenant', 'avgLatencyMs', 'successRate'];

  ngOnInit(): void {
    this.summary = this.evaluationService.getMockSummary();
  }
}
