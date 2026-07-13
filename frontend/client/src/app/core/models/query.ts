export interface QueryRequest {
  tenant_id: string;
  question: string;
  top_k?: number;
  debug?: boolean;
}

export interface ReasoningNotes {
  has_multiple_cases?: boolean;
  has_partial_support?: boolean;
  [key: string]: unknown;
}

export interface QueryCitation {
  chunk_number?: number;
  chunk_id?: string;
  tenant_id?: string;
  document_id?: string;
  title?: string;
  doc_type?: string;
  file_name?: string;
  page_number?: number;
  chunk_index?: number;
  retrieval_sources?: string[];
  vector_score?: number | null;
  text_score?: number | null;
  rerank_score?: number | null;
}

export interface LexicalOverlap {
  question_tokens?: string[];
  matched_tokens?: string[];
  coverage_ratio?: number;
}

export interface RetrievedDebugChunk {
  chunk_id?: string;
  document_id?: string;
  title?: string;
  doc_type?: string;
  file_name?: string;
  page_number?: number;
  chunk_index?: number;
  retrieval_sources?: string[];
  vector_score?: number | null;
  text_score?: number | null;
  rerank_score?: number | null;
  vector_rank?: number;
  text_rank?: number;
  chunk_preview?: string;
}

export interface RetrievalDebug {
  top_vector_score?: number | null;
  top_rerank_score?: number | null;
  num_chunks?: number;
  lexical_overlap?: LexicalOverlap;
}

export interface QueryDebugInfo {
  rescue_used?: boolean;
  retrieval?: RetrievalDebug & {
    retrieved_chunks?: RetrievedDebugChunk[];
  };
}

export interface QueryResponse {
  tenant?: string;
  question?: string;
  answer_mode?: string;
  answer?: string;
  reasoning_notes?: ReasoningNotes;
  used_citations?: QueryCitation[];
  retrieval_debug?: RetrievalDebug;
  debug_info?: QueryDebugInfo;
}
