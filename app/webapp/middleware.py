from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class OneStudentPerSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.path == reverse('unified-login'):
            # Log out any currently logged-in student
            if request.session.get('student_id'):
                # Clear all session data to ensure only one student is logged in at a time
                request.session.flush()
        response = self.get_response(request)
        return response
