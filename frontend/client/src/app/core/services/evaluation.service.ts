import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class EvaluationService {
  getMockSummary() {
    return {
      overallPassRate: 82,
      answerabilityPassRate: 78,
      docTypePassRate: 89,
      keywordPassRate: 74,
      tenantIsolationPassRate: 91,
      summaryRows: [
        { tenant: 'acme-tech', avgLatencyMs: 1320, successRate: 86 },
        { tenant: 'nova-finance', avgLatencyMs: 1180, successRate: 91 },
        { tenant: 'zenith-retail', avgLatencyMs: 1410, successRate: 79 },
      ],
      failedCases: [
        { id: 'case-104', question: 'What is the refund policy?', status: 'Needs review' },
        { id: 'case-112', question: 'Summarize the onboarding process', status: 'Needs review' },
      ],
    };
  }
}
