def add_show_menu(request):
    exclude_paths = ['/auth/login/', '/auth/logout/']
    return {'show_menu': request.path not in exclude_paths}