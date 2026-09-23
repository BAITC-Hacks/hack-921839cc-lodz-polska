"""Build a shareable report from engine facts and validated AI findings."""
from ..ai.schemas import AnalysisResponse, ExecutiveBrief, Finding, ScenarioSnapshot


def _bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- Нет данных"


def build_executive_brief(
    scenario: ScenarioSnapshot,
    analysis: AnalysisResponse,
) -> ExecutiveBrief:
    """Create JSON fields and Markdown without recalculating simulation values."""
    district_facts = [
        Finding(
            text=f"{district.district_name}: {district.before_score} → {district.after_score}",
            evidence=[
                f"Расчётный показатель района {district.district_name}",
                f"До: {district.before_score}; после: {district.after_score}",
            ],
        )
        for district in scenario.districts
        if district.after_score > district.before_score
    ]
    improvements = analysis.strengths or district_facts
    budget = scenario.budget
    decision_lines = [
        f"{d.measure_id} — {d.name} ({d.category}, {d.cost}; "
        f"{d.district_name or 'весь город'})"
        for d in scenario.decisions
    ]
    major_lines = [f.text for f in improvements]
    risk_lines = [f.text for f in analysis.risks]
    equity_lines = [f.text for f in analysis.tradeoffs]
    markdown = "\n".join(
        [
            "# City Management Report",
            "",
            f"**Astana Quality of Life Score:** {scenario.score_before} → {scenario.score_after} "
            f"(изменение: {scenario.score_delta})",
            f"**Бюджет:** {budget.spent} из {budget.initial}; остаток {budget.remaining}",
            "",
            "## Решения",
            _bullet_list(decision_lines),
            "",
            "## Основные улучшения",
            _bullet_list(major_lines),
            "",
            "## Оставшиеся риски",
            _bullet_list(risk_lines),
            "",
            "## Компромиссы и равенство районов",
            _bullet_list(equity_lines),
            "",
            "## Рекомендации",
            _bullet_list(analysis.recommendations),
        ]
    )
    return ExecutiveBrief(
        title="City Management Report",
        score_before=scenario.score_before,
        score_after=scenario.score_after,
        score_delta=scenario.score_delta,
        budget=budget,
        decisions=scenario.decisions,
        major_improvements=improvements,
        remaining_risks=analysis.risks,
        equity=analysis.tradeoffs,
        recommendations=analysis.recommendations,
        markdown=markdown,
    )
