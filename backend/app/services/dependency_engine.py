from collections import defaultdict, deque
from datetime import datetime, timezone


class DependencyEngine:
    """Resolves document dependency chains using topological sort."""

    def __init__(self, document_types: list[dict]):
        self.types_by_name = {dt["name"]: dt for dt in document_types}
        self.graph = {}
        for dt in document_types:
            deps = dt.get("dependency_chain") or []
            self.graph[dt["name"]] = deps

    def get_dependency_tree(self, doc_type_name: str) -> list[str]:
        """Return ordered list of prerequisites (topological order)."""
        visited = set()
        order = []

        def dfs(name: str):
            if name in visited:
                return
            visited.add(name)
            for dep in self.graph.get(name, []):
                dfs(dep)
            order.append(name)

        dfs(doc_type_name)
        # Remove the target itself from prerequisites
        return [n for n in order if n != doc_type_name]

    def get_renewal_order(self, user_docs: list[dict]) -> list[dict]:
        """Compute optimal renewal order across all user documents."""
        # Build a subgraph of only the user's document types
        user_type_names = set()
        doc_by_type = {}
        for doc in user_docs:
            type_info = doc.get("document_types", {})
            if type_info:
                name = type_info.get("name")
                if name:
                    user_type_names.add(name)
                    doc_by_type[name] = doc

        # Kahn's algorithm for topological sort
        in_degree = defaultdict(int)
        adj = defaultdict(list)
        for name in user_type_names:
            for dep in self.graph.get(name, []):
                if dep in user_type_names:
                    adj[dep].append(name)
                    in_degree[name] += 1
            if name not in in_degree:
                in_degree[name] = 0

        queue = deque([n for n in user_type_names if in_degree[n] == 0])
        order = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return [
            {
                "document_type": name,
                "document": doc_by_type.get(name),
                "prerequisites": self.get_dependency_tree(name),
            }
            for name in order
            if name in doc_by_type
        ]

    def check_prerequisites(self, doc_type_name: str, user_docs: list[dict]) -> dict:
        """Check if all prerequisites are met for a document type."""
        prereqs = self.get_dependency_tree(doc_type_name)
        now = datetime.now(timezone.utc).date()

        doc_by_type = {}
        for doc in user_docs:
            type_info = doc.get("document_types", {})
            if type_info:
                doc_by_type[type_info.get("name")] = doc

        missing = []
        expired = []
        valid = []

        for prereq in prereqs:
            doc = doc_by_type.get(prereq)
            if not doc:
                missing.append(prereq)
            elif doc.get("expiry_date"):
                exp = datetime.fromisoformat(doc["expiry_date"]).date()
                if exp < now:
                    expired.append({"type": prereq, "expired_on": str(exp)})
                else:
                    valid.append(prereq)
            else:
                valid.append(prereq)

        all_met = len(missing) == 0 and len(expired) == 0
        warnings = []
        if missing:
            warnings.append(f"Missing prerequisites: {', '.join(missing)}")
        if expired:
            names = [e["type"] for e in expired]
            warnings.append(f"Expired prerequisites: {', '.join(names)}. Renew before proceeding.")

        return {
            "document_type": doc_type_name,
            "prerequisites_met": all_met,
            "valid": valid,
            "missing": missing,
            "expired": expired,
            "warnings": warnings,
        }
