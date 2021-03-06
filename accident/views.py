from django.shortcuts import render, get_object_or_404
from .models import Accident, Events, Tag, StatusHist, Source, System
from django.shortcuts import redirect
from django.db.models import Max
from .forms import PostForm, EventForm, LinkForm, PostFormEdit, NameForm
from datetime import datetime

from django.conf import settings
from easy_pdf.views import PDFTemplateView
from django.contrib import auth
from django.http import HttpResponseRedirect


def login(request, template_name='accident/auth.html'):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")
    else:
        if request.method == 'POST':
            form = NameForm(request.POST)
            if form.is_valid():
                user_name = request.POST['username']
                passwd = request.POST['password']
                user = auth.authenticate(username=user_name, password=passwd)
                if user is not None and user.is_active:
                    # Правильный пароль и пользователь "активен"
                    auth.login(request, user)
                    # Перенаправление на "правильную" страницу
                    return HttpResponseRedirect("/")
                else:
                    # Отображение страницы с ошибкой
                    message = 'Не верно введен логин или пароль или такого пользователя не существует'
                    form = NameForm()
                    context = {'form': form, 'message': message}
                    #return render(request, 'accident/auth.html', context)
        else:
            form = NameForm()
            context = {'form': form}
        return render(request, 'accident/auth.html', context)


def logout(request):
    auth.logout(request)
    # Перенаправление на страницу.
    return HttpResponseRedirect("/")


class HelloPDFView(PDFTemplateView):

    template_name = 'hello.html'
    download_filename = 'hello.pdf'
    base_url = 'file://' + settings.STATIC_ROOT + '/'

    def get_context_data(self, pk):
        accident = get_object_or_404(Accident, pk=pk)
        events = Events.objects.filter(accident=pk).order_by('date_time')
        tag = Tag.objects.filter(accident=pk)
        last_date = events.aggregate(Max('date_time'))
        return super(HelloPDFView, self).get_context_data(
            pagesize='A4',
            title='Hi there!',
            encoding=u"utf-8",
            accident=accident,
            tag=tag,
            events=events,
            last_date=last_date

        )


def nopdf(request, pk):
    accident = get_object_or_404(Accident, pk=pk)
    events = Events.objects.filter(accident=pk).order_by('date_time')
    tag = Tag.objects.filter(accident=pk)
    last_date = events.aggregate(Max('date_time'))
    context = {'accident': accident, 'events': events,
               'tag': tag, 'last_date': last_date}
    return render(request, 'hello.html', context)


def accident_list(request):
    accident = Accident.objects.all().order_by('-created_date')
    tags = Tag.objects.all()
    context = {'accident': accident, 'tags': tags}
    return render(request, 'accident/accident_list.html', context)


def accident_detail(request, pk):
    accident = get_object_or_404(Accident, pk=pk)
    events = Events.objects.filter(accident=pk).order_by('date_time')
    tag = Tag.objects.filter(accident=pk)
    last_date = events.aggregate(Max('date_time'))
    context = {'events': events, 'tag': tag,
               'accident': accident, 'last_date': last_date}
    return render(request, 'accident/accident_detail.html', context)


def accident_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            accident = Accident()
            accident.headline = form.cleaned_data['headline']
            accident.text = form.cleaned_data['text']
            accident.system = get_object_or_404(
                System, pk=form.cleaned_data['system_id'])
            accident.source = get_object_or_404(
                Source, pk=form.cleaned_data['source'])
            accident.author = request.user
            if 'public' in request.POST:
                request.POST['public']
                date_time = request.POST['datetime']
                date_time_obj = datetime.strptime(date_time, "%d.%m.%Y %H:%M")
                accident.created_date = date_time_obj
            accident.save()
            if request.POST['link'] != '' and request.POST['link_text'] !='':
                accident = get_object_or_404(Accident, id=accident.id)
                link = Tag()
                link.tag_text = form.cleaned_data['link_text']
                link.accident = accident
                link.link = form.cleaned_data['link']
                link.save()
                event = Events()
                event.accident = accident
                event.istag = True
                event.tag = link
                event.save()
            return redirect('accident_detail', pk=accident.id)
    else:
        form = PostForm()
    context = {'form': form}
    return render(request, 'accident/accident_edit.html', context)


def event_new(request, pk):
    accident = get_object_or_404(Accident, id=pk)
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = Events()
            event.event = form.cleaned_data['event_text']
            event.accident = accident

            if 'public' in request.POST:
                date_time = request.POST['datetime']
                date_time_obj = datetime.strptime(date_time, "%d.%m.%Y %H:%M")
                event.date_time = date_time_obj

            if request.POST['link'] != '' and request.POST['link_text'] !='':
                link = Tag()
                link.tag_text = form.cleaned_data['link_text']
                link.accident = accident
                link.link = form.cleaned_data['link']
                link.save()
                event.istag = True
                event.tag = link
            event.save()
            return redirect('accident_detail', pk=accident.pk)
    else:
        form = EventForm()
    context = {'form': form, 'accident': accident}
    return render(request, 'accident/event_edit.html', context)


def link_new(request, pk):
    accident = get_object_or_404(Accident, id=pk)
    if request.method == "POST":
        form = LinkForm(request.POST)
        if form.is_valid():
            link = Tag()
            link.tag_text = form.cleaned_data['tag_text']
            link.accident = accident
            link.link = form.cleaned_data['link']
            link.save()
            event = Events()
            event.accident = accident
            event.istag = True
            event.tag = link
            if 'public' in request.POST:
                date_time = request.POST['datetime']
                date_time_obj = datetime.strptime(date_time, "%d.%m.%Y %H:%M")
                event.date_time = date_time_obj
            event.save()
            return redirect('accident_detail', pk=accident.pk)
    else:
        form = LinkForm()
    context = {'form': form, 'accident': accident}
    return render(request, 'accident/link_edit.html', context)


def accident_edit(request, pk):
    accident = get_object_or_404(Accident, id=pk)
    old_status = str(accident.status)
    if request.method == "POST":
        form = PostFormEdit(request.POST, instance=accident)
        if form.is_valid():
            accident = form.save()
            new_status = str(form.cleaned_data['status'])
            if (old_status != new_status):
                status_hist = StatusHist()
                status_hist.status = form.cleaned_data['status']
                status_hist.save()
                event = Events()
                event.accident = accident
                event.isstatus_change = True
                event.status = status_hist
                event.save()
            return redirect('accident_detail', pk=accident.id)
    else:
        form = PostFormEdit(instance=accident)
    context = {'form': form}
    return render(request, 'accident/accident_edit_form.html', context)
