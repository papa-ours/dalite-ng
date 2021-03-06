# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .answer import Answer
from .assignment import Assignment
from .group import StudentGroup
from .question import Discipline, Question
from .student import Student, StudentGroupAssignment


class Institution(models.Model):
    name = models.CharField(
        max_length=100, unique=True, help_text=_("Name of school.")
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("institution")
        verbose_name_plural = _("institutions")


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institutions = models.ManyToManyField(Institution, blank=True)
    disciplines = models.ManyToManyField(Discipline, blank=True)
    assignments = models.ManyToManyField(Assignment, blank=True)
    deleted_questions = models.ManyToManyField(Question, blank=True)
    favourite_questions = models.ManyToManyField(
        Question, blank=True, related_name="favourite_questions"
    )
    current_groups = models.ManyToManyField(
        StudentGroup, blank=True, related_name="current_groups"
    )

    def get_absolute_url(self):
        return reverse("teacher", kwargs={"pk": self.pk})

    def student_activity(self):
        last_login = self.user.last_login
        current_groups = self.current_groups.all()

        all_current_students = Student.objects.filter(
            groups__in=current_groups
        ).values("student__username")

        all_assignments = StudentGroupAssignment.objects.filter(
            group__in=current_groups
        ).values("assignment")

        activity = (
            Answer.objects.filter(assignment__in=all_assignments)
            .filter(user_token__in=all_current_students)
            .filter(time__gt=last_login)
            .count()
        )

        return activity

    @staticmethod
    def get(hash_):
        try:
            username = str(base64.urlsafe_b64decode(hash_.encode()).decode())
        except UnicodeDecodeError:
            username = None
        if username:
            try:
                teacher = Teacher.objects.get(user__username=username)
            except Teacher.DoesNotExist:
                teacher = None
        else:
            teacher = None

        return teacher

    @property
    def hash(self):
        return base64.urlsafe_b64encode(
            str(self.user.username).encode()
        ).decode()

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _("teacher")
        verbose_name_plural = _("teachers")


class VerifiedDomain(models.Model):
    domain = models.CharField(
        max_length=100,
        help_text=_(
            "Teacher-only email domain, if available. "
            "Email addresses with these domains will be treated as verified."
        ),
    )
    institution = models.ForeignKey(Institution)
