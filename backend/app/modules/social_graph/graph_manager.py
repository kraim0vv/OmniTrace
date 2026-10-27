"""
OmniTrace Social Graph Mapping — Graph Manager
===============================================
Central orchestrator managing:
- NetworkX MultiDiGraph lifecycle (nodes, edges, attributes, metrics).
- Asynchronous multi-platform network crawling and cross-platform pivoting.
- Automated heuristic analysis execution.
- Export to clean JSON and interactive Pyvis HTML visualization with dark-mode styling.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import networkx as nx
from pyvis.network import Network

from app.modules.social_graph.base_extractor import BaseExtractor
from app.modules.social_graph.matcher import HeuristicMatcher
from app.modules.social_graph.models import (
    ExtractionResult,
    HeuristicMatchResult,
    NodeClassification,
    PlatformType,
    ProfileNode,
    RelationshipEdge,
    RelationType,
)

logger = logging.getLogger("omnitrace.social_graph.manager")


class SocialGraphManager:
    """
    Manages the NetworkX in-memory social graph structure, orchestrates
    async multi-depth OSINT discovery, executes heuristic correlation,
    and produces forensic exports.
    """

    def __init__(
        self,
        matcher: Optional[HeuristicMatcher] = None,
        extractors: Optional[List[BaseExtractor]] = None
    ) -> None:
        """
        Args:
            matcher: HeuristicMatcher instance for relative & associate scoring.
            extractors: List of registered BaseExtractor instances.
        """
        self.graph: nx.MultiDiGraph = nx.MultiDiGraph()
        self.matcher: HeuristicMatcher = matcher or HeuristicMatcher()
        self.extractors: List[BaseExtractor] = extractors or []
        self._crawled_ids: Set[str] = set()

    def register_extractor(self, extractor: BaseExtractor) -> None:
        """Registers a platform-specific extractor into the pipeline."""
        self.extractors.append(extractor)
        logger.info(f"Registered extractor for platform: {extractor.platform.value}")

    def get_extractor_for_seed(self, seed: str) -> Optional[BaseExtractor]:
        """Finds the first extractor capable of processing the given seed."""
        for extractor in self.extractors:
            if extractor.can_handle(seed):
                return extractor
        return None

    def add_profile(self, profile: ProfileNode) -> None:
        """
        Inserts or updates a ProfileNode in the NetworkX graph.
        """
        self.graph.add_node(
            profile.id,
            label=profile.display_name,
            platform=profile.platform.value,
            classification=profile.classification.value,
            data=profile.model_dump(),
            avatar=profile.avatar_url,
            profile_url=profile.profile_url
        )
        logger.debug(f"Added/Updated profile node: {profile.id} ({profile.display_name})")

    def add_relationship(self, edge: RelationshipEdge) -> None:
        """
        Inserts a directed relationship edge between two nodes.
        """
        self.graph.add_edge(
            edge.source_id,
            edge.target_id,
            relation_type=edge.relation_type.value,
            weight=edge.weight,
            metadata=edge.metadata,
            discovered_at=edge.discovered_at
        )

    def ingest_extraction_result(self, result: ExtractionResult) -> None:
        """
        Ingests a complete ExtractionResult payload into the graph:
        Inserts seed, all connections, and all observed edges.
        """
        # Add Seed Node
        self.add_profile(result.seed_profile)

        # Add Connected Profile Nodes
        for conn in result.connections:
            self.add_profile(conn)

        # Add Edges
        for rel in result.relationships:
            self.add_relationship(rel)

        logger.info(
            f"Ingested extraction for {result.seed_profile.id}: "
            f"+{len(result.connections)} nodes, +{len(result.relationships)} edges. "
            f"Total graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges."
        )

    async def crawl_seed(
        self,
        seed: str,
        max_depth: int = 1,
        max_connections_per_node: int = 50
    ) -> List[HeuristicMatchResult]:
        """
        Asynchronously crawls the social network starting from a seed identifier/URL
        up to `max_depth`, discovers friend networks, cross-platform pivots,
        and runs heuristic matching.

        Args:
            seed: Initial target profile URL or platform URN.
            max_depth: Maximum hops from seed (1 = friends only, 2 = friends of friends).
            max_connections_per_node: Limit on harvested contacts per node.

        Returns:
            List[HeuristicMatchResult]: Filtered list of correlated high-probability targets.
        """
        extractor = self.get_extractor_for_seed(seed)
        if not extractor:
            raise ValueError(f"No registered extractor can handle seed: {seed}")

        # Extract initial seed profile
        seed_profile = await extractor.extract_profile(seed)
        seed_profile.classification = NodeClassification.SEED_TARGET
        self.add_profile(seed_profile)

        queue: List[tuple[ProfileNode, int]] = [(seed_profile, 0)]
        self._crawled_ids.add(seed_profile.id)

        while queue:
            current_profile, current_depth = queue.pop(0)

            # Check depth boundary
            if current_depth >= max_depth:
                continue

            current_extractor = self.get_extractor_for_seed(current_profile.profile_url or current_profile.raw_id)
            if not current_extractor:
                current_extractor = extractor

            logger.info(
                f"Crawling depth {current_depth + 1}/{max_depth} for node {current_profile.id} "
                f"({current_profile.display_name})..."
            )

            try:
                extraction = await current_extractor.extract_connections(
                    current_profile,
                    limit=max_connections_per_node
                )
                self.ingest_extraction_result(extraction)

                # Queue unvisited connections for next depth iteration
                for next_node in extraction.connections:
                    if next_node.id not in self._crawled_ids and (current_depth + 1) < max_depth:
                        self._crawled_ids.add(next_node.id)
                        queue.append((next_node, current_depth + 1))

            except Exception as e:
                logger.error(f"Failed extracting connections for {current_profile.id}: {e}")

        # Execute Heuristic Correlation Analysis
        logger.info(f"Running heuristic matcher across graph for seed {seed_profile.id}...")
        matches = self.matcher.analyze_graph(self.graph, seed_profile.id)
        return matches

    def export_json(self, indent: int = 2) -> str:
        """
        Exports the entire graph topology, node data, edge relations, and network
        statistics into clean, standards-compliant JSON.
        """
        nodes_data = []
        for node_id, attrs in self.graph.nodes(data=True):
            node_dict = {
                "id": node_id,
                "label": attrs.get("label", node_id),
                "platform": attrs.get("platform"),
                "classification": attrs.get("classification"),
                "profile": attrs.get("data", {}),
            }
            nodes_data.append(node_dict)

        edges_data = []
        for u, v, k, attrs in self.graph.edges(keys=True, data=True):
            edge_dict = {
                "source": u,
                "target": v,
                "key": k,
                "relation_type": attrs.get("relation_type", RelationType.FRIEND.value),
                "weight": attrs.get("weight", 1.0),
                "metadata": attrs.get("metadata", {}),
            }
            edges_data.append(edge_dict)

        density = nx.density(self.graph) if self.graph.number_of_nodes() > 1 else 0.0

        payload = {
            "metadata": {
                "framework": "OmniTrace OSINT Social Graph Engine",
                "nodes_count": self.graph.number_of_nodes(),
                "edges_count": self.graph.number_of_edges(),
                "graph_density": round(density, 4),
            },
            "nodes": nodes_data,
            "edges": edges_data,
        }
        return json.dumps(payload, indent=indent, ensure_ascii=False)

    def export_pyvis_html(
        self,
        output_path: str | Path,
        title: str = "OmniTrace Forensic Social Graph",
        height: str = "850px",
        width: str = "100%"
    ) -> str:
        """
        Renders an interactive, responsive HTML visualization powered by PyVis / Vis.js
        custom-themed in OmniTrace's dark-white aesthetic.

        Args:
            output_path: File path to save the generated HTML report.
            title: Title banner for the HTML document.
            height: Canvas viewport height.
            width: Canvas viewport width.

        Returns:
            str: Path to the generated standalone HTML file.
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        net = Network(
            height=height,
            width=width,
            bgcolor="#09090b",
            font_color="#f4f4f5",
            directed=True
        )

        # Configure Vis.js physics for stable cluster layout
        net.set_options("""
        {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 100,
              "springConstant": 0.08
            },
            "maxVelocity": 30,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {"iterations": 150}
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 100,
            "navigationButtons": true
          }
        }
        """)

        # Add Nodes with Dark-Mode Styling
        for node_id, attrs in self.graph.nodes(data=True):
            classification = attrs.get("classification", NodeClassification.PERIPHERAL.value)
            profile_data = attrs.get("data", {})
            label = attrs.get("label", node_id)

            # Node Aesthetic Palette
            if classification == NodeClassification.SEED_TARGET.value:
                color = {"background": "#ffffff", "border": "#ffffff", "highlight": {"background": "#e4e4e7", "border": "#ffffff"}}
                size = 34
                shape = "dot"
            elif classification == NodeClassification.HIGH_PROBABILITY_RELATIVE.value:
                color = {"background": "#f43f5e", "border": "#ffffff", "highlight": {"background": "#e11d48", "border": "#ffffff"}}
                size = 28
                shape = "dot"
            elif classification == NodeClassification.CLOSE_ASSOCIATE.value:
                color = {"background": "#38bdf8", "border": "#ffffff", "highlight": {"background": "#0284c7", "border": "#ffffff"}}
                size = 22
                shape = "dot"
            else:
                color = {"background": "#27272a", "border": "#71717a", "highlight": {"background": "#3f3f46", "border": "#a1a1aa"}}
                size = 15
                shape = "dot"

            # Rich Tooltip
            bio_snippet = profile_data.get("bio") or "N/A"
            city = profile_data.get("current_city") or profile_data.get("hometown") or "Unknown"
            tooltip = f"""
            <div style="font-family:sans-serif; padding:6px; font-size:12px; color:#18181b; background:#fafafa; border-radius:6px; max-width:240px;">
                <strong>{label}</strong><br>
                <span>Platform: {attrs.get('platform', 'N/A').upper()}</span><br>
                <span>Location: {city}</span><br>
                <span>Class: {classification.upper()}</span><br>
                <small style="color:#71717a;">Bio: {bio_snippet[:80]}...</small>
            </div>
            """

            net.add_node(
                node_id,
                label=label,
                title=tooltip,
                color=color,
                size=size,
                shape=shape,
                font={"size": 12, "face": "JetBrains Mono", "color": "#f4f4f5"}
            )

        # Add Edges
        for u, v, k, attrs in self.graph.edges(keys=True, data=True):
            rel_type = attrs.get("relation_type", "friend")
            weight = attrs.get("weight", 1.0)

            if rel_type == RelationType.RELATIVE_CANDIDATE.value:
                edge_color = "#f43f5e"
                dashes = True
                width_val = 2.5
            elif rel_type in (RelationType.FRIEND.value, RelationType.MUTUAL.value):
                edge_color = "rgba(255, 255, 255, 0.4)"
                dashes = False
                width_val = 1.5
            else:
                edge_color = "rgba(113, 113, 122, 0.3)"
                dashes = False
                width_val = 1.0

            title_info = f"Relation: {rel_type.upper()} (Weight: {weight:.2f})"
            if "inferred" in attrs:
                title_info += f" | Inferred: {attrs['inferred']}"

            net.add_edge(
                u,
                v,
                color=edge_color,
                width=width_val,
                dashes=dashes,
                title=title_info
            )

        net.save_graph(str(output_file))
        logger.info(f"Interactive Pyvis social graph generated successfully at: {output_file}")
        return str(output_file.resolve())
