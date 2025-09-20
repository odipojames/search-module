import django_filters
from .models import OfficialSearchApplication

class ApplicationFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    parcel_number = django_filters.CharFilter(field_name="parcel_number", lookup_expr="icontains")
    reference_number = django_filters.CharFilter(field_name="reference_number", lookup_expr="icontains")

    class Meta:
        model = OfficialSearchApplication
        fields = ["status", "parcel_number", "reference_number"]

