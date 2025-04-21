def is_librarian(request):
    return {
        'is_librarian': request.user.is_authenticated and request.user.groups.filter(name='Librarian').exists()
    }
