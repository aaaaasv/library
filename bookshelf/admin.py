from django.contrib import admin
from bookshelf.models import Book, Author, Profile

from import_export.admin import ImportExportModelAdmin
from import_export import resources

class BookResource(resources.ModelResource):

    class Meta:
        model = Book

class BookAdmin(ImportExportModelAdmin):
    resource_class = BookResource

admin.site.register(Book, BookAdmin)
admin.site.register(Author)
admin.site.register(Profile)


