from django.contrib import admin
from bookshelf.models import Book, Author, Profile, ElectronicBook, PaperBook

from import_export.admin import ImportExportModelAdmin
from import_export import resources

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

# admin.site.register(Book, BookAdmin)
admin.site.register(Author)
admin.site.register(Profile)
admin.site.register(PaperBook, PBookAdmin)
admin.site.register(ElectronicBook, EBookAdmin)
admin.site.register(Book, BookAdmin)



