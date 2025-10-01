from __future__ import annotations

from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple

from experta import KnowledgeEngine, Fact, Rule


class TopicFact(Fact):
    course_id: str
    topic_id: str
    difficulty: float
    mastery: float
    importance: float
    exam_type: str
    days_to_exam: int
    est_hours: float
    prereqs: List[str]


def urgency_factor(days_to_exam: int, cram_mode: bool) -> float:
    if cram_mode:
        # Strong urgency curve
        if days_to_exam <= 1:
            return 2.0
        if days_to_exam <= 3:
            return 1.8
        if days_to_exam <= 7:
            return 1.6
        if days_to_exam <= 14:
            return 1.3
        return 1.0
    else:
        if days_to_exam <= 1:
            return 1.8
        if days_to_exam <= 3:
            return 1.5
        if days_to_exam <= 7:
            return 1.3
        if days_to_exam <= 14:
            return 1.15
        return 1.0


class StudyEngine(KnowledgeEngine):
    def __init__(self, cram_mode: bool):
        super().__init__()
        self.cram_mode = cram_mode
        self.adjustments: Dict[str, List[Tuple[str, float, str]]] = {}
        self.explanations: List[str] = []

    def record(self, topic_id: str, rule_id: str, boost: float, explanation: str):
        self.adjustments.setdefault(topic_id, []).append((rule_id, boost, explanation))
        self.explanations.append(f"{rule_id}: {explanation} (boost {boost:+.2f})")

    def get_current_fact(self):
        for factid, fact in self.facts.items():
            if isinstance(fact, TopicFact):
                return fact
        return None

    # Urgency rules
    @Rule(TopicFact(days_to_exam=1))
    def R_Urgent_01(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-01", 0.50, "Exam is tomorrow: heavy urgency boost")

    @Rule(TopicFact(days_to_exam=2))
    def R_Urgent_02(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-02", 0.35, "Exam in 2 days: strong urgency boost")

    @Rule(TopicFact(days_to_exam=3))
    def R_Urgent_03(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-03", 0.35, "Exam in 3 days: strong urgency boost")

    @Rule(TopicFact(days_to_exam=4))
    def R_Urgent_04(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-04", 0.20, "Exam in 4 days: medium urgency boost")

    @Rule(TopicFact(days_to_exam=5))
    def R_Urgent_05(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-05", 0.20, "Exam in 5 days: medium urgency boost")

    @Rule(TopicFact(days_to_exam=6))
    def R_Urgent_06(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-06", 0.20, "Exam in 6 days: medium urgency boost")

    @Rule(TopicFact(days_to_exam=7))
    def R_Urgent_07(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-07", 0.20, "Exam in 7 days: medium urgency boost")

    @Rule(TopicFact(days_to_exam=8))
    def R_Urgent_08(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-08", 0.10, "Exam in 8 days: light urgency boost")

    @Rule(TopicFact(days_to_exam=9))
    def R_Urgent_09(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-09", 0.10, "Exam in 9 days: light urgency boost")

    @Rule(TopicFact(days_to_exam=10))
    def R_Urgent_10(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-10", 0.10, "Exam in 10 days: light urgency boost")

    @Rule(TopicFact(days_to_exam=11))
    def R_Urgent_11(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-11", 0.10, "Exam in 11 days: light urgency boost")

    @Rule(TopicFact(days_to_exam=12))
    def R_Urgent_12(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-12", 0.10, "Exam in 12 days: light urgency boost")

    @Rule(TopicFact(days_to_exam=13))
    def R_Urgent_13(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-13", 0.10, "Exam in 13 days: light urgency boost")

    @Rule(TopicFact(days_to_exam=14))
    def R_Urgent_14(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "URG-14", 0.10, "Exam in 14 days: light urgency boost")

    # Mastery rules
    @Rule(TopicFact(mastery=0.0))
    def R_Master_01(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "MAS-01", 0.40, "Very low mastery (0.0): large boost")

    @Rule(TopicFact(mastery=0.1))
    def R_Master_02(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "MAS-02", 0.40, "Very low mastery (0.1): large boost")

    @Rule(TopicFact(mastery=0.2))
    def R_Master_03(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "MAS-03", 0.25, "Low mastery (0.2): moderate boost")

    @Rule(TopicFact(mastery=0.3))
    def R_Master_04(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "MAS-04", 0.25, "Low mastery (0.3): moderate boost")

    @Rule(TopicFact(mastery=0.4))
    def R_Master_05(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "MAS-05", 0.10, "Medium mastery (0.4): small boost")

    @Rule(TopicFact(mastery=0.5))
    def R_Master_06(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "MAS-06", 0.10, "Medium mastery (0.5): small boost")

    @Rule(TopicFact(mastery=0.8))
    def R_Master_07(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "MAS-07", -0.20, "High mastery (0.8): reduce focus")

    @Rule(TopicFact(mastery=0.9))
    def R_Master_08(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "MAS-08", -0.20, "High mastery (0.9): reduce focus")

    @Rule(TopicFact(mastery=1.0))
    def R_Master_09(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "MAS-09", -0.20, "High mastery (1.0): reduce focus")

    # Difficulty rules
    @Rule(TopicFact(difficulty=0.8))
    def R_Diff_01(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "DIF-01", 0.25, "Very hard topic (0.8)")

    @Rule(TopicFact(difficulty=0.9))
    def R_Diff_02(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "DIF-02", 0.25, "Very hard topic (0.9)")

    @Rule(TopicFact(difficulty=1.0))
    def R_Diff_03(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "DIF-03", 0.25, "Very hard topic (1.0)")

    @Rule(TopicFact(difficulty=0.6))
    def R_Diff_04(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "DIF-04", 0.15, "Hard topic (0.6)")

    @Rule(TopicFact(difficulty=0.7))
    def R_Diff_05(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "DIF-05", 0.15, "Hard topic (0.7)")

    # Importance rules
    @Rule(TopicFact(importance=1.5))
    def R_Imp_01(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "IMP-01", 0.20, "High-importance course (1.5)")

    @Rule(TopicFact(importance=1.6))
    def R_Imp_02(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "IMP-02", 0.20, "High-importance course (1.6)")

    @Rule(TopicFact(importance=1.7))
    def R_Imp_03(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "IMP-03", 0.20, "High-importance course (1.7)")

    @Rule(TopicFact(importance=1.8))
    def R_Imp_04(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "IMP-04", 0.20, "High-importance course (1.8)")

    @Rule(TopicFact(importance=1.9))
    def R_Imp_05(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "IMP-05", 0.20, "High-importance course (1.9)")

    @Rule(TopicFact(importance=2.0))
    def R_Imp_06(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "IMP-06", 0.20, "High-importance course (2.0)")

    @Rule(TopicFact(importance=1.2))
    def R_Imp_07(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "IMP-07", 0.10, "Moderately important course (1.2)")

    @Rule(TopicFact(importance=1.3))
    def R_Imp_08(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "IMP-08", 0.10, "Moderately important course (1.3)")

    @Rule(TopicFact(importance=1.4))
    def R_Imp_09(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "IMP-09", 0.10, "Moderately important course (1.4)")

    # Exam type rules
    @Rule(TopicFact(exam_type="mcq"))
    def R_Exam_01(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "EXM-01", 0.05, "MCQ: frequent short reviews beneficial")

    @Rule(TopicFact(exam_type="written"))
    def R_Exam_02(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "EXM-02", 0.10, "Written: deeper practice sessions")

    @Rule(TopicFact(exam_type="practical"))
    def R_Exam_03(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "EXM-03", 0.15, "Practical: hands-on time emphasis")

    @Rule(TopicFact(exam_type="oral"))
    def R_Exam_04(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "EXM-04", 0.12, "Oral: practice speaking/explaining")

    # Prerequisites rules
    @Rule(TopicFact(prereqs=["limits"]))
    def R_Prereq_01(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "PRE-01", 0.10, "Has prerequisites: schedule earlier")

    @Rule(TopicFact(prereqs=["derivatives"]))
    def R_Prereq_02(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "PRE-02", 0.10, "Has prerequisites: schedule earlier")

    @Rule(TopicFact(prereqs=["integration"]))
    def R_Prereq_03(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "PRE-03", 0.10, "Has prerequisites: schedule earlier")

    @Rule(TopicFact(prereqs=["algebra"]))
    def R_Prereq_04(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "PRE-04", 0.10, "Has prerequisites: schedule earlier")

    @Rule(TopicFact(prereqs=["geometry"]))
    def R_Prereq_05(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "PRE-05", 0.10, "Has prerequisites: schedule earlier")

    # Spaced repetition rules
    @Rule(TopicFact(days_to_exam=21))
    def R_Space_01(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-01", 0.05, "Plenty of time: plan spaced repetition")

    @Rule(TopicFact(days_to_exam=22))
    def R_Space_02(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-02", 0.05, "Plenty of time: plan spaced repetition")

    @Rule(TopicFact(days_to_exam=23))
    def R_Space_03(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-03", 0.05, "Plenty of time: plan spaced repetition")

    @Rule(TopicFact(days_to_exam=24))
    def R_Space_04(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-04", 0.05, "Plenty of time: plan spaced repetition")

    @Rule(TopicFact(days_to_exam=25))
    def R_Space_05(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-05", 0.05, "Plenty of time: plan spaced repetition")

    @Rule(TopicFact(days_to_exam=26))
    def R_Space_06(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-06", 0.05, "Plenty of time: plan spaced repetition")

    @Rule(TopicFact(days_to_exam=27))
    def R_Space_07(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-07", 0.05, "Plenty of time: plan spaced repetition")

    @Rule(TopicFact(days_to_exam=28))
    def R_Space_08(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-08", 0.05, "Plenty of time: plan spaced repetition")

    @Rule(TopicFact(days_to_exam=29))
    def R_Space_09(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-09", 0.05, "Plenty of time: plan spaced repetition")

    @Rule(TopicFact(days_to_exam=30))
    def R_Space_10(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-10", 0.05, "Plenty of time: plan spaced repetition")

    # Buffer day rules
    @Rule(TopicFact(days_to_exam=2))
    def R_Buffer_01(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "BUF-01", 0.05, "Add buffer/review sessions near exam")

    @Rule(TopicFact(days_to_exam=1))
    def R_Buffer_02(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "BUF-02", 0.05, "Add buffer/review sessions near exam")

    # Combo rules for low mastery + high difficulty
    @Rule(TopicFact(mastery=0.0, difficulty=0.8))
    def R_Combo_01(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-01", 0.12, "Low mastery and high difficulty: prioritize")

    @Rule(TopicFact(mastery=0.1, difficulty=0.8))
    def R_Combo_02(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-02", 0.12, "Low mastery and high difficulty: prioritize")

    @Rule(TopicFact(mastery=0.2, difficulty=0.8))
    def R_Combo_03(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-03", 0.12, "Low mastery and high difficulty: prioritize")

    @Rule(TopicFact(mastery=0.3, difficulty=0.8))
    def R_Combo_04(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-04", 0.12, "Low mastery and high difficulty: prioritize")

    @Rule(TopicFact(mastery=0.0, difficulty=0.9))
    def R_Combo_05(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-05", 0.12, "Low mastery and high difficulty: prioritize")

    @Rule(TopicFact(mastery=0.1, difficulty=0.9))
    def R_Combo_06(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-06", 0.12, "Low mastery and high difficulty: prioritize")

    @Rule(TopicFact(mastery=0.2, difficulty=0.9))
    def R_Combo_07(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-07", 0.12, "Low mastery and high difficulty: prioritize")

    @Rule(TopicFact(mastery=0.3, difficulty=0.9))
    def R_Combo_08(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-08", 0.12, "Low mastery and high difficulty: prioritize")

    @Rule(TopicFact(mastery=0.0, difficulty=1.0))
    def R_Combo_09(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-09", 0.12, "Low mastery and high difficulty: prioritize")

    @Rule(TopicFact(mastery=0.1, difficulty=1.0))
    def R_Combo_10(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-10", 0.12, "Low mastery and high difficulty: prioritize")

    @Rule(TopicFact(mastery=0.2, difficulty=1.0))
    def R_Combo_11(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-11", 0.12, "Low mastery and high difficulty: prioritize")

    @Rule(TopicFact(mastery=0.3, difficulty=1.0))
    def R_Combo_12(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-12", 0.12, "Low mastery and high difficulty: prioritize")

    # Combo rules for high importance + high difficulty
    @Rule(TopicFact(importance=1.3, difficulty=0.8))
    def R_Combo_13(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-13", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.4, difficulty=0.8))
    def R_Combo_14(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-14", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.5, difficulty=0.8))
    def R_Combo_15(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-15", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.6, difficulty=0.8))
    def R_Combo_16(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-16", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.7, difficulty=0.8))
    def R_Combo_17(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-17", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.8, difficulty=0.8))
    def R_Combo_18(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-18", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.9, difficulty=0.8))
    def R_Combo_19(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-19", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=2.0, difficulty=0.8))
    def R_Combo_20(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-20", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.3, difficulty=0.9))
    def R_Combo_21(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-21", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.4, difficulty=0.9))
    def R_Combo_22(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-22", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.5, difficulty=0.9))
    def R_Combo_23(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-23", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.6, difficulty=0.9))
    def R_Combo_24(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-24", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.7, difficulty=0.9))
    def R_Combo_25(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-25", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.8, difficulty=0.9))
    def R_Combo_26(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-26", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.9, difficulty=0.9))
    def R_Combo_27(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-27", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=2.0, difficulty=0.9))
    def R_Combo_28(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-28", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.3, difficulty=1.0))
    def R_Combo_29(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-29", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.4, difficulty=1.0))
    def R_Combo_30(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-30", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.5, difficulty=1.0))
    def R_Combo_31(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-31", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.6, difficulty=1.0))
    def R_Combo_32(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-32", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.7, difficulty=1.0))
    def R_Combo_33(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-33", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.8, difficulty=1.0))
    def R_Combo_34(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-34", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=1.9, difficulty=1.0))
    def R_Combo_35(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-35", 0.10, "Hard and important: additional boost")

    @Rule(TopicFact(importance=2.0, difficulty=1.0))
    def R_Combo_36(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "CMB-36", 0.10, "Hard and important: additional boost")

    # Penalty rules for very high mastery
    @Rule(TopicFact(mastery=0.9))
    def R_Penalty_01(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "PEN-01", -0.10, "Very high mastery: deprioritize")

    @Rule(TopicFact(mastery=1.0))
    def R_Penalty_02(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "PEN-02", -0.10, "Very high mastery: deprioritize")

    # Triage rules for very large topics
    @Rule(TopicFact(est_hours=16.0))
    def R_Triage_01(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "TRG-01", -0.05, "Very large topic: may need trimming")

    @Rule(TopicFact(est_hours=20.0))
    def R_Triage_02(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "TRG-02", -0.05, "Very large topic: may need trimming")

    @Rule(TopicFact(est_hours=25.0))
    def R_Triage_03(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "TRG-03", -0.05, "Very large topic: may need trimming")

    @Rule(TopicFact(est_hours=30.0))
    def R_Triage_04(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "TRG-04", -0.05, "Very large topic: may need trimming")

    # Additional spaced repetition rules for moderate time
    @Rule(TopicFact(days_to_exam=15))
    def R_Space_11(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-11", 0.08, "Moderate time: ensure multiple touches")

    @Rule(TopicFact(days_to_exam=16))
    def R_Space_12(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-12", 0.08, "Moderate time: ensure multiple touches")

    @Rule(TopicFact(days_to_exam=17))
    def R_Space_13(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-13", 0.08, "Moderate time: ensure multiple touches")

    @Rule(TopicFact(days_to_exam=18))
    def R_Space_14(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-14", 0.08, "Moderate time: ensure multiple touches")

    @Rule(TopicFact(days_to_exam=19))
    def R_Space_15(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-15", 0.08, "Moderate time: ensure multiple touches")

    @Rule(TopicFact(days_to_exam=20))
    def R_Space_16(self):
        fact = self.get_current_fact()
        self.record(fact["topic_id"], "SPR-16", 0.08, "Moderate time: ensure multiple touches")
