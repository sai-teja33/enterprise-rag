// need to remove
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class EvaluationService {
  getMockSummary() {
    return {
      overallPassRate: 92,
      answerabilityPassRate: 90,
      docTypePassRate: 94,
      keywordPassRate: 96,
      departmentRoutingPassRate: 100,

      summaryRows: [
        {
          department: 'HR',
          avgLatencyMs: 910,
          successRate: 95,
        },
        {
          department: 'IT',
          avgLatencyMs: 870,
          successRate: 96,
        },
      ],

      failedCases: [
        {
          id: 'case-021',
          question: 'Can I work remotely while travelling internationally?',
          status: 'Needs review',
        },
        {
          id: 'case-034',
          question: 'What happens if MFA fails during VPN login?',
          status: 'Needs review',
        },
      ],
    };
  }
}
