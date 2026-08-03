from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(max_length=500, blank=True)
    reputation_score = models.IntegerField(default=0)
    questions_asked = models.IntegerField(default=0)
    answers_given = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


SUBJECT_CHOICES = [
    ("math", "Mathematics"),
    ("physics", "Physics"),
    ("cs", "Computer Science"),
    ("chemistry", "Chemistry"),
    ("biology", "Biology"),
    ("english", "English"),
    ("history", "History"),
    ("economics", "Economics"),
    ("other", "Other"),
]


class Question(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default="other")
    tags = models.CharField(max_length=200, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def answer_count(self):
        return self.answers.count()

    def vote_score(self):
        total = 0
        for answer in self.answers.all():
            total += answer.upvotes - answer.downvotes
        return total


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    content = models.TextField()
    is_ai_generated = models.BooleanField(default=False)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Answer to '{self.question.title}' by {self.author.username}"

    def score(self):
        return self.upvotes - self.downvotes


class Vote(models.Model):
    VOTE_CHOICES = [(1, "Upvote"), (-1, "Downvote")]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="votes")
    vote_type = models.SmallIntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ("user", "answer")
