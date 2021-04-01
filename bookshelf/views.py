from django.views.generic.list import ListView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
import django_filters

from .models import Book, Profile, ElectronicBook, PaperBook
from .forms import BookEdit, EBookEdit, BorrowerCardNumberForm, EBookCreate, BookCreate


def handler404(request, exception, template_name="404.html"):
    return render(request, template_name=template_name)


class BookFilter(django_filters.FilterSet):
    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        data.setdefault('order', 'added')
        super().__init__(data, *args, **kwargs)

    class Meta:
        model = Book
        exclude = 'cover'


class FilteredListView(ListView):
    filterset_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class BookListView(FilteredListView):
    paginate_by = 3
    filterset_class = BookFilter
    model = Book
    template_name = 'bookshelf/book_list.html'


class BookUpdate(UpdateView):
    model = PaperBook
    form_class = BookEdit
    template_name = 'bookshelf/book_form.html'

    def get_success_url(self):
        return reverse('index')


class EBookUpdate(UpdateView):
    model = ElectronicBook
    form_class = EBookEdit
    template_name = 'bookshelf/book_form.html'

    def get_success_url(self):
        return reverse('index')


class BookCreate(CreateView):
    model = PaperBook
    form_class = BookCreate
    success_url = '/'
    template_name_suffix = '_create_form'

    def form_valid(self, form):
        self.object = form.save()
        if self.object.current_amount > self.object.total_amount:
            self.object.current_amount = self.object.total_amount
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class EBookCreate(CreateView):
    model = ElectronicBook
    form_class = EBookCreate
    success_url = '/'
    template_name = 'bookshelf/paperbook_create_form.html'


class BookDelete(DeleteView):
    model = Book
    success_url = '/'


class BookBorrowersDetailView(DetailView):
    model = Book
    template_name = 'bookshelf/borrowers_detail.html'


def borrowerbooklist(request, user_id, book_pk, type):
    context = {}
    if type == 'borrow':
        borrow = User.objects.all().filter(id=user_id)
        context['borrower'] = borrow.values()
        context['borrowed_books'] = PaperBook.objects.all().filter(borrower=borrow[0])
        context['to_borrow'] = PaperBook.objects.all().filter(pk=book_pk).values()
        books_amount = len(PaperBook.objects.all().filter(borrower=borrow[0]))
        context['books_amount'] = books_amount

        if request.method == "POST":
            b = PaperBook.objects.get(pk=book_pk)
            u = User.objects.get(id=user_id)
            if books_amount >= 5:
                show_error_message(request, "Book limit reached (>5)")
            else:
                b.borrower.add(u)
                boooks = PaperBook.objects.get(pk=book_pk)
                amount_of_borrowers = boooks.borrower.all().count()
                total_amount_books = PaperBook.objects.all().filter(pk=book_pk).values()[0]['total_amount']
                b = PaperBook.objects.get(pk=book_pk)
                b.current_amount = total_amount_books - amount_of_borrowers
                b.save()
            return redirect('/')
        else:
            return render(request, 'bookshelf/borrowerbooklist.html', context)

    elif type == 'reserve':
        reserve = User.objects.all().filter(id=user_id)
        context['reserver'] = reserve.values()
        context['reserved_books'] = PaperBook.objects.all().filter(reserver=reserve[0])
        context['to_reserve'] = PaperBook.objects.all().filter(pk=book_pk).values()
        books_amount = len(PaperBook.objects.all().filter(reserver=reserve[0]))
        context['books_amount'] = books_amount

        book_reservers_amount = PaperBook.objects.get(pk=book_pk).reserver.all().count()

        if reserve.values()[0] in PaperBook.objects.get(pk=book_pk).borrower.all().values() \
                or \
                reserve.values()[0] in PaperBook.objects.get(pk=book_pk).reserver.all().values():
            # check if book is not in borrowers (or reservers) already (reserver cannot be borrower at the same time)
            show_error_message(request, "User is already borrowing/reserving this book")
            return redirect('/')

        if request.method == "POST":
            b = PaperBook.objects.get(pk=book_pk)
            u = User.objects.get(id=user_id)
            if books_amount >= 3:
                show_error_message(request, "Reserved books limit reached (>3)")
            elif book_reservers_amount >= 3:
                show_error_message(request, "The book cannot have more than 3 reservation")
            elif reserve.values()[0] in PaperBook.objects.get(pk=book_pk).borrower.all().values():
                # check if book is not in borrowers already (reserver cannot be borrower at the same time)
                show_error_message(request, "User is already borrowing this book")
            elif reserve.values()[0] in PaperBook.objects.get(pk=book_pk).reserver.all().values():
                show_error_message(request, "User is already reserving this book")
            else:
                b.reserver.add(u)
            return redirect('/')
        else:
            return render(request, 'bookshelf/reserverbooklist.html', context)
    elif type == 'return':
        user = User.objects.all().filter(id=user_id)
        book = PaperBook.objects.all().filter(pk=book_pk)

        user_obj = User.objects.get(id=user_id)
        book_obj = PaperBook.objects.get(pk=book_pk)

        if user.values()[0] in PaperBook.objects.get(pk=book_pk).borrower.all().values():
            book_obj.borrower.remove(user_obj)
            book_obj.save()  # to make all amounts correct
        elif user.values()[0] in PaperBook.objects.get(pk=book_pk).reserver.all().values():
            pass
        else:  # user did not borrow the book
            show_error_message(request, "This user did not borrow the book")
        return redirect('/')


from django.contrib import messages


def show_error_message(request, message):
    messages.info(request, message)


def bookborrow_getcardnumber(request, book_pk, type):
    context = {}
    context['borrow_book'] = PaperBook.objects.all().filter(pk=book_pk).values()
    context['type'] = type
    if request.method == "GET":
        form = BorrowerCardNumberForm(request.GET)
        if form.is_valid():
            card_number = form.cleaned_data['card_number']
            if len(card_number) != 9:
                show_error_message(request, 'Inputted card number is not correct. Try again.')
            try:  # check if there is a user with inputted card number
                borrower_profile = Profile.objects.all().filter(card_number=card_number).values()
                borrower_user = User.objects.all().filter(profile=borrower_profile[0]['id']).values()
                return redirect('borrower_detail', user_id=borrower_user[0]['id'], book_pk=book_pk, type=type)
            except IndexError:
                show_error_message(request, 'User with card number {} does not exist'.format(card_number))
    else:
        form = BorrowerCardNumberForm()
    context['form'] = form
    return render(request, 'bookshelf/bookborrow_getcardnumber.html', context)


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
