from django.test import TestCase

import datetime
from django.utils import timezone

from .models import Question, Choice

from django.urls import reverse


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)

    print("question id = " + f'{question.id}')
    return question


def create_choice(question, choice_text):
    """
    Create a choice with the given 'question' and 'choice_text'
    :param question:Question object
    :param choice_text:Text
    :return:Choice object
    """
    choice = Choice.objects.create(question=question, choice_text=choice_text)
    print("choice id = " + f'{choice.id}')
    return choice


class QuestionIndexViewTests(TestCase):
    def test_no_question(self):
        """
        If no question exist, an appropriate message is displayed.
        :return:
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")

    def test_past_question_with_no_choice(self):
        """
        Question with a pub_date in the past and without choices aren't displayed on the
        index page.
        :return:
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")

    def test_future_question_and_past_question_with_no_choice(self):
        """
        Even if both past and future questions exist and that questions have no choices, displayed nothing.
        :return:
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")

    def test_two_past_question_with_no_choice(self):
        """
        The questions index page may display nothing with multiple questions that
        have no choices.
        :return:
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")

    def test_past_question_with_choices(self):
        """
        Question with a pub_date in the past are displayed on the
        index page.
        :return:
        """
        question = create_question(question_text="Past question.", days=-30)
        create_choice(question, "test1")
        create_choice(question, "test2")

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question_with_choices(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        :return:
        """
        question = create_question(question_text="Future question.", days=30)
        create_choice(question, "test1")
        create_choice(question, "test2")
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")

    def test_future_question_and_past_question_with_choices(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        :return:
        """
        question_p = create_question(question_text="Past question.", days=-30)
        create_choice(question_p, "test1")
        create_choice(question_p, "test2")

        question_f = create_question(question_text="Future question.", days=30)
        create_choice(question_f, "test1")
        create_choice(question_f, "test2")

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question_p],
        )

    def test_two_past_question_with_choices(self):
        """
        The questions index page may display multiple questions.
        :return:
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        create_choice(question1, "test1")
        create_choice(question1, "test2")

        question2 = create_question(question_text="Past question 2", days=-5)
        create_choice(question2, "test1")
        create_choice(question2, "test2")

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )

    def test_without_choice_question(self):
        """
        The question that have no choice should be not published.
        """
        question = create_question(question_text="Without question.", days=0)
        response = self.client.get(reverse('polls:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")


class QuestionDetailViewTests(TestCase):
    # def test_question_without_choice(self):
    #     """
    #     Questions have no choices displayed nothing.
    #     :return:
    #     """
    #     q = create_question(question_text='No choice question.', days=0)
    #     url = reverse('polls:results', args=(q.id,))
    #     response = self.client.get(url)
    #     self.assertContains(response, "Question has no choices.")

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        :return:
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        :return:
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
