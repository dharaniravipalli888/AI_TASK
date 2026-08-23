import re
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.data.document_loader import doc_db, DocumentChunk
from app.auth.access_control import UserContext

class DocumentSearchTool:
    def __init__(self):
        self.chunks = doc_db.chunks
        self.vectorizer = None
        self.tfidf_matrix = None
        self._build_index()

    def _build_index(self):
        """Builds TF-IDF index over all document chunks."""
        if not self.chunks:
            return
        corpus = [f"{c.title} {c.section} {c.content}" for c in self.chunks]
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, user: UserContext, top_k: int = 5) -> Dict[str, Any]:
        """
        Executes document retrieval with access control filtering and precedence ordering.
        Tool 1 of Minimum Requirements.
        """
        if not self.chunks or not self.vectorizer:
            return {"query": query, "results": [], "warning": "No documents indexed."}

        # Vector search similarity scores
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        scored_chunks = []
        for idx, chunk in enumerate(self.chunks):
            sim = float(similarities[idx])

            # Keyword boost for direct term matches
            q_terms = [t for t in re.findall(r'\w+', query.lower()) if len(t) > 2]
            content_lower = f"{chunk.title} {chunk.section} {chunk.content}".lower()
            keyword_matches = sum(1 for term in q_terms if term in content_lower)
            boosted_score = sim + (keyword_matches * 0.15)

            # Data-layer access filter: exclude other customers' private agreements
            if not user.is_internal and chunk.account_id and chunk.account_id != user.account_id:
                continue  # Block access

            if boosted_score > 0.01:
                scored_chunks.append({
                    "chunk": chunk,
                    "score": boosted_score,
                    "sim": sim
                })

        # Sort by source precedence first (1 is highest), then score (descending)
        # Note: Precedence 1 = Enterprise Agreement, 2 = v3 Current, 3 = SOP, 4 = Ops, 9 = Deprecated
        scored_chunks.sort(key=lambda x: (x["chunk"].precedence, -x["score"]))

        top_results = scored_chunks[:top_k]

        results_payload = []
        has_deprecated = False
        overrides_detected = []

        for item in top_results:
            c: DocumentChunk = item["chunk"]
            
            warning = None
            if c.status == "DEPRECATED":
                has_deprecated = True
                warning = "DEPRECATED SOURCE: This document is obsolete and MUST NOT be used for current requests."

            if c.precedence == 1:
                overrides_detected.append(f"Signed agreement ({c.title}) overrides general policies.")

            results_payload.append({
                "doc_id": c.doc_id,
                "file_name": c.file_name,
                "title": c.title,
                "section": c.section,
                "content": c.content,
                "status": c.status,
                "precedence_rank": c.precedence,
                "account_id": c.account_id,
                "relevance_score": round(item["score"], 4),
                "warning": warning
            })

        return {
            "query": query,
            "results_count": len(results_payload),
            "results": results_payload,
            "has_deprecated_sources": has_deprecated,
            "overrides_applied": list(set(overrides_detected)),
            "source_precedence_rule": "Order of authority: 1. Signed Agreement > 2. Support Policy v3 > 3. Cancellation SOP > 4. Product Ops Guide > 9. Deprecated Docs / Historical Tickets"
        }

document_search_tool = DocumentSearchTool()
