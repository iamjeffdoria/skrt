from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse    
from .forms import LoginForm, CreateRecordForm, UpdateRecordForm, CreateAdminForm
from django.contrib.auth.models import User  
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import localtime
from .models import studRec
from django.db import transaction
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
import csv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import studRec, AttendanceLog
from django.conf import settings  # Needed for MEDIA_URL
from .models import UserProfile
from django.views.decorators.http import require_GET
from .forms import ReportForm, StudRecForm
from .models import Report
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage,  PageNotAnInteger
from django.contrib.auth import authenticate, login as auth_login
from django.template.loader import get_template
from xhtml2pdf import pisa
import cv2

import numpy as np
from io import BytesIO
from django.http import HttpResponse
from django.core.files.base import ContentFile
import base64
import json
from .models import PendingRequests
from django.utils.timezone import now
from django.db.models import Count
from django.utils.dateparse import parse_date
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import HeadOfSecurity
from django.views import View
from django.core.mail import send_mail
from dateutil.relativedelta import relativedelta
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Image, Spacer, Frame
from reportlab.lib.units import inch
import os
from django.templatetags.static import static

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer
from reportlab.lib import colors
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Q
import os

def student_list(request):
      # Only allow access to head of security and OSDS users
    user_type = request.session.get('user_type')
    if user_type != 'head_of_security' and user_type != 'admin':
        # Redirect students or unauthorized users
        if user_type == 'student':
            return redirect('stud-dash')
        else:
            return redirect('unified-login')
    students = studRec.objects.all()
    context = {'students': students}
    return render(request, 'webapp/student-list.html', context)

def mark_loss_rfid(request, student_id):
    if request.method == 'POST':
        try:
            student = get_object_or_404(studRec, id=student_id)
            student.status = "Loss RFID"
            student.save()
            return JsonResponse({'message': 'RFID marked as lost successfully!'})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    return JsonResponse({'message': 'Invalid request method.'}, status=400)

def unmark_loss_rfid(request, student_id):
    if request.method == 'POST':
        try:
            student = get_object_or_404(studRec, id=student_id)
            if student.status == "Loss RFID":
                student.status = "Active"  # Assuming "Active" is the default restored status
                student.save()
                return JsonResponse({'message': 'RFID unmarked as lost successfully!'})
            return JsonResponse({'message': 'Student is not marked as Loss RFID.'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    return JsonResponse({'message': 'Invalid request method.'}, status=400)

def download_logs_pdf(request):
    # Retrieve filters from the request
    log_type = request.GET.get('log_type', '')
    date = request.GET.get('date', '')
    course = request.GET.get('course', '')
    major = request.GET.get('major', '')
    time_frame = request.GET.get('time_frame', '')

    # Apply filters for log entries
    filters = Q()
    if log_type:
        filters &= Q(type=log_type)
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            filters &= Q(time__date=date_obj)
        except ValueError:
            pass
    if course:
        filters &= Q(student__course=course)
    if major:
        filters &= Q(student__major=major)

    # Time frame filters
    today = timezone.now().date()
    if time_frame == 'today':
        filters &= Q(time__date=today)
    elif time_frame == 'this_week':
        start_of_week = today - timedelta(days=today.weekday())
        filters &= Q(time__date__range=[start_of_week, today])
    elif time_frame == 'this_month':
        filters &= Q(time__year=today.year, time__month=today.month)

    # Retrieve logs based on filters
    filtered_logs = AttendanceLog.objects.filter(filters)

    # Paths to logo images
    logo_left_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'pitLOGO.png')
    logo_right_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'cote.png')

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="logs.pdf"'

    # Set up PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Header with institutional details
    header_data = [
        [
            Image(logo_left_path, width=50, height=50),
            "Republic of the Philippines\nPalompon Institute of Technology\nPalompon, Leyte\nCOLLEGE OF TECHNOLOGY AND ENGINEERING",
            Image(logo_right_path, width=50, height=50)
        ],
    ]

    # Styling for header table with added line spacing and adjustments
    header_table = Table(header_data, colWidths=[None, 350, None])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.black),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 0), (1, 0), 12),  # Slightly reduce font size for better spacing
        ('LEADING', (1, 0), (1, 0), 14),   # Increase line spacing for readability
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),  # Additional padding for the header
    ]))

    # Table data for logs
    table_data = [['Student Name', 'Course', 'Major', 'Log Type', 'Time']]
    for log in filtered_logs:
        row = [
            f"{log.student.first_name} {log.student.middle_name or ''} {log.student.last_name} {log.student.suffix or ''}",
            log.student.course,
            log.student.major,
            'Login' if log.type == 'login' else 'Logout',
            log.time.strftime("%Y-%m-%d %H:%M:%S"),
        ]
        table_data.append(row)

    # Styling the data table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Build PDF elements
    elements = [header_table, Spacer(1, 20), table]

    # Generate PDF
    doc.build(elements)

    return response


def activate_account(request, student_id):
    pending_request = get_object_or_404(PendingRequests, id=student_id)

    # Move data from PendingRequests to studRec
    studRec.objects.create(
        student_id=pending_request.student_id,
        first_name=pending_request.first_name,
        middle_name=pending_request.middle_name,
        last_name=pending_request.last_name,
        suffix=pending_request.suffix,
        course=pending_request.course,
        major=pending_request.major,
        picture=pending_request.picture,
        email=pending_request.email,
        password=pending_request.password,
        username=pending_request.username,
        status='Active',
        expiration=timezone.now() + relativedelta(months=5)
    )

    # Delete from PendingRequests
    pending_request.delete()

    messages.success(request, 'Your account has been activated.')
    return redirect('unified-login')  # Redirect to login page or dashboard


def unified_login(request):
   
    if request.session.get('student_id'):
        return redirect('stud-dash') 
 
    if request.user.is_authenticated:
        if request.session.get('user_type') == 'student':
            return redirect('stud-dash')
        elif request.session.get('user_type') == 'head_of_security':
            return redirect('head-dashboard')
        return redirect('dashboard-real')

    if request.method == "POST":
        username = request.POST.get('username', None)
        password = request.POST.get('password')

        # Check if the user is a student (by username)
        try:
            student = studRec.objects.get(username=username)
            if check_password(password, student.password):
                # Log the student in
                request.session['user_type'] = 'student'
                request.session['student_id'] = student.student_id
                request.session['student_name'] = f"{student.first_name} {student.last_name}"
                request.session['student_picture'] = student.picture.url if student.picture else None
                messages.success(request, "Logged in successfully.")
                return redirect('stud-dash')
            else:
                messages.warning(request, "Invalid username or password.")
        except studRec.DoesNotExist:
            pass

        # Check if the user is the head of security
        try:
            head_security = HeadOfSecurity.objects.get(username=username)
            if check_password(password, head_security.password):
                request.session['user_type'] = 'head_of_security'
                request.session['security_id'] = head_security.id
                messages.success(request, "Logged in successfully.")
                return redirect('head-dashboard')
            else:
                messages.warning(request, "Invalid username or password.")
        except HeadOfSecurity.DoesNotExist:
            pass

        # Check for regular user login
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            try:
                user_profile = UserProfile.objects.get(user=user)
                request.session['user_type'] = user_profile.user_type
                messages.success(request, "Logged in successfully.")
                return redirect('dashboard-real')
            except UserProfile.DoesNotExist:
                messages.warning(request, "User profile not found.")
        else:
            messages.warning(request, "Invalid username or password.")

    # Render the unified login form
    context = {
        'form': LoginForm()  # Make sure to include your unified form
    }
    return render(request, 'webapp/unified-login.html', context)


def head_dashboard(request):
    recent_students = studRec.objects.all().order_by('-creation_date')[:3]
    student_count = studRec.objects.count()
    recent_logs = AttendanceLog.objects.order_by('-time')[:3] 
    admin_count = User.objects.filter(is_superuser=True).count()
    context = {
        'student_count': student_count,
         'admin_count': admin_count,
         'recent_students':recent_students,
        'recent_logs': recent_logs,
        # Add other context variables as needed
    }   
    return render(request, 'webapp/head-dashboard.html',context)


def student_register(request):
    if request.method == 'POST':
        form = StudRecForm(request.POST, request.FILES)
        if form.is_valid():
            student_id = form.cleaned_data.get('student_id')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            # Check if the student ID, username, or email already exists
            if studRec.objects.filter(student_id=student_id).exists():
                messages.warning(request, 'A student with this ID already exists.')
            elif PendingRequests.objects.filter(student_id=student_id).exists():
                messages.warning(request, 'A pending request with this student ID already exists.')
            elif studRec.objects.filter(username=username).exists():
                messages.warning(request, 'A student with this username already exists.')
            elif PendingRequests.objects.filter(username=username).exists():
                messages.warning(request, 'A pending request with this username already exists.')
            elif studRec.objects.filter(email=email).exists():
                messages.warning(request, 'A student with this email already exists.')
            elif PendingRequests.objects.filter(email=email).exists():
                messages.warning(request, 'A pending request with this email already exists.')
            else:
                student = form.save(commit=False)
                # Set the status to 'Pending'
                student.status = 'Pending'
                # Save to PendingRequests, including email and password
                PendingRequests.objects.create(
                    student_id=student.student_id,
                    username=student.username,
                    first_name=student.first_name,
                    middle_name=student.middle_name,
                    last_name=student.last_name,
                    suffix=student.suffix,
                    course=student.course,
                    major=student.major,
                    picture=student.picture,
                    email=student.email,       # Include email
                    password=make_password(student.password)  # Include hashed password
                )
                messages.success(request, 'Student record created successfully and is now pending approval!')
                return redirect('unified-login')  # Redirect to a login page or relevant page
        else:
            messages.warning(request, 'Please correct the errors below.')
    else:
        form = StudRecForm()

    return render(request, 'webapp/student-register.html', {'form': form})


@csrf_exempt
def process_rfid(request):
    if request.method == 'POST':
        rfid_number = request.POST.get('rfid_number')
        student = studRec.objects.filter(rfid_number=rfid_number).first()

        if student:
            if student.status == 'Active':
                current_time = timezone.now()
                local_time = localtime(current_time)
                current_date = local_time.date()

                # Check logs for the current day
                today_logs = AttendanceLog.objects.filter(student=student, time__date=current_date)
                record_type = 'login' if today_logs.count() == 0 else 'logout' if today_logs.order_by('-time').first().type == 'login' else 'login'

                new_log = AttendanceLog.objects.create(
                    student=student,
                    student_reference_id=student.student_id,
                    type=record_type,
                    time=current_time,
                )

                new_log.date_in = current_date if record_type == 'login' else None
                new_log.date_out = current_date if record_type == 'logout' else None
                new_log.save()

                # Fetch recent logs excluding the current student, ensure three distinct students
                recent_logs = AttendanceLog.objects.exclude(student=student).order_by('-time')

                # Use a set to track seen students and limit to the first 3 distinct
                seen_students = set()
                distinct_recent_logs = []
                for log in recent_logs:
                    if log.student not in seen_students:
                        seen_students.add(log.student)
                        distinct_recent_logs.append(log)
                    if len(distinct_recent_logs) == 3:
                        break

                recent_log_list = [
                    {
                        'student': {
                            'picture': log.student.picture.url if log and log.student.picture else None
                        },
                    }
                    for log in distinct_recent_logs
                ]

                response_data = {
                    'first_name': student.first_name,
                    'middle_name': student.middle_name,
                    'last_name': student.last_name,
                    'suffix': student.suffix,
                    'course': student.course,
                    'major': student.major,
                    'time': local_time.strftime('%I:%M %p'),
                    'date': local_time.strftime('%Y-%m-%d'),
                    'picture': settings.MEDIA_URL + str(student.picture) if student.picture else None,
                    'type': record_type,
                    'recent_logs': recent_log_list  # Pass recent logs to the template
                }

                return JsonResponse({'status': 'success', 'data': response_data})
            elif student.status == 'Loss RFID':
                # Return specific error for Loss RFID
                return JsonResponse({'status': 'error', 'message': 'Reported Loss RFID'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Student is inactive'})
        return JsonResponse({'status': 'error', 'message': 'Student not found'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


# Homepage

def home(request):
    # Check if the user is authenticated (Django's built-in user authentication)
    if request.user.is_authenticated:
        return redirect('dashboard-real')  # Redirect to the admin/dashboard-real if authenticated
    
    # Check if the student is logged in using session data
    if request.session.get('student_id'):
        return redirect('stud-dash')  # Redirect to the student dashboard if a student is logged in

    if request.session.get('security_id'):
        return redirect('head-dashboard')

    # If neither, render the index page
    return render(request, 'webapp/index.html')


#Students logs




# def view_student_logs(request, student_id):
#     # Retrieve the student by their student_id
#     student = get_object_or_404(studRec, student_id=student_id)

#     # Get all logs for this student, ordered by time (latest to oldest)
#     logs = AttendanceLog.objects.filter(student=student).order_by('-time')

#     # Calculate total login and logout counts
#     total_login = logs.filter(type='login').count()
#     total_logout = logs.filter(type='logout').count()

#     # Date filtering
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')

#     # Convert date strings to date objects
#     try:
#         if start_date:
#             start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
#         if end_date:
#             end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
#     except ValueError:
#         messages.error(request, 'Invalid date format.')
#         start_date = None
#         end_date = None

#     # Apply filters
#     if start_date and end_date:
#         logs = logs.filter(time__date__range=[start_date, end_date])
#     elif start_date:
#         logs = logs.filter(time__date=start_date)
#     elif end_date:
#         logs = logs.filter(time__date=end_date)

#     # Pagination
#     entries_str = request.GET.get('entries', '')  # Default to empty string if not specified
#     if entries_str == 'all':
#         entries_per_page = None  # This means no pagination, show all records
#     else:
#         try:
#             entries_per_page = int(entries_str)
#             if entries_per_page <= 0:
#                 entries_per_page = 10  # Fallback default value
#         except ValueError:
#             entries_per_page = 10  # Fallback default value

#     if entries_per_page:
#         paginator = Paginator(logs, entries_per_page)
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
#     else:
#         page_obj = logs  # If "All" is selected, no pagination

#     context = {
#         'student': student,
#         'logs': page_obj,  # Pass the page object to the template
#         'total_login': total_login,
#         'total_logout': total_logout,
#         'page_obj': page_obj,  # Needed for pagination controls if not "all"
#         'entries_str': entries_str  # Pass entries string to the template for dropdown control
#     }

#     return render(request, 'webapp/student-logs.html', context)


def student_attendance_chart(request, student_id):
    student = get_object_or_404(studRec, pk=student_id)
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week

    # Get attendance logs for the current week
    attendance_logs = AttendanceLog.objects.filter(
        student=student,
        date_in__gte=start_of_week
    )

    # Prepare data for chart
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    login_data = [0] * 7
    logout_data = [0] * 7

    for log in attendance_logs:
        if log.date_in:
            day_index = (log.date_in.weekday())  # Monday = 0, Sunday = 6
            if log.type == 'login':
                login_data[day_index] += 1
            elif log.type == 'logout':
                logout_data[day_index] += 1

    return JsonResponse({
        "days": days,
        "logins": login_data,
        "logouts": logout_data
    })


def view_student_logs(request, student_id):
    student = get_object_or_404(studRec, student_id=student_id)
    logs = AttendanceLog.objects.filter(student=student).order_by('-time')
    print(student.first_name)

    chart_data = {i: {'logins': 0, 'logouts': 0} for i in range(7)}  # 7 for Monday to Sunday

    # Get login counts grouped by date_in (login date)
    login_data = logs.filter(type='login').values('date_in').annotate(count=Count('id'))

    # Get logout counts grouped by date_out (logout date)
    logout_data = logs.filter(type='logout').values('date_out').annotate(count=Count('id'))

    print("Login data:")
    for log in login_data:
        print(log)  # Print the login data

    print("Logout data:")
    for log in logout_data:
        print(log)  # Print the logout data
    
     # Accumulate login counts by day of the week
    for log in login_data:
        date_in = log['date_in']
        if date_in:
            day_of_week = date_in.weekday()  # Monday = 0, Sunday = 6
            chart_data[day_of_week]['logins'] += log['count']  # Accumulate the login count for each day

    # Accumulate logout counts by day of the week
    for log in logout_data:
        date_out = log['date_out']
        if date_out:
            day_of_week = date_out.weekday()  # Monday = 0, Sunday = 6
            chart_data[day_of_week]['logouts'] += log['count']  # Accumulate the logout count for each day


    # Prepare chart data labels and counts
    chart_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    login_counts = [chart_data[i]['logins'] for i in range(7)]
    logout_counts = [chart_data[i]['logouts'] for i in range(7)]

    # Serialize the data for AJAX response
    serialized_chart_labels = json.dumps(chart_labels)
    serialized_login_counts = json.dumps(login_counts)
    serialized_logout_counts = json.dumps(logout_counts)


    print("Serialized Chart Labels:", serialized_chart_labels)
    print("Serialized Login Counts:", serialized_login_counts)
    print("Serialized Logout Counts:", serialized_logout_counts)
        # Handle AJAX request for filtering
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
        time_frame = request.GET.get('time_frame')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if time_frame == "today":
            start_date = now().date()
            logs = logs.filter(date_in=start_date) | logs.filter(date_out=start_date)
        elif time_frame == "week":
            start_date = now() - timedelta(days=now().weekday())
            logs = logs.filter(date_in__gte=start_date) | logs.filter(date_out__gte=start_date)
        elif time_frame == "month":
            start_date = now().replace(day=1)
            logs = logs.filter(date_in__gte=start_date) | logs.filter(date_out__gte=start_date)

        # Filter by start and end date if provided
        if start_date:
            logs = logs.filter(date_in__gte=start_date) | logs.filter(date_out__gte=start_date)
        if end_date:
            logs = logs.filter(date_in__lte=end_date) | logs.filter(date_out__lte=end_date)
        
        # Format the response while handling None values
        return JsonResponse({
            'logs': [
                {
                    'type': log.type,
                    'date_in': log.date_in.strftime("%b %d, %Y") if log.date_in else 'Not Available',
                    'date_out': log.date_out.strftime("%b %d, %Y") if log.date_out else 'Not Available',
                    'time': log.time.strftime("%I:%M %p") if log.time else 'Not Available',
                    'note': log.note or 'No Note'
                }
                for log in logs
            ],
            'chart_labels': serialized_chart_labels,
            'login_counts': serialized_login_counts,
            'logout_counts': serialized_logout_counts,
        })
    # Prepare context for rendering
    for log in logs:
        log.formatted_date_in = log.date_in.strftime("%b %d, %Y") if log.date_in else "Not Available"
        log.formatted_date_out = log.date_out.strftime("%b %d, %Y") if log.date_out else "Not Available"

    context = {
        'student': student,
        'logs': logs,
        'login_counts': serialized_login_counts,
        'logout_counts': serialized_logout_counts,
        'chart_labels': serialized_chart_labels,
        
    }
    return render(request, 'webapp/student-logs.html', context)


#Login a admin

# def osds_login(request):
#     if request.session.get('student_id'):
#         return redirect('stud-dash')
#     form = LoginForm()

#     if request.method == "POST":
#         form = LoginForm(data=request.POST)

#         if form.is_valid():
#             username = request.POST.get('username')
#             password = request.POST.get('password')

#             user = authenticate(request, username=username, password=password)

#             if user is not None:
#                 auth_login(request, user)
                
#                 # Fetch the user's profile to determine user type
#                 try:
#                     user_profile = UserProfile.objects.get(user=user)
#                     request.session['user_type'] = user_profile.user_type
#                 except UserProfile.DoesNotExist:
#                     request.session['user_type'] = 'Unknown'  # or handle as needed

#                 messages.success(request, "Logged in successfully.")
#                 return redirect('dashboard-real')
#             else:
#                 messages.warning(request, "Invalid username or password.")
#         else:
#             messages.warning(request, "Invalid username or password.")

#     context = {'form': form}
#     return render(request, 'webapp/login.html', context)



@login_required(login_url='unified-login')
def dashboard_real(request):
    
    recent_students = studRec.objects.all().order_by('-creation_date')[:3]
    student_count = studRec.objects.count()
    recent_logs = AttendanceLog.objects.order_by('-time')[:3] 
    admin_count = User.objects.filter(is_superuser=True).count()
    context = {
        'student_count': student_count,
         'admin_count': admin_count,
         'recent_students':recent_students,
        'recent_logs': recent_logs,
        # Add other context variables as needed
    }   
    return render(request, 'webapp/dashboard2.html',context)



def student_dashboard(request):
    if request.user.is_authenticated:
        return redirect('dashboard-real')  # Redirect to the admin/dashboard-real if authenticated
    
    
    student_id = request.session.get('student_id')
    
    if student_id:
        student = studRec.objects.get(student_id=student_id)
        full_name = f"{student.first_name} {student.middle_name or ''} {student.last_name}".strip()
    else:
        full_name = "Student"  # Default if no student is logged in

    return render(request, 'webapp/stud-dash.html', {
        'student_name': full_name,
    })


# def student_login(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard-real')

#     if request.method == 'POST':
#         # Log out any currently logged-in student
#         if request.session.get('student_id'):
#             # Clear all session data to ensure only one student is logged in at a time
#             request.session.flush()

#         student_id = request.POST.get('student_id')
#         password = request.POST.get('password')
#         try:
#             student = studRec.objects.get(student_id=student_id)
            
#             # Verify password
#             if not check_password(password, student.password):
#                 messages.warning(request, 'Invalid password')
#                 return render(request, 'webapp/student-login.html')

#             # Log the student in
#             request.session['user_type'] = 'student'
#             request.session['student_id'] = student.student_id  # Save student ID in session
#             request.session['student_name'] = f"{student.first_name} {student.last_name}"  # Save student name in session
#             if student.picture:
#                 request.session['student_picture'] = student.picture.url  # Save student picture URL in session
#             else:
#                 request.session['student_picture'] = None  # Handle case with no picture

#             messages.success(request, "Logged in successfully.")
#             return redirect(reverse('stud-dash'))
#         except studRec.DoesNotExist:
#             # If student ID does not match, show an error message
#             messages.warning(request, 'Invalid student ID')
#     return render(request, 'webapp/student-login.html')


#dashboard/SEARCH


def dashboard(request):
     # Only allow access to head of security and OSDS users
    user_type = request.session.get('user_type')
    if user_type != 'head_of_security' and user_type != 'admin':
        # Redirect students or unauthorized users
        if user_type == 'student':
            return redirect('stud-dash')
        else:
            return redirect('unified-login')  # Or another appropriate view for unauthorized access
    # Fetch all available courses and majors for dropdowns
    courses = studRec.objects.values_list('course', flat=True).distinct()
    majors = studRec.objects.values_list('major', flat=True).distinct()

    # Start with all records
    my_records = studRec.objects.all()

    # Handle search query
    query = request.GET.get('q', '')
    if query:
        # Split the query into words and create Q objects for each word
        query_words = query.split()
        multiple_q = Q()
        for word in query_words:
            multiple_q |= Q(first_name__icontains=word) | Q(last_name__icontains=word) | \
                          Q(course__icontains=word) | Q(rfid_number__icontains=word) | \
                          Q(major__icontains=word) | Q(student_id__icontains=word)
        my_records = my_records.filter(multiple_q)

    # Handle course filter
    selected_course = request.GET.get('course', '')
    if selected_course:
        my_records = my_records.filter(course=selected_course)

    # Handle major filter
    selected_major = request.GET.get('major', '')
    if selected_major:
        my_records = my_records.filter(major=selected_major)

    # Get the number of entries per page from the request, defaulting to 10
    entries_per_page_str = request.GET.get('entries', '10')  # Default to '10' if not provided
    try:
        entries_per_page = int(entries_per_page_str)
        if entries_per_page <= 0:
            entries_per_page = 10  # Fallback default value if non-positive
    except ValueError:
        entries_per_page = 10  # Fallback default value in case of invalid input

    # Set up pagination
    paginator = Paginator(my_records, entries_per_page)
    page_number = request.GET.get('page', '1')  # Default to the first page if not provided
    try:
        records = paginator.get_page(page_number)
    except EmptyPage:
        records = paginator.get_page(1)  # Fallback to the first page in case of invalid page number

    filtered_count = my_records.count()
    context = {
        'records': records,
        'courses': courses,
        'majors': majors,
        'entries': entries_per_page,
        'paginator': paginator,
        'filtered_count': filtered_count, 
    }
    return render(request, 'webapp/dashboard.html', context=context)



def search_records(request):
    query = request.GET.get('q', '')
    course = request.GET.get('course', '')
    major = request.GET.get('major', '')

    records = studRec.objects.all()

    if query:
        # Split query into words
        query_words = query.split()
        multiple_q = Q()
        for word in query_words:
            multiple_q |= Q(first_name__icontains=word) | Q(last_name__icontains=word) | \
                          Q(course__icontains=word) | Q(rfid_number__icontains=word) | \
                          Q(major__icontains=word) | Q(student_id__icontains=word) | \
                          Q(middle_name__icontains=word) | Q(suffix__icontains=word)
        records = records.filter(multiple_q)
    
    if course:
        records = records.filter(course=course)
    if major:
        records = records.filter(major=major)

    results = []
    for record in records:
        results.append({
            'id': record.id,
            'picture': {'url': record.picture.url} if record.picture else None,
            'student_id': record.student_id,
            'first_name': record.first_name,
            'middle_name': record.middle_name,
            'last_name': record.last_name,
            'suffix': record.suffix,
            'course': record.course,
            'major': record.major,
            'rfid_number': record.rfid_number,
        })

    return JsonResponse({'results': results})

# Create a record




def create_record(request):
    if request.method == 'POST':
        form = CreateRecordForm(request.POST, request.FILES)
        if form.is_valid():
            rfid_number = form.cleaned_data['rfid_number']
            student_id = form.cleaned_data['student_id']
            email = form.cleaned_data.get('email') 
            password = form.cleaned_data['password']  # Get the plain password from the form

            # Check for existing RFID number or student ID
            if studRec.objects.filter(rfid_number=rfid_number).exists():
                messages.warning(request, 'RFID number already exists.')
                
            elif studRec.objects.filter(student_id=student_id).exists():
                messages.warning(request, 'Student ID already exists.')
            
            elif studRec.objects.filter(email=email).exists():
                messages.warning(request, 'Email already exists.')
            else:
                # Create the student instance but don't save yet
                student = form.save(commit=False)

                # Hash the password
                student.password = make_password(password)

                # Set the expiration date to 5 months from now
                student.expiration = timezone.now() + relativedelta(months=5)

                # Save the student record with the hashed password
                student.save()

                messages.success(request, 'Record added successfully.')
                return redirect('dashboard')
        else:
            # If the form is invalid, retain the picture and other data
            picture = request.FILES.get('picture')
            if picture:
                form.instance.picture = picture  # Retain the uploaded picture
    else:
        form = CreateRecordForm()

    return render(request, 'webapp/create-record.html', {'form': form})
        
# Update Record

def update_record(request, pk):
    record = get_object_or_404(studRec, pk=pk)  # Retrieve the record using the primary key (pk)
    
    if request.method == 'POST':
        form = UpdateRecordForm(request.POST, request.FILES, instance=record)  # Ensure to include request.FILES
        if form.is_valid():
            student_id = form.cleaned_data.get('student_id')
            rfid_number = form.cleaned_data.get('rfid_number')
            email = form.cleaned_data.get('email')

            # Check if student ID or RFID number already exists in another record
            if studRec.objects.filter(student_id=student_id).exclude(pk=pk).exists():
                messages.warning(request, 'A student with this ID already exists. Please check the details.')
                return render(request, 'webapp/update-record.html', {'form': form, 'record': record})

            if studRec.objects.filter(rfid_number=rfid_number).exclude(pk=pk).exists():
                messages.warning(request, 'A student with this RFID number already exists. Please check the details.')
                return render(request, 'webapp/update-record.html', {'form': form, 'record': record})

            if studRec.objects.filter(email=email).exclude(pk=pk).exists():
                messages.warning(request, 'A student with this email already exists. Please check the details.')
                return render(request, 'webapp/update-record.html', {'form': form, 'record': record})
            
            # If validation passes, save the updated record
            updated_record = form.save()  # Save the form
            messages.success(request, "Record Updated")  # Add success message
            return redirect('record', pk=updated_record.pk)  # Redirect after saving
    else:
        form = UpdateRecordForm(instance=record)  # Load existing data
    
    context = {'form': form, 'record': record}  # Pass the record object to the template context
    return render(request, 'webapp/update-record.html', context=context)


# View a record



def view_record(request, pk):
        
        all_records = studRec.objects.get(id=pk)

        context = {'record': all_records}

        return render(request, 'webapp/view-record.html', context=context)


#Delete a record 


def delete_record(request, pk):
    if request.method == 'POST':
        record = get_object_or_404(studRec, id=pk)
        record.delete()
        messages.success(request, "Record Deleted.")
        return JsonResponse({'status': 'success', 'message': 'Record deleted', 'redirect_url': reverse('dashboard')})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


# View admin lists


def view_admin(request):
    # Retrieve all users with their profiles
    users_list = User.objects.select_related('userprofile').all()

    # Get the number of entries per page from the request
    entries_str = request.GET.get('entries', '')  # Default to empty string if not provided

    if entries_str == '':
        # If '-----' is selected, don't paginate and show all records
        users = users_list
    else:
        try:
            entries = int(entries_str)
            if entries <= 0:
                entries = 10  # Fallback default value if non-positive
        except ValueError:
            entries = 10  # Fallback default value in case of invalid input

        # Set up pagination
        paginator = Paginator(users_list, entries)
        page_number = request.GET.get('page', '1')  # Default to the first page if not provided

        try:
            users = paginator.get_page(page_number)
        except EmptyPage:
            users = paginator.get_page(1)  # Fallback to the first page in case of invalid page number

    return render(request, 'webapp/admin-record.html', {'users': users})

    
def create_admin(request):
    if request.method == 'POST':
        form = CreateAdminForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            picture = form.cleaned_data.get('picture')
            # Create a UserProfile for the new admin
            UserProfile.objects.create(user=user, picture=picture, user_type='admin')
            messages.success(request, 'Admin record added successfully.')
            return redirect('admin-record')
    else:
        form = CreateAdminForm()
    
    context = {'form': form}
    return render(request, 'webapp/create-record-admin.html', context)


def update_profile(request):
    if request.method == 'POST':
        user = request.user
        
        # Ensure the user has a UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Update user fields
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.username = request.POST.get('username')  # Add this line to update the username
        user.email = request.POST.get('email')  
        
        # Update profile picture
        if 'picture' in request.FILES:
            user_profile.picture = request.FILES['picture']
        
        # Handle password change
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password and new_password == confirm_password:
            user.set_password(new_password)
            update_session_auth_hash(request, user)  # Keep the user logged in after password change
        
        # Save user and profile
        user.save()
        user_profile.save()

        messages.success(request, 'Profile updated successfully.')

        # Redirect back to the previous page
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return redirect('dashboard')


@login_required(login_url='unified-login')
def prompt(request):
      recent_logs = AttendanceLog.objects.order_by('-time')[:2]
      context = {
        'recent_logs': recent_logs
        }
      return render(request, 'webapp/student-prompt.html',context)

def recent_logs(request):
    if request.method == 'GET':
        # Get the latest 10 logs
        logs = AttendanceLog.objects.order_by('-time')[:10]
        log_list = [
            {
                'time': log.time.isoformat(),
                'student': {
                    'first_name': log.student.first_name,
                    'middle_name': log.student.middle_name,
                    'last_name': log.student.last_name
                },
                'type': log.type
            }
            for log in logs
        ]
        return JsonResponse({'recent_logs': log_list})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

# User Logout

def logout(request):
        auth.logout(request)
        messages.success(request, "Logged out.")
        return redirect('unified-login')

def student_logout(request):
        auth.logout(request)
        messages.success(request, "Logged out.")
        return redirect('unified-login')

def head_logout(request):
        auth.logout(request)
        messages.success(request, "Logged out.")
        return redirect('unified-login')
            

def block_student(request, pk):
    student = get_object_or_404(studRec, pk=pk)
    student.status = 'Inactive'
   
    student.save()

    return JsonResponse({'status': 'success', 'message': 'Student blocked'})



def unblock_student(request, pk):
    student = get_object_or_404(studRec, pk=pk)
    student.status = 'Active'
    student.save()
   
    return JsonResponse({'status': 'success', 'message': 'Student unblocked'})


def create_report(request):
    if request.user.is_authenticated:
        return redirect('dashboard-real')
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            # Save the report with the current student's ID
            report = form.save(commit=False)
            report.student_id = request.session.get('student_id')
            report.save()
            messages.success(request,'Report Created')
            return redirect('create-report')  # Redirect to the same page or another page
    else:
        form = ReportForm()

    # Fetch reports for the currently logged-in student
    student_id = request.session.get('student_id')
    reports = Report.objects.filter(student_id=student_id)

    return render(request, 'webapp/create-report.html', {
        'form': form,
        'reports': reports,
    })

@login_required(login_url='unified-login')
def student_reports(request):
    # Order reports by 'date_submitted' in descending order
    reports = Report.objects.all().order_by('-date_submitted')
    
    return render(request, 'webapp/student-reports.html', {
        'reports': reports,
    })

def sidebar_view(request):
    if request.user.is_authenticated:
        # Assuming `student_id` is stored in the `username` field; adjust as needed
        student_record = studRec.objects.filter(student_id=request.user.username).first()
    else:
        student_record = None

    return render(request, 'webapp/navbar.html', {'student_record': student_record})


def view_own_logs(request):
    if request.user.is_authenticated:
        return redirect('dashboard-real')
    
    # Get the student_id from the session
    student_id = request.session.get('student_id')
    
    # Initialize variables to avoid UnboundLocalError
    student = None
    logs = []
    total_login = 0
    total_logout = 0
    page_obj = None
    entries_str = request.GET.get('entries', '')  # Default to empty string if not specified
    time_frame = request.GET.get('time_frame', '')

    if student_id:
        try:
            # Fetch the student record based on student_id
            student = studRec.objects.get(student_id=student_id)
            
            # Get all logs for this student, ordered by time (latest to oldest)
            logs = AttendanceLog.objects.filter(student=student).order_by('-time')

            # Calculate total login and logout counts
            total_login = logs.filter(type='login').count()
            total_logout = logs.filter(type='logout').count()

            # Time frame filtering
            if time_frame == "this_day":
                today = datetime.today().date()
                logs = logs.filter(time__date=today)
            elif time_frame == "this_week":
                start_of_week = datetime.today() - timedelta(days=datetime.today().weekday())
                logs = logs.filter(time__date__gte=start_of_week.date())
            elif time_frame == "this_month":
                start_of_month = datetime.today().replace(day=1)
                logs = logs.filter(time__date__gte=start_of_month.date())

            # Date filtering (same as before)
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            # Convert date strings to date objects
            try:
                if start_date:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                if end_date:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid date format.')
                start_date = None
                end_date = None

            # Apply filters
            if start_date and end_date:
                logs = logs.filter(time__date__range=[start_date, end_date])
            elif start_date:
                logs = logs.filter(time__date=start_date)
            elif end_date:
                logs = logs.filter(time__date=end_date)

            # Pagination
            if entries_str == 'all':
                entries_per_page = None  # This means no pagination, show all records
            else:
                try:
                    entries_per_page = int(entries_str)
                    if entries_per_page <= 0:
                        entries_per_page = 10  # Fallback default value
                except ValueError:
                    entries_per_page = 10  # Fallback default value

            if entries_per_page:
                paginator = Paginator(logs, entries_per_page)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
            else:
                page_obj = logs  # If "All" is selected, no pagination

        except studRec.DoesNotExist:
            # Handle case where student record does not exist
            messages.error(request, 'Student record does not exist.')

    return render(request, 'webapp/own_logs.html', {
        'student': student,
        'logs': page_obj,  # Pass the page object to the template
        'total_login': total_login,
        'total_logout': total_logout,
        'page_obj': page_obj,
        'entries_str': entries_str,  # Pass entries string to the template for dropdown control
        'time_frame': time_frame  # Pass the selected time frame
    })

def student_request(request):
    
    students = PendingRequests.objects.all()

    return render(request, 'webapp/student-requests.html', {'students': students})

def approve_request(request, request_id):
    pending_request = get_object_or_404(PendingRequests, id=request_id)
    
    pending_request.status = 'Processing'
    pending_request.save()
    
    # Generate activation link
    activation_link = request.build_absolute_uri(
        reverse('activate-account', args=[pending_request.id])
    )

    # Send activation email to the student
    send_mail(
        'Activate Your Student Account',
        f'Hello {pending_request.first_name},\n\n'
        f'Please activate your student account by clicking the link below:\n\n'
        f'{activation_link}\n\n'
        f'Thank you!',
        settings.DEFAULT_FROM_EMAIL,
        [pending_request.email],
        fail_silently=False,
    )

    messages.success(request, 'Activation email sent to the student.')
    return redirect('student-request')



def reject_request(request, request_id):
    pending_request = get_object_or_404(PendingRequests, id=request_id)
    # Delete from PendingRequests
    pending_request.delete()

    messages.success(request, 'Student request rejected and removed.')
    return redirect('student-request')  # Redirect to the pending requests list view

def registration_data(request):
    # Retrieve the current year for filtering
    year = request.GET.get('year', now().year)

    # Fetch registration counts per month for the specified year
    registrations = studRec.objects.filter(creation_date__year=year).values('creation_date__month').annotate(count=Count('id')).order_by('creation_date__month')

    # Prepare data for the chart
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    data = [0] * 12
    
    for entry in registrations:
        month = entry['creation_date__month']  # Get the month number (1-12)
        count = entry['count']  # Get the count of registrations for that month
        data[month - 1] = count  # Store the count in the corresponding month index

    return JsonResponse({
        'labels': months,
        'data': data
    })

def get_attendance_data(request):
    month = request.GET.get('month')
    if month:
        try:
            # Parse the month into a date object (e.g., 2024-09)
            month_date = parse_date(f"{month}-01")
            start_date = month_date.replace(day=1)
            end_date = (start_date + timedelta(days=31)).replace(day=1)  # Next month first day

            # Filter logs based on the selected month
            logs = AttendanceLog.objects.filter(time__range=[start_date, end_date])
            labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            login_data = [0] * 7
            logout_data = [0] * 7

            for log in logs:
                day_of_week = log.time.weekday()  # Monday=0, Sunday=6
                if log.type == 'login':
                    login_data[day_of_week] += 1
                elif log.type == 'logout':
                    logout_data[day_of_week] += 1

            data = {
                'labels': labels,
                'login_data': login_data,
                'logout_data': logout_data
            }
            return JsonResponse(data)
        except ValueError:
            return JsonResponse({'error': 'Invalid month format'}, status=400)
    else:
        return JsonResponse({'error': 'Month parameter is required'}, status=400)



def all_logs(request):
    user_type = request.session.get('user_type')
    if user_type != 'head_of_security' and user_type != 'admin':
        # Redirect students or unauthorized users
        if user_type == 'student':
            return redirect('stud-dash')
        else:
            return redirect('unified-login')
    
    # Get filter parameters from the request
    log_type = request.GET.get('log_type', '')
    date = request.GET.get('date', '')
    course = request.GET.get('course', '')
    major = request.GET.get('major', '')
    time_frame = request.GET.get('time_frame', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
   
    filters = Q()

    # Filter by log type if selected
    if log_type:
        filters &= Q(type=log_type)

    # Filter by specific date if selected
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            filters &= Q(time__date=date_obj)
        except ValueError:
            pass  # Ignore invalid date formats

    # Filter by course if selected
    if course:
        filters &= Q(student__course=course)

    # Filter by major if selected
    if major:
        filters &= Q(student__major=major)

    # Filter by time frame (today, this week, this month) if selected
    today = timezone.now().date()
    if time_frame == 'today':
        filters &= Q(time__date=today)
    elif time_frame == 'this_week':
        start_of_week = today - timedelta(days=today.weekday())  # Monday as start of the week
        filters &= Q(time__date__range=[start_of_week, today])
    elif time_frame == 'this_month':
        filters &= Q(time__year=today.year, time__month=today.month)

     # Filter by start date and end date if both are provided
    if start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            filters &= Q(time__date__range=[start_date_obj, end_date_obj])
        except ValueError:
            pass  # Ignore invalid date formats

    # Retrieve all logs based on filters
    all_logs = AttendanceLog.objects.filter(filters)
    total_login = all_logs.filter(type='login').count()
    total_logout = all_logs.filter(type='logout').count()
    print(total_login)
    print(total_logout)

    # Course choices for the dropdown
    course_choices = [
        ('BSMT', 'Bachelor of Science in Marine Transportation(BSMT)'),
        ('BSMar-E', 'Bachelor of Science in Marine Engineering(BSMar-E)'),
        ('BEEd', 'Bachelor of Elementary Education(BEEd)'),
        ('BSed', 'Bachelor of Secondary Education(BSed)'),
        ('BTLEd', 'Bachelor of Technology and Livelihood Education(BTLEd)'),
        ('BTVTEd', 'Bachelor of Technical Vocational Teacher Education(BTVTEd)'),
        ('BPEd', 'Bachelor of Physical Education(BPEd)'),
        ('BACom', 'Bachelor of Arts in Communication(BACom)'),
        ('BSHM', 'Bachelor of Science in Hospitality Management(BSHM)'),
        ('BSBA', 'Bachelor of Science in Business Administration major in Marketing Management(BSBA)'),
        ('BSMarBio', 'Bachelor of Science in Marine Biology(BSMarBio)'),
        ('BSIE', 'Bachelor of Science in Industrial Engineering(BSIE)'),
        ('BSME', 'Bachelor of Science in Mechanical Engineering(BSME)'),
        ('BSEE', 'Bachelor of Science in Electrical Engineering(BSEE)'),
        ('BSIT', 'Bachelor of Science in Information Technology(BSIT)'),
        ('BSInT', 'Bachelor of Science in Industrial Technology(BSInT)'),
    ]

    # Major choices for the dropdown
    major_choices = [
        ('English', 'English'),
        ('Filipino', 'Filipino'),
        ('Mathematics', 'Mathematics'),
        ('Social Studies', 'Social Studies'),
        ('Automotive', 'Automotive'),
        ('Drafting', 'Drafting'),
        ('Electrical', 'Electrical'),
        ('Electronics', 'Electronics'),
        ('Fashion and Apparel', 'Fashion and Apparel'),
        ('Food and Beverages Preparation Service Management', 'Food and Beverages Preparation Service Management'),
        ('Mechanical', 'Mechanical'),
        ('Powerplant', 'Powerplant'),
        ('Welding and Fabrication', 'Welding and Fabrication'),
        ('No Major', 'No Major'),
    ]

    # Render the template with logs and dropdown choices
    return render(request, 'webapp/all-logs.html', {
        'logs': all_logs,
        'course_choices': course_choices,
        'major_choices': major_choices,
        'total_login': total_login,
        'total_logout': total_logout,
    })

def student_details(request, student_id):
    try:
        student = PendingRequests.objects.get(id=student_id)
        data = {
            'student_id': student.student_id,
            'first_name': student.first_name,
            'middle_name': student.middle_name,
            'last_name': student.last_name,
            'email': student.email,
            'suffix': student.suffix,
            'course': student.course,
            'major': student.major,
            'picture': student.picture.url if student.picture else None,
            'creation_date': student.creation_date.strftime('%Y-%m-%d'),
            'status': student.status,
            'username': student.username,
        }
        return JsonResponse(data)
    except PendingRequests.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

def check_username_availability(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': studRec.objects.filter(username=username).exists() or PendingRequests.objects.filter(username=username).exists()
    }
    return JsonResponse(data)


def check_student_id_availability(request):
    student_id = request.GET.get('student_id', None)
    data = {
        'is_taken': studRec.objects.filter(student_id=student_id).exists() or PendingRequests.objects.filter(student_id=student_id).exists()
    }
    return JsonResponse(data)

def check_email_availability(request):
    email = request.GET.get('email', None)
    data = {'is_taken': False, 'invalid_email': False}

    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        data['invalid_email'] = True
    else:
        # Check if email exists in either the main or pending records
        data['is_taken'] = studRec.objects.filter(email=email).exists() or PendingRequests.objects.filter(email=email).exists()
    
    return JsonResponse(data)