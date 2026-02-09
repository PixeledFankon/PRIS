
import networkx as nx

def CreateGraph(rules: dict) -> nx.Graph:
    g = nx.Graph()

    patch = rules.get("patch", "unknown_patch")
    g.add_node(patch, type="patch")

    for heroClass, tier in rules["tiers"].items():
        g.add_node(heroClass, type="hero_class")
        g.add_node(tier, type="tier")

        g.add_edge(heroClass, tier, relation="has_tier")

        g.add_edge(heroClass, patch, relation="active_in_patch")

    for attacker, defenders in rules["counters"].items():
        for defender in defenders:
            g.add_edge(attacker, defender, relation="counters")

    return g

def FindRelatedEntities(graph: nx.Graph, startNode: str):
    if startNode not in graph:
        return []
    return list(graph.neighbors(startNode))
