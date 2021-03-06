from django.db import models
from django.utils import timezone


class Users(models.Model):
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    family_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    email = models.EmailField()

    def __str__(self):
        return "%s %s" % (self.family_name, self.name)


class System(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Status(models.Model):
    headline = models.CharField(max_length=20)
    comment = models.TextField(null=True)
    end_point = models.BooleanField(default=False)

    def __str__(self):
        return self.headline


class Accident(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    headline = models.CharField(max_length=200, verbose_name='заголовок')
    text = models.TextField(verbose_name='Описание аварии')
    system = models.ForeignKey(
        'System', on_delete=models.PROTECT, verbose_name='Система')
    created_date = models.DateTimeField(default=timezone.now)
    update_date = models.DateTimeField(blank=True, null=True)
    tag_var = models.TextField(blank=True)
    status = models.ForeignKey(
        'Status', on_delete=models.PROTECT, verbose_name='Статус', default=1)
    causes = models.TextField(null=True, blank=True, verbose_name='Причины')
    source = models.ForeignKey(
        'Source', on_delete=models.PROTECT, null=True, verbose_name='Источник')
    action = models.TextField(
        null=True, blank=True, verbose_name='Предпринятые действия по предупреждению/ликвидации')
    fin_effect = models.TextField(
        null=True, blank=True, verbose_name='Влияние на абонентов/сервис')

    def __str__(self):
        return self.headline


class Events(models.Model):
    date_time = models.DateTimeField(default=timezone.now)
    event = models.TextField(verbose_name='Действие', null=True)
    accident = models.ForeignKey(
        'Accident', on_delete=models.CASCADE, verbose_name='')
    isstatus_change = models.BooleanField(default=False)
    status = models.ForeignKey(
        'StatusHist', on_delete=models.PROTECT, null=True)
    istag = models.BooleanField(default=False)
    tag = models.ForeignKey('Tag', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.event


class Tag(models.Model):
    tag_text = models.TextField()
    accident = models.ForeignKey('Accident', on_delete=models.CASCADE)
    link = models.TextField(null=True, blank=True)
    is_opened = models.BooleanField(default=False)

    def __str__(self):
        return self.tag_text


class Source(models.Model):
    headline = models.TextField()
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.headline


class StatusHist(models.Model):
    status = models.ForeignKey('Status', on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=timezone.now)
