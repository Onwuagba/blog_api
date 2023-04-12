from django.views.generic import ListView, DetailView
import os, logging
from mainapp.models import Post
from django_filters import FilterSet

base_url = os.getenv("BASE_URL")
logger = logging.getLogger('qc_log')


class NewsFilter(FilterSet):
    class Meta:
        model = Post
        fields = ["type"]


class NewsView(ListView):
    model = Post
    paginate_by = 15
    template_name = "news/blog.html"
    filterset_fields = ["title"]
    # ordering = ['date_updated']

    def get_queryset(self):
        """
        return only news that haven't been deleted and sets lorem ipsum for posts with empty text
        """
        if query := self.request.GET.get("q"):
            queryset = Post.objects.filter(
                text__icontains=query, deleted=False
            ).order_by("date_added")
        else:
            queryset = Post.objects.filter(
                deleted=False
                ).order_by("-date_added")

        if queryset:
            for item in queryset:
                if not item.text:
                    item.text = "lorem ipsum placeholder"
            news_filter = NewsFilter(self.request.GET, queryset)
            return news_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context["filter"] = NewsFilter(self.request.GET, queryset)
        return context


class NewsDetailView(DetailView):
    model = Post
    template_name = "news/blog_detail.html"

    def get_object(self, **kwargs):
        try:
            queryset = Post.objects.get(pk=self.kwargs["pk"], deleted=False)
            if not queryset.text:
                queryset.text = "In publishing and graphic design, Lorem ipsum is a placeholder text commonly used to demonstrate the visual form of a document or a typeface without relying on meaningful content. Lorem ipsum may be used as a placeholder before final copy is available."
            return queryset
        except Post.DoesNotExist as ex:
            logger.error('Error retrieving post: %s', ex)
            return False
