"""GRIDSENTINEL — Autonomous Learning & Pattern Discovery"""

from datetime import datetime
from typing import Optional


class LearningEngine:
    """Stores patterns, hypotheses, and learns from simulation outcomes."""

    def __init__(self):
        self.memory: list[dict] = []
        self.patterns: list[dict] = []
        self.hypotheses: list[dict] = []

    def record_event(self, event_type: str, context: dict, outcome: dict):
        """Record a grid event for future pattern analysis."""
        self.memory.append({
            "event_type": event_type,
            "context": context,
            "outcome": outcome,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self._discover_patterns()

    def _discover_patterns(self):
        """Analyze memory for recurring patterns."""
        if len(self.memory) < 3:
            return

        # Pattern: repeated failure types
        type_counts: dict[str, int] = {}
        for m in self.memory:
            t = m["event_type"]
            type_counts[t] = type_counts.get(t, 0) + 1

        for event_type, count in type_counts.items():
            if count >= 2:
                existing = [p for p in self.patterns if p["pattern_type"] == event_type]
                if not existing:
                    self.patterns.append({
                        "pattern_type": event_type,
                        "occurrences": count,
                        "description": f"{event_type} has occurred {count} times. Recommend preemptive action.",
                        "confidence": min(0.95, 0.5 + count * 0.1),
                        "discovered_at": datetime.utcnow().isoformat(),
                    })

    def generate_hypothesis(self, context: dict) -> Optional[dict]:
        """Generate a hypothesis based on current patterns."""
        if not self.patterns:
            return None

        top_pattern = max(self.patterns, key=lambda p: p["confidence"])
        hypothesis = {
            "based_on": top_pattern["pattern_type"],
            "hypothesis": f"Based on {top_pattern['occurrences']} observations, "
                          f"{top_pattern['description']} "
                          f"Recommend: preemptive load migration before predicted event.",
            "confidence": top_pattern["confidence"],
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.hypotheses.append(hypothesis)
        return hypothesis

    def get_state(self) -> dict:
        return {
            "total_memories": len(self.memory),
            "patterns_discovered": len(self.patterns),
            "hypotheses_generated": len(self.hypotheses),
            "patterns": self.patterns[-10:],
            "hypotheses": self.hypotheses[-5:],
        }


# Global instance
learning_engine = LearningEngine()
