from django.urls import path, include
from bookshelf.views import *

handler404 = handler404


urlpatterns = [
    path('', BookListView.as_view(), name='index'),
    path('book/<int:pk>/update', BookUpdate.as_view(), name='book_update'),
    path('ebook/<int:pk>/update', EBookUpdate.as_view(), name='ebook_update'),
    path('book/create', BookCreate.as_view(), name='book_create'),
    path('ebook/create', EBookCreate.as_view(), name='ebook_create'),
    path('book/<int:pk>/delete', BookDelete.as_view(), name='book_delete'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', signup, name='signup'),
    path('book/borrowers/<int:pk>/', BookBorrowersDetailView.as_view(), name='borrowers_detail'),
    # path('borrowerbooks/<int:pk>/', BorrowerDetailView.as_view(), name='borrower_detail'),
    path('<int:book_pk>/<str:type>/', bookborrow_getcardnumber, name='getcardnumber'), #'book_borrow'),
    path('borrowerbooks/<int:user_id>/<str:type>/<int:book_pk>/', borrowerbooklist, name='borrower_detail'),
    # path('user/<int:user_pk>/borrow_book/<int:book_pk>', BookBorrow.as_view(), name='book_borrow'),
]

