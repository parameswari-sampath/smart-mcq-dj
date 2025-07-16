import os
import platform
import psutil
import time
import pytz
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
from django.utils import timezone


def server_status(request):
    """Display comprehensive server status information"""
    try:
        # System Information
        system_info = {
            'hostname': platform.node(),
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor() or 'Unknown',
        }
        
        # Server Resources
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resources = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_count': psutil.cpu_count(),
            'memory_total': round(memory.total / (1024**3), 2),  # GB
            'memory_used': round(memory.used / (1024**3), 2),    # GB
            'memory_percent': memory.percent,
            'disk_total': round(disk.total / (1024**3), 2),      # GB
            'disk_used': round(disk.used / (1024**3), 2),        # GB
            'disk_percent': round((disk.used / disk.total) * 100, 2),
        }
        
        # Database Status
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = "Connected"
                db_error = None
        except Exception as e:
            db_status = "Error"
            db_error = str(e)
        
        # Application Status
        app_info = {
            'django_version': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
            'debug_mode': settings.DEBUG,
            'time_zone': settings.TIME_ZONE,
            'secret_key_set': bool(getattr(settings, 'SECRET_KEY', None)),
            'database_engine': settings.DATABASES['default']['ENGINE'].split('.')[-1],
        }
        
        # Server Uptime (approximate)
        try:
            uptime_seconds = psutil.boot_time()
            uptime = datetime.fromtimestamp(uptime_seconds)
            uptime_str = f"{(datetime.now() - uptime).days} days"
        except:
            uptime_str = "Unknown"
        
        # Environment Variables (safe ones only)
        env_vars = {
            'ALLOWED_HOSTS': os.getenv('ALLOWED_HOSTS', 'Not Set'),
            'DATABASE_URL': 'Set' if os.getenv('DATABASE_URL') else 'Not Set',
            'SECRET_KEY': 'Set' if os.getenv('SECRET_KEY') else 'Not Set',
        }
        
        # TIMING INFORMATION FOR AUTO-SUBMIT DEBUGGING
        now_utc = timezone.now()
        server_local_tz = timezone.get_current_timezone()
        server_local_time = timezone.localtime(now_utc)
        
        # Get system timezone info
        system_tz = time.tzname
        system_offset = time.timezone
        
        timing_info = {
            'current_utc': now_utc.isoformat(),
            'current_utc_formatted': now_utc.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'server_timezone': str(server_local_tz),
            'server_local_time': server_local_time.isoformat(),
            'server_local_formatted': server_local_time.strftime('%Y-%m-%d %H:%M:%S'),
            'system_timezone': system_tz,
            'system_offset_hours': -system_offset // 3600,
            'django_timezone_setting': settings.TIME_ZONE,
            'django_use_tz': settings.USE_TZ,
            'timestamp_unix': int(now_utc.timestamp()),
            'timestamp_ms': int(now_utc.timestamp() * 1000),
        }
        
        # Test different timezone representations
        common_timezones = ['UTC', 'US/Eastern', 'US/Pacific', 'Europe/London', 'Asia/Tokyo']
        timezone_comparison = {}
        for tz_name in common_timezones:
            try:
                tz = pytz.timezone(tz_name)
                local_time = now_utc.astimezone(tz)
                timezone_comparison[tz_name] = {
                    'time': local_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'offset': local_time.strftime('%z'),
                    'dst': local_time.dst() != None
                }
            except:
                timezone_comparison[tz_name] = {'error': 'Invalid timezone'}
        
        # Network and request timing
        request_info = {
            'request_time': now_utc.isoformat(),
            'remote_addr': request.META.get('REMOTE_ADDR', 'Unknown'),
            'http_x_forwarded_for': request.META.get('HTTP_X_FORWARDED_FOR', 'Not Set'),
            'http_x_real_ip': request.META.get('HTTP_X_REAL_IP', 'Not Set'),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
            'server_name': request.META.get('SERVER_NAME', 'Unknown'),
            'server_port': request.META.get('SERVER_PORT', 'Unknown'),
        }
        
        context = {
            'system_info': system_info,
            'resources': resources,
            'db_status': db_status,
            'db_error': db_error,
            'app_info': app_info,
            'uptime': uptime_str,
            'env_vars': env_vars,
            'timing_info': timing_info,
            'timezone_comparison': timezone_comparison,
            'request_info': request_info,
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status_ok': db_status == "Connected" and resources['cpu_percent'] < 90 and resources['memory_percent'] < 90,
        }
        
        # Return JSON for API requests
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse(context)
        
        return render(request, 'server_status/status.html', context)
        
    except Exception as e:
        error_context = {
            'error': str(e),
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status_ok': False,
        }
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse(error_context, status=500)
        
        return render(request, 'server_status/status.html', error_context)


def health_check(request):
    """Simple health check endpoint"""
    try:
        # Quick database check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }, status=500)