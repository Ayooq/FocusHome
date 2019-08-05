from django.db import models


class Family(models.Model):
    name = models.CharField(max_length=10)
    title = models.CharField(max_length=20, blank=True)
    comment = models.CharField(max_length=40, blank=True)

    class Meta:
        verbose_name = 'Семейство'
        verbose_name_plural = 'Семейства'

    def __str__(self):
        return self.name


class Unit(models.Model):
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='unit',
    )
    name = models.CharField(max_length=10)
    title = models.CharField(max_length=20, blank=True)
    is_custom = models.BooleanField(default=True)
    is_gpio = models.BooleanField(default=True)
    comment = models.CharField(max_length=40, blank=True)
    format = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'units'
        verbose_name = 'Компонент'
        verbose_name_plural = 'Компоненты'

    def __str__(self):
        return self.name + (' (' + self.title + ')' if self.title else '')
