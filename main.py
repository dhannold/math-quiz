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
    planning=["plan.pdf", "design.pdf"],
    links=["https://github.com/your-username/your-repository"]
)
hide_debug_information()
set_website_framed(False)

def make_question(state: State):

    mode = state.practice_mode

    if mode == "combination":
        operation = choice(["+", "-", "*", "/"])
    elif mode == "long_division":
        operation = "/"
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

    state.practice_mode = operation
    state.operation = operation
    state.current_page = "setup"

    return Page(state, [
        Header("Math Practice Setup"),
        "Selected practice: " + operation,
        "How many seconds would you like to practice?",
        TextBox("time_limit", "60"),
        Button("Start Practice", "start_practice"),
        Button("Back to Home", "index"),
    ])


@route
def addition(state: State) -> Page:
    return setup_page(state, "+")


@route
def multiplication(state: State) -> Page:
    return setup_page(state, "*")


@route
def subtraction(state: State) -> Page:
    return setup_page(state, "-")


@route
def whole_division(state: State) -> Page:
    return setup_page(state, "/")

@route
def combination(state: State) -> Page:
    return setup_page(state, "combination")
    
@route
def start_practice(state: State, time_limit: int) -> Page:

    if time_limit <= 0:
        return setup_page(state, state.operation)

    state.time_limit = time_limit
    state.score = 0
    state.questions_answered = 0
    state.problems = []
    state.start_time = time()

    make_question(state)

    return practice(state)

@route
def practice(state: State) -> Page:

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

    state.current_page = "results"

    return Page(state, [
        Header("Practice Complete!"),
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
