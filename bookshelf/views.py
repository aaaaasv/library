from django.shortcuts import render
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User

from .models import Book, Profile
from .forms import BookEdit, BorrowerCardNumberForm


class BookListView(ListView):
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


def borrowerbooklist(request, user_id, book_pk):
    context = {}
    borrow = User.objects.all().filter(id=user_id)
    context['borrower'] = borrow.values()
    context['borrowed_books'] = Book.objects.all().filter(borrower=borrow[0])
    context['to_borrow'] = Book.objects.all().filter(pk=book_pk).values()
    books_amount = len(Book.objects.all().filter(borrower=borrow[0]))
    context['books_amount'] = books_amount

    if request.method == "POST":
        b = Book.objects.get(pk=book_pk)
        u = User.objects.get(id=user_id)
        if books_amount > 5:
            show_error_message(request, "Book limit reached (>5)")
        else:
            # TODO: minus one from current books (total books - borrower books amount)
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


class BookBorrow(DetailView):
    # model = user
    fields = '__all__'

    def get_success_url(self):
        return reverse('index')


from django.contrib import messages


def show_error_message(request, message):
    messages.info(request, message)


def bookborrow_getcardnumber(request, book_pk):
    context = {}
    context['borrow_book'] = Book.objects.all().filter(pk=book_pk).values()
    if request.method == "GET":
        form = BorrowerCardNumberForm(request.GET)
        if form.is_valid():
            card_number = form.cleaned_data['card_number']
            borrower_profile = Profile.objects.all().filter(card_number=card_number).values()
            borrower_user = User.objects.all().filter(profile=borrower_profile[0]['id']).values()
            print(borrower_user[0]['id'])
            if len(card_number) != 9:
                show_error_message(request, 'Inputted card number is not correct. Try again.')
                return redirect('/')
            else:  # Card number is inputted correctly
                try:  # check if there is a user with inputted card number
                    return redirect('borrower_detail', user_id=borrower_user[0]['id'], book_pk=book_pk)
                except IndexError:
                    show_error_message(request)
    else:
        form = BorrowerCardNumberForm()

    context['form'] = form
    return render(request, 'bookshelf/bookborrow_getcardnumber.html', context)
