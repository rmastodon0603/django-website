from django.test import TestCase
from django.http import HttpRequest
from django.conf import settings

from django.urls import resolve

from blog import views


class TestProject(TestCase):
    def test_project_name(self):
        """1) Создать проект на django с названием website"""
        self.assertEqual("website", settings.BASE_DIR.name, "Отсутствует проект website")

    def test_application(self):
        """2) В проект добавить приложение blog"""
        path = settings.BASE_DIR / "blog"
        self.assertTrue(path.exists(), "Отстутвует приложение blog")

    def test_app_blog_in_settings(self):
        """3) В файле настроек settings.py добавить приложение blog в список приложений проекта"""
        self.assertTrue(('blog' in settings.INSTALLED_APPS) or ('blog.apps.BlogConfig' in settings.INSTALLED_APPS),
                        "Не добавлено приложение blog в список INSTALLED_APPS")

    def test_templates_dir(self):
        """4) В проекте создать директорию templates в проекте (внутри папки website)"""
        path = settings.BASE_DIR / "templates"
        self.assertTrue(path.exists(), "Отстутвует директория templates")

    def test_templates_blog_dir(self):
        """5) 	В директории templates создать директорию blog"""
        path = settings.BASE_DIR / "templates" / "blog"
        self.assertTrue(path.exists(), "Отстутвует директория templates/blog")

    def test_settings_templates(self):
        """6) В файле настроек settings.py прописать путь к директории с шаблонами templates"""
        path = settings.BASE_DIR / "templates"
        self.assertTrue(path in settings.TEMPLATES[0]['DIRS'],
                        "Не настроен путь к диретории с шаблонами в TEMPLATES[0]['DIRS']")

    def test_exists_static_dirs(self):
        """7) В директории проекта создать директорию static и static/blog"""
        path = settings.BASE_DIR / "static"
        self.assertTrue(path.exists(), "Отсутствует директория static")
        path /= "blog"
        self.assertTrue(path.exists(), "Отсутствует директория static/blog")

    def test_settings_static_dir(self):
        """8) Добавить настройки в файл settings.py для указания местоположения директории статических файлов"""
        path = settings.BASE_DIR / "static"
        self.assertTrue(path in settings.STATICFILES_DIRS,
                        "Отстутсвуют настройки статических файлов в STATICFILES_DIRS")

    def test_exists_css_dir(self):
        """10) Скопировать директории css, assets, images и js в static/blog"""
        static = settings.BASE_DIR / 'static' / 'blog'
        css_path = static / "css" / 'styles.css'
        self.assertTrue(css_path.exists(), "Отсутствует файл static/blog/css/styles.css")
        js_path = static / "js" / 'scripts.js'
        self.assertTrue(js_path.exists(), "Отсутствует файл static/blog/js/scripts.js")
        fabicon_path = static / "assets" / 'favicon.ico'
        self.assertTrue(fabicon_path.exists(), "Отсутствует файл static/blog/assets/favicon.ico")
        images_path = static / 'images'
        self.assertTrue(images_path.exists(), "Отсутствует папка static/blog/images")

    def test_exists_templates_file(self):
        """11) Поместить файлы index.html и post.html в директорию templates/blog"""
        base = settings.BASE_DIR / "templates" / "blog"
        path = base / "index.html"
        self.assertTrue(path.exists(), "Отсутствует файл templates/blog/index.html")
        path = base / "post.html"
        self.assertTrue(path.exists(), "Отсутствует файл templates/blog/post.html")

    def test_exists_layout_file(self):
        """12) На базе файлов index.html и post.html создать общий шаблон layout.html в папке templates"""
        base = settings.BASE_DIR / "templates"
        path = base / "layout.html"
        self.assertTrue(path.exists(), "Отсутствует файл templates/blog/index.html")

    def test_layout_file(self):
        """
        13) В базовом шаблоне layout.html необходимо:
        а) подгрузить статические файлы
        б) изменить ссылки в атрибуте href в тегах link и атрибут src в тегах script
        в) содержимое элемента div с классом col-md-8 заменить на блок {% block content %}{% endblock %}
        """
        layout = settings.BASE_DIR / "templates" / 'layout.html'
        self.assertTrue(layout.exists(), "layout.html не существует")
        with layout.open() as f:
            html = "".join(f.readlines())
            self.assertRegex(html, r'{%\s+load\s+static\s+%}', msg="Не подгружены статические файлы")
            self.assertNotRegex(html, r'<div\s+class="col-md-8"\s*>',
                                msg='Этот элемент нужно заменить на {% block content %}{% endblock %}')
            self.assertNotRegex(html, r'<div\s+class="col-lg-8"\s*>',
                                msg='Этот элемент нужно заменить на {% block content %}{% endblock %}')
            self.assertRegex(html, r'{%\s+block\s+content\s+%}{%\s+endblock\s+%}',
                             msg="Нет блока content")

    def test_index_post_file(self):
        """
        14) В файлах index.html и post.html необходимо:
            а) подгрузить статические файлы
            б) наследовать шаблон layout.html
            в) из содердимого оставить только то, что входило в <div class="col-md-8">
            г) поместить это содержимое в блок content
            д) обновить ссылки с в index.html на /blog
        """
        path = settings.BASE_DIR / "templates" / 'blog'
        files = 'index.html', 'post.html'
        for file in files:
            template = path / file
            self.assertTrue(template.exists(), f"{file} не существует")
            with template.open() as f:
                html = "".join(f.readlines())
                self.assertRegex(html, r'{%\s+load\s+static\s+%}', msg="Не подгружены статические файлы")
                self.assertNotRegex(html, r'{%\s*extends\+(["''])layout.html$1\s*%}',
                                    msg='Шаблон должен наследовать laytou.html')
                self.assertRegex(html, r'<div\s+class="col-md-8"\s*>')
                self.assertRegex(html, r'{%\s+block\s+content\s+%}', msg="Нет блока content")

    def test_index_content(self):
        """15) Добавить представление index в файле blog/views.py, которое должно возвращать
        отрендеренный шаблон blog/index.html"""
        request = HttpRequest()
        response = views.index(request)
        content = response.content.decode("utf-8")
        pattern = r'<h1\s+class\s*=\s*\"my-4\">\s*Page\s+Heading\s+<small>\s*Secondary\s+Text\s*</small>\s*</h1>'
        self.assertRegex(content, pattern)

    def test_present_module_urls(self):
        """16) Добавить модуль urls.py в приложение blog"""
        from blog.urls import urlpatterns

    def test_index_route(self):
        """17) Добавить привязку представления index к пути /"""
        index = resolve("/")
        self.assertEqual(index.func, views.index)

    def test_post_comment(self):
        """18) Добавить представление post в файле blog/views.py, которое должно возвращать
        отрендеренный шаблон blog/post.html"""
        request = HttpRequest()
        response = views.post(request)
        content = response.content.decode("utf-8")
        pattern = r'<h1 class="mt-4">Post Title</h1>'
        self.assertRegex(content, pattern)

    def test_post_route(self):
        """19) Добавить привязку представления post к пути /post"""
        index = resolve("/post/")
        self.assertEqual(index.func, views.post)
