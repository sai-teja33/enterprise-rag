export interface DocumentStatusItem {
  document_id: string;
  department_id?: string;
  title: string;
  doc_type: string;
  file_name: string;
  uploaded_at?: string;
  total_chunks: number;
  embedded_chunks: number;
  ready_for_query: boolean;
}

export interface DepartmentDocumentStatusResponse {
  department_id: string;
  total_documents: number;
  documents: DocumentStatusItem[];
}

export interface UploadDocumentResponse {
  id: string;
  department_id: string;
  title: string;
  doc_type: string;
  file_name: string;
  file_path: string;
  uploaded_at?: string;
}

export interface PreviewDocumentResponse {
  document_id: string;
  title: string;
  doc_type: string;
  file_name: string;
  num_langchain_docs: number;
  text_preview: string;
  text_length: number;
}

export interface DocumentChunk {
  id: string;
  chunk_index?: number;
  page_number?: number;
  section_title?: string;
  chunking_strategy?: string;
  chunk_size?: number;
  chunk_preview: string;
}

export interface DocumentChunksResponse {
  document_id: string;
  total_chunks: number;
  chunks: DocumentChunk[];
}

export interface ReprocessDocumentResponse {
  message: string;
  department_id: string;
  document_id: string;
  title: string;
  doc_type: string;
  deleted_old_chunks?: number;
  final_status: {
    total_chunks: number;
    embedded_chunks: number;
    ready_for_query: boolean;
  };
}
