from functools import reduce
import operator

from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView
from rest_framework import viewsets

from comics.models import (Series, Issue, Character,
                           Arc, Team, Publisher,
                           Creator, Roles, Settings)
from comics.serializers import IssueSerializer, PublisherSerializer,\
    SeriesSerializer, CreatorSerializer, CharacterSerializer, TeamSerializer
from comics.tasks import import_comic_files_task


PAGINATE = 30


class SeriesList(ListView):
    model = Series
    paginate_by = PAGINATE


class SearchSeriesList(SeriesList):

    def get_queryset(self):
        result = super(SearchSeriesList, self).get_queryset()
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(name__icontains=q) for q in query_list)))

        return result


class SeriesDetail(DetailView):
    model = Series


class IssueList(ListView):
    model = Issue
    paginate_by = PAGINATE


class IssueDetail(DetailView):
    model = Issue

    def get_context_data(self, **kwargs):
        context = super(IssueDetail, self).get_context_data(**kwargs)
        issue = self.get_object()
        context['roles_list'] = Roles.objects.filter(issue=issue)
        return context


class CharacterList(ListView):
    model = Character
    paginate_by = PAGINATE


class SearchCharacterList(CharacterList):

    def get_queryset(self):
        result = super(SearchCharacterList, self).get_queryset()
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(name__icontains=q) for q in query_list)))

        return result


class CharacterDetail(DetailView):
    model = Character

    def get_context_data(self, **kwargs):
        context = super(CharacterDetail, self).get_context_data(**kwargs)
        character = self.get_object()
        context['issue_list'] = character.issue_set.all(
        ).order_by('series__sort_title', 'date')
        return context


class ArcList(ListView):
    model = Arc
    paginate_by = PAGINATE


class SearchArcList(ArcList):

    def get_queryset(self):
        result = super(SearchArcList, self).get_queryset()
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(name__icontains=q) for q in query_list)))

        return result


class ArcDetail(DetailView):
    model = Arc

    def get_context_data(self, **kwargs):
        context = super(ArcDetail, self).get_context_data(**kwargs)
        arc = self.get_object()
        context['issue_list'] = arc.issue_set.all(
        ).order_by('series__sort_title', 'date')
        return context


class TeamList(ListView):
    model = Team
    paginate_by = PAGINATE


class SearchTeamList(TeamList):

    def get_queryset(self):
        result = super(SearchTeamList, self).get_queryset()
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(name__icontains=q) for q in query_list)))

        return result


class TeamDetail(DetailView):
    model = Team

    def get_context_data(self, **kwargs):
        context = super(TeamDetail, self).get_context_data(**kwargs)
        team = self.get_object()
        context['issue_list'] = team.issue_set.all(
        ).order_by('series__sort_title', 'date')
        return context


class PublisherList(ListView):
    model = Publisher
    paginate_by = PAGINATE


class SearchPublisherList(PublisherList):

    def get_queryset(self):
        result = super(SearchPublisherList, self).get_queryset()
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(name__icontains=q) for q in query_list)))

        return result


class PublisherDetail(DetailView):
    model = Publisher


class CreatorList(ListView):
    model = Creator
    paginate_by = PAGINATE


class SearchCreatorList(CreatorList):

    def get_queryset(self):
        result = super(SearchCreatorList, self).get_queryset()
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(name__icontains=q) for q in query_list)))

        return result


class CreatorDetail(DetailView):
    model = Creator

    def get_context_data(self, **kwargs):
        context = super(CreatorDetail, self).get_context_data(**kwargs)
        creator = self.get_object()
        roles = Roles.objects.filter(creator=creator)
        context['issue_list'] = Issue.objects.filter(
            id__in=roles.values('issue_id')).order_by('series__sort_title', 'date')
        return context


class ServerSettingsView(UpdateView):
    model = Settings
    fields = '__all__'
    template_name = 'comics/server_settings.html'

    def get_object(self, *args, **kwargs):
        return Settings.get_solo()

    def form_valid(self, form):
        self.object = form.save()
        return render(self.request, 'comics/server-settings-success.html', {'server-settings': self.object})


def importer(request):
    import_comic_files_task()
    return HttpResponseRedirect('/')


class IssueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Returns a list of all issues in the database.

    read:
    Returns the information of an individual issue.
    """
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    lookup_field = 'slug'


class PublisherViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Returns a list of all publishers.

    read:
    Returns the information of an individual publisher.
    """
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    lookup_field = 'slug'


class SeriesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Returns a list of all the comic series.

    read:
    Returns the information of an individual comic series.
    """
    queryset = Series.objects.all()
    serializer_class = SeriesSerializer
    lookup_field = 'slug'


class CreatorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Returns a list of all creators in the database.

    read:
    Returns the information of an individual creator.
    """
    queryset = Creator.objects.all()
    serializer_class = CreatorSerializer
    lookup_field = 'slug'


class CharacterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Returns a list of all the characters in the database.

    read:
    Returns the information for an individual character.
    """
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    lookup_field = 'slug'


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Returns a list of all the teams in the database.

    read:
    Returns the information for an individual team.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    lookup_field = 'slug'
