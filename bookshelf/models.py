from django.db import models
from django.db.models.signals import post_save, post_init
from django.core.signals import request_finished

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return ("%s %s" % (self.last_name, self.first_name))


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    cover = models.CharField(max_length=200)
    total_amount = models.IntegerField(default=1)
    current_amount = models.IntegerField(default=1)

    reserved_amount = models.IntegerField(default=0)

    ISBN = models.CharField(max_length=13, default='0000000000000')

    TYPE_CHOICES = [
        ('paperback', 'Paperback'),
        ('electronic', 'Electronic')
    ]
    type = models.CharField(max_length=11,
                            choices=TYPE_CHOICES,
                            default='paperback')

    STATUS_CHOICES = [
        ('A', 'Available'),
        ('R', 'Reserved'),
        ('L', 'Loaned'),
    ]
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='A',
    )

    borrower = models.ManyToManyField(User, blank=True, related_name='borrowerOfBook')
    reserver = models.ManyToManyField(User, blank=True, related_name='reserverOfBook')

    def save(self, *args, **kwargs):
        """
        When zero books are available, automatically change its status to - 'Loaned';
        When > 0 books are available, change its status to - 'Available'
        :param args:
        :param kwargs:
        :return:
        """


        if self.current_amount == 0:
            self.status = 'L'
        else:
            reserved_amount = self.reserver.all().count()
            if reserved_amount > 0:
                # TODO: 3 reserved books per user and 3 reservations per book is maximum
                for i in self.reserver.all():
                    print(i)
                enough_list = self.reserver.all()[:self.current_amount] # slice so that all users will get reserved book and current amount wont be < 0
                for reserver_user in enough_list:
                    self.borrower.add(reserver_user) # set user who is now reserver to borrower
                    self.reserver.remove(reserver_user) # remove user from reserver (because moved to borrower)
                super().save(*args, **kwargs)
                self.current_amount -= reserved_amount
                self.reserved_amount -= reserved_amount
            if self.current_amount == 0:
                self.status = 'L'

            self.status = 'A'

        if self.current_amount > self.total_amount:
            self.current_amount = self.total_amount

        if self.current_amount < 0:
            self.current_amount = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return ("%s %s. %s" % (self.title, self.author.first_name[:1], self.author.last_name))


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=13, default='000000000')

    def save(self, *args, **kwargs):
        """
        set right card number
        :param args:
        :param kwargs:
        :return:
        """
        card_n = ('0' * (9 - len(str(self.id)))) + str(self.id)
        self.card_number = card_n

        super().save(*args, **kwargs)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        return self.user.username
