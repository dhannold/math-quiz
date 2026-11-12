from drafter import *
from dataclasses import dataclass
from random import randint, choice
from time import time

@dataclass
class MathProblem:
    first_number: int
    second_number: int
    operation: str
    correct_answer: int
    user_answer: str
    was_correct: bool
    time_taken: int


@dataclass
class State:
    name: str
    current_page: str
    first_number: int
    second_number: int
    operation: str
    correct_answer: int
    user_answer: str
    feedback: str
    score: int
    questions_answered: int
    problems: list[MathProblem]
    time_limit: int
    start_time: float
    question_started_at: float
    practice_mode: str

set_website_title("MathQuiz")
set_site_information(
    author="Danielle Hannold",
    description="Practice your basic math skills!",
    sources="Thanks to the Drafter docs and my study group.",
    planning=["project_design.pdf", "project_pick.pdf", "chatgpt.pdf"],
    links=["https://github.com/dhannold/math-quiz/blob/main/project_design.pdf",
           "https://github.com/dhannold/math-quiz/blob/main/project_pick.pdf",
           "https://github.com/dhannold/math-quiz/blob/main/chatgpt.pdf"]
)
hide_debug_information()
set_website_framed(False)

def make_question(state: State) -> None:
    """Creates a random math question and updates the state.

    Exact question values cannot be predicted because numbers
    and operations are randomly selected, making exact-output
    unit tests impractical.
    """
    mode = state.practice_mode

    if mode == "combination":
        operation = choice(["+", "-", "*", "/"])
    elif mode == "whole_division":
        operation = "/"
    else:
        operation = mode

    state.operation = operation
    state.first_number = randint(1, 12)
    state.second_number = randint(1, 12)

    if operation == "+":
        state.correct_answer = (
            state.first_number + state.second_number
        )

    elif operation == "-":
        state.correct_answer = (
            state.first_number - state.second_number
        )

    elif operation == "*":
        state.correct_answer = (
            state.first_number * state.second_number
        )

    elif operation == "/":
        state.correct_answer = randint(1, 12)
        state.first_number = (
            state.second_number * state.correct_answer
        )

    state.user_answer = ""
    state.question_started_at = time()

@route
def index(state: State) -> Page:
    """
    Displays the home page and practice choices.
    """
    state.current_page = "home"

    return Page(state, [
        Header("Math Practice"),
        "Welcome! Choose what you would like to practice.",
        Button("Addition", "addition"),
        Button("Multiplication", "multiplication"),
        Button("Subtraction", "subtraction"),
        Button("Whole Number Division", "whole_division"),
        Button("Combination", "combination"),
    ])


def setup_page(state: State, operation: str) -> Page:
    """
    Displays the setup page for the selected operation.
    """
    state.practice_mode = operation
    state.operation = operation
    state.current_page = "setup"

    return Page(state, [
        Header("Math Practice Setup"),
        "What is your name?",
        TextBox("name"),
        "Selected practice: " + operation,
        "How many seconds would you like to practice?",
        TextBox("time_limit", "60"),
        Button("Start Practice", "start_practice"),
        Button("Back to Home", "index"),
    ])


@route
def addition(state: State) -> Page:
    """
    Displays the setup page for addition practice.
    """
    return setup_page(state, "+")


@route
def multiplication(state: State) -> Page:
    """
    Displays the setup page for multiplication practice.
    """
    return setup_page(state, "*")


@route
def subtraction(state: State) -> Page:
    """
    Displays the setup page for subtraction practice.
    """
    return setup_page(state, "-")


@route
def whole_division(state: State) -> Page:
    """
    Displays the setup page for whole number division practice.
    """
    return setup_page(state, "/")

@route
def combination(state: State) -> Page:
    """
    Displays the setup page for mixed operation practice.
    """
    return setup_page(state, "combination")
    
@route
def start_practice(state: State, time_limit: int, name: str) -> Page:
    """Starts a practice session with the chosen settings."""

    if time_limit <= 0:
        return setup_page(state, state.operation)

    state.name = name
    state.time_limit = time_limit
    state.score = 0
    state.questions_answered = 0
    state.problems = []
    state.start_time = time()

    make_question(state)

    return practice(state)

@route
def practice(state: State) -> Page:
    """
    Displays the current question and practice progress.
    """
    state.current_page = "practice"

    elapsed = int(time() - state.start_time)
    remaining = state.time_limit - elapsed

    if remaining <= 0:
        return results(state)

    question = (
        str(state.first_number)
        + " "
        + state.operation
        + " "
        + str(state.second_number)
    )

    return Page(state, [
        Header("Math Practice"),
        "Good luck, " + state.name + "!",
        "Time remaining: " + str(remaining) + " seconds",
        "Score: " + str(state.score),
        "Questions answered: " + str(state.questions_answered),
        Header(question),
        "Enter your answer:",
        TextBox("user_answer"),
        Button("Submit Answer", "submit_answer"),
        state.feedback,
    ])

@route
def submit_answer(state: State, user_answer: str) -> Page:
    """
    Checks the user's answer and updates the score.
    """
    current_time = time()

    elapsed = int(current_time - state.start_time)

    if elapsed >= state.time_limit:
        return results(state)

    # Check whether the answer is a valid integer.
    if not user_answer.strip().lstrip("-").isdigit() or user_answer.strip().count("-") > 1:
        state.feedback = "Please enter a whole number."
        return practice(state)

    answer = int(user_answer)

    was_correct = answer == state.correct_answer

    if was_correct:
        state.score += 1
        state.feedback = "Correct! Great job!"
    else:
        state.feedback = (
            "Incorrect. The correct answer was "
            + str(state.correct_answer)
        )

    state.questions_answered += 1

    # Save this question for the review page.
    problem = MathProblem(
        state.first_number,
        state.second_number,
        state.operation,
        state.correct_answer,
        user_answer,
        was_correct,
        int(current_time - state.question_started_at),
    )

    state.problems.append(problem)

    # Generate another question.
    make_question(state)

    return practice(state)

@route
def results(state: State) -> Page:
    """
    Displays the final practice results.
    """
    state.current_page = "results"

    return Page(state, [
        Header("Practice Complete!"),
        "Great work, " + state.name + "!",
        Header("Your Results"),
        "Your score: " + str(state.score),
        "Questions answered: " + str(state.questions_answered),
        "Incorrect answers: " + str(
            state.questions_answered - state.score
        ),
        Button("Review My Answers", "review"),
        Button("Practice Again", "index"),
    ])

@route
def review(state: State) -> Page:
    """
    Displays the user's previous questions and answers.
    """
    content = [
        Header("Answer Review"),
        "Here are all the questions you answered.",
    ]

    for problem in state.problems:

        question = (
            str(problem.first_number)
            + " "
            + problem.operation
            + " "
            + str(problem.second_number)
        )

        content.append(Header(question))

        content.append(
            "Your answer: " + problem.user_answer
        )

        content.append(
            "Correct answer: " + str(problem.correct_answer)
        )

        content.append(
            "Time taken: " + str(problem.time_taken) + " seconds"
        )

        if problem.was_correct:
            content.append("Result: Correct!")
        else:
            content.append("Result: Incorrect")

        content.append(HorizontalRule())

    content.append(Button("Back to Results", "results"))
    content.append(Button("Practice Again", "index"))

    return Page(state, content)

initial_state = State(
    name = "",
    current_page="home",
    first_number=0,
    second_number=0,
    operation="+",
    correct_answer=0,
    user_answer="",
    feedback="",
    score=0,
    questions_answered=0,
    problems=[],
    time_limit=60,
    start_time=0.0,
    question_started_at=0.0,
    practice_mode="+"
)
# --------------------
# Test index
# --------------------

assert_equal(index(State(
    current_page="", name="Alex", first_number=0, second_number=0,
    operation="+", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="+"
)).state.current_page, "home")

assert_equal(index(State(
    current_page="setup", name="Sam", first_number=2, second_number=3,
    operation="*", correct_answer=6, user_answer="", feedback="",
    score=5, questions_answered=5, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="*"
)).state.current_page, "home")

assert_equal(index(State(
    current_page="results", name="Taylor", first_number=4, second_number=2,
    operation="-", correct_answer=2, user_answer="2", feedback="",
    score=3, questions_answered=4, problems=[], time_limit=30,
    start_time=0.0, question_started_at=0.0, practice_mode="-"
)).state.current_page, "home")


# --------------------
# Test setup_page
# --------------------

assert_equal(setup_page(State(
    current_page="home", name="Alex", first_number=0, second_number=0,
    operation="+", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="+"
), "+").state.practice_mode, "+")

assert_equal(setup_page(State(
    current_page="home", name="Alex", first_number=0, second_number=0,
    operation="+", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="+"
), "*").state.operation, "*")

assert_equal(setup_page(State(
    current_page="home", name="Alex", first_number=0, second_number=0,
    operation="+", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="+"
), "-").state.current_page, "setup")


# --------------------
# Test addition
# --------------------

assert_equal(addition(State(
    current_page="home", name="Alex", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.practice_mode, "+")

assert_equal(addition(State(
    current_page="home", name="Sam", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.current_page, "setup")

assert_equal(addition(State(
    current_page="results", name="Taylor", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=5, questions_answered=5, problems=[], time_limit=30,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.operation, "+")


# --------------------
# Test multiplication
# --------------------

assert_equal(multiplication(State(
    current_page="home", name="Alex", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.practice_mode, "*")

assert_equal(multiplication(State(
    current_page="home", name="Sam", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.current_page, "setup")

assert_equal(multiplication(State(
    current_page="results", name="Taylor", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=5, questions_answered=5, problems=[], time_limit=30,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.operation, "*")


# --------------------
# Test subtraction
# --------------------

assert_equal(subtraction(State(
    current_page="home", name="Alex", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.practice_mode, "-")

assert_equal(subtraction(State(
    current_page="home", name="Sam", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.current_page, "setup")

assert_equal(subtraction(State(
    current_page="results", name="Taylor", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=5, questions_answered=5, problems=[], time_limit=30,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.operation, "-")


# --------------------
# Test whole_division
# --------------------

assert_equal(whole_division(State(
    current_page="home", name="Alex", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.practice_mode, "/")

assert_equal(whole_division(State(
    current_page="home", name="Sam", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.current_page, "setup")

assert_equal(whole_division(State(
    current_page="results", name="Taylor", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=5, questions_answered=5, problems=[], time_limit=30,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.operation, "/")


# --------------------
# Test combination
# --------------------

assert_equal(combination(State(
    current_page="home", name="Alex", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.practice_mode, "combination")

assert_equal(combination(State(
    current_page="home", name="Sam", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.current_page, "setup")

assert_equal(combination(State(
    current_page="results", name="Taylor", first_number=0, second_number=0,
    operation="", correct_answer=0, user_answer="", feedback="",
    score=5, questions_answered=5, problems=[], time_limit=30,
    start_time=0.0, question_started_at=0.0, practice_mode=""
)).state.operation, "combination")


# --------------------
# Test start_practice
# --------------------

assert_equal(start_practice(State(
    current_page="setup", name="", first_number=0, second_number=0,
    operation="+", correct_answer=0, user_answer="", feedback="",
    score=5, questions_answered=5, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="+"
), 60, "Alex").state.name, "Alex")

assert_equal(start_practice(State(
    current_page="setup", name="", first_number=0, second_number=0,
    operation="*", correct_answer=0, user_answer="", feedback="",
    score=5, questions_answered=5, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="*"
), 30, "Sam").state.score, 0)

assert_equal(start_practice(State(
    current_page="setup", name="", first_number=0, second_number=0,
    operation="-", correct_answer=0, user_answer="", feedback="",
    score=5, questions_answered=5, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="-"
), 0, "Taylor").state.current_page, "setup")

# Tests whether the selected name is saved.
assert_equal(start_practice(State(
    current_page="setup", name="", first_number=0, second_number=0,
    operation="+", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="+"
), 45, "Jordan").state.name, "Jordan")

# Tests whether the selected time limit is saved.
assert_equal(start_practice(State(
    current_page="setup", name="", first_number=0, second_number=0,
    operation="*", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="*"
), 90, "Morgan").state.time_limit, 90)

# Tests whether the number of questions answered is reset.
assert_equal(start_practice(State(
    current_page="setup", name="", first_number=0, second_number=0,
    operation="-", correct_answer=0, user_answer="", feedback="",
    score=5, questions_answered=8, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="-"
), 30, "Riley").state.questions_answered, 0)

# Tests whether previous problems are cleared.
assert_equal(start_practice(State(
    current_page="setup", name="", first_number=0, second_number=0,
    operation="+", correct_answer=0, user_answer="", feedback="",
    score=5, questions_answered=1,
    problems=[MathProblem(2, 3, "+", 5, "5", True, 2)],
    time_limit=60, start_time=0.0, question_started_at=0.0,
    practice_mode="+"
), 30, "Casey").state.problems, [])

# Tests whether a negative time limit is rejected.
assert_equal(start_practice(State(
    current_page="setup", name="", first_number=0, second_number=0,
    operation="+", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="+"
), -10, "Alex").state.current_page, "setup")


# --------------------
# Test practice
# --------------------

assert_equal(practice(State(
    current_page="practice", name="Alex", first_number=2, second_number=3,
    operation="+", correct_answer=5, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=time(), question_started_at=time(), practice_mode="+"
)).state.current_page, "practice")

assert_equal(practice(State(
    current_page="practice", name="Sam", first_number=4, second_number=2,
    operation="*", correct_answer=8, user_answer="", feedback="",
    score=2, questions_answered=3, problems=[], time_limit=60,
    start_time=time(), question_started_at=time(), practice_mode="*"
)).state.score, 2)

assert_equal(practice(State(
    current_page="practice", name="Taylor", first_number=4, second_number=2,
    operation="-", correct_answer=2, user_answer="", feedback="",
    score=2, questions_answered=3, problems=[], time_limit=1,
    start_time=0.0, question_started_at=0.0, practice_mode="-"
)).state.current_page, "results")

# Tests whether the user's name is preserved.
assert_equal(practice(State(
    current_page="practice", name="Jordan", first_number=2,
    second_number=3, operation="+", correct_answer=5,
    user_answer="", feedback="", score=2, questions_answered=3,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="+"
)).state.name, "Jordan")

# Tests whether the score remains unchanged when displaying the page.
assert_equal(practice(State(
    current_page="practice", name="Morgan", first_number=4,
    second_number=5, operation="*", correct_answer=20,
    user_answer="", feedback="", score=4, questions_answered=6,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="*"
)).state.score, 4)

# Tests whether the number of answered questions remains unchanged.
assert_equal(practice(State(
    current_page="practice", name="Riley", first_number=8,
    second_number=3, operation="-", correct_answer=5,
    user_answer="", feedback="", score=2, questions_answered=7,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="-"
)).state.questions_answered, 7)

# Tests whether an expired practice session displays the results page.
assert_equal(practice(State(
    current_page="practice", name="Casey", first_number=8,
    second_number=4, operation="/", correct_answer=2,
    user_answer="", feedback="", score=3, questions_answered=5,
    problems=[], time_limit=1, start_time=0.0,
    question_started_at=0.0, practice_mode="/"
)).state.current_page, "results")


# --------------------
# Test submit_answer
# --------------------

assert_equal(submit_answer(State(
    current_page="practice", name="Alex", first_number=3, second_number=4,
    operation="+", correct_answer=7, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=time(), question_started_at=time(), practice_mode="+"
), "7").state.score, 1)

assert_equal(submit_answer(State(
    current_page="practice", name="Sam", first_number=3, second_number=4,
    operation="+", correct_answer=7, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=time(), question_started_at=time(), practice_mode="+"
), "9").state.questions_answered, 1)

assert_equal(submit_answer(State(
    current_page="practice", name="Taylor", first_number=3, second_number=4,
    operation="+", correct_answer=7, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=60,
    start_time=time(), question_started_at=time(), practice_mode="+"
), "hello").state.questions_answered, 0)

# Tests whether an incorrect answer leaves the score unchanged.
assert_equal(submit_answer(State(
    current_page="practice", name="Alex", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=2, questions_answered=2,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="+"
), "9").state.score, 2)

# Tests whether a correct answer increases an existing score.
assert_equal(submit_answer(State(
    current_page="practice", name="Jordan", first_number=5,
    second_number=5, operation="*", correct_answer=25,
    user_answer="", feedback="", score=3, questions_answered=3,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="*"
), "25").state.score, 4)

# Tests whether a valid incorrect answer still increases the question count.
assert_equal(submit_answer(State(
    current_page="practice", name="Morgan", first_number=9,
    second_number=3, operation="-", correct_answer=6,
    user_answer="", feedback="", score=0, questions_answered=4,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="-"
), "5").state.questions_answered, 5)

# Tests whether a negative integer is accepted.
assert_equal(submit_answer(State(
    current_page="practice", name="Alex", first_number=3,
    second_number=5, operation="-", correct_answer=-2,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="-"
), "-2").state.score, 1)

# Tests whether an answer containing surrounding spaces is accepted.
assert_equal(submit_answer(State(
    current_page="practice", name="Jordan", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="+"
), " 7 ").state.score, 1)

# Tests whether a decimal answer is rejected.
assert_equal(submit_answer(State(
    current_page="practice", name="Morgan", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="+"
), "7.5").state.questions_answered, 0)

# Tests whether an empty answer is rejected.
assert_equal(submit_answer(State(
    current_page="practice", name="Riley", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="+"
), "").state.questions_answered, 0)

# Tests whether an answer containing only spaces is rejected.
assert_equal(submit_answer(State(
    current_page="practice", name="Casey", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="+"
), "   ").state.questions_answered, 0)

# Tests whether alphabetic input is rejected.
assert_equal(submit_answer(State(
    current_page="practice", name="Taylor", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="+"
), "hello").state.questions_answered, 0)

# Tests the feedback message after a correct answer.
assert_equal(submit_answer(State(
    current_page="practice", name="Alex", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="+"
), "7").state.feedback, "Correct! Great job!")

# Tests the feedback message after an incorrect answer.
assert_equal(submit_answer(State(
    current_page="practice", name="Jordan", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="+"
), "9").state.feedback, "Incorrect. The correct answer was 7")

# Tests the feedback message after invalid input.
assert_equal(submit_answer(State(
    current_page="practice", name="Morgan", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="+"
), "hello").state.feedback, "Please enter a whole number.")

# Tests whether a correctly answered problem is saved.
assert_equal(submit_answer(State(
    current_page="practice", name="Alex", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="+"
), "7").state.problems[0].was_correct, True)

# Tests whether an incorrectly answered problem is saved.
assert_equal(submit_answer(State(
    current_page="practice", name="Jordan", first_number=8,
    second_number=3, operation="-", correct_answer=5,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="-"
), "6").state.problems[0].was_correct, False)

# Tests whether the user's submitted answer is saved in the problem record.
assert_equal(submit_answer(State(
    current_page="practice", name="Morgan", first_number=5,
    second_number=5, operation="*", correct_answer=25,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="*"
), "20").state.problems[0].user_answer, "20")

# Tests whether the original question's correct answer is saved.
assert_equal(submit_answer(State(
    current_page="practice", name="Riley", first_number=5,
    second_number=5, operation="*", correct_answer=25,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="*"
), "25").state.problems[0].correct_answer, 25)

# Tests whether the original operation is saved.
assert_equal(submit_answer(State(
    current_page="practice", name="Casey", first_number=5,
    second_number=5, operation="*", correct_answer=25,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="*"
), "25").state.problems[0].operation, "*")

# Tests whether an invalid answer is NOT saved as a completed problem.
assert_equal(submit_answer(State(
    current_page="practice", name="Taylor", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=time(),
    question_started_at=time(), practice_mode="+"
), "hello").state.problems, [])

# Tests whether submitting an answer after the time limit ends
# sends the user to the results page.
assert_equal(submit_answer(State(
    current_page="practice", name="Alex", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=2, questions_answered=3,
    problems=[], time_limit=1, start_time=0.0,
    question_started_at=0.0, practice_mode="+"
), "7").state.current_page, "results")

# Tests whether an expired session does not increase the score.
assert_equal(submit_answer(State(
    current_page="practice", name="Jordan", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=2, questions_answered=3,
    problems=[], time_limit=1, start_time=0.0,
    question_started_at=0.0, practice_mode="+"
), "7").state.score, 2)

# Tests whether an expired session does not save another problem.
assert_equal(submit_answer(State(
    current_page="practice", name="Morgan", first_number=3,
    second_number=4, operation="+", correct_answer=7,
    user_answer="", feedback="", score=2, questions_answered=3,
    problems=[], time_limit=1, start_time=0.0,
    question_started_at=0.0, practice_mode="+"
), "7").state.problems, [])

# --------------------
# Test results
# --------------------

assert_equal(results(State(
    current_page="practice", name="Alex", first_number=0, second_number=0,
    operation="+", correct_answer=0, user_answer="", feedback="",
    score=5, questions_answered=5, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="+"
)).state.score, 5)

assert_equal(results(State(
    current_page="practice", name="Sam", first_number=0, second_number=0,
    operation="*", correct_answer=0, user_answer="", feedback="",
    score=3, questions_answered=4, problems=[], time_limit=60,
    start_time=0.0, question_started_at=0.0, practice_mode="*"
)).state.questions_answered, 4)

assert_equal(results(State(
    current_page="practice", name="Taylor", first_number=0, second_number=0,
    operation="-", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=0, problems=[], time_limit=30,
    start_time=0.0, question_started_at=0.0, practice_mode="-"
)).state.current_page, "results")

# --------------------
# Additional results tests
# --------------------

# Tests a session where every answer was correct.
assert_equal(results(State(
    current_page="practice", name="Alex", first_number=0,
    second_number=0, operation="+", correct_answer=0,
    user_answer="", feedback="", score=5, questions_answered=5,
    problems=[], time_limit=60, start_time=0.0,
    question_started_at=0.0, practice_mode="+"
)).state.score, 5)

# Tests a session where every answer was incorrect.
assert_equal(results(State(
    current_page="practice", name="Jordan", first_number=0,
    second_number=0, operation="+", correct_answer=0,
    user_answer="", feedback="", score=0, questions_answered=5,
    problems=[], time_limit=60, start_time=0.0,
    question_started_at=0.0, practice_mode="+"
)).state.score, 0)

# Tests a session where no questions were answered.
assert_equal(results(State(
    current_page="practice", name="Morgan", first_number=0,
    second_number=0, operation="+", correct_answer=0,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=0.0,
    question_started_at=0.0, practice_mode="+"
)).state.questions_answered, 0)

# Tests whether the user's name is preserved on the results page.
assert_equal(results(State(
    current_page="practice", name="Riley", first_number=0,
    second_number=0, operation="+", correct_answer=0,
    user_answer="", feedback="", score=3, questions_answered=5,
    problems=[], time_limit=60, start_time=0.0,
    question_started_at=0.0, practice_mode="+"
)).state.name, "Riley")

# --------------------
# Test review
# --------------------

assert_equal(review(State(
    current_page="results", name="Alex", first_number=0, second_number=0,
    operation="+", correct_answer=0, user_answer="", feedback="",
    score=1, questions_answered=1,
    problems=[MathProblem(3, 4, "+", 7, "7", True, 2)],
    time_limit=60, start_time=0.0, question_started_at=0.0,
    practice_mode="+"
)).state.problems[0].was_correct, True)

assert_equal(review(State(
    current_page="results", name="Sam", first_number=0, second_number=0,
    operation="-", correct_answer=0, user_answer="", feedback="",
    score=0, questions_answered=1,
    problems=[MathProblem(8, 3, "-", 5, "6", False, 4)],
    time_limit=60, start_time=0.0, question_started_at=0.0,
    practice_mode="-"
)).state.problems[0].user_answer, "6")

assert_equal(len(review(State(
    current_page="results", name="Taylor", first_number=0, second_number=0,
    operation="*", correct_answer=0, user_answer="", feedback="",
    score=1, questions_answered=2,
    problems=[
        MathProblem(3, 4, "*", 12, "12", True, 2),
        MathProblem(5, 2, "*", 10, "8", False, 3)
    ],
    time_limit=60, start_time=0.0, question_started_at=0.0,
    practice_mode="*"
)).state.problems), 2)

# --------------------
# Additional review tests
# --------------------

# Tests whether the review page preserves a correct answer.
assert_equal(review(State(
    current_page="results", name="Alex", first_number=0,
    second_number=0, operation="+", correct_answer=0,
    user_answer="", feedback="", score=1, questions_answered=1,
    problems=[MathProblem(3, 4, "+", 7, "7", True, 2)],
    time_limit=60, start_time=0.0, question_started_at=0.0,
    practice_mode="+"
)).state.problems[0].correct_answer, 7)

# Tests whether the review page preserves the time taken.
assert_equal(review(State(
    current_page="results", name="Jordan", first_number=0,
    second_number=0, operation="-", correct_answer=0,
    user_answer="", feedback="", score=0, questions_answered=1,
    problems=[MathProblem(8, 3, "-", 5, "6", False, 4)],
    time_limit=60, start_time=0.0, question_started_at=0.0,
    practice_mode="-"
)).state.problems[0].time_taken, 4)

# Tests whether the review page handles an empty problem list.
assert_equal(len(review(State(
    current_page="results", name="Morgan", first_number=0,
    second_number=0, operation="+", correct_answer=0,
    user_answer="", feedback="", score=0, questions_answered=0,
    problems=[], time_limit=60, start_time=0.0,
    question_started_at=0.0, practice_mode="+"
)).state.problems), 0)


start_server(initial_state)
