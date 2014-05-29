from apps.core.helpers import render_to_json
from apps.accounts.models import User, Spec
from apps.core.helpers import get_object_or_None
from django.db.models import Q


@render_to_json()
def users(request):
    q = request.GET.get('q', None)
    admin = request.user.is_authenticated() and request.user.is_admin
    operator = request.user.is_authenticated() and request.user.is_operator
    teacher = request.user.is_authenticated() and request.user.is_teacher

    if not all([admin or operator or teacher, q]):
        return []

    qset = (
        Q(username__icontains=q) |
        Q(email__icontains=q)
    )
    users = User.objects.filter(qset)
    lst = []
    for user in users:
        lst.append({
            'id': user.id, 'username': user.username,
            'email': user.email
        })
    return lst


@render_to_json()
def spec_patterns(request, pk):
    spec = get_object_or_None(Spec, pk=pk)
    if not spec:
        return []
    return spec.pattern_spec_set.all()