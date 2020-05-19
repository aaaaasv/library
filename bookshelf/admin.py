from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from bookshelf.models import Book, Author, Profile, ElectronicBook, PaperBook


class PBookResource(resources.ModelResource):
    class Meta:
        model = PaperBook

class PBookAdmin(ImportExportModelAdmin):
    resource_class = PBookResource

class EBookResource(resources.ModelResource):
    class Meta:
        model = ElectronicBook

class EBookAdmin(ImportExportModelAdmin):
    resource_class = EBookResource

class BookResource(resources.ModelResource):
    class Meta:
        model = Book

class BookAdmin(ImportExportModelAdmin):
    resource_class = BookResource

class AuthorResource(resources.ModelResource):
    class Meta:
        model = Author

class AuthorAdmin(ImportExportModelAdmin):
    resource_class = AuthorResource

admin.site.register(Author, AuthorAdmin)
admin.site.register(Profile)
admin.site.register(PaperBook, PBookAdmin)
admin.site.register(ElectronicBook, EBookAdmin)
admin.site.register(Book, BookAdmin)



