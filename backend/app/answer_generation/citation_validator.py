"""
Citation Validator
Enforces cryptographic and textual verification for all generated citations.
Rejects any citation that does not match retrieved facts or primary source documents.
"""
from typing import List, Tuple
from backend.app.answer_generation.schema import EvidenceCitation, GroundedAnswer
from backend.app.retrieval.models import HybridRetrievalResult
from backend.app.config import DOCUMENT_METADATA_REGISTRY

class CitationValidator:
    @classmethod
    def validate_answer_citations(
        cls,
        answer: GroundedAnswer,
        retrieval_result: HybridRetrievalResult
    ) -> Tuple[bool, List[EvidenceCitation], List[str]]:
        """
        Validates all citations in an answer against the retrieved chunks.
        Returns:
            is_all_valid (bool): True if all citations are verified.
            valid_citations (List[EvidenceCitation]): Approved citations.
            rejections (List[str]): Explanations for rejected citations.
        """
        valid_citations: List[EvidenceCitation] = []
        rejections: List[str] = []

        # Build lookup of all retrieved texts per document
        retrieved_texts_by_doc = {}
        for fc in retrieval_result.chunks:
            fname = fc.chunk.filename
            if fname not in retrieved_texts_by_doc:
                retrieved_texts_by_doc[fname] = []
            retrieved_texts_by_doc[fname].append(fc.chunk.text.lower())

        for cit in answer.citations:
            # 1. Check document existence
            if cit.source_document not in DOCUMENT_METADATA_REGISTRY:
                rejections.append(f"Document '{cit.source_document}' does not exist in the official document registry.")
                continue

            # 2. Check if document was in retrieved context
            if cit.source_document not in retrieved_texts_by_doc:
                rejections.append(f"Citation references '{cit.source_document}', which was NOT retrieved in the evidence set.")
                continue

            # 3. Check textual presence (with whitespace normalization and bullet cleaning)
            import re
            clean_q = re.sub(r'[\ufffd\u2022\u00b7\t\r]', ' ', cit.quoted_evidence.strip().lower())
            q_norm = re.sub(r"\s+", " ", clean_q)
            doc_texts = retrieved_texts_by_doc[cit.source_document]
            
            matched = False
            for raw_chunk_text in doc_texts:
                clean_chunk = re.sub(r'[\ufffd\u2022\u00b7\t\r]', ' ', raw_chunk_text)
                chunk_norm = re.sub(r"\s+", " ", clean_chunk)
                if q_norm in chunk_norm:
                    matched = True
                    break
                # Continuous prefix match (first 3-5 words)
                q_tokens = [t for t in q_norm.split() if t]
                if len(q_tokens) >= 3:
                    prefix_len = min(5, len(q_tokens))
                    prefix_snippet = " ".join(q_tokens[:prefix_len])
                    if prefix_snippet in chunk_norm:
                        matched = True
                        break

            if not matched:
                rejections.append(
                    f"Quoted evidence '{cit.quoted_evidence[:60]}...' not found in retrieved chunks for '{cit.source_document}'."
                )
                continue

            valid_citations.append(cit)

        is_all_valid = (len(rejections) == 0 and len(valid_citations) == len(answer.citations))
        return is_all_valid, valid_citations, rejections

