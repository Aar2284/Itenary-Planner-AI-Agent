import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Question


def find_similar_questions(query_text, threshold=0.3, max_results=5):
    questions = Question.objects.exclude(description="").values_list("id", "title", "description")
    if not questions:
        return []

    ids = [q[0] for q in questions]
    texts = [f"{q[1]} {q[2]}" for q in questions]

    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    all_texts = texts + [query_text]
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    query_vec = tfidf_matrix[-1]
    doc_vecs = tfidf_matrix[:-1]

    similarities = cosine_similarity(query_vec, doc_vecs).flatten()

    results = []
    for idx in similarities.argsort()[::-1]:
        if similarities[idx] >= threshold:
            results.append({
                "id": ids[idx],
                "title": questions[idx][1],
                "similarity": round(similarities[idx] * 100, 1),
            })
        if len(results) >= max_results:
            break

    return results


ANSWER_TEMPLATES = {
    "math": [
        "Here's how to approach this math problem:\n\n1. **Identify the key concepts** - Look at what variables and operations are involved.\n2. **Set up the equation** - Translate the problem into mathematical notation.\n3. **Solve step by step** - Work through the algebra carefully.\n4. **Verify your answer** - Plug it back in to check.\n\nIf you share your work so far, I can help identify where you might be stuck.",
        "For this type of math problem, try breaking it down:\n\n- First, identify what's being asked\n- List out the given information\n- Choose the right formula or method\n- Show each step clearly\n\nFeel free to share your attempt and I'll guide you through it!",
    ],
    "physics": [
        "To solve this physics problem:\n\n1. **Draw a diagram** - Visualize the setup\n2. **List knowns and unknowns** - Identify given values and what you need to find\n3. **Choose the right equation** - Match the scenario to physics principles\n4. **Solve with units** - Always include and check your units\n\nWhat specific concept is this problem about? That will help me give more targeted guidance.",
        "For physics problems, remember:\n\n- Always define your coordinate system\n- Identify all forces or principles at play\n- Use dimensional analysis to check your work\n- Consider limiting cases to verify reasonableness\n\nShare your approach and I can help identify any issues!",
    ],
    "cs": [
        "For this programming/CS question:\n\n1. **Understand the problem** - What's the input, output, and constraints?\n2. **Plan your approach** - Think about the algorithm before coding\n3. **Write pseudocode** - Outline your logic in plain English\n4. **Implement and test** - Code it up and test with edge cases\n\nWhat language are you working with? And what have you tried so far?",
        "Here's a systematic approach:\n\n- Break the problem into smaller sub-problems\n- Consider time and space complexity\n- Think about edge cases\n- Use meaningful variable names\n\nIf you share your code or attempt, I can point out specific improvements!",
    ],
    "chemistry": [
        "For this chemistry problem:\n\n1. **Write the reaction/equation** - Balance it if needed\n2. **Identify what's given** - Concentrations, masses, volumes\n3. **Choose the right approach** - Stoichiometry, equilibrium, etc.\n4. **Calculate with proper units** - Watch your significant figures\n\nWhat topic does this cover? That'll help me give more specific guidance.",
    ],
    "biology": [
        "For this biology question:\n\n1. **Identify the biological concept** - Is this genetics, cell biology, ecology?\n2. **Recall the relevant processes** - What mechanisms are involved?\n3. **Connect the dots** - How do the concepts relate to the question?\n4. **Use examples** - Concrete examples help solidify understanding\n\nCan you tell me which topic this relates to?",
    ],
    "english": [
        "For this English/Language Arts question:\n\n1. **Read the passage carefully** - Look for key themes and evidence\n2. **Identify the main idea** - What's the author's central argument?\n3. **Support with quotes** - Use textual evidence\n4. **Structure your response** - Introduction, body, conclusion\n\nWhat type of analysis are you working on? Literary, rhetorical, or analytical?",
    ],
    "other": [
        "Great question! Here's how to approach it:\n\n1. **Break it down** - Split the question into smaller parts\n2. **Research** - Look at your notes and textbook\n3. **Organize** - Structure your thoughts logically\n4. **Verify** - Double-check your answer\n\nFeel free to share more details and I can give more specific help!",
    ],
}


def generate_answer(question):
    subject = question.subject
    templates = ANSWER_TEMPLATES.get(subject, ANSWER_TEMPLATES["other"])
    np.random.seed(question.pk)
    answer_text = np.random.choice(templates)

    if question.tags:
        tags = [t.strip() for t in question.tags.split(",") if t.strip()]
        if tags:
            answer_text += f"\n\n**Related concepts:** {', '.join(tags)}"

    return answer_text
