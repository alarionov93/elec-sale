from io import StringIO
from django.core.serializers.json import Serializer

class JSONSerializer(Serializer):

    fields = []

    def __init__(self, fields=fields):
        super(JSONSerializer, self).__init__()
        self.fields = fields

    def serialize(self, queryset, **options):
        self.options = options
        self.stream = options.get("stream", StringIO())
        self.start_serialization()
        self.use_natural_primary_keys = True
        self.use_natural_foreign_keys = True
        self.first = True

        for obj in queryset:
            self.start_object(obj)
            for field in self.fields:
                self.handle_field(obj, field)
            self.end_object(obj)
            if self.first:
                self.first = False
        self.end_serialization()

        return self.getvalue()

    def handle_field(self, obj, field):
        self._current[field] = getattr(obj, field)

