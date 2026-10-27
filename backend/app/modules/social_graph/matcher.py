"""
OmniTrace Social Graph Mapping — Heuristic Matcher
===================================================
Analyzes social graph nodes and their topological neighborhood to uncover
hidden correlations:
- Relatives (matching surnames, gender inflection normalization, age differences)
- Geographical clusters (identical hometown, regional co-location)
- Structural density (Jaccard neighborhood similarity of mutual friends)
"""

from __future__ import annotations

import difflib
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx

from app.modules.social_graph.models import (
    HeuristicMatchResult,
    NodeClassification,
    ProfileNode,
    RelationType,
)

logger = logging.getLogger("omnitrace.social_graph.matcher")


class HeuristicMatcher:
    """
    Graph analysis engine for inferring family relations, primary targets,
    and close associates using multi-factor heuristic correlation.
    """

    def __init__(
        self,
        weight_surname: float = 0.40,
        weight_location: float = 0.25,
        weight_age: float = 0.15,
        weight_structural: float = 0.20,
        relative_threshold: float = 0.65,
        associate_threshold: float = 0.45
    ) -> None:
        """
        Args:
            weight_surname: Relative importance of matching surnames.
            weight_location: Relative importance of matching hometown/city.
            weight_age: Relative importance of generational/age compatibility.
            weight_structural: Relative importance of shared neighborhood density.
            relative_threshold: Composite probability cutoff to flag as relative.
            associate_threshold: Cutoff to flag as close associate.
        """
        self.w_surname = weight_surname
        self.w_location = weight_location
        self.w_age = weight_age
        self.w_structural = weight_structural
        self.relative_threshold = relative_threshold
        self.associate_threshold = associate_threshold

    @staticmethod
    def normalize_surname(surname: Optional[str]) -> str:
        """
        Normalizes surnames across Cyrillic and Latin inflections:
        - Removes gendered endings (e.g., 'Иванова' -> 'иванов', 'Петрова' -> 'петров')
        - Normalizes case and trims whitespace.
        """
        if not surname:
            return ""
        norm = surname.strip().lower()

        # Cyrillic female patronymic/surname suffixes -> root form
        cyrillic_suffixes = ("ова", "ева", "ина", "ына", "ая")
        for suffix in cyrillic_suffixes:
            if norm.endswith(suffix):
                # Replace 'ова' -> 'ов', 'ая' -> 'ий'/'ый'
                if suffix == "ая":
                    return norm[:-2] + "ий"
                return norm[:-1]  # remove trailing 'а'

        return norm

    def compute_surname_score(self, node_a: ProfileNode, node_b: ProfileNode) -> Tuple[float, Optional[str]]:
        """
        Evaluates surname correlation between two entities.
        """
        if not node_a.last_name or not node_b.last_name:
            return 0.0, None

        raw_a = node_a.last_name.strip().lower()
        raw_b = node_b.last_name.strip().lower()

        if raw_a == raw_b:
            return 1.0, f"Exact surname match: '{node_a.last_name}'"

        norm_a = self.normalize_surname(raw_a)
        norm_b = self.normalize_surname(raw_b)

        if norm_a == norm_b:
            return 0.95, f"Gender-inflected surname match: '{node_a.last_name}' ~ '{node_b.last_name}'"

        # Levenshtein/Jaro similarity for transliterations or minor spelling variations
        ratio = difflib.SequenceMatcher(None, norm_a, norm_b).ratio()
        if ratio >= 0.85:
            return float(ratio * 0.8), f"High phonetic/fuzzy surname similarity: {ratio:.2f}"

        return 0.0, None

    @staticmethod
    def compute_location_score(node_a: ProfileNode, node_b: ProfileNode) -> Tuple[float, Optional[str]]:
        """
        Evaluates geographical co-location based on hometown and current city.
        """
        score = 0.0
        reasons: List[str] = []

        # Hometown comparison (strongest geographic family signal)
        if node_a.hometown and node_b.hometown:
            ha = node_a.hometown.strip().lower()
            hb = node_b.hometown.strip().lower()
            if ha == hb:
                score += 0.70
                reasons.append(f"Identical hometown: '{node_a.hometown}'")
            elif ha in hb or hb in ha:
                score += 0.50
                reasons.append(f"Regional hometown co-location: '{ha}' ~ '{hb}'")

        # Current city comparison
        if node_a.current_city and node_b.current_city:
            ca = node_a.current_city.strip().lower()
            cb = node_b.current_city.strip().lower()
            if ca == cb:
                score += 0.30
                reasons.append(f"Same residence city: '{node_a.current_city}'")

        final_score = min(score, 1.0)
        return final_score, "; ".join(reasons) if reasons else None

    @staticmethod
    def compute_age_score(node_a: ProfileNode, node_b: ProfileNode) -> Tuple[float, Optional[str], Optional[str]]:
        """
        Evaluates generational delta if birth years are available.
        Returns:
            (score, reason, inferred_role)
        """
        year_a = node_a.birth_year
        year_b = node_b.birth_year

        if not year_a or not year_b:
            return 0.2, None, None  # Neutral baseline when age is missing

        delta = abs(year_a - year_b)

        # Sibling generational window (0-10 years)
        if delta <= 10:
            return 0.90, f"Compatible sibling age delta ({delta} yrs: {year_a} vs {year_b})", "SIBLING"

        # Parent-Child generational window (18-42 years)
        if 18 <= delta <= 45:
            role = "PARENT" if year_a < year_b else "CHILD"
            return 0.85, f"Compatible parent-child age delta ({delta} yrs: {year_a} vs {year_b})", role

        # Grandparent-Grandchild window (46-75 years)
        if 46 <= delta <= 75:
            return 0.60, f"Generational gap: grandparent/grandchild ({delta} yrs)", "EXTENDED_FAMILY"

        return 0.10, f"Unusual family age delta: {delta} years", "ACQUAINTANCE"

    @staticmethod
    def compute_structural_jaccard(
        graph: nx.MultiDiGraph,
        node_id_a: str,
        node_id_b: str
    ) -> Tuple[float, Optional[str]]:
        """
        Calculates Jaccard similarity of graph neighborhoods (mutual connections):
        J(A, B) = |Neighbors(A) ∩ Neighbors(B)| / |Neighbors(A) ∪ Neighbors(B)|
        """
        if not graph.has_node(node_id_a) or not graph.has_node(node_id_b):
            return 0.0, None

        # Undirected view for symmetric mutual neighbors
        adj_a: Set[str] = set(graph.predecessors(node_id_a)).union(graph.successors(node_id_a))
        adj_b: Set[str] = set(graph.predecessors(node_id_b)).union(graph.successors(node_id_b))

        # Remove each other from comparison sets
        adj_a.discard(node_id_b)
        adj_b.discard(node_id_a)

        intersection = adj_a.intersection(adj_b)
        union = adj_a.union(adj_b)

        if not union:
            return 0.0, None

        jaccard = len(intersection) / len(union)
        reason = f"{len(intersection)} mutual connections (Jaccard: {jaccard:.2f})"
        return float(min(jaccard * 2.5, 1.0)), reason

    def evaluate_pair(
        self,
        graph: nx.MultiDiGraph,
        node_a: ProfileNode,
        node_b: ProfileNode
    ) -> HeuristicMatchResult:
        """
        Computes composite correlation metrics between two entities in the graph.
        """
        justifications: List[str] = []

        # 1. Surname Score
        s_surname, reason_surname = self.compute_surname_score(node_a, node_b)
        if reason_surname:
            justifications.append(reason_surname)

        # 2. Location Score
        s_location, reason_loc = self.compute_location_score(node_a, node_b)
        if reason_loc:
            justifications.append(reason_loc)

        # 3. Age Score & Inferred Relation
        s_age, reason_age, inferred_role = self.compute_age_score(node_a, node_b)
        if reason_age:
            justifications.append(reason_age)

        # 4. Graph Topological Mutual Friends Density
        s_struct, reason_struct = self.compute_structural_jaccard(graph, node_a.id, node_b.id)
        if reason_struct:
            justifications.append(reason_struct)

        # Weighted composite probability
        composite = (
            (self.w_surname * s_surname) +
            (self.w_location * s_location) +
            (self.w_age * s_age) +
            (self.w_structural * s_struct)
        )
        composite = round(min(max(composite, 0.0), 1.0), 3)

        # Infer relationship semantic label
        if s_surname >= 0.85 and composite >= self.relative_threshold:
            relation = inferred_role or "IMMEDIATE_FAMILY"
        elif composite >= self.relative_threshold:
            relation = "HIGH_PROBABILITY_RELATIVE"
        elif composite >= self.associate_threshold:
            relation = "CLOSE_ASSOCIATE"
        else:
            relation = "PERIPHERAL_CONNECTION"

        return HeuristicMatchResult(
            source_id=node_a.id,
            target_id=node_b.id,
            surname_score=round(s_surname, 2),
            location_score=round(s_location, 2),
            age_score=round(s_age, 2),
            structural_score=round(s_struct, 2),
            composite_probability=composite,
            inferred_relation=relation,
            justification=justifications
        )

    def analyze_graph(
        self,
        graph: nx.MultiDiGraph,
        seed_id: str
    ) -> List[HeuristicMatchResult]:
        """
        Iterates across all neighbors of the seed target in the graph, evaluates
        heuristic correlation, assigns updated node classifications, and injects
        inferred relationship candidate edges into the graph.

        Returns:
            List[HeuristicMatchResult]: Filtered candidates meeting threshold.
        """
        if not graph.has_node(seed_id):
            logger.warning(f"Seed node {seed_id} not present in graph.")
            return []

        seed_data: Dict[str, Any] = graph.nodes[seed_id].get("data", {})
        seed_node = ProfileNode.model_validate(seed_data)

        matches: List[HeuristicMatchResult] = []

        # Analyze all nodes in the graph against the seed
        for node_id in graph.nodes():
            if node_id == seed_id:
                continue

            target_data: Dict[str, Any] = graph.nodes[node_id].get("data", {})
            if not target_data:
                continue

            target_node = ProfileNode.model_validate(target_data)
            result = self.evaluate_pair(graph, seed_node, target_node)

            if result.composite_probability >= self.associate_threshold:
                matches.append(result)

                # Mutate graph attributes with forensic findings
                if result.composite_probability >= self.relative_threshold:
                    graph.nodes[node_id]["classification"] = NodeClassification.HIGH_PROBABILITY_RELATIVE.value
                    # Inject candidate edge
                    graph.add_edge(
                        seed_id,
                        node_id,
                        relation_type=RelationType.RELATIVE_CANDIDATE.value,
                        weight=result.composite_probability,
                        inferred=result.inferred_relation,
                        justification="; ".join(result.justification)
                    )
                else:
                    graph.nodes[node_id]["classification"] = NodeClassification.CLOSE_ASSOCIATE.value

        # Sort descending by composite probability
        matches.sort(key=lambda m: m.composite_probability, reverse=True)
        logger.info(f"Heuristic analysis complete for seed '{seed_id}': {len(matches)} correlated nodes flagged.")
        return matches
