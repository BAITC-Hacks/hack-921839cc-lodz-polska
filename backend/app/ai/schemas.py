"""Validated input and output contracts for the AI analyst.

The input contains simulation results only. This package does not accept or
calculate raw policy effects, budgets, district scores, or the official score.
"""
from typing import Literal

from pydantic import BaseModel, Field


class StrictModel(BaseModel):
    class Config:
        extra = "forbid"


class BudgetSummary(StrictModel):
    initial: float
    spent: float
    remaining: float


class DecisionSummary(StrictModel):
    measure_id: str
    name: str
    category: str
    scope: Literal["district", "city"]
    cost: float
    district_id: str | None = None
    district_name: str | None = None
    # Supplied by the simulation engine when contribution analysis is available.
    contribution: float | None = None


class DistrictScoreChange(StrictModel):
    district_id: str
    district_name: str
    before_score: float
    after_score: float
    # Indicator values are already calculated by the simulation engine.
    indicators_before: dict[str, float] = Field(default_factory=dict)
    indicators_after: dict[str, float] = Field(default_factory=dict)


class CategoryScoreChange(StrictModel):
    category: str
    before_score: float
    after_score: float


class ScenarioSnapshot(StrictModel):
    """Facts computed by the simulation engine and safe to explain."""

    score_before: float
    score_after: float
    score_delta: float
    budget: BudgetSummary
    decisions: list[DecisionSummary]
    districts: list[DistrictScoreChange]
    category_scores: list[CategoryScoreChange] = Field(default_factory=list)
    critical_indicators_before: int | None = None
    critical_indicators_after: int | None = None
    synergies: list[str] = Field(default_factory=list)


class AnalysisRequest(StrictModel):
    scenario: ScenarioSnapshot
    question: str | None = Field(default=None, max_length=1000)


class Finding(StrictModel):
    text: str
    evidence: list[str] = Field(default_factory=list)


class AnalysisResponse(StrictModel):
    strengths: list[Finding]
    risks: list[Finding]
    tradeoffs: list[Finding]
    recommendations: list[str]
    answer: str | None = None


class ExecutiveBrief(StrictModel):
    title: str
    score_before: float
    score_after: float
    score_delta: float
    budget: BudgetSummary
    decisions: list[DecisionSummary]
    major_improvements: list[Finding]
    remaining_risks: list[Finding]
    equity: list[Finding]
    recommendations: list[str]
    markdown: str
