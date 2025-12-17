# bodmas_ontology.py
#
# Build an ontology for a BODMAS-focused Intelligent Tutoring System
# using Owlready2. This script defines the core classes, properties,
# some example individuals, and an example SWRL rule.

from owlready2 import get_ontology, Thing, ObjectProperty, DataProperty


# Create / load ontology
onto = get_ontology(r"C:\Users\opeye\OneDrive\Documents\Assessment\Second Semester\AIC\BODMAS\bodmas_tutor.owx")


with onto:
    # =========================
    # Core classes
    # =========================
    class Expression(Thing):
        """Any arithmetic expression."""
        pass

    class SimpleExpression(Expression):
        """Expression with a single operation."""
        pass

    class CompoundExpression(Expression):
        """Expression with multiple operations / nested parts."""
        pass

    class Operation(Thing):
        """An arithmetic operation occurring in an expression."""
        pass

    class BracketOperation(Operation):
        pass

    class OrderOperation(Operation):
        """Powers / roots etc."""
        pass

    class DivisionOperation(Operation):
        pass

    class MultiplicationOperation(Operation):
        pass

    class AdditionOperation(Operation):
        pass

    class SubtractionOperation(Operation):
        pass

    class BODMASStage(Thing):
        """Brackets, Orders, Division/Multiplication, Addition/Subtraction."""
        pass

    class Skill(Thing):
        """A sub-skill, e.g. 'Apply brackets first'."""
        pass

    class ErrorPattern(Thing):
        """A recurring type of error / misconception."""
        pass

    class IgnoredBracketsError(ErrorPattern):
        """Student ignored brackets that should be evaluated first."""
        pass

    class IgnoredPrecedenceError(ErrorPattern):
        """Student chose a lower-precedence operation while a higher one was available."""
        pass

    class FeedbackAction(Thing):
        """A tutoring action triggered by an error pattern."""
        pass

    class Student(Thing):
        """Learner using the tutor."""
        pass

    class Attempt(Thing):
        """A single step in solving an expression."""
        pass

    # =========================
    # Object properties
    # =========================
    class hasOperation(ObjectProperty):
        domain = [Expression]
        range = [Operation]

    class hasSubExpression(ObjectProperty):
        domain = [CompoundExpression]
        range = [Expression]

    class hasStage(ObjectProperty):
        domain = [Operation]
        range = [BODMASStage]

    class targetsStage(ObjectProperty):
        domain = [Skill]
        range = [BODMASStage]

    class attemptOf(ObjectProperty):
        domain = [Attempt]
        range = [Expression]

    class performedBy(ObjectProperty):
        domain = [Attempt]
        range = [Student]

    class appliedOperation(ObjectProperty):
        domain = [Attempt]
        range = [Operation]

    class violatesError(ObjectProperty):
        domain = [Attempt]
        range = [ErrorPattern]

    class suggestsFeedback(ObjectProperty):
        domain = [ErrorPattern]
        range = [FeedbackAction]

    class hasNextProblem(ObjectProperty):
        """Optional link from a student to the next recommended expression."""
        domain = [Student]
        range = [Expression]

    # =========================
    # Data properties
    # =========================
    class hasDifficultyLevel(DataProperty):
        domain = [Expression]
        range = [int]

    class hasPrecedenceLevel(DataProperty):
        """Numeric precedence: Brackets=4, Orders=3, Div/Mul=2, Add/Sub=1."""
        domain = [BODMASStage]
        range = [int]

    class hasMastery(DataProperty):
        """Mastery score for a skill (0–1)."""
        domain = [Skill]
        range = [float]

    class isCorrectStep(DataProperty):
        domain = [Attempt]
        range = [bool]

    class timeTakenSeconds(DataProperty):
        domain = [Attempt]
        range = [int]

    class naturalLanguageText(DataProperty):
        """Human-readable text for a feedback action."""
        domain = [FeedbackAction]
        range = [str]

    # =========================
    # Stage individuals (BODMAS)
    # =========================
    stage_brackets = BODMASStage("StageBrackets")
    stage_orders = BODMASStage("StageOrders")
    stage_div_mul = BODMASStage("StageDivMul")
    stage_add_sub = BODMASStage("StageAddSub")

    stage_brackets.hasPrecedenceLevel.append(4)
    stage_orders.hasPrecedenceLevel.append(3)
    stage_div_mul.hasPrecedenceLevel.append(2)
    stage_add_sub.hasPrecedenceLevel.append(1)

    # =========================
    # Feedback actions
    # =========================
    fb_concept_hint = FeedbackAction("GiveConceptHint")
    fb_concept_hint.naturalLanguageText.append(
        "Remember BODMAS: solve brackets and orders before multiplication, "
        "division, addition and subtraction."
    )

    fb_worked_example = FeedbackAction("ShowWorkedExample")
    fb_worked_example.naturalLanguageText.append(
        "Let us walk through a similar expression step by step."
    )

    fb_simpler_problem = FeedbackAction("SuggestSimplerProblem")
    fb_simpler_problem.naturalLanguageText.append(
        "Let's try a simpler expression with the same idea, then come back to this one."
    )

    # =========================
    # Error patterns
    # =========================
    ignored_brackets = IgnoredBracketsError("IgnoredBrackets")
    ignored_brackets.suggestsFeedback.append(fb_concept_hint)

    ignored_precedence = IgnoredPrecedenceError("IgnoredPrecedence")
    ignored_precedence.suggestsFeedback.append(fb_concept_hint)

    # You can map specific errors to different feedback if desired
    # e.g. ignored_precedence.suggestsFeedback.append(fb_worked_example)

    # =========================
    # Skills
    # =========================
    skill_brackets_first = Skill("SkillApplyBracketsFirst")
    skill_brackets_first.targetsStage.append(stage_brackets)
    skill_brackets_first.hasMastery.append(0.0)

    skill_orders = Skill("SkillApplyOrders")
    skill_orders.targetsStage.append(stage_orders)
    skill_orders.hasMastery.append(0.0)

    skill_div_mul = Skill("SkillDivMulBeforeAddSub")
    skill_div_mul.targetsStage.append(stage_div_mul)
    skill_div_mul.hasMastery.append(0.0)

    skill_add_sub = Skill("SkillAddSubAtEnd")
    skill_add_sub.targetsStage.append(stage_add_sub)
    skill_add_sub.hasMastery.append(0.0)

    # =========================
    # Example expression, operations, student and attempt
    # =========================
    # Expression: 7 + 3 × 4  (without brackets)
    expr1 = CompoundExpression("Expr_7_plus_3_times_4")
    expr1.hasDifficultyLevel.append(1)

    op_add = AdditionOperation("Plus_Expr1")
    op_mul = MultiplicationOperation("Times_Expr1")

    op_add.hasStage.append(stage_add_sub)
    op_mul.hasStage.append(stage_div_mul)

    expr1.hasOperation.extend([op_add, op_mul])

    # Example student
    s1 = Student("Student_Ali")

    # Attempt: student incorrectly chooses to do addition first
    attempt1 = Attempt("Attempt1")
    attempt1.performedBy.append(s1)
    attempt1.attemptOf.append(expr1)
    attempt1.appliedOperation.append(op_add)
    attempt1.isCorrectStep.append(False)
    attempt1.timeTakenSeconds.append(15)

    # For now we can manually attach an error pattern
    attempt1.violatesError.append(ignored_precedence)

    # =========================
    # Example SWRL rule
    # =========================
    #
    # Idea:
    # If an Attempt uses an operation whose BODMAS stage has a LOWER
    # precedenceLevel than another operation still in the same Expression,
    # then classify that Attempt as an IgnoredPrecedenceError.
    #
    # Note: SWRL rule with built-ins (swrlb:lessThan) is commented out
    # because owlready2 has limited SWRL support. You can implement this
    # logic in Python or use a full reasoner (Pellet, Hermit) externally.
    
    # rule_ignored_precedence = Imp()
    # rule_ignored_precedence.set_as_rule("""
    #     Attempt(?a),
    #     appliedOperation(?a, ?opLow),
    #     hasStage(?opLow, ?stageLow),
    #     hasPrecedenceLevel(?stageLow, ?pLow),
    #     attemptOf(?a, ?expr),
    #     hasOperation(?expr, ?opHigh),
    #     hasStage(?opHigh, ?stageHigh),
    #     hasPrecedenceLevel(?stageHigh, ?pHigh),
    #     swrlb:lessThan(?pLow, ?pHigh)
    #     ->
    #     IgnoredPrecedenceError(?a)
    # """)


# =========================
# Save ontology
# =========================
def main():
    print("Classes in ontology:", list(onto.classes()))
    onto.save(file="bodmas_tutor.owl", format="rdfxml")
    print("Ontology saved as bodmas_tutor.owl")
    
    # Start Flask web server
    print("\n" + "="*60)
    print("🎓 BODMAS Master - Intelligent Tutoring System")
    print("="*60)
    print("Starting web interface...")
    print("Opening browser at http://localhost:5000\n")
    
    import webbrowser
    import threading
    import time
    from flask_app import app
    
    # Start Flask in a background thread
    def run_flask():
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Give Flask a moment to start, then open browser
    time.sleep(2)
    webbrowser.open('http://localhost:5000')
    
    # Keep the main thread alive
    try:
        flask_thread.join()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")


if __name__ == "__main__":
    main()
