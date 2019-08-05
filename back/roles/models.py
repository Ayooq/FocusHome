from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.name


class Role(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        default=2,
    )
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return self.name + ' (' + self.group.name + ')'
