from drafter import *
from dataclasses import dataclass
from random import randint, choice
from time import time
from bakery import assert_equal

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
    planning=["project_design.pdf", "project_pick.pdf"],
    links=["https://github.com/dhannold/math-quiz/blob/main/project_design.pdf", "https://github.com/dhannold/math-quiz/blob/main/project_pick.pdf"]
)
hide_debug_information()
set_website_framed(False)

def make_question(state: State) -> None:
    """Creates a random math question and updates the state.

    Random number generation makes exact output difficult to test.
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
    if not user_answer.strip().lstrip("-").isdigit():
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

start_server(initial_state)
