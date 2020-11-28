from django.shortcuts import render, get_object_or_404
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
import datetime
from django.urls import reverse
from catalog.forms import RenewBookForm


@login_required
def index(request):
	"""
	Функция отображения для домашней страницы сайта.
	"""
	# Генерация "количеств" некоторых главных объектов
	num_books=Book.objects.all().count()
	num_instances=BookInstance.objects.all().count()
	# Доступные книги (статус = 'a')
	num_instances_available=BookInstance.objects.filter(status__exact='a').count()
	num_authors=Author.objects.count()  # Метод 'all()' применен по умолчанию.

	# Отрисовка HTML-шаблона index.html с данными внутри 
	# переменной контекста context
	
# Number of visits to this view, as counted in the session variable.
	num_visits=request.session.get('num_visits', 0)
	request.session['num_visits'] = num_visits + 1
	print('num_visits')

	return render(
	   	request,
	   	'catalog/index.html',
	   	context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors,
	       	'num_visits':num_visits,} # num_visits appended

    	)

class BookListView(LoginRequiredMixin, generic.ListView):
	model = Book
	paginate_by = 2
	#context_object_name = 'my_book_list'   # ваше собственное имя переменной контекста в шаблоне
	#queryset = Book.objects.filter(title__icontains='war')[:5] # Получение 5 книг, содержащих слово 'war' в заголовке
	#template_name = 'books/my_arbitrary_template_name_list.html'  # Определение имени вашего шаблона и его расположения

class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book
    def book_detail_view(request,pk):
	    try:
	        book_id=Book.objects.get(pk=pk)
	    except Book.DoesNotExist:
	        raise Http404("Book does not exist")
	    #book_id=get_object_or_404(Book, pk=pk)
	    return render(
	        request,
	        'catalog/book_detail.html',
	        context={'book':book_id,}
	    )


class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    paginate_by = 2

class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author
    def author_detail_view(request,pk):
	    try:
	        author_id=Author.objects.get(pk=pk)
	    except Author.DoesNotExist:
	        raise Http404("Author does not exist")
	    #book_id=get_object_or_404(Book, pk=pk)
	    return render(
	        request,
	        'catalog/author_detail.html',
	        context={'author':author_id,}
	    )


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user. 
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name ='catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')




@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')




class BookCreate(CreateView):
    model = Book
    fields = '__all__'

class BookUpdate(UpdateView):
    model = Book
    fields = ['title','author','genre','language']

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')

# Create your views here.
