from django.shortcuts import render
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import Book, Profile
from .forms import BookEdit, BorrowerCardNumberForm


class BookListView(ListView):
    paginate_by = 2 # TODO: Remove if page is filtering now
    model = Book

    def get_queryset(self):
        filter_val = self.request.GET.get('filterstatus')
        query = self.request.GET.get('search')

        if query:
            if len(query) > 30:
                return Book.objects.all()
        if query:
            new_context = Book.objects.filter(
                Q(title__icontains=query) |
                Q(author__first_name__icontains=query) |
                Q(author__last_name__icontains=query)
            )
        else:
            new_context = Book.objects.all()
        if filter_val:
            new_context = new_context.filter(status=filter_val)

        return new_context

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        # context['filtered'] = True
        context['filter'] = self.request.GET.get('filter', '')
        context['orderby'] = self.request.GET.get('orderby', 'id')
        return context


class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'

    def get_success_url(self):
        return reverse('index')


class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    success_url = '/'
    template_name_suffix = '_create_form'


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
        context['borrowed_books'] = Book.objects.all().filter(borrower=borrow[0])
        context['to_borrow'] = Book.objects.all().filter(pk=book_pk).values()
        books_amount = len(Book.objects.all().filter(borrower=borrow[0]))
        context['books_amount'] = books_amount

        if request.method == "POST":
            b = Book.objects.get(pk=book_pk)
            u = User.objects.get(id=user_id)
            if books_amount >= 5:
                show_error_message(request, "Book limit reached (>5)")
            else:
                b.borrower.add(u)

                boooks = Book.objects.get(pk=book_pk)
                amount_of_borrowers = boooks.borrower.all().count()
                total_amount_books = Book.objects.all().filter(pk=book_pk).values()[0]['total_amount']
                b = Book.objects.get(pk=book_pk)
                b.current_amount = total_amount_books - amount_of_borrowers
                b.save()
            return redirect('/')
        else:
            return render(request, 'bookshelf/borrowerbooklist.html', context)

    elif type == 'reserve':
        reserve = User.objects.all().filter(id=user_id)
        context['reserver'] = reserve.values()
        context['reserved_books'] = Book.objects.all().filter(reserver=reserve[0])
        context['to_reserve'] = Book.objects.all().filter(pk=book_pk).values()
        books_amount = len(Book.objects.all().filter(reserver=reserve[0]))
        context['books_amount'] = books_amount

        book_reservers_amount = Book.objects.get(pk=book_pk).reserver.all().count()

        if reserve.values()[0] in Book.objects.get(pk=book_pk).borrower.all().values() \
                or \
                reserve.values()[0] in Book.objects.get(pk=book_pk).reserver.all().values():
            # check if book is not in borrowers (or reservers) already (reserver cannot be borrower at the same time)
            show_error_message(request, "User is already borrowing/reserving this book")
            return redirect('/')

        if request.method == "POST":
            b = Book.objects.get(pk=book_pk)
            u = User.objects.get(id=user_id)
            if books_amount >= 3:
                show_error_message(request, "Reserved books limit reached (>3)")
            elif book_reservers_amount >= 3:
                show_error_message(request, "The book cannot have more than 3 reservation")
            elif reserve.values()[0] in Book.objects.get(pk=book_pk).borrower.all().values():
                # check if book is not in borrowers already (reserver cannot be borrower at the same time)
                show_error_message(request, "User is already borrowing this book")
            elif reserve.values()[0] in Book.objects.get(pk=book_pk).reserver.all().values():
                show_error_message(request, "User is already reserving this book")
            else:
                b.reserver.add(u)
            return redirect('/')
        else:
            return render(request, 'bookshelf/reserverbooklist.html', context)
    elif type == 'return':
        user = User.objects.all().filter(id=user_id)
        book = Book.objects.all().filter(pk=book_pk)

        user_obj = User.objects.get(id=user_id)
        book_obj = Book.objects.get(pk=book_pk)

        if user.values()[0] in Book.objects.get(pk=book_pk).borrower.all().values():
            book_obj.borrower.remove(user_obj)
            book_obj.save()  # to make all amounts correct
        elif user.values()[0] in Book.objects.get(pk=book_pk).reserver.all().values():
            # TODO: remove user from borrowers or reservers and check if Book model saves correct amount
            pass
        else:  # user did not borrow the book
            show_error_message(request, "This user did not borrow the book")
        return redirect('/')


class BookBorrow(DetailView):
    # model = user
    fields = '__all__'

    def get_success_url(self):
        return reverse('index')


from django.contrib import messages


def show_error_message(request, message):
    messages.info(request, message)


def bookborrow_getcardnumber(request, book_pk, type):
    context = {}
    context['borrow_book'] = Book.objects.all().filter(pk=book_pk).values()
    context['type'] = type
    if request.method == "GET":
        form = BorrowerCardNumberForm(request.GET)
        if form.is_valid():
            card_number = form.cleaned_data['card_number']
            if len(card_number) != 9:
                show_error_message(request, 'Inputted card number is not correct. Try again.')
                return redirect('/')
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
