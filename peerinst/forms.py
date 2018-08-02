# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import (
    StudentGroup,
    StudentGroupAssignment,
    Assignment,
    BlinkAssignmentQuestion,
    BlinkQuestion,
    Question,
    Teacher,
    Discipline,
    Category,
)
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count, Q
from django.forms import ModelForm

import password_validation


class FirstAnswerForm(forms.Form):
    """Form to select one of the answer choices and enter a rationale."""

    error_css_class = "validation-error"

    first_answer_choice = forms.ChoiceField(
        label=_("Choose one of these answers:"), widget=forms.RadioSelect
    )
    rationale = forms.CharField(
        widget=forms.Textarea(attrs={"cols": 100, "rows": 7})
    )

    def __init__(self, answer_choices, *args, **kwargs):
        print([pair[1] for pair in answer_choices])
        choice_texts = [
            mark_safe(
                ". ".join(
                    (
                        pair[0],
                        ("<br>" + "&nbsp" * 5).join(
                            re.split(r"<br(?: /)?>", pair[1])
                        ),
                    )
                )
            )
            for pair in answer_choices
        ]
        #  choice_texts = [mark_safe(". ".join(pair)) for pair in answer_choices]
        self.base_fields["first_answer_choice"].choices = enumerate(
            choice_texts, 1
        )
        forms.Form.__init__(self, *args, **kwargs)


class ReviewAnswerForm(forms.Form):
    """Form on the answer review page."""

    error_css_class = "validation-error"

    second_answer_choice = forms.ChoiceField(
        label="", widget=forms.RadioSelect
    )

    RATIONALE_CHOICE = "rationale_choice"

    def __init__(self, rationale_choices, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        answer_choices = []
        rationale_choice_fields = []
        for i, (choice, label, rationales) in enumerate(rationale_choices):
            field_name = "{}_{}".format(self.RATIONALE_CHOICE, i)
            self.fields[field_name] = forms.ChoiceField(
                label="",
                required=False,
                widget=forms.RadioSelect,
                choices=rationales,
            )
            answer_choices.append((choice, label))
            rationale_choice_fields.append(self[field_name])
        self.fields["second_answer_choice"].choices = answer_choices
        self.rationale_groups = zip(
            self["second_answer_choice"], rationale_choice_fields
        )

    def clean(self):
        cleaned_data = forms.Form.clean(self)
        rationale_choices = [
            value
            for key, value in cleaned_data.iteritems()
            if key.startswith(self.RATIONALE_CHOICE)
        ]
        if sum(map(bool, rationale_choices)) != 1:
            # This should be prevented by the UI on the client side, so this check is mostly to
            # protect against bugs and people transferring made-up data.
            raise forms.ValidationError(
                _("Please select exactly one rationale.")
            )
        chosen_rationale_id = next(
            value for value in rationale_choices if value
        )
        cleaned_data.update(chosen_rationale_id=chosen_rationale_id)
        return cleaned_data


class SequentialReviewForm(forms.Form):
    """Form to vote on a single rationale."""

    def clean(self):
        cleaned_data = forms.Form.clean(self)
        if "upvote" in self.data:
            cleaned_data["vote"] = "up"
        elif "downvote" in self.data:
            cleaned_data["vote"] = "down"
        else:
            raise forms.ValidationError(_("Please vote up or down."))
        return cleaned_data


class AssignmentCreateForm(forms.ModelForm):
    """Simple form to create a new Assignment"""

    class Meta:
        model = Assignment
        fields = ["identifier", "title"]


class AssignmentMultiselectForm(forms.Form):
    def __init__(self, user=None, question=None, *args, **kwargs):
        super(AssignmentMultiselectForm, self).__init__(*args, **kwargs)
        if user:
            # Remove assignments with question and assignments with student answers
            queryset = user.assignment_set.all()
        else:
            queryset = Assignment.objects.all()

        num_student_rationales = Count("answer", filter=~Q(user_token=""))

        if question:
            queryset = (
                queryset.annotate(
                    num_student_rationales=num_student_rationales
                )
                .filter(Q(num_student_rationales=0))
                .exclude(questions=question)
            )
        else:
            queryset = queryset.annotate(
                num_student_rationales=num_student_rationales
            ).filter(Q(num_student_rationales=0))

        self.fields["assignments"] = forms.ModelMultipleChoiceField(
            queryset=queryset,
            label=_("Assignments"),
            help_text=_(
                "Optional. Select assignments to add this question.  You can select multiple assignments.  Assignments that this question is already a part of will not appear in list."
            ),
        )


class TeacherAssignmentsForm(forms.Form):
    """Simple form to help update teacher assignments"""

    assignment = forms.ModelChoiceField(queryset=Assignment.objects.all())


class TeacherGroupsForm(forms.Form):
    """Simple form to help update teacher groups"""

    group = forms.ModelChoiceField(queryset=StudentGroup.objects.all())


class TeacherBlinksForm(forms.Form):
    """Simple form to help update teacher blinks"""

    blink = forms.ModelChoiceField(queryset=BlinkQuestion.objects.all())


class CreateBlinkForm(forms.Form):
    """Simple form to help create blink for teacher"""

    new_blink = forms.ModelChoiceField(queryset=Question.objects.all())


class BlinkAnswerForm(forms.Form):
    """Form to select one of the answer choices."""

    error_css_class = "validation-error"

    first_answer_choice = forms.ChoiceField(
        label=_("Choose one of these answers:"), widget=forms.RadioSelect
    )

    def __init__(self, answer_choices, *args, **kwargs):
        choice_texts = [
            mark_safe(
                ". ".join(
                    (
                        pair[0],
                        ("<br>" + "&nbsp" * 5).join(
                            re.split(r"<br(?: /)?>", pair[1])
                        ),
                    )
                )
            )
            for pair in answer_choices
        ]
        #choice_texts = [mark_safe(". ".join(pair)) for pair in answer_choices]
        self.base_fields["first_answer_choice"].choices = enumerate(
            choice_texts, 1
        )
        forms.Form.__init__(self, *args, **kwargs)


class BlinkQuestionStateForm(ModelForm):
    """Form to set active state of a BlinkQuestion."""

    class Meta:
        model = BlinkQuestion
        fields = ["active"]


class RankBlinkForm(forms.Form):
    """Form to handle reordering or deletion of blinkquestions in a blinkassignment."""

    # Might be better to set the queryset to limit to teacher's blink set
    q = forms.ModelMultipleChoiceField(
        queryset=BlinkAssignmentQuestion.objects.all(),
        to_field_name="blinkquestion_id",
    )
    rank = forms.CharField(max_length=5, widget=forms.HiddenInput)


class AddBlinkForm(forms.Form):
    """Form to add a blinkquestion to a blinkassignment."""

    # Might be better to set the queryset to limit to teacher's blinks
    blink = forms.ModelChoiceField(queryset=BlinkQuestion.objects.all())


class SignUpForm(UserCreationForm):
    """Form to register a new user (teacher) with e-mail address.

    The clean method is overridden to add basic password validation."""

    url = forms.URLField(
        label=_("Website"),
        initial="http://",
        max_length=200,
        help_text=_(
            "Please provide an institutional url listing yourself as a faculty member and showing your e-mail address."
        ),
    )

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        pwd = cleaned_data.get("password1")
        if pwd:
            password_validation.validate_password(pwd)

        return cleaned_data

    class Meta:
        model = User
        fields = ["email", "username"]


class ActivateForm(forms.Form):
    """Form to activate a User and initialize as Teacher, if indicated."""

    is_teacher = forms.BooleanField(required=False)
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=False)
    )


class EmailForm(forms.Form):
    """Form for user email address"""
    email = forms.EmailField()


class AddRemoveQuestionForm(forms.Form):
    q = forms.ModelChoiceField(queryset=Question.objects.all())


class DisciplineForm(forms.ModelForm):
    class Meta:
        model = Discipline
        fields = ["title"]


class DisciplineSelectForm(forms.Form):
    discipline = forms.ModelChoiceField(queryset=Discipline.objects.all())


class DisciplinesSelectForm(forms.Form):
    disciplines = forms.ModelMultipleChoiceField(queryset=Discipline.objects.all())


class CategorySelectForm(forms.Form):
    category = forms.ModelMultipleChoiceField(queryset=Category.objects.all())


class ReportSelectForm(forms.Form):

    student_groups = forms.ModelMultipleChoiceField(
        label=_("Choose which groups you would like your report to include:"),
        widget=forms.CheckboxSelectMultiple,
        queryset=StudentGroup.objects.none(),
    )

    assignments = forms.ModelMultipleChoiceField(
        label=_(
            "Choose which assignments you would like your report to include:"
        ),
        widget=forms.CheckboxSelectMultiple,
        queryset=Assignment.objects.none(),
    )

    def __init__(self, teacher_username, *args, **kwargs):
        self.base_fields["assignments"].queryset = Teacher.objects.get(
            user__username=teacher_username
        ).assignments.all()
        self.base_fields["student_groups"].queryset = Teacher.objects.get(
            user__username=teacher_username
        ).groups.all()
        forms.Form.__init__(self, *args, **kwargs)


class AnswerChoiceForm(forms.ModelForm):
    def clean_text(self):
        if self.cleaned_data["text"].startswith("<p>"):
            return "<br>".join(
                re.findall(r"(?<=<p>)(.+)(?=</p>)", self.cleaned_data["text"])
            )
        else:
            return self.cleaned_data["text"]


class StudentGroupCreateForm(forms.ModelForm):
    """Simple form to create a new group"""

    class Meta:
        model = StudentGroup
        fields = ["title", "name"]


class StudentGroupAssignmentForm(ModelForm):
     class Meta:
         model = StudentGroupAssignment
         fields = '__all__'
