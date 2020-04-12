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


class BorrowerDetailView(DetailView):
    # TODO: the problem is in that the user's model has no pk and 'detailview' generic view ONLY can "create" page with pk (or slug),
    #  so i cant use id for this purposes (profile model has no pk too)
    #  after solving this problem and creating page, where all the books that user borrowed are shown
    #  add "Confirm borrowing" button for this page, add book to user's borrowed book and do minus one to available books

    model = User
    template_name = 'bookshelf/borrower_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        borrower_book_list = Book.objects.all().filter(borrower=self.object)
        context['books'] = borrower_book_list
        context['books_amount'] = len(borrower_book_list)
        return context

    # def get_object(self):
    #     return self.request.user


class BookBorrow(DetailView):
    # model = user
    fields = '__all__'

    def get_success_url(self):
        return reverse('index')


from django.contrib import messages


def show_error_message(request):
    messages.info(request, 'Inputted card number is not correct. Try again.')


def bookborrow_getcardnumber(request, book_pk):
    context = {}
    context['borrow_book'] = Book.objects.all().filter(pk=book_pk).values()
    if request.method == "GET":
        form = BorrowerCardNumberForm(request.GET)
        if form.is_valid():
            card_number = form.cleaned_data['card_number']
            borrower_profile = Profile.objects.all().filter(card_number=card_number).values()
            print(borrower_profile)
            # TODO: Change id here for pk or smth for detail borrowed books view
            borrower_user = User.objects.all().filter(profile=borrower_profile[0]['id']).values()
            if len(card_number) != 9:
                show_error_message(request)
                return redirect('/')
            else: # Card number is inputted correctly
                try: # check if there is a user with inputted card number
                    print(borrower_user)
                    return redirect('borrower_detail', id=borrower_user[0]['pk'])
                except IndexError:
                    show_error_message(request)

else:
form = BorrowerCardNumberForm()

context['form'] = form
return render(request, 'bookshelf/bookborrow_getcardnumber.html', context)
