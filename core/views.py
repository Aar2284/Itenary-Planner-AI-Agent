from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from .models import UserProfile, Question, Answer, Vote, SUBJECT_CHOICES
from .ai_service import find_similar_questions, generate_answer


# ── Auth ──────────────────────────────────────────────

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect("register")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("register")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user)
        login(request, user)
        messages.success(request, f"Welcome {username}!")
        return redirect("home")
    return render(request, "core/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect("home")
        messages.error(request, "Invalid username or password")
        return redirect("login")
    return render(request, "core/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("home")


# ── Home ──────────────────────────────────────────────

def home_view(request):
    total_questions = Question.objects.count()
    total_answers = Answer.objects.count()
    total_users = User.objects.count()
    recent_questions = Question.objects.select_related("author")[:10]
    return render(request, "core/home.html", {
        "total_questions": total_questions,
        "total_answers": total_answers,
        "total_users": total_users,
        "recent_questions": recent_questions,
    })


# ── Profile ───────────────────────────────────────────

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_questions = Question.objects.filter(author=request.user)[:10]
    user_answers = Answer.objects.filter(author=request.user)[:10]
    return render(request, "core/profile.html", {
        "profile": profile,
        "user_questions": user_questions,
        "user_answers": user_answers,
    })


# ── Questions ─────────────────────────────────────────

def question_list_view(request):
    subject = request.GET.get("subject", "")
    search = request.GET.get("q", "")
    questions = Question.objects.select_related("author")

    if subject:
        questions = questions.filter(subject=subject)
    if search:
        questions = questions.filter(Q(title__icontains=search) | Q(description__icontains=search))

    questions = questions.annotate(num_answers=Count("answers"))
    return render(request, "core/question_list.html", {
        "questions": questions,
        "subjects": SUBJECT_CHOICES,
        "current_subject": subject,
        "search_query": search,
    })


@login_required
def ask_question_view(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        subject = request.POST.get("subject")
        tags = request.POST.get("tags", "")

        if not title or not description:
            messages.error(request, "Title and description are required")
            return redirect("ask")

        question = Question.objects.create(
            title=title,
            description=description,
            subject=subject,
            tags=tags,
            author=request.user,
        )

        ai_answer_text = generate_answer(question)
        Answer.objects.create(
            question=question,
            author=request.user,
            content=ai_answer_text,
            is_ai_generated=True,
        )

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.questions_asked += 1
        profile.reputation_score += 10
        profile.save()

        messages.success(request, "Question posted! AI has generated an initial answer.")
        return redirect("question_detail", pk=question.pk)

    return render(request, "core/ask_question.html", {"subjects": SUBJECT_CHOICES})


def question_detail_view(request, pk):
    question = get_object_or_404(Question, pk=pk)
    question.view_count += 1
    question.save(update_fields=["view_count"])

    answers = question.answers.select_related("author").all()
    user_votes = {}
    if request.user.is_authenticated:
        votes = Vote.objects.filter(user=request.user, answer__in=answers)
        user_votes = {v.answer_id: v.vote_type for v in votes}

    query_text = f"{question.title} {question.description}"
    similar_questions = find_similar_questions(query_text, threshold=0.2, max_results=3)
    similar_questions = [q for q in similar_questions if q["id"] != question.pk]

    return render(request, "core/question_detail.html", {
        "question": question,
        "answers": answers,
        "user_votes": user_votes,
        "similar_questions": similar_questions,
    })


# ── Answers ───────────────────────────────────────────

@login_required
def post_answer_view(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        content = request.POST.get("content")
        if not content:
            messages.error(request, "Answer cannot be empty")
            return redirect("question_detail", pk=pk)

        Answer.objects.create(
            question=question,
            author=request.user,
            content=content,
        )
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.answers_given += 1
        profile.reputation_score += 5
        profile.save()

        messages.success(request, "Answer posted!")
    return redirect("question_detail", pk=pk)


# ── Voting ────────────────────────────────────────────

@login_required
def toggle_vote_view(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    answer = get_object_or_404(Answer, pk=pk)
    vote_type = int(request.POST.get("vote_type", 1))

    vote, created = Vote.objects.get_or_create(
        user=request.user, answer=answer,
        defaults={"vote_type": vote_type}
    )

    if not created:
        if vote.vote_type == vote_type:
            vote.delete()
            if vote_type == 1:
                answer.upvotes = max(0, answer.upvotes - 1)
            else:
                answer.downvotes = max(0, answer.downvotes - 1)
        else:
            if vote.vote_type == 1:
                answer.upvotes = max(0, answer.upvotes - 1)
            else:
                answer.downvotes = max(0, answer.downvotes - 1)
            vote.vote_type = vote_type
            vote.save()
            if vote_type == 1:
                answer.upvotes += 1
            else:
                answer.downvotes += 1
    else:
        if vote_type == 1:
            answer.upvotes += 1
        else:
            answer.downvotes += 1

    answer.save(update_fields=["upvotes", "downvotes"])

    return JsonResponse({
        "upvotes": answer.upvotes,
        "downvotes": answer.downvotes,
        "score": answer.score(),
    })
