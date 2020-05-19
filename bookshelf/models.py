from django.db import models
from django.db.models.signals import post_save, post_init
from django.core.signals import request_finished
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from sortedm2m.fields import SortedManyToManyField

class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def full_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return ("%s %s" % (self.last_name, self.first_name))

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    cover = models.CharField(max_length=200, default='static/bookshelf/standard_cover.png')
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
        ('N', 'Not available'),
    ]
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='A',
    )

    def __str__(self):
        return ("%s %s. %s" % (self.title, self.author.first_name[:1], self.author.last_name))


class PaperBook(Book):
    total_amount = models.IntegerField(default=1)
    current_amount = models.IntegerField(default=1)
    reserved_amount = models.IntegerField(default=0)

    borrower = models.ManyToManyField(User, blank=True, related_name='borrowerOfBook')
    reserver = SortedManyToManyField(User, blank=True, related_name='reserverOfBook')
    to_giveout = models.ManyToManyField(User, blank=True, related_name='toGiveOut')

    def save(self, *args, **kwargs):
        """
        When zero books are available, change its status to - 'Not available';
        When > 0 books are available, change its status to - 'Available'
        Lend book to reservee when it becomes available
        """
        if self.type == 'paperback':
            try:
                self.current_amount = self.total_amount - self.borrower.all().count()
            except ValueError:
                super().save(*args, **kwargs)
                return
            if self.current_amount == 0:
                self.status = 'N'
            else:
                reserved_amount = self.reserver.all().count()
                if reserved_amount > 0:
                    enough_list = self.reserver.all()[
                                  :self.current_amount]  # slice so that all users will get reserved book and current amount wont be < 0
                    for reserver_user in enough_list:
                        self.borrower.add(reserver_user)  # set user who is now reserver to borrower
                        self.to_giveout.add(reserver_user)
                        self.reserver.remove(reserver_user)  # remove user from reserver (because moved to borrower)
                    super().save(*args, **kwargs)
                    reserved_amount = self.reserver.all().count()
                    self.reserved_amount = reserved_amount
                    self.current_amount = self.total_amount - self.borrower.all().count() - reserved_amount
        else:
            self.type = 'paperback'

        if self.current_amount > self.total_amount:
            self.current_amount = self.total_amount

        if self.current_amount < 0:
            self.current_amount = 0

        if self.current_amount == 0:
            self.status = 'N'
        else:
            self.status = 'A'
        self.reserved_amount = self.reserver.all().count()
        super().save(*args, **kwargs)

class ElectronicBook(Book):
    file_format = models.CharField(max_length=10, default='')
    link = models.CharField(max_length=100, default='')

    def save(self, *args, **kwargs):
        self.type = 'electronic'
        super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=13, default='000000000')

    def save(self, *args, **kwargs):
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

